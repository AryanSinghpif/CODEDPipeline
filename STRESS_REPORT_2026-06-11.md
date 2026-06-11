# Stress Report — 2026-06-11

Stress-tested the pipeline against 8 government PDFs (4× DARPG monthly GRAI
reports, CPGRAMS Feb-2023, MoSPI Annual Report, Energy Statistics 2026,
PLFS 2025). Found and fixed 6 defects; all 3 regression guards GREEN at HEAD.

Harness: `backend/tools/stress_run.py` (chunked headless runs, CSV + metadata
per PDF) and `backend/tools/regression_guards.py` (DES / DARPG / PLFS guards).

## Results at HEAD (after fixes)

| PDF | Pages | Found | Passed | After stitch | Titled | col_N | Fail reasons |
|---|---|---|---|---|---|---|---|
| DARPG Jan 2026 | 38 | 37 | 37 (100%) | 26 (11 merges) | 46% | 4% | — |
| DARPG Feb 2026 | 45 | 37 | 36 (97%) | 30 (6 merges) | 43% | 22% | 1× too_few_rows |
| DARPG Mar 2026 | 54 | 52 | 51 (98%) | 27 (24 merges) | 52% | 6% | 1× too_few_rows |
| DARPG Apr 2026 | 64 | 67 | 66 (99%) | 42 (24 merges) | 33% | 31% | 1× too_few_rows |
| CPGRAMS 2023-02 | 28 | 15 | 13 (87%) | 13 | 31% | 8% | 2× too_few_rows (KPI strips) |
| Annual Report | 163 | 19 | 18 (95%) | 18 | 56% | 25% | 1× too_few_columns |
| Energy Statistics 2026 | 204 | 104 | 104 (100%) | 103 | 72% | 26% | — |
| PLFS 2025 | 653 | 598 | 583 (97%) | 321 (262 merges) | 87% | 59% | 12× too_few_rows, 2× mostly_empty, 1× merged_rows |

"Titled" = real printed title found (sequential `Table N (p.X)` is correct
when the PDF prints none). "col_N" = average share of unnamed fallback
columns per table.

## Defects found and fixed

### 1. Translation silently skipped for every cell (fixed: `de377ee`)
`translate_dataframe` matched only `dtype == object`, but `clean_dataframe`
returns pandas `StringDtype` columns on pandas≥2/py3.14 — the entire
Hindi-translation layer was a no-op in this environment.
**Before:** DES district column = Kruti Dev soup (`';ksiqj`), PLFS rows in
mangled Devanagari, guard suite 6 failures.
**After:** districts = Sheopur/Morena/…, PLFS p11 fully English; 3 failures left.

### 2. Title fragments leaked into column headers (fixed: `69afaea`)
DES pages span the printed title across the header grid, so columns came out
as `table_tabel_telephone_number_center_2020_21`; bilingual headers also
duplicated words (`telephone_centre_center`, `number_number`).
**After:** p148 = `[s_no, district, telephone_number_center_2020_21,
telephone_center_number_2021_22]`; 11/11 DES tables named from printed
titles (was 4).

### 3. Kruti soup evading detection (fixed: `cc03c05`)
`izfr`, `iathd\`r` are lowercase-with-vowels and dodge `looks_kruti`; naive
marker extension would mangle English ("utilization" contains `iz`).
Fix: glossary-confirmed conversion — token counts as soup only if its
Devanagari conversion is a known glossary word.
**After:** `izfr Lakh Population` → `per Lakh Population`; English verified
untouched; guard suite GREEN.

### 4. Stitcher crash on duplicate column names (fixed: `8cde831`)
`pd.concat` raises `InvalidIndexError` when fragments carry duplicate labels
(several unnamed `col` columns) — this killed the entire PLFS run (fatal
crash mid-upload in the app). Also `_named_frac` only excluded `col_<n>`,
counting bare `col` as "named" → false-merge eligibility for unnamed pages.
**Before:** PLFS = 0 tables (crash). **After:** PLFS = 583 passed / 321 stitched.

### 5. First data row eaten on headerless continuation pages (fixed: `6a682b8`)
DARPG indicator matrices print data from row one on follow-on pages.
`detect_data_start` demanded a serial number in column 0 (label-first rows
never matched) and returned `0` ambiguously for "not found"; the override
ignored `data_start == 0`. Result: **one ministry silently deleted per
continuation page** (6 rows lost in Feb alone) + fragments never stitched.
**After:** rows preserved (`Department of Land Resources` back), Group A/B
matrices stitch across pages (Group B pp13-15 = 49 rows), DARPG Mar merges
24 fragments.

### 6. Single-mega-row crushed tables passed extraction (fixed: `4ac3a35`)
Annual Report GVA statements collapse to 4 lattice rows with the whole data
block inside one cell; 1-of-4 multiline rows sat exactly at the 25% crush
threshold, so the page never reached the stream fallback and failed later as
`merged_rows` (data lost). New signal: any cell splitting into ≥4 mostly-
numeric fragments. **After:** Annual p19 stream-extracts 26+29 rows × 6 cols
row-wise; Annual passed 16 → 18.

### 7. Guard spec discrepancy (documented, `69afaea`)
The given regression expectation "DARPG 3.1 = 60 rows" does not match the
PDF: serials run 1-20 (p8) + 21-40 (p9) and table 3.2 starts on p10. Guard
now asserts the verifiable truth (40 rows, unbroken serial sequence).

## Known limitations (not fixed, with suggested approach)

- **KPI strips rejected** (`too_few_rows`): 3-cell summary strips
  ("Receipts Disposed Pending — 9,576 / 8,808 / 768", CPGRAMS p15/p21,
  DARPG p24/p37/p44, PLFS p6/p9). These aren't tables; if wanted, add a
  KPI-strip extractor that emits them as key-value records instead of
  forcing them through table validation.
- **PLFS bilingual multi-band headers** → 59% col_N. Headers are rotated,
  wrapped, bilingual 3-band grids camelot mangles badly. Approach: extend
  `_repair_header_positionally` to cluster pdfplumber words into bands per
  x-range, translate each band via glossary, then join bands per column.
- **Devanagari residue** in 70/321 PLFS and 31/103 Energy tables: glossary
  coverage gaps (long phrases, sample-survey jargon). Approach: auto-learn
  pairs from bilingual cells the same way `learn_legacy_map.py` paired the
  district columns — most PLFS cells print Hindi and English side by side.
- **Annual p110 `too_few_columns`**: a 2-column timeline list, genuinely not
  a data table.

## Top 3 remaining opportunities (by impact)

1. **PLFS-style positional header reconstruction** — would cut PLFS col_N
   from 59% toward ~15% across 321 tables; PLFS is the largest corpus here
   (653 pages) and the layout family is shared with NSS reports.
2. **Auto-learned bilingual glossary** — removes Devanagari residue in ~100
   tables across PLFS + Energy without hand-curating entries.
3. **Section-heading name mining for stitched ranking tables** — DARPG
   titled% sits at 33-52%; the big pp15-21 ranking grid (90 rows, serials
   verified) still gets fallback `Table 11 (p.15)` because its heading
   ("2.4 Ranking of Ministries/Departments…") sits two lines above the
   bbox. Search upward for the nearest numbered heading before falling back.
