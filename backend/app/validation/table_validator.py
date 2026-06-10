import re


MERGED_RUN = re.compile(
    r"^(-?[\d,]+(\.\d+)?%?\s+){3,}-?[\d,]+(\.\d+)?%?$"
)


def validate_table(df):

    rows = len(df)
    cols = len(df.columns)

    #
    # Keep every real table, even tiny or headingless ones.
    # Reject only degenerate shapes that cannot be a table.
    #

    if rows < 2:

        return {
            "passed": False,
            "reason": "too_few_rows"
        }

    if cols < 2:

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

    # phantom tables (charts parsed as tables) are almost entirely blank
    if total and empty / total > 0.85:

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

    #
    # Headingless tables are kept (named "Table N" downstream);
    # weak headers alone are not grounds for rejection.
    #

    return {
        "passed": True,
        "reason": "ok"
    }
