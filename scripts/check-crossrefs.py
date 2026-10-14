#!/usr/bin/env python3
"""A sentence refers to a section or a page we wrote, and does not link to it.

WHY THIS EXISTS. Ty, 2026-10-13: "We straight up refer to another section, but don't link
out to it? That's a huge huge no no we should ALWAYS provide a link if we feel the need to
mention another section we have content for." The live case that opened it, from
guides/rv-outlets-not-working.html:

    <h3>Any shock or tingle from the bodywork</h3>
    <p>Stop here and read the hot skin section. That is a different class of problem.</p>

There is a "Hot skin" <h2> further down that SAME page, and the sentence points at it with
no <a>. The reader has to scroll and hunt for a section we could have linked for free. The
same defect appears cross-page: "see the guide on X" where X is a page we wrote.

FALSE POSITIVES ARE THE ENEMY, so the rules are deliberately narrow and every one of them
resolves the reference before it reports it:

  * An in-page reference is only flagged when the named target MATCHES A HEADING ON THAT
    PAGE. "the hot skin section" on a page with an "Hot skin" <h2> is a real pointer; a
    phrase that names no heading here is not our content and is left alone.
  * A cross-page reference is only flagged when the named target MATCHES A PAGE WE HAVE
    ("the furnace guide" only fires on a site that HAS a furnace page). "your owner's
    manual" names no page of ours and can never fire.
  * A reference followed by "of the/your ..." is a section of SOMEBODY ELSE'S document
    ("the maintenance section of the warranty guide") and is never flagged.
  * Any <a> in the same sentence, or an anchor ending immediately before it, clears the
    sentence. A sentence that links is doing the right thing.
  * A directional pointer has to be an explicit one: "see/read ... above|below", "covered
    above|below", "further down this page", "the section above|below", "the next section".
    "the readings below", "the cross-section", "a section of cable", "the method described
    above" are NOT section pointers and are left alone. This is where most of the judgement
    sits; the broad version fired on 20 good sentences, so the narrow version ships.

WHAT IT DOES NOT DO: it cannot tell whether the link it wants is already the subject of the
sentence's own link, and it does not judge which of two pages is the better destination. It
reports the reference and the thing it appears to point at; the reading is the work.

Run:  python3 scripts/check-crossrefs.py              report, exit 1 when it finds any
      python3 scripts/check-crossrefs.py --self-test  prove the rules catch and do not over-catch
"""
import argparse
import html as _html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The path parts that are never published source. Copied from scripts/verify.py on purpose;
# .letta holds agent worktrees that are full copies of this repo and walking into one scans
# the worktree's pages as if they were the site.
SKIP_PARTS = {".git", ".letta", ".canary.lock", "node_modules", "_log", "_data"}

# Words that carry no subject. A reference made only of these names nothing we can point at.
STOP = {
    "the", "a", "an", "and", "or", "of", "on", "in", "to", "for", "with", "at", "by", "as",
    "is", "are", "was", "were", "be", "been", "has", "have", "had", "it", "its", "this",
    "that", "these", "those", "we", "our", "us", "you", "your", "they", "their", "them",
    "here", "there", "when", "where", "which", "what", "who", "how", "why", "if", "then",
    "than", "so", "but", "not", "no", "all", "any", "each", "one", "two", "three", "next",
    "same", "other", "another", "more", "most", "own", "whole", "last", "first", "before",
    "after", "down", "up", "out", "about", "into", "over", "under", "again", "also", "very",
    "every", "both", "several", "some", "many", "such", "just", "still", "only", "even",
}
# Subject words that are too generic to prove we own the thing being named. The agent nouns
# ("maker", "manufacturer", "brand" ...) are here because "the maker's towing guide" names
# SOMEBODY ELSE'S document, not one of our pages; the same goes for "owner's".
GENERIC = {
    "guide", "guides", "page", "pages", "section", "sections", "article", "chapter",
    "part", "parts", "rv", "rvs", "thing", "stuff", "above", "below",
    "manual", "manuals", "book", "document", "documentation", "warranty", "owner", "owners",
    "maker", "makers", "manufacturer", "manufacturers", "brand", "brands", "supplier",
    "suppliers", "dealer", "dealers", "vendor", "vendors", "shop", "shops", "support",
    "replacement", "troubleshooting", "diagnostic", "diagnostics", "complete",
}
# A sentence that says the thing IS linked is describing the link, not missing it.
LINK_WORD = re.compile(r"\blink(?:ed|s|ing)?\b", re.I)
MIN_SENTENCE = 12        # shorter than this is not prose worth judging (see check-prose.py)


