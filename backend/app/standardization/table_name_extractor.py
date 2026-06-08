import re


KEEP_WORDS = {
    "area",
    "population",
    "density",
    "growth",
    "rate",
    "male",
    "males",
    "female",
    "females",
    "rural",
    "urban",
    "scheduled",
    "caste",
    "tribe",
    "literacy",
    "education",
    "agriculture",
    "forest",
    "irrigation",
    "irrigated",
    "gross",
    "net",
    "cropping",
    "intensity",
    "production",
    "banking",
    "credit",
    "loan",
    "worker",
    "workers",
    "cultivator",
    "labourers",
    "household",
    "school",
    "schools",
    "students",
    "teachers",
    "institution",
    "institutions"
}


def extract_table_name(df, header_rows):

    header_df = df.iloc[:header_rows]

    text = " ".join(
        header_df.astype(str)
        .fillna("")
        .values
        .flatten()
    )

    words = re.findall(
        r"[A-Za-z]+",
        text.lower()
    )

    words = [
        word
        for word in words
        if word in KEEP_WORDS
    ]

    if not words:
        return "table"

    words = list(
        dict.fromkeys(words)
    )

    return " ".join(words[:8])