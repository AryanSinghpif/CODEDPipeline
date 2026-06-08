import pandas as pd


def standardize(df):

    cols = list(df.columns)

    #
    # First column usually S.No
    #

    if len(cols) > 0:
        cols[0] = "s_no"

    #
    # Move district next to s_no
    #

    if "district" in cols:

        cols.remove("district")

        cols.insert(1, "district")

        df = df[cols]

    df.columns = cols

    return df