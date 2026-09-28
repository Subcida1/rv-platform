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
CACHE = pathlib.Path("/tmp/quote-source-cache")
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
    out = []
    for m in re.finditer(r"<b>\s*[\"\"](.*?)[\"\"]\s*</b>", body, re.S):
        q = norm(m.group(1))
        if len(q.split()) >= 6 and looks_like_prose(q):
            out.append(q)
    for m in re.finditer(r"[\"\"]([^\"\"<>]{40,400})[\"\"]", body):
        q = norm(m.group(1))
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


def fetch(url):
    """Cached fetch. PDFs are downloaded and read with pdftotext, which is how the verifiers read them."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    cached = CACHE / key
    if cached.exists():
        return cached.read_text(encoding="utf-8", errors="replace")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
    except Exception as e:
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
    txt = norm(txt)
    cached.write_text(txt, encoding="utf-8")
    return txt


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
                corpus.append(cached.read_text(encoding="utf-8", errors="replace"))
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
    def word_run(needle, hay, need=0.85):
        """Fallback for character-level disagreement between a page and its source.

        Found by re-running after the first fix: "low gas pressure caused by a number of factors..." is
        genuinely on the Suburban FAQ page cited for it, and "Do not use silicone..." is genuine Dicor
        text, and both still read as missing because the page and its PDF punctuate them differently.
        An instrument that flags correct behaviour teaches its reader to ignore it, so before calling a
        quote absent, allow a word sequence that is at least 85 percent present in order.
        """
        nw = needle.split()
        if len(nw) < 5:
            return needle in hay
        hw = hay.split()
        if len(hw) < len(nw):
            return False
        # Positional word comparison is not enough. ONE inserted word shifts every following word, so
        # "remove the old sealant | because ..." scored 53 percent against a source reading "remove the
        # old sealant | TO because ..." - a single stray word the page had tidied, reported as a missing
        # source. SequenceMatcher compares subsequences, so an insert or a delete does not defeat it.
        for start in range(0, len(hw) - len(nw) + 1):
            if difflib.SequenceMatcher(None, nw, hw[start:start + len(nw)]).ratio() >= need:
                return True
        return False

    corpus_fold = [c.lower() for c in corpus]

    def present(q, c):
        """A quote containing an ellipsis has had text omitted, so check its fragments separately.
        The first run flagged genuine Winnebago wording as unsourced purely because the page wrote
        "... on the roof ..." while the manual writes it as one sentence."""
        frags = [f.strip() for f in re.split(r"\s*\.\.\.+\s*|\s*\u2026\s*", q) if len(f.split()) >= 3]
        return all(any(f.lower() in cf or word_run(f.lower(), cf) for cf in corpus_fold)
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
        best = (0, None)
        for c in corpus:
            cw = c.lower().split()
            for start in range(0, max(1, len(cw) - len(qw) + 1)):
                window = cw[start:start + len(qw)]
                hits = sum(1 for a, b in zip(qw, window) if a == b)
                if hits > best[0]:
                    best = (hits, " ".join(window))
        if best[1] and best[0] / max(1, len(qw)) >= 0.7:
            return best[0] / len(qw), best[1]
        return 0, None

    missing, near = [], []
    for q in qs:
        if present(q, corpus):
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
