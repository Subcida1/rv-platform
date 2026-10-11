#!/usr/bin/env python3
"""Check that the quotations on a page actually appear in the documents it cites.

WHY THIS EXISTS. Five independent verifiers checked five guides on 2026-09-27 and every one found defects.
Not one was fabrication: in every single case the words were GENUINE manufacturer language and the
CITATION was wrong - a Kidde sentence credited to a Kidde page that does not carry it, a Winnebago
sentence from a different model's manual, a REMCO troubleshooting line attributed to Aquatec, an ASHRAE
figure from Standard 62.1 cited to the FAQ for Standard 55.

Every one of those pages had had its URLs verified. They all resolved 200. **A URL resolving is not the
same as the quoted sentence being in it**, and only the second test would have caught any of this.

WHAT THIS DOES, AND WHAT IT DELIBERATELY DOES NOT. It extracts the quotations from a page, fetches every
source the page cites, and reports any quotation that appears in NONE of them. That is the honest limit of
a mechanical check here: the page states which sources it used but does not pair each quote to one, so
this cannot say "this quote belongs to the wrong source" - only "this quote is not in anything you cited",
which is the failure that matters and the one a human then resolves in seconds.

A quote that passes is NOT proven correctly attributed. It is proven to exist somewhere in the page's
sources, which is strictly weaker. Read the report as a filter, not a verdict.

IT USED TO NOT SCALE PAST ABOUT FORTY SOURCES, AND THE EARLIER DIAGNOSIS OF WHY WAS WRONG.
Measured 2026-10-07 against manuals/start-here.html (187 sources, 404 quotations): a run exceeded 50
minutes with --no-fetch and timed out with the cache warm, so the cost was not the network. The note
left here blamed near_miss(). Instrumenting both functions on 2026-10-08 showed near_miss() never
even ran: the time is in present()'s word_run() fallback, because a quotation that is genuinely
absent costs a full sliding-window scan of every document, and then near_miss() costs a second one.
Measured per quotation: 19 seconds average, 42 seconds for the worst, against 167 documents.

THE FIX, and it is the one the note proposed for near_miss() applied to both. A near-miss can only
be found where the quotation's own words occur, so the positions of every word the page quotes are
indexed once, and both fallbacks visit those positions instead of all of them. Two different rules
decide which positions:

  near_miss() is EXACTLY equivalent at its threshold and that is provable, not hoped for. A window is
  only reported when at least ceil(0.7n) of its words match, and a window that matches no word from
  any set S of n-need+1 quote positions can supply at most need-1 matches. So anchoring on the
  rarest n-need+1 distinct quote words cannot hide a qualifying window.

  word_run() is a heuristic by nature, because difflib compares characters rather than words and no
  word-level rule bounds a character ratio exactly. It anchors on the quotation's rarest words of
  five characters or more; a window that has altered every one of them while still matching 85
  percent of the characters is not a thing a tidy-up produces. The differential test that backs this
  claim is described at the call site.

Do NOT simply cap the number of starts: that would turn a slow true answer into a fast false one, and
a false "not in any cited source" is the failure this whole file exists to avoid.

Run:
  python3 scripts/check-quotes.py                          # every guide
  python3 scripts/check-quotes.py guides/rv-delamination.html
  python3 scripts/check-quotes.py --no-fetch               # use the cache only, never hit the network
"""
import difflib
import hashlib
import html as H
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
# ON DISK, NOT IN /tmp. On the-grid /tmp is a 7.8G tmpfs, so this cache was spending RAM:
# by 2026-10-10 it held 907MB and the link-intent cache another 725MB, both of them on the
# tmpfs-reaper's PROTECT list because refetching bot-protected sources is expensive. The
# reaper's own note says the answer is to relocate them rather than delete them, so they
# live under ~/.cache now (disk-backed, 100G free) and /tmp went from 2.9G to 76M.
CACHE = pathlib.Path.home() / ".cache" / "originrv" / "quote-source-cache-v2"   # v2 stores RAW text and normalises on read
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/154.0.0.0 Safari/537.36")