# ---------------------------------------------------------------------------- page walking
def walked(pattern):
    """Every path matching the pattern inside THIS checkout, and nothing outside it.

    The test is on the path RELATIVE to ROOT, the same reason verify.py gives: in an agent
    worktree the absolute path of every file contains ".letta", so an absolute-path prune
    matches everything and the scan passes over nothing at all.
    """
    return sorted(p for p in ROOT.rglob(pattern)
                  if not (SKIP_PARTS & set(p.relative_to(ROOT).parts)))


def _blank(m):
    """Replace a region with spaces but KEEP its newlines, so line numbers survive."""
    return "".join("\n" if c == "\n" else " " for c in m.group(0))


REGIONS = (
    r"<script\b[^>]*>.*?</script>",
    r"<style\b[^>]*>.*?</style>",
    r"<svg\b[^>]*>.*?</svg>",
    # HEADINGS ARE NOT PROSE. Scanning them produced a false positive on every guide whose
    # H1 ends "The complete guide": the H1's own words were read as a sentence referring to
    # "the complete ... guide". The headings are still read from the raw HTML for in-page
    # resolution; they are just not scanned as prose.
    r"<h[1-4]\b[^>]*>.*?</h[1-4]>",
    r"<head\b[^>]*>.*?</head>",
    r"<!--\s*nav:start\s*-->.*?<!--\s*nav:end\s*-->",
    r"<!--\s*footer:start\s*-->.*?<!--\s*footer:end\s*-->",
    r"<!--.*?-->",
)


def article_html(raw):
    """Only the article prose, with every character's position preserved.

    Nav, footer, head, scripts, styles and SVG are blanked rather than sliced out, and the
    result is trimmed to the <main> element, so a line number computed against this string
    is the line number in the real file.
    """
    for pat in REGIONS:
        raw = re.sub(pat, _blank, raw, flags=re.S | re.I)
    out = list(raw)
    head = re.search(r"<main\b[^>]*>", raw, re.I)
    tail = re.search(r"</main>", raw, re.I)
    a = head.start() if head else 0
    b = tail.end() if tail else len(raw)
    for i in range(a):
        if out[i] != "\n":
            out[i] = " "
    for i in range(b, len(out)):
        if out[i] != "\n":
            out[i] = " "
    return "".join(out)


def visible_map(html):
    """(text, offsets): the words a reader sees, and where each one sits in `html`."""
    text, offs, i = [], [], 0
    for m in re.finditer(r"<[^>]*>", html):
        for j in range(i, m.start()):
            text.append(html[j]); offs.append(j)
        i = m.end()
    for j in range(i, len(html)):
        text.append(html[j]); offs.append(j)
    return "".join(text), offs


def sentences_of(text, offs):
    """Yield (start, end) spans in `text` for each sentence, trimmed of edge whitespace."""
    for m in re.finditer(r"[^.!?]*[.!?]+|[^.!?]+$", text):
        s, e = m.start(), m.end()
        while s < e and text[s].isspace():
            s += 1
        while e > s and text[e - 1].isspace():
            e -= 1
        if e - s >= MIN_SENTENCE:
            yield s, e


