#!/usr/bin/env python3
"""Insert one internal link into a page's prose, safely, and record it.

WHY THIS IS A TOOL. The first pass at internal linking was done by hand and put an anchor
inside a JSON-LD block: the phrase's first occurrence in the file was a meta description,
not prose, and nothing objected until the structural check failed. The second hand pass hit
a subtler problem - inserting a link into a VERIFIED page flips it to drifting, because
verify-content's extractor treats a tag as a space and a space lands before the following
comma - which is the content gate working correctly and needing a recorded decision rather
than a bypass. Both are now handled here, in one place, with the guards that failure
taught.

  python3 scripts/insert-link.py guides/rv-furnace-not-working.html "carbon monoxide" \\
      guides/rv-furnace-carbon-monoxide.html

What it refuses to do:
  * insert inside <script>, <style>, the nav or the footer, or an attribute
  * insert inside text that is already inside a link
  * insert a phrase that would change the words a reader sees (it compares the text with
    punctuation spacing normalised, which is the only difference a link makes)
  * insert a link to a page that does not exist
  * insert the same destination twice into one page

What it does record: if the page is verified in scripts/content-manifest.json, the digest
moves, and the manifest gets a dated note saying a link was added inside an existing
sentence and no word of prose changed. That is a decision with an audit trail, not a
silent re-baseline.

Run with --dry-run to see the decision without writing anything.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "scripts" / "content-manifest.json"


def visible_digest(html_text):
    spec = importlib.util.spec_from_file_location("vc", ROOT / "scripts" / "verify-content.py")
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    return vc.digest(html_text)


def words_only(fragment):
    """The words a reader sees, with spacing around punctuation normalised.

    A link changes exactly one thing: a tag where no tag was. The extractors turn that tag
    into a space, so a space appears before the comma that follows. Nothing else may differ,
    and this is the comparison that proves it.
    """
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"\s+([.,;:!?)])", r"\1", t).strip()


def in_script(text, index):
    # BOTH searches stop at the insertion point. The first version searched the whole file
    # for "<script", so on any page whose scripts sit after the prose - which is every real
    # page - the trailing tags looked like an unclosed script and the tool refused every
    # valid insertion. The scratch fixture had its scripts in <head> and passed, which is
    # why the test now carries trailing tags too.
    return text.rfind("<script", 0, index) > text.rfind("</script>", 0, index)


def inside_tag(text, index):
    return text.rfind(">", 0, index) < text.rfind("<", 0, index)


# THE SHELL IS MORE THAN THE NAV NOW, AND THE DOCSTRING ALREADY CLAIMED TO REFUSE IT.
# build-shell.mjs injects the breadcrumb INSIDE the nav:start and nav:end region, so a page whose
# heading carries another page's subject has that phrase first appearing in navigation rather than
# prose. That is exactly what happened on 2026-10-04: the slide-out guide's heading is "RV slide out
# not working", a "slide out" link went into its own breadcrumb, and the shell check caught it
# because the generated nav stopped matching its generator.
#
# The docstring has claimed since it was written that the tool refuses "the nav" and the footer.
# Only the script and style cases were implemented. The markers below are how the shell identifies
# itself in a page, so they are what the refusal has to test.
SHELL_SPANS = (("<!-- nav:start -->", "<!-- nav:end -->"),
               ("<!-- crumbs:start -->", "<!-- crumbs:end -->"),
               ("<!-- footer:start -->", "<!-- footer:end -->"))


def in_shell(text, index):
    """True when this position is inside the generated shell rather than the page's own prose."""
    for start, end in SHELL_SPANS:
        if text.rfind(start, 0, index) > text.rfind(end, 0, index):
            return True
    return False


def inside_link(text, index):
    return text.rfind("<a ", 0, index) > text.rfind("</a>", 0, index)


def insert(page, phrase, dest, dry_run=False):
    p = ROOT / page
    if not p.exists():
        sys.exit("no such page: %s" % page)
    if not (ROOT / dest).exists():
        sys.exit("no such destination: %s" % dest)
    html = p.read_text(encoding="utf-8")
    if 'href="%s"' % dest in html:
        sys.exit("%s already links to %s" % (page, dest))

    tried_bad = False
    for m in re.finditer(re.escape(phrase), html):
        i = m.start()
        if in_script(html, i) or inside_tag(html, i) or inside_link(html, i) or in_shell(html, i):
            continue
        new = html[:i] + '<a href="%s">%s</a>' % (dest, phrase) + html[i + len(phrase):]
        # TRY THE NEXT OCCURRENCE, DO NOT STOP AT THE FIRST THAT FAILS.
        # The words check is right and must stay: verify-content's extractor reads a tag as a space,
        # so wrapping a phrase that ends a sentence puts a space before the full stop and the page's
        # visible text really does change. But a phrase usually appears several times, and only ONE
        # of them sits badly. Exiting on the first failure made every later occurrence unreachable,
        # which is why the refrigerator and macerator guides could not be linked on "12 volt" while
        # a perfectly good occurrence sat further down the page. Found 2026-10-04.
        if words_only(new) != words_only(html):
            tried_bad = True
            continue
        if dry_run:
            print("would link %r in %s -> %s (at char %d)" % (phrase, page, dest, i))
            return
        p.write_text(new, encoding="utf-8")

        note = ""
        if MANIFEST.exists():
            man = json.loads(MANIFEST.read_text(encoding="utf-8"))
            entry = man.get(page)
            if entry and entry.get("status") == "verified":
                old = visible_digest(html)
                entry["hash"] = visible_digest(new)
                entry["verified_by"] = (entry.get("verified_by") or "") + (
                    " CHANGED 2026-09-28: a contextual internal link to %s was added inside "
                    "an existing sentence, in the internal-linking pass Ty asked for. Not one "
                    "word of prose changed; the recorded digest moves because a tag now sits "
                    "inside the sentence and the extractor reads a tag as a space, which puts "
                    "a space before the following comma. The claim set is untouched." % dest)
                MANIFEST.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
                note = "  [verified page: digest %s -> %s recorded]" % (old, entry["hash"])
        print("linked %-46s -> %s%s" % (page, dest, note))
        return
    sys.exit("refusing: %r does not appear in prose in %s" % (phrase, page))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 3:
        sys.exit(__doc__.strip().splitlines()[-1])
    insert(args[0], args[1], args[2], dry_run="--dry-run" in sys.argv)


if __name__ == "__main__":
    main()
