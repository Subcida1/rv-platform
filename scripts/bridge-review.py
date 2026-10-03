#!/usr/bin/env python3
"""Dispatch a bridge-lane review of a guide, keeping everything needed to validate the reply.

WHY THIS IS A SCRIPT AND NOT THREE COMMANDS I RETYPE. Three things have to happen in order, and one of
them is easy to forget:

  1. STAGE the page, because a lane reads `staged/<slug>.html` and a stale staged copy makes an accurate
     quotation look fabricated. `stage-for-bridge.py` also reports staleness, which is why it runs here.
  2. DISPATCH a job file per lane.
  3. **PRESERVE A COPY OF THE JOB.** The bridge deletes a job file once a lane consumes it, so after the
     fact there is no way to tell a lane quoting the PAGE from a lane echoing the PROMPT -- and those are
     opposite diagnoses. Discovering that cost a round; this step stops it recurring.

The review prompt requires every criticism to quote the page verbatim, which is what makes
`validate-lane-replies.py` able to check the reply mechanically.

Usage:
  python3 scripts/bridge-review.py --guides rv-delamination,rv-water-pump-wont-prime
  python3 scripts/bridge-review.py --guides <slugs> --round 3
  python3 scripts/bridge-review.py --status
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRIDGE = pathlib.Path("/home/user/claude-bridge")
KEEP = BRIDGE / "queue" / "job-sources"

LANES = ["aistudio.google.com", "chat.deepseek.com", "chatgpt.com",
         "chat.qwen.ai", "gemini.google.com", "grok.com"]

BODY = """You are reviewing one page from a website. No human is watching. Earlier jobs in this
conversation are FINISHED and this one stands alone.

A PAGE ARRIVES IN TWO CHUNKS. This is deliberate and it is not a workaround for a broken tool. THE TWO
CHUNKS OVERLAP, so between them you are reading the WHOLE page and there is no unread middle.

CALL 1 - call_id 7714, tool read_text_file, two parameters:
  path="staged/{staged}"
  head=150
That gives you the top of the page, in order.

CALL 2 - call_id 7714, tool read_text_file, two parameters:
  path="staged/{staged}"
  tail=150
That gives you the BOTTOM of the page, and the source list is in it. Read both before answering, and do
not ask for the same path a third time with no head or tail: that exact call has already run and will be
dropped as a duplicate.

WHY TWO CALLS: a very large tool result cannot be typed back into this conversation - it goes into the
message box and will not send, so the whole result is lost rather than cut. Two smaller slices always
arrive. THE SIZE WAS RAISED FROM 70 AND 80 TO 125 AND 125 ON 2026-10-03, and then to 150 AND 150 the same
night. The first raise came because a reviewing lane reported that the two slices did not meet and the
middle of the page was in neither. The second came from measuring rather than guessing: the longest
staged page is 296 lines and 25,191 characters, so 125 plus 125 still left 46 lines unread. 150 plus
150 covers three hundred lines, every page this site ships, at about 12,700 characters per slice. If you ever find the chunks do not meet, SAY SO AT THE TOP OF YOUR REVIEW rather
than reviewing the part you were given.

CALL 3 - call_id 7714, tool write_file, two parameters:
  path="/home/user/claude-bridge/outbox/REPLY-{jobid}.md"
  content=<your whole review, beginning with the JOB ID line {jobid}>
Write the review into that file. Do not print it in the chat. The file IS the reply.

## THE ONE RULE THAT MATTERS

**Every criticism you make must quote the exact sentence from the page, word for word, inside double
quotation marks.** Copy it, do not paraphrase it. If you cannot copy the exact words, then do not make
the criticism. This page will be checked mechanically: your quoted sentences are matched against the
page text, and a quote that does not appear makes your whole review worthless.

So: if you have nothing to quote, say so. "I found nothing wrong in this section" is a valid and useful
answer. An invented criticism is worse than no criticism at all.

## Part 1 - the sourcing rule

The page's rule is that every factual claim traces to a manufacturer's own document, and the source list
at the end says what each source supports. Does any claim look stronger than the source could support?
Quote the claim. The source list is at the END of the page and arrives in your second call, so do not answer this part before you have read it.

## Part 2 - overclaiming

Does any sentence state more certainty than the evidence allows? Look for an inference presented as
fact, a number without a unit or without its conditions, or advice that could damage equipment or hurt
someone if followed carelessly. Quote the sentence.

## Part 3 - what a reader would still not know