def headings_of(raw):
    """The visible heading text on a page, as token sets."""
    out = []
    for m in re.finditer(r"<h[1-4]\b[^>]*>(.*?)</h[1-4]>", raw, re.S | re.I):
        txt = _html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
        toks = tokens(txt)
        if toks:
            out.append((re.sub(r"\s+", " ", txt).strip(), toks))
    return out


def title_tokens(raw):
    """The distinctive subject words a page advertises: its title, its H1 and its slug."""
    out = set()
    for pat in (r"<title\b[^>]*>(.*?)</title>", r"<h1\b[^>]*>(.*?)</h1>"):
        m = re.search(pat, raw, re.S | re.I)
        if m:
            out |= tokens(_html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))))
    return out


def tokens(text):
    """Lowercased content words, with stops and non-subject words dropped."""
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return {w for w in words if w not in STOP and len(w) >= 4 and w not in GENERIC}


# How far into a heading a named reference is allowed to match. Six words covers "The
# voltage-drop test", "Low voltage: The fault" and "Sizing: Can it run", and it excludes a
# word eight tokens into a long heading, which is an incidental collision rather than a named
# section.
LEADING_WINDOW = 6


def leading_tokens(label):
    """The opening content words of a heading, with a leading article skipped."""
    words = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", label.lower())
    if words and words[0] in ("a", "an", "the"):
        words = words[1:]
    return tokens(" ".join(words[:LEADING_WINDOW]))


# ------------------------------------------------------------------------------- detectors
# In-page: an explicit pointer that names no target. The shapes come straight from the brief.
INPAGE_DIRECTIONAL = (
    r"\b(?:see|read)\s+(?:the\s+section\s+)?(?:above|below)\b",
    r"\bcovered\s+(?:above|below)\b",
    r"\bfurther\s+down\s+this\s+page\b",
    r"\bthe\s+section\s+(?:above|below)\b",
    r"\b(?:the\s+)?next\s+section\b",
)
# In-page: "the X section" (X is a short subject phrase) optionally with a direction. X is
# resolved against the page's own headings, so a name that matches nothing here is left alone.
INPAGE_STRICT = (
    r"\bthe\s+(?P<ref>[\w'’-]+(?:\s+[\w'’-]+){0,4}?)\s+section\s+(?:above|below)\b",
    r"\bthe\s+(?P<ref>[\w'’-]+(?:\s+[\w'’-]+){0,4}?)\s+section\b",
)
# In-page: "the section on X". X is a CLAUSE, so stopwords are expected in it; only the
# heading match decides whether we own it.
INPAGE_CLAUSE = (
    r"\bthe\s+section\s+on\s+(?P<ref>[^.,;:!?]{1,60}?)(?=[.,;:!?]|\s+(?:that|which|is|are|and|where|below|above|for)\b|$)",
)
# Cross-page: "the X guide" / "the X page". X is a short subject phrase and is resolved
# against the pages we publish, so a name that matches no page is left alone.
CROSSPAGE_STRICT = (
    r"\b(?:the|our)\s+(?P<ref>[\w'’-]+(?:\s+[\w'’-]+){0,4}?)\s+guide\b",
    r"\b(?:the|our)\s+(?P<ref>[\w'’-]+(?:\s+[\w'’-]+){0,4}?)\s+page\b",
)
# Cross-page: "the guide on X" / "the page on X". X is a clause.
CROSSPAGE_CLAUSE = (
    r"\b(?:see|read)\s+the\s+guide\s+on\s+(?P<ref>[^.,;:!?]{1,60}?)(?=[.,;:!?]|\s+(?:that|which|is|and|for)\b|$)",
    r"\b(?:see|read)\s+the\s+page\s+on\s+(?P<ref>[^.,;:!?]{1,60}?)(?=[.,;:!?]|\s+(?:that|which|is|and|for)\b|$)",
)
# A "section of the/your/its X" is a section of somebody else's document. Not our content.
EXTERNAL_TAIL = re.compile(r"\s+of\s+(?:the|your|our|its|their|a|an|this)\b", re.I)


