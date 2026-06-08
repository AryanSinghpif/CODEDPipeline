import os
import pandas as pd

from backend.app.extract.table_extractor import extract_tables
from backend.app.cleaning.universal_cleaner import clean_dataframe
from backend.app.cleaning.header_detector import detect_header_rows
from backend.app.cleaning.header_builder import apply_headers
from backend.app.cleaning.header_postprocessor import clean_headers
from backend.app.standardization.table_name_extractor import extract_table_name
from backend.app.standardization.metadata_builder import build_metadata

PDF = "Sample.pdf"

OUT = "backend/data/exports"

CSV = f"{OUT}/csv"

os.makedirs(
    CSV,
    exist_ok=True
)

tables = extract_tables(PDF)

failed = []

done = 0

catalog = []

for table in tables:

    try:

        df = clean_dataframe(
            table["dataframe"]
        )

        h = detect_header_rows(df)

        table_name = extract_table_name(
            df,
            h
        )

        df = apply_headers(
            df,
            h
        )

        df = clean_headers(df)

        from backend.app.validation.table_validator import validate_table

        status = validate_table(df)

        if status["passed"]:

            metadata = build_metadata(
                table["table_id"],
                table_name,
                table["page"],
                df
            )

            catalog.append(
                metadata
            )

            path = (
                f"{CSV}/"
                f"table_"
                f"{table['table_id']}.csv"
            )

            df.to_csv(
                path,
                index=False
            )

            done += 1

        else:

            failed.append({
                "table": table["table_id"],
                "page": table["page"],
                "reason": status["reason"]
            })

    except Exception as e:

        failed.append({
            "table": table["table_id"],
            "page": table["page"],
            "reason": str(e)
        })

pd.DataFrame(
    catalog
).to_csv(
    f"{OUT}/table_catalog.csv",
    index=False
)

pd.DataFrame(
    failed
).to_csv(
    f"{OUT}/failed_tables.csv",
    index=False
)

print()

print(f"TOTAL {len(tables)}")
print(f"SUCCESS {done}")
print(f"FAILED {len(failed)}")