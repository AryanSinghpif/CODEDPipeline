import re


def looks_like_data_row(row):

    values = [
        str(x).strip()
        for x in row.tolist()
    ]

    non_empty = [v for v in values if v]

    if len(non_empty) < 3:
        return False

    numeric_count = 0

    for v in non_empty:

        v = v.replace(",", "")

        try:
            float(v)
            numeric_count += 1
        except (TypeError, ValueError):
            pass

    #
    # Classic layout: serial number first, then numbers
    #

    if re.match(r"^\d+$", values[0]) and numeric_count >= 3:
        return True

    #
    # Label-first layout (DARPG matrices: "Department of X" then
    # 20 numbers) — mostly-numeric row is data even without a serial
    #

    return (
        numeric_count >= 3
        and numeric_count / len(non_empty) >= 0.6
    )


def detect_data_start(df):
    """Index of the first data-like row, or None if none found.

    0 is a meaningful answer (continuation pages print data from the
    very first row, with no header at all)."""

    for i, row in df.iterrows():

        if looks_like_data_row(row):

            return i

    return None