def owns_page(ref, page_tokens):
    """The page a named target most likely points at, or None when it points at none of ours.

    Scoring rather than a bare membership test, so the reported destination names the page
    with the strongest overlap ("our black tank guide" reports the black tank page, not
    whichever page happened to share one word).
    """
    toks = tokens(ref)
    if not toks:
        return None
    best, best_n = None, 0
    for rel, ptoks in page_tokens.items():
        n = len(toks & ptoks)
        if n > best_n:
            best, best_n = rel, n
    return best if best_n else None


# A reference is a CONTIGUOUS SUBJECT PHRASE, not a stretch of the sentence. "the thing every
# step on this page" is not a reference to "the thing every step on this" page; a phrase that
# runs through a determiner, pronoun or conjunction ("the maintenance chapter and the warranty
# guide") is prose that happens to end in "guide". Any such word inside the captured phrase
# means the capture is wrong, so the reference is dropped rather than reported.
def ref_is_clean(ref):
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", ref)
    if not words:
        return False
    for w in words:
        # Only a POSSESSIVE suffix is stripped, never a trailing "s": rstrip("'s") turned
        # "this" into "thi" and let a captured "setup this guide" through as a real ref.
        low = re.sub(r"['’]s$", "", w.lower())
        if low in STOP:
            return False
        if w.lower().endswith(("'s", "’s")):
            return False
    return bool(tokens(ref))


def clause_ref_ok(ref):
    """The same test, relaxed for clause references ("the guide on chasing a short")."""
    if re.search(r"['’]s\b", ref):
        return False
    return bool(tokens(ref))


def _ref_is_generic(ref):
    return not tokens(ref)


def detect(sentence, headings, page_tokens):
    """Every unlinked reference in one sentence.

    Returns a list of (kind, ref_text, what_it_points_at). The caller decides link state,
    because a sentence that carries an <a> is doing the right thing whatever this finds.
    """
    if sentence.rstrip().endswith("?"):
        # A QUESTION IS NOT A POINTER. "Just want to say the winter guide saved your pipes?"
        # names a page in passing from inside a question, and it is not sending anyone there.
        # An instruction to a reader is never phrased as a question, so this cannot hide a real
        # pointer; it only stops the check arguing with prose that is already correct.
        return []
    if LINK_WORD.search(sentence):
        # The sentence itself says the thing is linked ("the water heater guide linked at the
        # end of this paragraph"). Judging it as an unlinked reference would argue with prose
        # that is already correct, which is the failure this instrument exists to avoid.
        return []
    hits = []
    for ref, desc in _named_inpage(sentence, headings):
        hits.append(("in-page section", ref, desc))
    for rx in INPAGE_DIRECTIONAL:
        m = re.search(rx, sentence, re.I)
        if m:
            hits.append(("section pointer", m.group(0), "another part of this page"))
    for ref, page in _crosspage(sentence, page_tokens):
        hits.append(("another page", ref, page))
    return hits


def _named_inpage(sentence, headings):
    out = []
    for rx in INPAGE_STRICT + INPAGE_CLAUSE:
        for m in re.finditer(rx, sentence, re.I):
            ref = m.group("ref")
            ok = ref_is_clean(ref) if rx in INPAGE_STRICT else clause_ref_ok(ref)
            if not ok:
                continue
            if EXTERNAL_TAIL.match(sentence, m.end()):
                continue
            toks = tokens(ref)
            # The heading with the STRONGEST overlap, not the first that shares a word:
            # "the section on when cleaning cannot help" points at the "When cleaning cannot
            # help" H2, even though an earlier H3 also contains "cleaning".
            #
            # AND THE OVERLAP HAS TO BE AT THE HEAD OF THE HEADING. Strongest overlap alone
            # matched "the appliance section" to "Finding your RV owner's manual and your
            # appliance manuals" on the strength of one word eight tokens in, which is an
            # incidental collision rather than the section being named. A reference names the
            # opening words of what it points at: "the voltage-drop section" points at "The
            # voltage-drop test", "the sizing section" at "Sizing: Can it run". A leading
            # article is skipped so "the X section" still matches a heading opening with "The".
            best, best_n = None, 0
            for label, htok in headings:
                n = len(toks & (htok & leading_tokens(label)))
                if n > best_n:
                    best, best_n = label, n
            if best:
                out.append((ref, 'the section "%s" on this page' % best))
    return out


