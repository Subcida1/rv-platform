#!/usr/bin/env python3
"""Check the 28 links on _todo/UNVERIFIED-LINKS.md the way that file says to check them.

Read only. For each URL: HTTP status, content type, and the page title (or the first bytes for a
PDF). A challenge page is reported as a challenge rather than as content, because the worklist's
whole point is that "the machine could not confirm it" and "it is wrong" are different answers.
"""
import re, sys, urllib.request, urllib.error, pathlib, json

ROOT = pathlib.Path("/home/user/Documents/rv-platform")
urls = [l.strip() for l in (ROOT / "_todo/UNVERIFIED-LINKS.md").read_text().splitlines()
        if l.startswith("## ") and "http" in l]
urls = [re.sub(r"^##\s*\d+\.\s*", "", u).strip() for u in urls]
print("checking %d url(s)" % len(urls))

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/155.0.0.0 Safari/537.36")
CHALLENGE = re.compile(r"just a moment|attention required|cf-|captcha|access denied|are you a robot",
                       re.I)
out = []
for u in urls:
    row = {"url": u}
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(400_000)
            row["status"] = r.status
            row["type"] = r.headers.get("Content-Type", "")
            row["final"] = r.geturl()
            if "pdf" in row["type"].lower() or body[:4] == b"%PDF":
                row["title"] = "(pdf, %d bytes read)" % len(body)
            else:
                text = body.decode("utf-8", errors="replace")
                m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
                row["title"] = re.sub(r"\s+", " ", m.group(1)).strip()[:90] if m else "(no title)"
                if CHALLENGE.search(text[:4000]):
                    row["title"] = "CHALLENGE PAGE: " + row["title"]
    except urllib.error.HTTPError as e:
        row["status"] = e.code
        row["type"] = e.headers.get("Content-Type", "") if e.headers else ""
        row["title"] = "HTTP %d" % e.code
    except Exception as e:
        row["status"] = "ERR"
        row["title"] = type(e).__name__ + ": " + str(e)[:70]
    out.append(row)
    print("%-4s %-45s %s" % (row.get("status"), u[:45], row.get("title", "")[:70]))

bad = [r for r in out if not (isinstance(r.get("status"), int) and r["status"] < 400)
       or "CHALLENGE" in (r.get("title") or "")]
print("\n%d of %d could not be confirmed" % (len(bad), len(out)))
for r in bad:
    print("  %s  %s" % (r.get("status"), r["url"]))
(Root := ROOT / "_todo").joinpath("LINK-CHECK-RESULTS.json").write_text(json.dumps(out, indent=1))
print("full result written to _todo/LINK-CHECK-RESULTS.json")
