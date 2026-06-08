import re


def detect_header_rows(df):

    if df.empty:
        return 1

    max_scan = min(
        8,
        len(df)
    )

    for i in range(max_scan):

        row = (
            df.iloc[i]
            .astype(str)
            .tolist()
        )

        text = " ".join(row)

        if re.search(
            r"2020[-–]21|2021[-–]22|2022[-–]23",
            text
        ):
            return i + 1

        if re.search(
            r"¿\d+À",
            text
        ):
            return i + 1

    return min(
        4,
        len(df)
    )