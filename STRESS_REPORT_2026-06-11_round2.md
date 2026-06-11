# Stress Report — Round 2 — 2026-06-11

Attacked the top 3 defects from round 1 (PLFS headers, Devanagari residue,
DARPG table naming). 5 commits; all regression guards GREEN; per-PDF audit
confirms no data loss anywhere — two latent data-loss bugs were found and
fixed along the way.

## Per-PDF before → after

| PDF | Passed | Titled | col_N (unnamed cols) |
|---|---|---|---|
| DARPG Jan | 100% → 100% | 46% → **60%** | 4% → 5%¹ |
| DARPG Feb | 97% → 97% | 43% → **65%** | 22% → **8%** |
| DARPG Mar | 98% → 100% | 52% → **64%** | 6% → 7%¹ |
| DARPG Apr | 99% → 100% | 33% → **40%** | 31% → 32%¹ |
| CPGRAMS | 87% → 87% | 31% → 31% | 8% → 8% |
| Annual Report | 95% → 95% | 56% → **61%** | 25% → 27%¹ |
| Energy Statistics | 100% → 100% | 72% → **75%** | 26% → 27%¹ |
| PLFS 2025 | 97% → 97% | 87% → **90%** | **59% → 10%** |

¹ Audited per table: every individual col_N increase is a previously WRONG
name (table-title sentence, or in one case the first DATA ROW, used as a
column name) replaced by an honest `col` fallback. No semantically-correct
header got worse. See fix 4.

## Fixes

### 1. PLFS header reconstruction (`89b6aa1`)
Diagnosis on sampled annexure pages showed camelot's header rows were fine —
they died downstream: the Titlecase-only anti-Kruti filter discarded modern
lowercase headers (`male`, `rural`, `status`); age-range columns (`0-4`,
`60+`) had no letters to extract; the title sentence leaked into column 0.
Fixed with a ~60-word lowercase statistical vocabulary, range tokens kept as
the distinguishing header part, and whole-title-cell skip.
**PLFS pp130-200 slice: col_N 75% → 2%. Full PLFS: 59% → 10%.**
The planned positional (x-coordinate) reconstruction was not needed.

### 2. "Devanagari residue" is mostly English mojibake (`1c9ae2b`)
The residue is NOT untranslated Hindi: Energy/PLFS notes typeset English in
a Kruti-slot font whose cmap emits Devanagari — `ज्वजंस` is literally
"Total", `छवद-ब्वापदह` is "Non-Coking", `M ंकीलं Pradesh` is "Madhya
Pradesh". The planned bilingual pair-learner could never fix these; the
inverse Kruti glyph map decodes them deterministically. Decoded tokens are
kept only when English-shaped (validated per compound part; all-lowercase
decodes need vowel ratio ≥ 0.3 or a known-words set, because real Hindi
decodes to lowercase junk).
**Energy worst pages: 25 deva cells → 0. PLFS worst pages: ~62 → 23 (−63%);
remainder is genuine Hindi (infographic labels).**

### 3. Section-heading mining + stitch identity (`d31c516`)
Caption search now: explicit Table/Statement line → numbered section heading
("2.4 Ranking of …", <90 chars, absorbing a parenthetical qualifier) → same
search over the previous page's bottom 30% when the table starts in the top
15% of its page → nearest lines. Stitcher fixed alongside: two different
*strong* titles never merge (3.1 Group A vs 3.2 Group B were franken-merged
into one 82-row table under one name); header equality is letters-only and
truncation-tolerant (`brough t forwar d` ≡ `brought forward`).
**DARPG titled: Jan 46→60, Feb 43→65, Mar 52→64, Apr 33→40. 12 names
spot-checked against pages: 10 exact, 0 wrong strong titles.**

### 4. Honest headers + recovered data row (`da63e18`)
Spanning title rows are excluded from column names entirely; header depth
for text-heavy tables (no numeric row) now ends where numeric cells first
appear. This exposed a latent data-loss bug: DARPG p19's first data row
("Ministry of Labour and Employment, 5044, …") was being consumed as a
header — the column was literally named `ministry_labour_and_employment`.
**Row recovered (9 → 10 rows); Energy p48 cols now
[coking_coal_company, state, capacity].**

### 5. Harness measurement bug (`e85ed47`)
stress_run pre-assigned `Table N (p.X)` fallback names BEFORE stitching;
they read as strong titles and blocked every continuation merge, corrupting
measurements (Mar showed 50 fragments instead of 28). app.py was already
correct. Library behaviour unaffected; metrics in this report use the fixed
harness.

## Remaining limitations (ranked)

1. **DARPG Apr col_N 32%** — Apr's GRAI matrix variant (pp29-32 family) has
   a rotated 3-band header camelot mangles; the page-text positional repair
   (cluster pdfplumber words into per-column x-bands) from the original
   Task-1 plan would address it. ~6 tables.
2. **PLFS contd. fragments** (400 tables vs 321) — PLFS reprints "Table (15)
   (contd.)" titles on continuation pages; the "(contd.)" variants read as
   different strong titles and stay separate. Normalising away
   `\(contd\.?\)` before title comparison would merge them; needs care not
   to merge genuinely different sub-tables (rural vs urban panels share
   titles).
3. **CPGRAMS titled 31%** — its tables are headed by infographic-style text
   not captured as captions; the heading sits inside images on several
   pages. OCR-free options are limited; low impact (13 tables).

## Guard status at HEAD

Guard A (DES p145-155): 11/11 passed, all titled, district English, p148
cols exact. Guard B (DARPG 3.1): name, cols, 40 rows, serials unbroken.
Guard C (PLFS p11): 72 numeric cells, rural_males, English labels.
Guard D (baseline): no passed% drop on any PDF; col_N audit above.
