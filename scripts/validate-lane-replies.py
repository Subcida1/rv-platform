#!/usr/bin/env python3
"""Check whether a bridge lane's review actually quotes the page it was given.

WHY THIS EXISTS. Asked to review a freshly written guide, one lane returned a confident review that
criticised two things which do not exist in the page: a claim that replacing the wiper seal "will
permanently resolve all water intrusion", and a "section advising owners to manually crank or override
electric slide motors". Neither phrase appears anywhere in the file. An obviously empty reply is easy to
discard; a fabricated one reads as usable and is therefore worse.

So the review prompt now requires every criticism to quote the exact sentence from the page, and this
script checks those quotations mechanically. A quote that is not in the page means the review was not
written from the page.

Run:
  python3 scripts/validate-lane-replies.py                 # every REPLY-*.md against its staged page
  python3 scripts/validate-lane-replies.py REPLY-x.md      # one file

Judgement is deliberately narrow. It reports the count of quotes found and not found, and names the
missing ones so a human can look. It does NOT declare a review good or bad: a review can quote
correctly and still be wrong about what the quote means.
"""
import difflib
import pathlib
import re
import sys

BRIDGE = pathlib.Path("/home/user/claude-bridge")
OUTBOX = BRIDGE / "outbox"
STAGED = BRIDGE / "staged"


def normalise(s):
    """Collapse whitespace and unify quotes, so a quote matches across markup wrapping."""
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def quotes_in(text):
    """Every run inside double quotes, long enough to be a real sentence rather than a word.

    The blind spot, learned by testing: a review that quotes NOTHING yields an empty list, and an empty
    list must be read as unverifiable rather than clean. See the caller.
    """
    out = []
    for m in re.finditer(r'"([^"]{25,400})"', text):
        q = normalise(m.group(1))
        if len(q.split()) >= 5:
            out.append(q)
    return out


HARNESS_HEADERS = (
    "CAPTURED BY THE BRIDGE HARNESS",
    "NO ANSWER WAS CAPTURED",
)


def harness_wrote(text):
    """True when the harness wrote the file rather than the lane.

    TWO HEADERS, NOT ONE. Both strings mean the harness authored the reply: one says it captured the
    lane's answer, the other says no answer arrived and the flight was released. A classifier that greps
    only the first labels every capture-ceiling reply as LANE-WRITTEN, which is the opposite of the
    truth -- measured 2026-09-27 17:47, it mislabelled 3 of 4 replies. Across the whole outbox: 48 files
    carry the first string and 27 carry the second, so a one-string check is wrong about 27 of them.
    """
    head = text[:600]
    return any(h in head for h in HARNESS_HEADERS)


def prompt_for(jobid):
    """The job file's own text, so a lane that echoes the instructions can be told apart from one
    that invented a quote. Learned from the first real run: four replies contained "quotes" that were
    actually my prompt sentences, which the checker reported as simply 'not in page'. Those are
    different failures -- a lane reading its own instructions is starved or confused; a lane quoting
    nothing and asserting anyway is fabricating -- and the fix differs.
    """
    # bridge-review.py keeps a copy here precisely because the bridge deletes the job on consumption
    for job in ([BRIDGE / "queue" / "job-sources" / (jobid + ".md")]
                + list((BRIDGE / "queue" / "jobs").glob(f"{jobid}.md"))
                + list(BRIDGE.glob(f"**/{jobid}.md"))):
        try:
            return normalise(job.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


def staged_for(jobid):
    """Recover the page a job pointed at, from the job file itself."""
    job = BRIDGE / "queue" / "jobs" / (jobid + ".md")
    if not job.exists():
        for cand in BRIDGE.glob(f"**/{jobid}.md"):
            job = cand
            break
    if not job.exists():
        return None, None
    txt = job.read_text(encoding="utf-8")
    m = re.search(r'path="staged/([^"]+)"', txt)
    if not m:
        return None, None
    slug = m.group(1)
    p = STAGED / slug
    return (normalise(p.read_text(encoding="utf-8")) if p.exists() else None), slug


def check(reply_path):
    reply = reply_path.read_text(encoding="utf-8")
    jobid = reply_path.name.replace("REPLY-", "").replace(".md", "")
    page, slug = staged_for(jobid)
    print(f"\n=== {jobid}")
    if harness_wrote(reply):
        kind = "capture" if "CAPTURED BY THE BRIDGE HARNESS" in reply[:600] else "NO ANSWER"
        print(f"    HARNESS-WRITTEN ({kind}): the lane did not author this file")
        print("    nothing here reflects the lane's review, so there is nothing to validate")
        return
    if page is None:
        print(f"    could not find the staged page for this job (looked for {slug})")
        return
    # the harness banner is not the lane's writing; ignore anything the lane did not say
    body = reply.split("---", 1)[1] if "\n---\n" in reply else reply
    qs = quotes_in(body)
    if not qs:
        # Found by testing against the case that must FAIL. The fabricated review used no quotation
        # marks at all, so a validator that only checks quotes reported "nothing to verify" -- neutral,
        # when the truth is that the review cannot be checked. A prompt that REQUIRES verbatim quotes
        # makes a quote-less reply suspicious in itself, so say so rather than shrugging.
        print(f"    UNVERIFIABLE: the reply contains no quoted sentences  |  page {slug}")
        print("    the review prompt requires every criticism to quote the page. A reply without")
        print("    quotes was either not written from the page, or ignored the instruction.")
        print(f"    reply length: {len(body.split())} words")
        return
    prompt = prompt_for(jobid)
    missing = [q for q in qs if q not in page]
    found = len(qs) - len(missing)
    echoed = [q for q in missing if prompt and q in prompt]
    print(f"    {found}/{len(qs)} quotes found in {slug}")
    for q in missing:
        tag = "FROM MY OWN PROMPT" if q in echoed else "NOT IN PAGE AT ALL"
        print(f"      {tag}: {q[:140]}")
    if echoed and not found:
        print("    every quote is my own instruction text echoed back: the lane was working from the")
        print("    prompt rather than the page, which is a starvation symptom, not a fabrication")
    elif missing:
        print("    a quote that is in neither the page nor the prompt means the review was not written")
        print("    from the page at all")


def main():
    args = sys.argv[1:]
    if args:
        files = [pathlib.Path(a) for a in args]
    else:
        files = sorted(OUTBOX.glob("REPLY-*.md"))
    if not files:
        print("no replies in the outbox")
        return
    for f in files:
        check(f)


if __name__ == "__main__":
    main()
