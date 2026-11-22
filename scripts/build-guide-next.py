#!/usr/bin/env python3
"""Insert the end-of-content link block into guide pages.

The block is the `flex between gap spread` strip of one or two high-scent links that
closes a guide's article body (check-ux.py step 2 looks for it). Its content comes from
`_data/guide-next.json`; this script is the only thing that writes that markup.

Placement is fixed by the precedent set on the 11 guides that already carry it: the strip
goes immediately after the `</div>` that closes the "Related guides" card, which itself
follows `<h2>Related guides</h2>`.

Idempotent by construction: a page that already carries the wrapper class is left alone, and
inserting an identical block twice is impossible because the guard is the wrapper itself.
A page with NO "Related guides" card is reported, never guessed at.

Run:      python3 scripts/build-guide-next.py            # write
Check:    python3 scripts/build-guide-next.py --check    # report drift, exit 1 if any
Self-test:python3 scripts/build-guide-next.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "guide-next.json"
WRAPPER = 'class="flex between gap spread"'
RELATED_H2 = re.compile(r'<h2[^>]*>\s*Related guides\s*</h2>', re.I)


def load_blocks(path: Path | None = None) -> dict:
    d = json.loads((path or DATA).read_text(encoding="utf-8"))
    return d["blocks"]


def render_block(links: list[dict]) -> str:
    """Render the strip. First link is the primary (btn-gb), a second is secondary."""
    out = [' <div class="flex between gap spread">']
    for i, link in enumerate(links):
        cls = "btn btn-gb" if i == 0 else "btn btn-secondary"
        label = link["label"]
        href = link["href"]
        # The precedent pages render the manuals link with a real arrow, not "->".
        if href.startswith("manuals/"):
            label = re.sub(r"\s*(?:->|→)\s*$", "", label) + " →"
        out.append(f' <a class="{cls}" href="{href}">{label}</a>')
    out.append(" </div>")
    return "\n".join(out) + "\n"


def closing_div_end(text: str, start: int) -> int | None:
    """Index just past the `</div>` that closes the div opening at/after `start`."""
    d = text.find("<div", start)
    if d == -1:
        return None
    depth = 0
    for m in re.finditer(r"<div\b|</div>", text[d:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return d + m.end()
    return None


def anchor_index(text: str) -> int | None:
    """Index just past the 'Related guides' card's own closing </div>, inside <main>."""
    h2 = RELATED_H2.search(text)
    if not h2:
        return None
    at = closing_div_end(text, h2.end())
    if at is None:
        return None
    # The strip belongs INSIDE <main>. A page whose Related card is the last child of <main>
    # (no wrapping .card div) makes the depth walk overshoot to an outer </div>, which landed
    # the block after </footer> on rv-heating-off-grid and rv-water-pressure. Never return an
    # index past </main>; refuse instead so the page is reported rather than silently broken.
    close_main = text.find("</main>")
    if close_main != -1 and at > close_main:
        return None
    return at


def find_block(text: str) -> tuple[int, int] | None:
    """Span of the existing strip (wrapper div through its closing </div>), or None."""
    at = text.find(WRAPPER)
    if at == -1:
        return None
    # back up to the '<' that opens this div, so the depth walk starts on the right tag
    start = text.rfind("<", 0, at)
    if start == -1:
        return None
    end = closing_div_end(text, start)
    return (start, end) if end is not None else None


def g_strip(text: str) -> str:
    """Just the link-block strip's own markup (empty string if there is no block)."""
    span = find_block(text)
    return text[span[0]:span[1]] if span else ""


def apply_one(text: str, block: str) -> tuple[str, str]:
    """Return (new_text, status): has-block, stale, inserted, or no-anchor.

    A block that is present but does not MATCH the map is 'stale' and gets rewritten. Comparing
    presence alone was a real bug: editing a destination in the map left the old strip on the page
    while every gate reported green.
    """
    span = find_block(text)
    if span is not None:
        start, end = span
        if text[start:end].strip() == block.strip():
            return text, "has-block"
        return text[:start] + block.strip() + text[end:], "stale"
    at = anchor_index(text)
    if at is None:
        return text, "no-anchor"
    if text[at:at + 1] == "\n":
        at += 1
    return text[:at] + "\n" + block + text[at:], "inserted"