def _crosspage(sentence, page_tokens):
    out = []
    for rx in CROSSPAGE_STRICT + CROSSPAGE_CLAUSE:
        for m in re.finditer(rx, sentence, re.I):
            ref = m.group("ref")
            ok = ref_is_clean(ref) if rx in CROSSPAGE_STRICT else clause_ref_ok(ref)
            if not ok:
                continue
            page = owns_page(ref, page_tokens)
            if page:
                out.append((ref, "the page %s" % page))
    return out


def anchor_regions(html):
    return [(m.start(), m.end()) for m in re.finditer(r"<a\b[^>]*>.*?</a>", html, re.S | re.I)]


def sentence_is_linked(html, anchors, hs, he):
    """True when the sentence already links: it overlaps an <a> element, or one ends just before.

    The overlap test is the fix for the common shape `<a href="...">Our black tank guide</a>
    has the seven-step procedure`: the opening tag sits BEFORE the sentence's first character,
    so looking only for "<a" inside the sentence missed it and reported prose that is linked.
    """
    for a, b in anchors:
        if a < he and hs < b:
            return True
    return bool(re.search(r"</a>\s*$", html[:hs]))


def scan(pages, page_tokens):
    """pages: [(rel, raw_html)], page_tokens: {rel: token set}. Returns report rows."""
    rows = []
    for rel, raw in pages:
        art = article_html(raw)
        text, offs = visible_map(art)
        anchors = anchor_regions(art)
        headings = headings_of(raw)
        for s, e in sentences_of(text, offs):
            sentence = re.sub(r"\s+", " ", text[s:e]).strip()
            hs, he = offs[s], offs[e - 1] + 1
            if sentence_is_linked(art, anchors, hs, he):
                continue
            hits = detect(sentence, headings, page_tokens)
            if not hits:
                continue
            line = art.count("\n", 0, hs) + 1
            # One report per distinct reference in the sentence; the same span can be caught
            # by two overlapping rules ("see the section below" and "the section below").
            seen, refs = set(), []
            for _, r, d in hits:
                key = (r.lower(), d)
                if key not in seen:
                    seen.add(key)
                    refs.append("%s -> %s" % (r, d))
            rows.append((rel, line, "; ".join(refs), sentence))
    return rows


