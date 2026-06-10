import re


MERGED_RUN = re.compile(
    r"^(-?[\d,]+(\.\d+)?%?\s+){3,}-?[\d,]+(\.\d+)?%?$"
)


def validate_table(df):

    rows = len(df)
    cols = len(df.columns)

    if rows < 5:

        return {
            "passed": False,
            "reason": "too_few_rows"
        }

    if cols < 3:

        return {
            "passed": False,
            "reason": "too_few_columns"
        }

    cells = df.astype(str).values.flatten()
    total = len(cells)

    empty = sum(
        1 for c in cells
        if c.strip() in ("", "nan", "None")
    )

    # phantom tables (charts parsed as tables) are mostly blank
    if total and empty / total > 0.6:

        return {
            "passed": False,
            "reason": "mostly_empty"
        }

    # crushed extraction: cells holding runs of values from many rows
    merged = sum(
        1 for c in cells
        if MERGED_RUN.match(c.strip())
    )

    if total and merged / total > 0.15:

        return {
            "passed": False,
            "reason": "merged_rows"
        }

    col_headers = sum(
        str(c).startswith("col")
        for c in df.columns
    )

    if cols and col_headers / cols > 0.7:

        return {
            "passed": False,
            "reason": "weak_headers"
        }

    return {
        "passed": True,
        "reason": "ok"
    }
