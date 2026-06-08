import os
import pandas as pd


CSV = "backend/data/exports/csv"

total = 0
good = 0
warnings = []


for file in sorted(os.listdir(CSV)):

    path = f"{CSV}/{file}"

    try:

        df = pd.read_csv(path)

        total += 1

        cols = len(df.columns)

        rows = len(df)

        unknown = sum(
            str(c).startswith("col_")
            for c in df.columns
        )

        score = 100

        if unknown:

            score -= (
                unknown
                / cols
            ) * 50

        if rows < 5:

            score -= 30

        if score >= 60:

            good += 1

        else:

            warnings.append(
                (
                    file,
                    rows,
                    cols,
                    round(score)
                )
            )

    except Exception:

        warnings.append(
            (
                file,
                "ERROR"
            )
        )

print()
print("TOTAL:", total)
print("GOOD:", good)
print("WARNING:", len(warnings))

print()

for x in warnings[:20]:

    print(x)