You are an RV owner with this exact problem. Having read the page, what would you still be unsure about?
Name the specific gap. If it helps, quote the part of the page that leaves you unsure.

## How to write it

Short and concrete. Three real findings beat twelve invented ones. Do not pad. If a section has no
problem, say that in one line and move on.
"""


def status():
    print("lane                    heartbeat   state        inflight")
    now = datetime.datetime.now().timestamp()
    for lane in LANES:
        hb = BRIDGE / "queue" / ("heartbeat-%s.txt" % lane)
        st = BRIDGE / "queue" / ("state-%s.json" % lane)
        age = "no file"
        if hb.exists():
            age = "%4ds" % (now - hb.stat().st_mtime)
        state = "?"
        if st.exists():
            import json
            try:
                d = json.loads(st.read_text())
                state = "%s v%s" % (d.get("state"), d.get("v"))
            except Exception:
                state = "unreadable"
        print("  %-22s %-11s %-12s" % (lane, age, state))
    jobs = sorted((BRIDGE / "queue" / "jobs").glob("*.md"))
    print("\n  jobs pending: %d" % len(jobs))
    for j in jobs[-8:]:
        print("    %s" % j.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guides", help="comma-separated slugs")
    ap.add_argument("--round", default="1")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--lane", help="send to this lane instead of the rotation. Repeatable as a "
                                  "comma-separated list. Use it when a lane is known to be "
                                  "answering: the rotation cannot tell a working lane from one "
                                  "that renders its page without an answer.")
    a = ap.parse_args()

    if a.status:
        status()
        return 0

    if not a.guides:
        print(__doc__)
        return 2

    slugs = [s.strip() for s in a.guides.split(",") if s.strip()]
    pages = ["guides/%s.html" % s for s in slugs]
    missing = [p for p in pages if not (ROOT / p).exists()]
    if missing:
        sys.exit("no such page: " + ", ".join(missing))

    # 1. stage, and let the stager's own staleness report be heard
    print("staging %d page(s)" % len(pages))
    subprocess.run([sys.executable, str(ROOT / "scripts" / "stage-for-bridge.py")] + pages, cwd=ROOT)

    # 1b. CLEAR ANSWERED JOBS FIRST, because the bridge does not and the queue fills up.
    # A spent job left in queue/jobs parks the lane at `prompt already sent`, which reads exactly
    # like a dead lane: on 2026-10-03 eight spent files produced one lane whose reply held only
    # its own UI chrome and another that released at capture-ceiling with chrome in the container.
    # Both lanes were healthy. Measured twice, so the sweep runs here rather than by hand.
    try:
        subprocess.run([sys.executable, '/home/user/claude-bridge/tools/sweep-spent-jobs.py'],
                       capture_output=True, timeout=30)
    except Exception:
        pass

    # 2. dispatch
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    KEEP.mkdir(parents=True, exist_ok=True)
    made = []
    # WHY THIS IS NOT JUST `LANES[i % len(LANES)]`. It was, and with a single slug i is always 0,
    # so EVERY single-guide dispatch went to LANES[0] whatever state that lane was in. On
    # 2026-10-02 that lane released the flight twice in a row -- "the reply container held only
    # page chrome and footer text" -- while the lane that had delivered a full review forty
    # minutes earlier sat idle, and there was no flag to say so. Heartbeat freshness is not the
    # signal (the lane that worked had the stalest heartbeat of the six), so this does not try to
    # guess health: it rotates by default and lets the caller name a lane when it knows one.
    pick = [l.strip() for l in (a.lane or "").split(",") if l.strip()] or LANES
    for i, slug in enumerate(slugs):
        lane = pick[i % len(pick)]
        jobid = "%s-RV-%s-REVIEW%s" % (stamp, slug, a.round)
        text = "LANE: %s\n\nJOB ID: %s\n\n" % (lane, jobid) + BODY.format(
            staged="guides__%s.html" % slug, jobid=jobid)
        (BRIDGE / "queue" / "jobs" / (jobid + ".md")).write_text(text, encoding="utf-8")
        # 3. the copy that makes validation possible after the job is consumed
        (KEEP / (jobid + ".md")).write_text(text, encoding="utf-8")
        made.append((lane, jobid))

    print("\ndispatched %d job(s), prompt copies kept in %s" % (len(made), KEEP))
    for lane, jobid in made:
        print("  %-22s %s" % (lane, jobid))
    print("\nwhen replies land:  python3 scripts/validate-lane-replies.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
