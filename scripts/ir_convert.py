#!/usr/bin/env python3
"""Convert archived rc.majlis.ir law pages (see ir_fetch.py) to Markdown.

Usage: ir_convert.py [RAW_DIR] [OUT_DIR]
"""
import collections
import glob
import html
import json
import os
import re
import sys
from datetime import date

import yaml
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "_raw", "ir")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..")
RETRIEVED = os.environ.get("RETRIEVED", date.today().isoformat())

FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# approving authority (مرجع تصویب) -> output directory
AUTH_DIRS = [
    ("مجلس شورا", "laws"),          # مصوبات مجلس شورا / مجلس شورای اسلامی / مجلس شورای ملی
    ("مجلس سنا", "laws"),
    ("مجمع تشخیص", "expediency-council"),
    ("شورای انقلاب", "revolutionary-council"),
    ("شورای عالی انقلاب فرهنگی", "cultural-revolution-council"),
    ("شورای عالی امنیت", "supreme-national-security-council"),
    ("مقام معظم رهبری", "leader"),
    ("رهبری", "leader"),
    ("هیات وزیران", "government"),
    ("هیئت وزیران", "government"),
    ("هیأت وزیران", "government"),
    ("کمیسیون", "commissions"),
    ("دیوان عالی کشور", "supreme-court-precedents"),
    ("دیوان عدالت اداری", "administrative-court"),
    ("شورای نگهبان", "guardian-council"),
]


def norm(s):
    s = s.replace("\xa0", " ").replace("‏", "").replace("‎", "")
    s = re.sub(r"^[‌\s]+|[‌\s]+$", "", s)
    return re.sub(r"[ \t]+", " ", s)


def field(h, label):
    m = re.search(r"(?:<h3[^>]*>|<span class=\"db\">)\s*" + re.escape(label)
                  + r"\s*:\s*(?:</h3>)?\s*(?:<a[^>]*>)?([^<]*)", h)
    return norm(html.unescape(m.group(1))) if m else None


def jdate(s):
    if not s:
        return None
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s.translate(FA_DIGITS))
    return f"{m.group(1)}/{int(m.group(2)):02d}/{int(m.group(3)):02d}" if m else None


