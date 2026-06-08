import os
import pandas as pd

CSV_DIR = "backend/data/exports/csv"

files = [
    f for f in os.listdir(CSV_DIR)
    if f.endswith(".csv")
]

print()
print("TOTAL CSV FILES:", len(files))
print()

for f in files[:10]:

    path = os.path.join(
        CSV_DIR,
        f
    )

    df = pd.read_csv(path)

    print(
        f,
        "| rows =", len(df),
        "| cols =", len(df.columns)
    )