# -------------------------------------------------------------------------------- self-test
def self_test():
    """Every rule must catch its real case, and every must-not-catch case must stay clean."""
    site_pages = {}          # populated per case below

    def page_html(body, headings=()):
        hs = "".join("<h2>%s</h2>" % h for h in headings)
        return ("<!DOCTYPE html><html><head><title>Test</title></head><body>"
                "<!-- nav:start --><nav><a href=\"/\">Home</a></nav><!-- nav:end -->"
                "<main id=\"main\"><div class=\"prose\">%s%s</div></main>"
                "<!-- footer:start --><footer>Guides</footer><!-- footer:end -->"
                "</body></html>" % (hs, body))

    # A synthetic site that owns a furnace page, and one that does not. The two inventories
    # are the whole point of the cross-page rule: the SAME sentence fires on one and not on
    # the other, because what we own is what decides it.
    FURNACE = {"furnace": "guides/rv-furnace-not-working.html"}
    NOTHING = {}

    failures = []

    def run(sentence, headings=(), inv=FURNACE):
        raw = page_html("<p>%s</p>" % sentence, headings=headings)
        return scan([("guides/x.html", raw)], {t: {t} for t in inv})

    # --- MUST CATCH, verbatim from the live site -------------------------------------------
    must_catch = [
        ("in-page section",
         "Stop here and read the hot skin section. That is a different class of problem.",
         ("Hot skin", "What to do"), NOTHING),
        ("section pointer",
         "The instruction is direct: replace it, after ruling out moisture (moisture is covered below).",
         (), NOTHING),
        ("section pointer",
         "Read the section below on what a sealant cannot fix.",
         ("What a sealant cannot fix",), NOTHING),
        ("another page",
         "If the generator is misbehaving, that is the generator fault guide.",
         (), {"generator": "guides/rv-generator-not-charging.html"}),
        ("another page",
         "See the guide on chasing a short, because tracing one is its own skill.",
         (), {"chasing": "guides/rv-fuse-keeps-blowing.html"}),
    ]
    for kind, sentence, headings, inv in must_catch:
        if not run(sentence, headings, inv):
            failures.append("MUST CATCH but did not: [%s] %s" % (kind, sentence))

    # --- MUST NOT CATCH --------------------------------------------------------------------
    must_not = [
        # the live sentence WITH the link: the reference is fine, it just needed the <a>
        ('Stop here and read the <a href="#hot-skin">hot skin section</a>. '
         'That is a different class of problem.', ("Hot skin",), NOTHING),
        # we do not own it
        ("Read your owner's manual for the interval.", (), NOTHING),
        # ordinary prose containing the word "section", no pointer at all
        ("A section of cable can carry the load even when a joint reads fine.", (), NOTHING),
        ("The cross-section shows the framing.", (), NOTHING),
        # a section of SOMEBODY ELSE'S document
        ("The maintenance section of the warranty guide lists the intervals.", (), NOTHING),
        # directional-sounding words that do not point at a section
        ("The readings below are typical for a rested battery.", (), NOTHING),
        ("The method described above is the maker's, not ours.", (), NOTHING),
        ("Work through the storage checklist further down this list.", (), NOTHING),
        # a QUESTION is not a pointer (the live contact-page case, 2026-10-13)
        ("Just want to say the winter guide saved your pipes?", (), FURNACE),
        # a word buried in a long heading is a collision, not a named section
        ("This is the most expensive mistake in the appliance section.",
         ("Finding your RV owner's manual and your appliance manuals",), NOTHING),
        # a cross-page reference to a page we do NOT have: must be clean even though the
        # same sentence would fire if a furnace page existed
        ("The furnace guide covers how a sagging battery stops an appliance.", (), NOTHING),
        ("the furnace guide covers how a sagging battery stops an appliance.", (), NOTHING),
    ]
    for sentence, headings, inv in must_not:
        rows = run(sentence, headings, inv)
        if rows:
            failures.append("MUST NOT CATCH but did: %s  ->  %s" % (sentence, rows[0][2]))

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print("self-test passed: %d must-catch case(s) caught, %d must-not-catch case(s) clean"
          % (len(must_catch), len(must_not)))
    return 0


# ------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Flag prose that names a section or page we own without linking it.")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    pages = [(str(p.relative_to(ROOT)), p.read_text(encoding="utf-8", errors="replace"))
             for p in walked("*.html")]

    page_tokens = {}
    for rel, raw in pages:
        toks = title_tokens(raw)
        if toks:
            page_tokens[rel] = toks

    rows = scan(pages, page_tokens)
    print("scanned %d page(s); %d unlinked reference(s)" % (len(pages), len(rows)))
    for rel, line, refs, sentence in rows:
        print("\n  %s:%d" % (rel, line))
        print("    references: %s" % refs)
        print("    sentence:   %s" % sentence[:300])
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