def j2g(jd):
    """Solar Hijri 'YYYY/MM/DD' -> ISO Gregorian date (standard arithmetic algorithm)."""
    if not jd:
        return None
    jy, jm, jdd = map(int, jd.split("/"))
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + jdd
    days += (jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    for gm, ml in enumerate([31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], 1):
        if gd <= ml:
            break
        gd -= ml
    return f"{gy:04d}-{gm:02d}-{gd:02d}"


ART = re.compile(r"^(ماده\s*(?:واحده|[0-9]+(?:\s*مکرر(?:\s*\d+)?)?)|اصل\s*[0-9]+(?:\s*مکرر)?)\s*[-–ـ:.]?\s*(.*)$")
HEAD = re.compile(r"^(فصل|بخش|باب|کتاب|مبحث|قسمت|جلد)\s+\S+")
ENUM = re.compile(r"^(?:تبصره|[0-9]+\s*[-–ـ.)]|(?:الف|ب|پ|ت|ث|ج|چ|ح|خ|د|ذ|ر|ز|ژ|س|ش)\s*[-–ـ)])")


def esc(line):
    if re.match(r"^(#|>|\d+\.\s|[-+*]\s|={3,}|-{3,})", line):
        return "\\" + line
    return line


def to_md(lines):
    out = []
    prev = False
    for ln in lines:
        m = ART.match(ln)
        if m:
            out += ["", "##### " + m.group(1).strip(), ""]
            if m.group(2):
                out.append(esc(m.group(2)))
            prev = bool(m.group(2))
            continue
        if HEAD.match(ln) and len(ln) < 80:
            out += ["", "### " + ln, ""]
            prev = False
            continue
        if prev and ENUM.match(ln):
            out.append("")
        out.append(esc(ln))
        prev = True
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def parse(h):
    s = BeautifulSoup(h, "lxml")
    div = s.find("div", class_="normal-text")
    title = None
    if div is not None:                      # site design until ~2013
        h1 = s.find("h1", string=re.compile("اطلاعات کامل قانون"))
        h2 = h1.find_next("h2") if h1 else None
        title = norm(h2.get_text(" ", strip=True)) if h2 else None
    else:                                    # site design ~2014-2022
        div = s.find("div", id="ltab1")
        if div is None:
            return None
        h4 = div.find("h4", class_="news-header")
        if h4 is not None:
            title = norm(h4.get_text(" ", strip=True))
            h4.decompose()
    if not title:
        t = s.find("title")
        title = norm(re.sub(r"^مرکز پژوهشها\s*-\s*", "", t.get_text(" ", strip=True))) if t else ""
    raw = div.decode_contents()
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", raw)
    parts = re.split(r"(?i)<br\s*/?>|</p>|</div>|</tr>", raw)
    lines = []
    for p in parts:
        t = norm(html.unescape(re.sub(r"<[^>]+>", "", p)))
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            lines.append(t)
    meta = {k: field(h, lab) for k, lab in [
        ("approved", "تاریخ تصویب"), ("authority", "مرجع تصویب"), ("signed", "تاریخ امضا"),
        ("published", "تاریخ انتشار"), ("confirmed", "تاریخ تایید"), ("file", "شماره پرونده"),
        ("gazette", "روزنامه")]}
    meta["amend_warning"] = "جدول نسخ" in h
    return title, lines, meta


def main():
    counts = collections.Counter()
    skipped = []
    for fn in sorted(glob.glob(os.path.join(RAW, "html", "*.html")), key=lambda x: int(os.path.basename(x)[:-5])):
        i = int(os.path.basename(fn)[:-5])
        h = open(fn, "rb").read().decode("utf-8", "replace")
        r = parse(h)
        if not r:
            skipped.append([i, "no law text in capture"])
            continue
        title, lines, meta = r
        if sum(len(x) for x in lines) < 40:
            skipped.append([i, "empty text"])
            continue
        auth = meta.get("authority") or ""
        d = next((v for k, v in AUTH_DIRS if k in auth), "other")
        if i == 133613 or title.startswith("قانون اساسی جمهوری اسلامی"):
            d = "constitution"
        appr = jdate(meta.get("approved"))
        year = appr[:4] if appr else "undated"
        fm = {
            "title": title,
            "identifier": f"rc.majlis.ir:{i}",
            "type": {"laws": "act", "constitution": "constitution"}.get(d, "other"),
            "approving_authority": auth or None,
            "jurisdiction": "ir",
            "language": "fa",
            "date": j2g(appr),
            "date_solar_hijri": appr,
            "published_solar_hijri": jdate(meta.get("published")),
            "signed_solar_hijri": jdate(meta.get("signed")),
            "gazette_number": meta.get("gazette") or None,
            "file_number": meta.get("file") or None,
            "status": "unknown",
            "source": f"https://rc.majlis.ir/fa/law/show/{i}",
            "retrieved": RETRIEVED,
        }
        fm["archived"] = None
        ts_file = fn + ".ts"
        if os.path.exists(ts_file):
            fm["archived"] = open(ts_file).read().strip()
        fm = {k: v for k, v in fm.items() if v is not None}
        if len(lines) and re.sub(r"\s", "", lines[0]) == re.sub(r"\s", "", title):
            lines = lines[1:]
        rel = os.path.join("fa", d, year, f"{i}.md")
        path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n")
            f.write(f"# {title}\n\n")
            f.write(to_md(lines))
        counts[d] += 1
    for k, v in counts.most_common():
        print(k, v)
    print("skipped", len(skipped))
    json.dump(skipped, open(os.path.join(RAW, "skipped.json"), "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
