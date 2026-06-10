import sys

from backend.app.cleaning.header_builder import apply_headers
from backend.app.cleaning.header_detector import detect_header_rows
from backend.app.cleaning.header_postprocessor import clean_headers
from backend.app.cleaning.universal_cleaner import clean_dataframe
from backend.app.extract.table_extractor import extract_tables
from backend.app.standardization.table_name_extractor import extract_table_name
from backend.app.translation.hindi_translator import translate_dataframe
from backend.app.validation.table_validator import validate_table

pdf = sys.argv[1]
tables = extract_tables(pdf)
print(f"extracted: {len(tables)} tables")

passed, failed = 0, {}
for t in tables:
    try:
        df = clean_dataframe(t["dataframe"])
        h = detect_header_rows(df)
        nm = extract_table_name(df, h, t.get("caption"))
        df = apply_headers(df, h)
        df = translate_dataframe(df)
        df = clean_headers(df)
        s = validate_table(df)
    except Exception as e:
        failed[f"err:{type(e).__name__}"] = failed.get(f"err:{type(e).__name__}", 0) + 1
        continue
    if s["passed"]:
        passed += 1
        if passed <= 12:
            print(f"  p{t['page']:>3} [{t['flavor']}] {df.shape} name='{nm}' cols={list(df.columns)[:5]}")
            print(f"        row0={[str(v)[:18] for v in df.iloc[0].tolist()[:5]]}")
    else:
        failed[s["reason"]] = failed.get(s["reason"], 0) + 1
print(f"PASSED: {passed}  FAILED: {failed}")
