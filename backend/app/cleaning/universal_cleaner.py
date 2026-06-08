import re
import ftfy
import pandas as pd


BAD_PATTERNS = [
    r"^nan$",
    r"^unnamed",
    r"^none$",
]


def remove_empty(df):

    return (
        df
        .dropna(how="all")
        .dropna(axis=1, how="all")
    )


def normalize(df):

    def clean_cell(x):

        if pd.isnull(x):
            return ""

        text = str(x)

        text = ftfy.fix_text(text)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    return df.map(clean_cell)


def is_garbage_row(row):

    text = " ".join(
        map(
            str,
            row.tolist()
        )
    ).lower()

    if re.fullmatch(
        r"(¿\d+à[\s,]*)+",
        text
    ):
        return True

    for pattern in BAD_PATTERNS:

        if re.search(
            pattern,
            text
        ):
            return True

    return False


def remove_garbage(df):

    rows = []

    for _, row in df.iterrows():

        if not is_garbage_row(row):

            rows.append(
                row.tolist()
            )

    if not rows:

        return pd.DataFrame(
            columns=df.columns
        )

    return pd.DataFrame(
        rows,
        columns=df.columns
    )


def clean_dataframe(df):

    df = remove_empty(df)

    df = normalize(df)

    df = remove_garbage(df)

    df = (
        df
        .drop_duplicates()
        .reset_index(
            drop=True
        )
    )

    return df