from backend.app.extract.table_extractor import extract_tables
from backend.app.cleaning.universal_cleaner import clean_dataframe
from backend.app.cleaning.header_detector import detect_header_rows
from backend.app.cleaning.header_builder import apply_headers


PDF_PATH = "Sample.pdf"

tables = extract_tables(PDF_PATH)

print(f"\nTotal Tables: {len(tables)}\n")


TARGET_TABLES = [111, 113, 171, 175]


for table in tables:

    table_id = table["table_id"]

    if table_id not in TARGET_TABLES:
        continue

    print(f"\n\n========== TABLE {table_id} ==========\n")

    raw_df = table["dataframe"]

    cleaned_df = clean_dataframe(raw_df)

    header_rows = detect_header_rows(cleaned_df)

    print(f"Detected Header Rows: {header_rows}")

    final_df = apply_headers(cleaned_df, header_rows)

    print(final_df.head())

    print("\nCOLUMNS:\n")

    for col in final_df.columns:
        print(col)