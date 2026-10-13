# Iran — LawCodex (قوانین و مقررات جمهوری اسلامی ایران)

Iranian legislation as Markdown, in Persian. The texts come from the laws database
(سامانه قوانین و مقررات) of the **Islamic Parliament Research Center** (مرکز پژوهش‌های مجلس
شورای اسلامی), `rc.majlis.ir`. Part of [LawCodex](https://github.com/LawCodex): one repository per
jurisdiction.

- Retrieved: **2026-10-13**, from **Internet Archive captures** of the official pages, taken
  between 2010 and 2022.
- Version: the database gives each instrument **as approved and published**. Amendments are
  separate instruments, so the texts are **not consolidated**. The Research Center's own
  warning is kept as metadata where present: «نسخ، اصلاح، الحاق، تمدید مهلت — جدول نسخ را بازبینی
  فرمایید» ("repeals or amendments exist — check the repeal table").

## Why Internet Archive copies

- `rc.majlis.ir` could not be reached from the network used for this build: the TLS
  connection was reset or timed out.
- The Ministry of Justice / Vice-Presidency for Legal Affairs portal `qavanin.ir` (dotic.ir)
  answers automated clients with an ArvanCloud JavaScript challenge. LawCodex does not work
  around bot protection.

The laws were therefore taken from the Wayback Machine's copies of the official page
`https://rc.majlis.ir/fa/law/show/<id>`. For each id, the newest capture from before 2023 that
holds the law text is used. Later captures are mostly bot-challenge pages. Each file records
the exact capture in `archived:`.

## Coverage

| Directory | Approving authority (مرجع تصویب) | Files |
| --- | --- | ---: |
| `fa/constitution/` | قانون اساسی جمهوری اسلامی ایران — the 1979 Constitution as revised in 1989 (1368), 177 articles | 1 |
| `fa/laws/<year>/` | مصوبات مجلس شورا — acts of the Majlis: the National Consultative Assembly (مجلس شورای ملی, 1906–1979), the Senate, and the Islamic Consultative Assembly (مجلس شورای اسلامی) since 1980 | 3,553 |
| `fa/revolutionary-council/<year>/` | مصوبات شورای انقلاب — Revolutionary Council, 1979–1980 | 344 |
| `fa/expediency-council/<year>/` | مصوبات مجمع تشخیص مصلحت نظام — Expediency Discernment Council | 124 |
| `fa/guardian-council/<year>/` | شورای نگهبان — Guardian Council | 7 |
| `fa/government/<year>/` | مصوبات هیات وزیران — Council of Ministers resolutions and regulations | 7,438 |
| `fa/cultural-revolution-council/<year>/` | مصوبات شورای عالی انقلاب فرهنگی — Supreme Council of the Cultural Revolution | 565 |
| `fa/judiciary/<year>/` | مصوبات / بخشنامه‌های قوه قضاییه — Judiciary regulations and circulars | 608 |
| `fa/supreme-court-precedents/<year>/` | آرای وحدت رویه دیوان عالی کشور — binding precedent rulings of the Supreme Court | 414 |
| `fa/administrative-court/<year>/` | آرای وحدت رویه دیوان عدالت اداری — Court of Administrative Justice rulings, including annulments of regulations | 2,017 |
| `fa/commissions/<year>/` | parliamentary commissions | 12 |
| `fa/other/<year>/` | other bodies: Supreme Council of Urban Planning and Architecture (410), Supreme Administrative Council (≈200), Government secretariat (99), Economic Council (≈100), Supreme Council of Cyberspace (33), ministries and others | 1,054 |
| **Total** | | **16,137** |

The texts date from 1906 (the constitutional period) to 2022. 130 files have no approval date
and are filed under `undated/`. `status` is `unknown` for all files except the Constitution
(`in_force`). The database does not give a machine-readable in-force flag.

**This is a partial set.** The Internet Archive holds captures for 17,009 law ids of
rc.majlis.ir, and 16,137 texts were converted. The live database is several times larger,
especially for secondary legislation. The main codes are included, for example:

- قانون مدنی (Civil Code, 1307–1314)
- قانون تجارت (Commercial Code, 1311)
- قانون مجازات اسلامی (Islamic Penal Code, 1392)
- قانون آیین دادرسی مدنی (Code of Civil Procedure, 1318)
- several labour laws (قانون کار)

### Skipped and gaps

- **Skipped captures:**
  - 41 constitutions of other countries (قانون اساسی کشور ها) that the database also holds;
  - 22 per-chapter pages of the Iranian Constitution (the full text comes from
    `/fa/content/iran_constitution` instead);
  - 49 captures with no or empty text.
- **About 760 law ids** had no usable capture: every capture was a bot-challenge page, an
  "invalid session" error, or failed to load.
- **No official English text** is included: none was available from the source.
- **Source quirks, kept as they are:**
  - Pre-2013 texts are hard-wrapped like the printed gazette.
  - In some recent texts (about 2015–2022) the gazette header, with the number and date, is
    in visual rather than logical order, for example «۱۶/۹/۱۳۹۵ هـ۵۳۲۷۳ت/۱۱۳۷۴۴شماره».
  - Some recent texts lack zero-width non-joiners (e.g. «میشود»).
  - Article bodies themselves read correctly.

## Structure

```
fa/constitution/1358-constitution.md
fa/<authority>/<year>/<id>.md         e.g. fa/laws/1307/97937.md  قانون مدنی
```

- `<year>` is the **Solar Hijri** (هجری شمسی) year of approval, the year Iranian law uses
  to cite legislation.
- `<id>` is the rc.majlis.ir law id.
- The front matter has `title`, `identifier` (`rc.majlis.ir:<id>`), `type`,
  `approving_authority`, `date` (Gregorian, converted), `date_solar_hijri` (تاریخ تصویب),
  `published_solar_hijri`, `signed_solar_hijri`, `gazette_number` (روزنامه رسمی),
  `file_number`, `status`, `source` (official URL), `archived` (capture used) and `retrieved`.
- In the body, articles (ماده N, ماده واحده, اصل) are `#####` headings, and chapters and parts
  (فصل, بخش, باب) are `###`. Notes (تبصره) and lettered or numbered clauses start new
  paragraphs. Nothing is translated or summarised.

The site changed design four times between 2010 and 2022. `scripts/ir_convert.py` handles
each layout.

## Licence / copyright

Laws and regulations are official texts, which are generally not subject to copyright. The
Research Center's pages carry a general copyright notice for the site. LawCodex reproduces only the legislative
texts, unchanged, each with a link to its official page.

## Regenerate

```sh
python3 scripts/ir_fetch.py   ../_raw/ir --workers 4    # Wayback CDX (cached) + captures
python3 scripts/ir_convert.py ../_raw/ir .
```
