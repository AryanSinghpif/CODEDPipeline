import re


def looks_like_data_row(row):

    values = [
        str(x).strip()
        for x in row.tolist()
    ]

    if not values:
        return False

    #
    # First column should be serial number
    #

    if not re.match(
        r"^\d+$",
        values[0]
    ):
        return False

    numeric_count = 0

    for v in values:

        v = v.replace(",", "")

        try:
            float(v)
            numeric_count += 1
        except:
            pass

    return numeric_count >= 3


def detect_data_start(df):

    for i, row in df.iterrows():

        if looks_like_data_row(row):

            return i

    return 0