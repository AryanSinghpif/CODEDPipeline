import pandas as pd

from backend.app.extract.table_extractor import extract_tables
from backend.app.cleaning.universal_cleaner import clean_dataframe
from backend.app.cleaning.header_detector import detect_header_rows
from backend.app.cleaning.data_start_detector import detect_data_start

tables = extract_tables("Sample.pdf")

for table in tables[:20]:

    df = clean_dataframe(
        table["dataframe"]
    )

    h = detect_header_rows(df)

    d = detect_data_start(df)

    print(
        f"TABLE {table['table_id']} "
        f"HEADER={h} "
        f"DATA={d}"
    )