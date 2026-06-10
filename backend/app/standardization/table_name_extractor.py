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


VOWELS = set("aeiou")

ALLOWED_LOWER = {
    "of", "per", "and", "the", "in", "on", "for", "to", "no", "by", "at",
}


def _looks_english(word):

    bare = re.sub(r"[^A-Za-z]", "", word)

    if not bare or not any(c in VOWELS for c in bare.lower()):
        return False

    if bare.lower() in ALLOWED_LOWER:
        return True

    if len(bare) < 3:
        return False

    return (
        (bare[0].isupper() and bare[1:].islower())
        or bare.isupper()
    )


def extract_pdf_title(df, header_rows):
    """
    Extract the real table title printed in the PDF,
    e.g. "Table 11.2 Number of Installed Hand Pumps".
    Returns None if no title pattern is found.
    """

    header_df = df.iloc[:header_rows]

    for value in header_df.astype(str).values.flatten():

        m = re.search(
            r"Tab[a-z]*\.?\s*(\d+[.\-]\d+)\s+(.+)",
            value,
        )

        if not m:
            continue

        number = m.group(1).replace("-", ".")

        words = [
            w for w in m.group(2).split()
            if _looks_english(w)
        ]

        if words:
            return f"Table {number} " + " ".join(words)

        return f"Table {number}"

    return None


def extract_table_name(df, header_rows):

    #
    # Prefer the actual title printed in the PDF
    #

    title = extract_pdf_title(df, header_rows)

    if title:
        return title

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