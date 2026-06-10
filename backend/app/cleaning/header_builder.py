import re
import pandas as pd
from backend.app.cleaning.data_start_detector import detect_data_start

DISTRICT_NAMES = {
    "sheopur",
    "morena",
    "bhind",
    "gwalior",
    "datia",
    "shivpuri",
    "guna",
    "ashok nagar",
    "tikamgarh",
    "chhatarpur",
    "panna",
    "sagar",
    "damoh",
    "satna",
    "rewa",
    "sidhi",
    "singrauli",
    "shahdol",
    "anuppur",
    "umaria",
    "katni",
    "jabalpur",
    "narsinghpur",
    "indore",
    "badwani",
    "khargone",
    "rajgarh",
    "vidisha",
    "bhopal",
    "raisen",
    "sehore",
    "betul",
    "harda",
    "burhanpur",
    "khandwa",
    "dewas",
    "ujjain",
    "mandsaur",
    "neemuch",
    "ratlam"
}


def is_year(text):

    text = str(text)

    return bool(
        re.search(
            r"\d{4}[-–]\d{2}",
            text
        )
    )


VOWELS = set("aeiou")


def _has_vowel(word):
    return any(c in VOWELS for c in word.lower())


#
# Lowercase words allowed in headers. Legacy Kruti Dev
# soup ("tula", "gtkj", "dh") is lowercase or has internal
# capitals ("gSaMiaiksa"), while real English header text
# in these PDFs is Titlecase ("Number of Installed Hand
# Pumps"). So a word is kept only if it is Titlecase,
# ALL-CAPS, or a known lowercase English word.
#

ALLOWED_LOWER = {
    "of", "per", "and", "the", "in", "on", "for", "to",
    "no", "by", "at",
}


def _looks_english(word):

    bare = re.sub(r"[^A-Za-z]", "", word)

    if not bare or not _has_vowel(bare):
        return False

    if bare.lower() in ALLOWED_LOWER:
        return True

    if len(bare) < 3:
        return False

    # Titlecase: Number, Telephone
    if bare[0].isupper() and bare[1:].islower():
        return True

    # ALL CAPS: DISTRICT
    if bare.isupper():
        return True

    # mixed internal caps (gSaMiaiksa) or lowercase soup (tula)
    return False


def extract_english(text):

    text = str(text)

    matches = re.findall(
        r"[A-Za-z][A-Za-z\s&().,\-/]{2,}",
        text
    )

    filtered = []
    for chunk in matches:
        words = [
            w for w in chunk.split()
            if _looks_english(w)
        ]
        if words:
            filtered.append(" ".join(words))

    return " ".join(filtered).strip()


def clean_header(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    text = re.sub(
        r"_+",
        "_",
        text
    )

    return text.strip("_")


def apply_headers(df, header_rows):

    #
    # Find actual start of data
    #

    data_start = detect_data_start(df)

    print(
        f"\nHEADER={header_rows} DATA={data_start}"
    )

    #
    # Trust data detector only when
    # it finds data BEFORE header detector
    #

    if (
        data_start > 0
        and data_start < header_rows
    ):
        header_rows = data_start

    header_df = df.iloc[:header_rows].copy()

    #
    # Merged (spanning) header cells: camelot puts the
    # group label only in the FIRST cell of the span and
    # leaves the rest empty. Forward-fill each header row
    # horizontally so every sub-column (e.g. each year)
    # inherits its parent group label.
    #
    # Skip rows that are table titles (only one non-empty
    # cell), otherwise the title would leak into every column.
    #

    #
    # Never fill the LAST header row (the sub-header row,
    # e.g. years) — its cells are per-column, not spans,
    # and filling would leak values into unrelated columns.
    #

    for i in range(max(len(header_df) - 1, 0)):

        row = header_df.iloc[i].astype(str).str.strip()

        non_empty = (row != "").sum()

        if non_empty < 2:
            continue

        filled = (
            header_df.iloc[i]
            .replace("", None)
            .ffill()
        )

        header_df.iloc[i] = filled.fillna("")

    data_df = (
        df.iloc[header_rows:]
        .reset_index(drop=True)
    )

    columns = []

    for col in range(df.shape[1]):

        parts = []

        for value in header_df.iloc[:, col]:

            value = str(value).strip()

            if not value:
                continue

            english_text = extract_english(value)

            if english_text:

                #
                # Ignore district names
                #

                if (
                    english_text.lower()
                    in DISTRICT_NAMES
                ):
                    continue

                parts.append(
                    english_text
                )

            elif is_year(value):

                parts.append(
                    value
                )

        if parts:

            header = clean_header(
                "_".join(parts)
            )

        else:

            header = f"col_{col}"

        columns.append(header)

    data_df.columns = columns
    #
# First column should be serial number,
# not table title
#

    if len(data_df.columns) > 0:

        first_col = data_df.columns[0]

    first_values = (
        data_df.iloc[:, 0]
        .astype(str)
        .head(10)
        .tolist()
    )

    numeric_count = sum(
        v.strip().isdigit()
        for v in first_values
    )

    if numeric_count >= 5:

        cols = list(
            data_df.columns
        )

        cols[0] = "s_no"

        data_df.columns = cols
    #
    # Replace Hindi district column
    # with English district column
    #

    district_cols = []

    for i, col in enumerate(data_df.columns):

        if "district" in str(col).lower():

            district_cols.append(i)

    if len(district_cols) >= 2:

        english_col = district_cols[-1]

        data_df.iloc[:, 1] = (
            data_df.iloc[:, english_col]
        )

        data_df = data_df.drop(
            columns=[
                data_df.columns[
                    english_col
                ]
            ]
        )

        cols = list(
            data_df.columns
        )

        cols[1] = "district"

        data_df.columns = cols

    print(
        "\nHEADER BUILDER RUNNING"
    )

    print(
        data_df.columns.tolist()
    )

    return data_df