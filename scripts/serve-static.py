#!/usr/bin/env python3
"""Static server for the local audits, with the URL rule GitHub Pages actually applies.

WHY THIS EXISTS. scripts/ci-full.sh used to serve the site with `python3 -m http.server`,
which only answers a request for a file that exists at that exact path. That was fine while
every internal link ended in `.html`. It stopped being fine on 2026-10-04, when the site moved
to EXTENSIONLESS URLs: `/guides/rv-towing-capacity` is served by Pages from
`guides/rv-towing-capacity.html`, but the plain server answered 404.

The result was silent and expensive. The link crawl reported 234 broken links of 461, of which
468 responses were `404` -- and every single one was `127.0.0.1`, meaning the audit was failing
on its own test server rather than on anything a reader would meet. It ran red on the weekly
schedule from 2026-10-04 until it was traced on 2026-10-05. **An audit that cannot serve the
site it audits is worse than no audit: it trains the reader to ignore the report.**

THE RULE, which is Pages' own, in order:
    /foo            -> foo.html, then foo/index.html
    /foo/           -> foo/index.html
    /foo.html       -> as-is (so explicit links keep working)
A directory request that has no index falls through to a listing only if it exists.

USAGE:  python3 scripts/serve-static.py <port>
"""
import http.server
import os
import socketserver
import sys


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = super().translate_path(path)
        # A path that already names a file, or a directory, is served normally.
        if os.path.isfile(p):
            return p
        if path.endswith("/"):
            idx = os.path.join(p, "index.html")
            return idx if os.path.exists(idx) else p
        # The Pages rule: try `<path>.html`, then `<path>/index.html`.
        as_html = p + ".html"
        if os.path.isfile(as_html):
            return as_html
        as_dir = os.path.join(p, "index.html")
        if os.path.isfile(as_dir):
            return as_dir
        return p

    def log_message(self, fmt, *args):
        pass  # quiet; the crawl output is the interesting part


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8177
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
