import re


TITLE_PATTERN = re.compile(
    r"(Table|Statement|Annexure|Appendix)"
    r"[\s\-:.]*"
    r"(\d+([.\-]\d+)*)"
    r"[\s\-:.]*"
    r"(.*)",
    re.IGNORECASE,
)

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
        or bare.islower()
    )


def _clean_title_words(text, limit=10):

    words = [w for w in text.split() if _looks_english(w)]

    return " ".join(words[:limit])


def _match_title(text):

    m = TITLE_PATTERN.search(text)

    if not m:
        return None

    label = m.group(1).title()
    number = m.group(2).replace("-", ".")
    rest = _clean_title_words(m.group(4))

    name = f"{label} {number}"

    if rest:
        name += " " + rest

    return name


def extract_table_name(df, header_rows, caption=None):

    # 1) explicit "Table X.Y ..." pattern — caption first, then header cells
    if caption:

        title = _match_title(caption)

        if title:
            return title

    header_df = df.iloc[:header_rows]

    for value in header_df.astype(str).values.flatten():

        title = _match_title(value)

        if title:
            return title

    # 2) caption text — but only if it reads like a TITLE, not prose:
    #    a short line (2–10 words) without sentence punctuation.
    if caption:

        for line in str(caption).splitlines():

            line = line.strip()
            cleaned = _clean_title_words(line, limit=12)
            n_words = len(cleaned.split())

            if (
                2 <= n_words <= 10
                and not re.search(r"[.;:]\s|\.$", line)
                and len(cleaned) >= 0.6 * len(line)
            ):
                return cleaned

    # 3) no confident title — caller assigns a sequential "Table N"
    return None
