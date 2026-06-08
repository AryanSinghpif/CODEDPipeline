import re


COLUMN_ALIASES = {
    "district": "district",
    "population": "population",
    "literacy": "literacy",
    "cropping": "cropping_intensity",
    "forest": "forest_area",
    "school": "school_count"
}


def normalize_column(col):

    col = str(col).lower().strip()

    col = re.sub(
        r"[^a-z0-9]+",
        "_",
        col
    )

    col = re.sub(
        r"_+",
        "_",
        col
    )

    return col.strip("_")


def standardize_columns(df):

    return df