def norm(s):
    """Whitespace, quote style and markup all vary between a page and its source; flatten them all."""
    s = H.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2014", "-"), ("\u2013", "-"), ("\u00a0", " "),
                 # the marks a page and a PDF disagree about: inch/foot primes, primes, low quotes
                 ("\u2033", '"'), ("\u2032", "'"), ("\u2039", "<"), ("\u203a", ">"),
                 ("\u201a", ","), ("\u201e", '"'), ("\u02bc", "'"), ("\u2122", "(tm)")):
        s = s.replace(a, b)
    # QUOTE MARKS. A page integrating a quotation may set it in single or double marks and the source may
    # do the opposite - "structural components" against 'Structural Components'. Unifying them is not a
    # judgement about style, it is removing a difference that has nothing to do with the words.
    for a in ("\u2018", "\u2019", "\u201a", "\u02bc", "\u2032", "\u201c", "\u201d", "\u201e", "\u2033"):
        s = s.replace(a, '"')
    # SUPERSCRIPTS. PDF extraction renders ft2, m3, 100 as ft2 / m3 / 100; a page writes ft.2 or ft2.
    for a, b in (("\u00b2", "2"), ("\u00b3", "3"), ("\u00b9", "1"), ("\u2070", "0")):
        s = s.replace(a, b)
    # FRACTIONS. A manual prints "approximately 1/2 inch" with a single fraction glyph; a page integrating
    # the same sentence writes "1/2 inch". Found by chasing one reported missing quote back into the cache,
    # where the source had it all along.
    for a, b in (("\u00bd", "1/2"), ("\u00bc", "1/4"), ("\u00be", "3/4"), ("\u2153", "1/3"),
                 ("\u2154", "2/3"), ("\u215b", "1/8"), ("\u215c", "3/8"), ("\u215d", "5/8")):
        s = s.replace(a, b)
    s = unify_units(s)
    return re.sub(r"\s+", " ", s).strip()


# the same measurement is written several ways across a page and its source; make them one way
UNIT_SUBS = (
    (r"(\d+)\s*(?:\u00b0|deg(?:rees)?)\s*F\b", r"\1 F"),
    (r"(\d+)\s*(?:\u00b0|deg(?:rees)?)\s*C\b", r"\1 C"),
    (r"(\d)\s*[\u2033\"]\s*(?:\[|\()?\s*(\d+)\s*mm", r"\1 inch (\2mm)"),
    (r"(\d+)\s*/\s*(\d+)\s*[\u2033\"]", r"\1/\2 inch"),
    (r"\bpsi\b", "PSI"), (r"\bwc\b", "WC"),
)


def unify_units(s):
    for pat, rep in UNIT_SUBS:
        s = re.sub(pat, rep, s, flags=re.I)
    return s


def looks_like_prose(q):
    """Reject anything that is not a sentence a person would quote.

    Learned from the first run, which reported the page's own <title> and meta description as quotations
    and ALSO reported an SVG path definition ("M8.2 16L8.2 13.6L9 13.2...") as one. Neither is a quote;
    both were pure noise in a report whose whole value is that a human only reads the hits.
    """
    if not re.search(r"[a-z]{3}", q):          # no ordinary words at all
        return False
    letters = sum(c.isalpha() or c.isspace() for c in q)
    if len(q) and letters / len(q) < 0.6:      # mostly digits, punctuation or path commands
        return False
    if re.search(r"\d+\.\d+\s+\d+\.\d+", q):  # coordinate pairs
        return False
    return True


