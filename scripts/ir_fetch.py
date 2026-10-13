#!/usr/bin/env python3
"""Fetch Iranian laws (rc.majlis.ir "سامانه قوانین") from the Internet Archive.

rc.majlis.ir (Islamic Parliament Research Center laws database) was not reachable from the
build network (TLS connection reset / timeouts) and qavanin.ir (Ministry of Justice / dotic)
answers with a JavaScript bot challenge, so this script reads the Wayback Machine captures of
the official rc.majlis.ir law pages: https://rc.majlis.ir/fa/law/show/<id>.

Usage: ir_fetch.py [RAW_DIR] [--workers 3]
  1. lists archived captures with the Wayback CDX API (cached in RAW_DIR/cdx.txt);
  2. downloads the newest capture of every law page into RAW_DIR/html/<id>.html.
"""
import argparse
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
HERE = os.path.dirname(os.path.abspath(__file__))
CDX = ("https://web.archive.org/cdx/search/cdx?url=rc.majlis.ir/fa/law/show/&matchType=prefix"
       "&filter=statuscode:200&fl=original,timestamp&limit=500000")

CONSTITUTION = ("https://web.archive.org/web/20220409043635id_/"
                "https://rc.majlis.ir/fa/content/iran_constitution")
S = requests.Session()
S.headers["User-Agent"] = UA


def get(url, tries=6):
    for a in range(tries):
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
            time.sleep(10 * (a + 1))
        except requests.RequestException:
            time.sleep(10 * (a + 1))
    return None


def captures(raw):
    fn = os.path.join(raw, "cdx.txt")
    if not os.path.exists(fn):
        r = get(CDX)
        open(fn, "w").write(r.text)
    caps = {}  # id -> list of (timestamp, url), newest first
    for line in open(fn):
        parts = line.split()
        if len(parts) != 2:
            continue
        url, ts = parts
        m = re.match(r"https?://rc\.majlis\.ir(?::80)?/fa/law/show/(\d+)/?$", url)
        if not m:
            continue
        caps.setdefault(int(m.group(1)), []).append((ts, url))
    for v in caps.values():
        v.sort(key=lambda c: (c[0] < "2023", c[0]), reverse=True)  # pre-2023 first: later captures are mostly bot-challenge pages
    return caps


def good(b):
    h = b.decode("utf-8", "replace")
    return "Transferring to the website" not in h and ("متن قانون" in h or "جزئیات قانون" in h
                                                       or "law-content" in h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", nargs="?", default=os.path.join(HERE, "..", "..", "_raw", "ir"))
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    out = os.path.join(a.raw, "html")
    os.makedirs(out, exist_ok=True)
    cfn = os.path.join(a.raw, "constitution.html")
    if not os.path.exists(cfn):
        r = get(CONSTITUTION)
        if r is not None:
            open(cfn, "wb").write(r.content)
    caps = captures(a.raw)
    jobs = []
    for i, lst in sorted(caps.items()):
        fn = os.path.join(out, f"{i}.html")
        if os.path.exists(fn) and good(open(fn, "rb").read()):
            continue
        if os.path.exists(fn + ".bad"):
            continue
        jobs.append((fn, lst))
    print(len(caps), "laws;", len(jobs), "to fetch", flush=True)
    n = [0]

    def job(j):
        fn, lst = j
        r = None
        used = None
        for ts, url in lst[:6]:
            r = get(f"https://web.archive.org/web/{ts}id_/{url}")
            time.sleep(1.0)
            if r is not None and good(r.content):
                used = f"https://web.archive.org/web/{ts}/{url}"
                break
            r = None
        if r is None:
            print("MISS", fn, flush=True)
            open(fn + ".bad", "w").close()
            if os.path.exists(fn):
                os.remove(fn)
            return
        open(fn + ".tmp", "wb").write(r.content)
        os.replace(fn + ".tmp", fn)
        open(fn + ".ts", "w").write(used)
        n[0] += 1
        if n[0] % 200 == 0:
            print("fetched", n[0], flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(job, jobs))
    print("done", n[0], flush=True)


if __name__ == "__main__":
    main()
