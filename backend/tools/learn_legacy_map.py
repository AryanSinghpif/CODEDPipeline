"""
Learn a legacy-Hindi (Kruti Dev / Chanakya font) -> English mapping
from a district handbook PDF by pairing the Hindi name column
(column 2) with the English "District" column (last column) of
every extracted table.

Usage:
    python -m backend.tools.learn_legacy_map <pdf_path> [--pages 1-200] [--min-count 2] [--out mapping.json]

The output JSON can be merged into LEGACY_MAP in
backend/app/translation/hindi_translator.py to support PDFs
from other states.
"""

import argparse
import json
import re
import warnings
from collections import Counter

warnings.filterwarnings("ignore")

import camelot


def learn_pairs(pdf_path, pages, chunk_size=40):
    """Extract (hindi, english) pairs page-chunk by page-chunk."""

    start, end = pages
    pairs = Counter()

    for lo in range(start, end + 1, chunk_size):
        hi = min(lo + chunk_size - 1, end)
        try:
            tables = camelot.read_pdf(
                pdf_path, pages=f"{lo}-{hi}", flavor="lattice"
            )
        except Exception as e:
            print(f"pages {lo}-{hi}: skipped ({e})")
            continue

        for t in tables:
            df = t.df
            if df.shape[1] < 3:
                continue

            for _, row in df.iterrows():
                vals = [
                    re.sub(r"\s+", " ", str(v).replace("\n", " ")).strip()
                    for v in row.tolist()
                ]
                hin, eng = vals[1], vals[-1]

                if not hin or not eng or hin == eng:
                    continue

                # english side: a plausible proper name
                if not re.fullmatch(
                    r"[A-Z][A-Za-z]+([ .][A-Za-z]+)*", eng
                ) or len(eng) < 4:
                    continue

                pairs[(hin, eng)] += 1

    return pairs


def build_mapping(pairs, min_count):
    """Keep the most frequent english value per hindi key."""

    mapping = {}
    for (hin, eng), count in sorted(pairs.items(), key=lambda x: -x[1]):
        if count >= min_count and hin not in mapping:
            mapping[hin] = eng
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path")
    parser.add_argument(
        "--pages",
        default="1-200",
        help="page range to scan, e.g. 10-160 (default 1-200)",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=2,
        help="min occurrences for a pair to be trusted (default 2)",
    )
    parser.add_argument(
        "--out",
        default="legacy_map.json",
        help="output JSON path (default legacy_map.json)",
    )
    args = parser.parse_args()

    start, end = (int(x) for x in args.pages.split("-"))
    pairs = learn_pairs(args.pdf_path, (start, end))
    mapping = build_mapping(pairs, args.min_count)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"{len(mapping)} mappings written to {args.out}")
    for hin, eng in list(mapping.items())[:10]:
        print(f"  {hin!r} -> {eng}")


if __name__ == "__main__":
    main()