def quotes_on_page(text):
    """Quotations from the BODY only, markup-free so matching is on words rather than tags.

    The <head> is skipped deliberately: a page's own title and meta description are its own words, not
    somebody else's, and reporting them as unsourced quotations is noise.
    """
    body = text.split("<body", 1)[1] if "<body" in text else text
    # Strip attribute values before looking for quotations. An alt or title attribute is a description of
    # an IMAGE, not a quotation from anybody, and the sweep reported three of them as unsourced quotes -
    # "Schematic of an RV 12-volt system...", "A Honda EU2000i portable inverter generator". Same class as
    # reading the <title> as a quote: the page describing itself is not the page quoting a source.
    body = re.sub(r'\b(?:alt|title|aria-label|placeholder)="[^"]*"', " ", body)
    # A SCRIPT BLOCK IS NOT PROSE. The breadcrumb's JSON-LD carries the page's own name inside
    # quotation marks, so the general pass read "New RV Owner: The Things to Get Right First" as a
    # quotation and reported the page's own title as missing from its sources. Exactly the class the
    # <title> exclusion above exists for: a page describing itself is not a page quoting anybody.
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S)
    # THE GENERAL PASS READS TEXT, NOT MARKUP, AND THAT IS THE POINT.
    # Found 2026-10-02 while adding a guide that quotes heavily: this pass matched against raw
    # HTML, where an ATTRIBUTE quote pairs with a real opening quotation mark, the span between
    # them ends at that mark, and finditer resumes past it. Quotations after the first stray
    # attribute were skipped, and the page reported "0 quote(s), nothing to check" while
    # carrying fifteen of them. An instrument that reports nothing on a page full of
    # quotations is worse than none, because a zero reads as a pass. Tags are stripped to a
    # space rather than deleted so word runs stay intact.
    plain = re.sub(r"<[^>]+>", " ", body)
    # A bolded quotation is consumed by the pass above, so its marks are removed here. Left in,
    # a SHORT bolded quote ("clog at pump inlet", four words, below the length floor) leaves a
    # pair of stray marks that the general pass then matches as one long span, capturing our own
    # prose between them and reporting it as a quotation from a source. That is a false positive
    # against correct writing, which is the one output this tool must never produce.
    plain = re.sub(r'<b>\s*[""](.*?)[""]\s*</b>', " ", plain, flags=re.S)
    out = []
    for m in re.finditer(r"<b>\s*[\"\"](.*?)[\"\"]\s*</b>", body, re.S):
        q = norm(m.group(1))
        if len(q.split()) >= 6 and looks_like_prose(q):
            out.append(q)
    # Marks are consumed in ORDERED PAIRS rather than by a length-limited regex match.
    # finditer only consumes a match when the span is 40 to 400 characters, so a SHORT quoted
    # fragment (our own prose quoting an owner: "It just hums") left two stray marks in the text
    # and the next match paired them across the sentences in between, reporting our own writing
    # as a quotation missing from a source. Pairing every mark strictly 1-2, 3-4 and then
    # filtering by length means a short quote consumes its own marks and cannot drag a span.
    marks = [m.start() for m in re.finditer(r"[\"\"]", plain)]
    for a, b in zip(marks[0::2], marks[1::2]):
        inner = plain[a + 1:b]
        if not (40 <= len(inner) <= 400):
            continue
        q = norm(inner)
        if len(q.split()) >= 6 and q not in out and looks_like_prose(q):
            out.append(q)
    return out


def sources_on_page(text):
    """Every external URL the page's Sources block links to."""
    urls = []
    for m in re.finditer(r'href="(https?://[^"]+)"', text):
        u = m.group(1)
        if "originrv.com" in u or u.endswith(".css") or u.endswith(".js"):
            continue
        if u not in urls:
            urls.append(u)
    return urls


CHROME_PROFILE = "/tmp/quotefetch-chrome"


CHALLENGE_MARKERS = (
    "just a moment", "enable javascript", "checking your browser", "cf-browser-verification",
    "cf-chl-", "attention required", "please verify you are a human", "ddos protection",
)


def looks_like_challenge(text):
    """True when a fetch returned an interstitial rather than the document.

    Learned the hard way. The browser fallback accepted a Cloudflare challenge page as a successful fetch -
    23 KB of "Just a moment..." passed a length check - and then every quotation from that source was
    reported as MISSING. That is the worst possible failure for this tool: a false negative that looks
    exactly like a real finding, produced by the very mechanism added to remove them. Two different
    Airstream URLs came back 28,975 and 28,954 bytes, which is what gave it away - identical sizes for
    different articles.
    """
    low = text[:4000].lower()
    return any(m in low for m in CHALLENGE_MARKERS)