def main(map_path: Path | None = None, check: bool = False) -> int:
    blocks = load_blocks(map_path)
    changed, has_block, no_anchor, missing, stale = [], [], [], [], []

    for slug, spec in sorted(blocks.items()):
        path = ROOT / "guides" / f"{slug}.html"
        if not path.exists():
            # a map entry naming a page that does not exist is a hard failure, never a note:
            # the block it describes can never ship, and a green gate would hide that.
            missing.append(slug)
            print(f"  MISSING PAGE: {slug}")
            continue
        text = path.read_text(encoding="utf-8")
        block = render_block(spec["links"])
        new, status = apply_one(text, block)
        if status in ("inserted", "stale"):
            (stale if status == "stale" else changed).append(slug)
            if not check:
                path.write_text(new, encoding="utf-8")
        elif status == "has-block":
            has_block.append(slug)
        else:
            no_anchor.append(slug)

    verb = "would change" if check else "changed"
    print(f"  {len(changed)} page(s) {verb}; {len(has_block)} already carry the block")
    if stale:
        print(f"  {len(stale)} page(s) carry a block that does NOT match the map "
              f"({'would be rewritten' if check else 'rewritten'}):")
        for s in stale:
            print(f"    {s}")
    if no_anchor:
        print(f"  {len(no_anchor)} page(s) have no 'Related guides' anchor (NOT touched):")
        for s in no_anchor:
            print(f"    {s}")
    if missing:
        print(f"  {len(missing)} map entr(ies) name a page that does not exist — fix the map:")
        for s in missing:
            print(f"    {s}")
    # In check mode any pending change (including a stale block) is a failure. In write mode the
    # stale block has just been rewritten, so only genuinely unresolved pages fail.
    unresolved = bool(no_anchor or missing)
    if check:
        return 1 if (changed or stale or unresolved) else 0
    return 1 if unresolved else 0


def self_test() -> int:
    """Reconstruct the insertion as data and assert the outcome, then negative-test it."""
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  {'PASS' if cond else 'FAIL'}: {name}")
        ok = ok and cond

    page = (
        '<main><h2>Body</h2><p>x</p>\n'
        '<h2>Related guides</h2>\n'
        '<div class="card">\n<p>see <a href="guides/other">other</a></p>\n</div>\n'
        '<details class="faq"><summary>q</summary><p>a</p></details></main>'
    )
    block = render_block([{"label": "Other", "href": "guides/other"}])
    out, status = apply_one(page, block)
    check("inserts at the Related card's close", status == "inserted")
    check("wrapper present after insert", WRAPPER in out)
    check("strip sits before the FAQ", out.index(WRAPPER) < out.index("<details"))
    check("card div still balanced", out.count("<div") == out.count("</div>"))
    check("idempotent on the second pass", apply_one(out, block)[1] == "has-block")

    # a block that is present but does NOT match the map must be detected and rewritten.
    # Presence-only comparison was a real bug: editing a destination in the map left the old
    # strip on the page while every gate reported green.
    other = render_block([{"label": "Different", "href": "guides/elsewhere"}])
    out_stale, st_stale = apply_one(out, other)
    check("a block that does not match the map is 'stale'", st_stale == "stale")
    check("the stale block is actually replaced", (
        "guides/elsewhere" in out_stale
        and 'href="guides/other"' not in g_strip(out_stale)
    ))
    check("rewriting a stale block is idempotent", apply_one(out_stale, other)[1] == "has-block")

    # negative test: no anchor -> refuse, do not guess
    bare = "<main><h2>Body</h2><p>no related card here</p></main>"
    check("refuses a page with no anchor", apply_one(bare, block)[1] == "no-anchor")

    # negative test: a Related card with NO wrapper div, last child of <main>, must not push the
    # strip past </main>. This is the rv-heating-off-grid / rv-water-pressure shape.
    tail = (
        '<main><h2>Sources</h2><p>x</p>\n'
        '<h2>Related guides</h2>\n'
        '<p>see <a href="guides/other">other</a></p>\n'
        '<p class="page-foot">Tell us</p>\n'
        '</main>\n<div id="site-footer">foot</div>'
    )
    out3, st3 = apply_one(tail, block)
    check("never inserts past </main>", st3 == "no-anchor")
    check("footer untouched when refusing", out3 == tail)

    # a nested card must not eat the wrong close
    nested = (
        '<h2>Related guides</h2>\n<div class="card">\n<div class="inner">x</div>\n</div>\n<p class="page-foot"></p>'
    )
    out2, st2 = apply_one(nested, block)
    check("handles a nested div inside the card", st2 == "inserted" and out2.index(WRAPPER) < out2.index("page-foot"))

    # a map entry naming a page that does not exist must fail the run, not print a note:
    # the block it describes can never ship, so a green gate would hide a real dead end.
    # Uses a TEMP map copy so the real _data/guide-next.json is never touched.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        ghost = Path(td) / "map.json"
        ghost.write_text(json.dumps({"note": "", "blocks": {
            "no-such-guide-xyz": {"links": [{"label": "X", "href": "guides/other"}]}}}), encoding="utf-8")
        check("a phantom map entry fails the run", main(ghost, check=True) != 0)
    _real = load_blocks()
    check("the real map is untouched by that test", len(_real) == 50)

    print("self-test:", "ok" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--check", action="store_true", help="report drift only, change nothing")
    _ap.add_argument("--self-test", action="store_true")
    _args = _ap.parse_args()
    if _args.self_test:
        sys.exit(self_test())
    sys.exit(main(check=_args.check))