def fetch_browser(url, budget=9000):
    """Second attempt at a source, through a real browser engine.

    WHY THIS EXISTS. Some of the sources this site cites refuse a plain HTTP client and work perfectly for
    a reader: government pages returning 403, and makers behind Cloudflare that serve a challenge to
    anything automated. The first pass reported those as unreachable and could not be judged at all, which
    left thirteen guides with a permanent hole in their verification.

    Flags chosen from what already works on this machine: flatpak Chrome, --headless=new, and a
    --virtual-time-budget so client-rendered pages have time to build their content before the DOM is
    dumped. The dedicated profile directory matters - using the default one races with the Chrome the user
    is running for his own work, and launching into a live profile can fail or, worse, disturb it.

    Deliberately NOT a guarantee: a web application firewall that refuses browsers too will still refuse
    this, and the caller reports that as blocked rather than quietly treating it as searched.
    """
    import subprocess
    cmd = ["flatpak", "run", "com.google.Chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
           f"--user-data-dir={CHROME_PROFILE}", f"--virtual-time-budget={budget}",
           "--dump-dom", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return r.stdout or ""
    except Exception:
        return ""


def fetch(url):
    """Cached fetch. PDFs are downloaded and read with pdftotext, which is how the verifiers read them."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    cached = CACHE / key
    if cached.exists():
        raw_cached = cached.read_text(encoding="utf-8", errors="replace")
        if looks_like_challenge(raw_cached):
            return "__FETCH_FAILED__ cached copy is a challenge page"
        # normalise HERE, not before writing. The v1 cache stored normalised text, so every change to the
        # normalisation rules silently invalidated every source already fetched - and a stale-normalised
        # source reads as a missing quotation, which is indistinguishable from a real finding.
        return norm(cached.read_text(encoding="utf-8", errors="replace"))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
    except Exception as e:
        # SECOND ATTEMPT, through a real browser. Government pages return 403 to an HTTP client while
        # working fine for a reader, and makers behind Cloudflare serve a challenge to anything automated.
        # The first pass could not judge those at all, which left thirteen guides permanently unverifiable.
        dom = fetch_browser(url)
        if dom and looks_like_challenge(dom):
            return f"__FETCH_FAILED__ browser got a challenge page, not the document"
        if dom and len(norm(dom)) > 600:
            cached.write_text(dom, encoding="utf-8")
            return norm(dom)
        # NEVER cache a failure. Writing "" on error means one transient network blip poisons the cache
        # permanently: a later --no-fetch run reads empty for that source and reports every quote from it
        # as missing, which is a silent false positive generator with no way to tell it apart from a real
        # finding.
        return f"__FETCH_FAILED__ {e}"
    if raw[:4] == b"%PDF":
        tmp = CACHE / (key + ".pdf")
        tmp.write_bytes(raw)
        try:
            import subprocess
            txt = subprocess.run(["pdftotext", str(tmp), "-"], capture_output=True, text=True,
                                 timeout=90).stdout
        except Exception:
            txt = ""
    else:
        txt = raw.decode("utf-8", errors="replace")
    cached.write_text(txt, encoding="utf-8")
    return norm(txt)


def check(path, no_fetch=False):
    text = path.read_text(encoding="utf-8")
    qs, urls = quotes_on_page(text), sources_on_page(text)
    if not qs or not urls:
        print(f"  {path.name}: {len(qs)} quote(s), {len(urls)} source(s) - nothing to check")
        return 0
    corpus, failed, thin, failed_urls = [], 0, [], []
    if no_fetch:
        for u in urls:
            cached = CACHE / hashlib.sha256(u.encode()).hexdigest()[:20]
            if cached.exists():
                corpus.append(norm(cached.read_text(encoding="utf-8", errors="replace")))
    else:
        for u in urls:
            t = fetch(u)
            if t.startswith("__FETCH_FAILED__"):
                failed += 1
                # list them, or a count is all you get and you cannot tell a WAF block from a typo
                failed_urls.append((u, t.replace("__FETCH_FAILED__", "").strip()[:90]))
            elif len(t) < 600:
                # Fetched, but there is almost no text in it. On these sites that means the page builds
                # its content in JavaScript, so an HTTP fetch returns a shell. Treating a shell as a
                # searched source is how a perfectly good quotation gets reported as unsourced.
                thin.append(u)
            corpus.append(t)
    # ONE index for the whole page. Every word the page quotes is looked up by position, so the two
    # fallbacks below visit only the places a match could possibly be, instead of every word position
    # of every document, once per quotation. See the module docstring for the measurement that
    # forced this. Memory is bounded by the words actually quoted, not by the corpus: on
    # manuals/start-here.html that is 1.16M corpus words against an index of a few hundred thousand
    # entries, where indexing the whole corpus would have been a needless multiple of it.
    quoted = {w for q in qs for w in q.lower().split()}
    doc_words, index = [], {}
    for di, c in enumerate(corpus):
        cw = c.lower().split()
        doc_words.append(cw)
        for p, w in enumerate(cw):
            if w in quoted:
                index.setdefault(w, []).append((di, p))

    def word_run(needle, di, need=0.85):
        """Fallback for character-level disagreement between a page and its source.

        Found by re-running after the first fix: "low gas pressure caused by a number of factors..." is
        genuinely on the Suburban FAQ page cited for it, and "Do not use silicone..." is genuine Dicor
        text, and both still read as missing because the page and its PDF punctuate them differently.
        An instrument that flags correct behaviour teaches its reader to ignore it, so before calling a
        quote absent, allow a word sequence that is at least 85 percent present in order.
        """
        nw = needle.split()
        if len(nw) < 5:
            return needle in corpus_fold[di]
        hw = doc_words[di]
        if len(hw) < len(nw):
            return False
        # Positional word comparison is not enough. ONE inserted word shifts every following word, so
        # "remove the old sealant | because ..." scored 53 percent against a source reading "remove the
        # old sealant | TO because ..." - a single stray word the page had tidied, reported as a missing
        # source. SequenceMatcher compares subsequences, so an insert or a delete does not defeat it.
        # Anchor on the rarest words of five characters or more, at their position in the quotation.
        # THE TEST THAT BACKS THIS: the old full scan and this one were run side by side over every
        # quotation on the page that reaches this function, and the verdicts were compared one by
        # one. It is a heuristic, not a proof, so if it ever disagrees with the old code the old code
        # wins and this goes back to the full scan.
        anchors = sorted({w for w in nw if w in index and len(w) >= 5},
                         key=lambda w: len(index[w]))[:5]
        if not anchors:
            starts = range(0, len(hw) - len(nw) + 1)
        else:
            cand = set()
            for i, w in enumerate(nw):
                if w not in anchors:
                    continue
                for d, p in index[w]:
                    if d == di:
                        s = p - i
                        if 0 <= s <= len(hw) - len(nw):
                            cand.add(s)
            starts = sorted(cand)
        for start in starts:
            if difflib.SequenceMatcher(None, nw, hw[start:start + len(nw)]).ratio() >= need:
                return True
        return False

    corpus_fold = [c.lower() for c in corpus]

    def present(q):
        """A quote containing an ellipsis has had text omitted, so check its fragments separately.
        The first run flagged genuine Winnebago wording as unsourced purely because the page wrote
        "... on the roof ..." while the manual writes it as one sentence."""
        frags = [f.strip() for f in re.split(r"\s*\.\.\.+\s*|\s*\u2026\s*", q) if len(f.split()) >= 3]
        return all(any(f.lower() in cf or word_run(f.lower(), di)
                       for di, cf in enumerate(corpus_fold))
                   for f in (frags or [q]))

    def near_miss(q):
        """Distinguish "not in any source" from "in a source but not verbatim".

        Found by investigating three reported hits: each one WAS in a cited source, and differed by a
        character or a word the page had silently tidied. One source reads "remove the old sealant TO
        because a bad surface..." and the page quoted it without the stray "to"; another reads "...by T
        molding. Q. With the slide out..." and the page joined the two sentences and dropped the "Q.".
        Those are quotation-fidelity defects, not missing sources, and they deserve saying differently -
        a reader checking either quote against the maker's page finds words that do not match.
        """
        qw = q.lower().split()
        n = len(qw)
        if n == 0:
            return 0, None
        need = (7 * n + 9) // 10          # ceil(0.7n), the integer form of the test at the end
        # A window is reported only when at least `need` of its words match, and a window matching no
        # word from any set covering n-need+1 quote POSITIONS can supply at most need-1 matches. So
        # anchoring on the rarest such words cannot hide a window that would have been reported:
        # every qualifying window matches at least one anchor, at its own position, and is generated
        # here. That is why this is a fix and not a compromise.
        anchors, seen = set(), set()
        for w in sorted(set(qw), key=lambda w: len(index.get(w, ()))):
            seen.add(w)
            anchors.add(w)
            if sum(1 for x in qw if x in seen) >= n - need + 1:
                break
        cand = {}
        for i, w in enumerate(qw):
            if w not in anchors:
                continue
            for di, p in index.get(w, ()):
                s = p - i
                if s >= 0 and s + n <= len(doc_words[di]):
                    cand.setdefault(di, set()).add(s)
        best = (0, None)
        for di, cw in enumerate(doc_words):
            if len(cw) < n:
                # The scan this replaces compared one truncated window here. Keeping it costs a few
                # words and preserves the old behaviour exactly, which is cheaper than arguing about
                # a document shorter than the quotation.
                window = cw[:n]
                hits = sum(1 for a, b in zip(qw, window) if a == b)
                if hits > best[0]:
                    best = (hits, " ".join(window))
                continue
            starts = cand.get(di)
            if not starts:
                continue
            for start in sorted(starts):
                window = cw[start:start + n]
                hits = sum(1 for a, b in zip(qw, window) if a == b)
                if hits > best[0]:
                    best = (hits, " ".join(window))
        if best[1] and best[0] / max(1, n) >= 0.7:
            return best[0] / n, best[1]
        return 0, None

    missing, near = [], []
    for q in qs:
        if present(q):
            continue
        ratio, src = near_miss(q)
        (near if src else missing).append((q, ratio, src))
    print(f"\n  {path.name}")
    print(f"    {len(qs)} quotes against {len(urls)} sources"
          f"{f', {failed} unreachable' if failed else ''}")
    if failed:
        print(f"    WARNING {failed} source(s) could not be fetched, so quotes from them will read as")
        print("            missing. Check the unreachable URLs before believing any hit below.")
        for u, why in failed_urls:
            print(f"              {u}")
            print(f"                {why}")
    if thin:
        print(f"    WARNING {len(thin)} source(s) returned almost no text - they are probably rendered in")
        print("            JavaScript, so an HTTP fetch cannot see their content. Any hit below may be")
        print("            quoting one of these correctly:")
        for u in thin:
            print(f"              {u}")
    if not missing:
        print("    every quote appears somewhere in the cited sources")
    for q, ratio, src in near:
        print(f"    NOT VERBATIM ({int(ratio*100)}% word match) - the page has tidied it:")
        print(f"      page:   {q[:150]}")
        print(f"      source: {src[:150]}")
    for q, _, _ in missing:
        print(f"    NOT IN ANY CITED SOURCE: {q[:150]}")
    return len(missing) + len(near)


def check_links(path):
    """Every source a page cites, fetched for status alone.

    WHY THIS IS SEPARATE FROM THE QUOTE CHECK. That check only touches a URL if the page happens to quote
    something attributed to it, so a dead citation with no quotation attached is invisible to it - and the
    condensation page had exactly that problem twice: an ASHRAE PDF returning 404 and an Airstream article
    URL that had been guessed rather than checked, both found only by accident while chasing something else.
    A citation is a promise that a document exists. This tests the promise directly.

    A 403 is reported as BLOCKED rather than dead: several makers here sit behind a web application
    firewall or Cloudflare, and one of those (Airstream) is known to serve 403 to everything automated
    while working perfectly in a browser.
    """
    text = path.read_text(encoding="utf-8")
    urls = sources_on_page(text)
    if not urls:
        return 0
    import urllib.error
    dead, blocked = [], []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                r.read(2048)
        except urllib.error.HTTPError as e:
            (blocked if e.code in (401, 403, 429) else dead).append((u, str(e.code)))
        except Exception as e:
            dead.append((u, type(e).__name__))
    print(f"\n  {path.name}: {len(urls)} source(s), {len(dead)} dead, {len(blocked)} blocked")
    for u, why in dead:
        print(f"    DEAD      {why:>4}  {u}")
    for u, why in blocked:
        print(f"    blocked   {why:>4}  {u}")
    return len(dead)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_fetch = "--no-fetch" in sys.argv
    if "--links-only" in sys.argv:
        pages = ([pathlib.Path(a) for a in args] if args
                 else sorted(q for q in (ROOT / "guides").glob("*.html") if q.name != "index.html"))
        total = sum(check_links(q) for q in pages)
        print(f"\n  dead source links: {total}")
        print("  BLOCKED is not dead: several makers serve 403 to automation and work fine in a browser.")
        return
    pages = ([pathlib.Path(a) for a in args] if args
             else sorted(p for p in (ROOT / "guides").glob("*.html") if p.name != "index.html"))
    total = sum(check(p, no_fetch) for p in pages)
    print(f"\n  quotes not found in any cited source: {total}")
    print("  a quote that PASSES is only proven to exist SOMEWHERE in the sources, not in the right one.")


if __name__ == "__main__":
    main()
