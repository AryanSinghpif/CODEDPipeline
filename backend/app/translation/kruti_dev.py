"""
Kruti Dev / DevLys (legacy 8-bit Devanagari font) -> Unicode converter.

Government PDFs typeset in Kruti Dev extract as ASCII soup ("ftyk"
for जिला). The font's glyph-to-character mapping is well known; this
module applies it: ordered multi-character rules first, then single
glyphs, then the positional fixes Devanagari needs (the pre-base
short-i matra and the reph).
"""

import re

# multi-character glyphs first (order matters)
_MULTI = [
    ("vkS", "औ"), ("vks", "ओ"), ("vk", "आ"), ("bZ", "ई"),
    ("{k", "क्ष"), ("K", "ज्ञ"), ("J", "श्र"),
    ("?k", "घ"), ("[k", "ख"), ("'k", "श"), ("’k", "श"),
    ('"k', "ष"), ("Fk", "थ"), ("Hk", "भ"), (".k", "ण"),
    ("/k", "ध"), ("Fk", "थ"),
    ("M+", "ड़"), ("<+", "ढ़"), ("t+", "ज़"), ("d+", "क़"),
    ("Q+", "फ़"), ("x+", "ग़"),
    ("ksa", "ों"), ("kSa", "ौं"), ("ks", "ो"), ("kS", "ौ"),
]

_SINGLE = {
    # independent vowels
    "v": "अ", "b": "इ", "m": "उ", "Å": "ऊ", ",": "ए",
    # consonants
    "d": "क", "x": "ग", "p": "च", "N": "छ", "t": "ज", ">": "झ",
    "V": "ट", "B": "ठ", "M": "ड", "<": "ढ",
    "r": "त", "n": "द", "/": "ध्", "[": "ख्", "u": "न",
    "i": "प", "Q": "फ", "c": "ब", "e": "म",
    ";": "य", "j": "र", "y": "ल", "o": "व",
    "l": "स", "g": "ह", ".": "ण्",
    # half forms
    "U": "न्", "R": "त्", "T": "ज्", "X": "ग्", "L": "स्",
    "D": "क्", "P": "च्", "C": "ब्", "O": "व्", "H": "भ्",
    "F": "थ्", "E": "म्", "Y": "ल्", "W": "व्",
    # matras / signs
    "k": "ा", "h": "ी", "q": "ु", "w": "ू", "s": "े", "S": "ै",
    "a": "ं", "¡": "ँ", "`": "ृ", "~": "्", "z": "्र",
    "f": "ि",
    # punctuation
    "&": "-", "A": "।", "]": ",", "_": ";", "=": "त्र", "|": "द्य", "Ø": "क्र", "{": "क्ष्", "º": "ह्", "¼": "(", "½": ")",
}

_DEV = "क-ह"


def kruti_to_unicode(text):
    """Convert a Kruti Dev-encoded string to Unicode Devanagari."""

    out = str(text)

    for glyph, dev in _MULTI:
        out = out.replace(glyph, dev)

    out = "".join(_SINGLE.get(ch, ch) for ch in out)

    # pre-base short-i: 'f' was emitted before its consonant cluster —
    # move the matra after the cluster it belongs to
    out = re.sub(
        rf"ि([{_DEV}]़?(?:्[{_DEV}]़?)*)",
        r"\1ि",
        out,
    )

    # reph: 'Z' marks र् belonging BEFORE the syllable it follows
    out = re.sub(
        rf"([{_DEV}]़?[ािीुूृेैोौंँ]*)Z",
        r"र्\1",
        out,
    )

    return out


# telltales that a token is Kruti Dev soup rather than English
_MARKERS = (
    "ks", "iq", "qj", "Uk", "[k", ".k", "kS", "Fk", "Hk", "?k",
    '"k', "'k", "M+", "<+", "~", "ftk", "yk", "uk", "ok", "dh",
    "kj", "fj", "Tt", "esa", "dz", "{k",
)

_ENGLISH_OK = {
    "of", "per", "and", "the", "in", "on", "for", "to", "no", "by",
    "at", "total", "male", "female", "males", "females", "persons",
    "years", "year", "rate", "all", "india", "district", "number",
}


def looks_kruti(token):
    """Heuristic: is this ASCII token legacy-font soup?"""

    bare = re.sub(r"[^A-Za-z]", "", str(token))

    if len(bare) < 3:
        return False

    if bare.lower() in _ENGLISH_OK:
        return False

    # real English in these PDFs is Titlecase or ALL CAPS
    if bare[0].isupper() and bare[1:].islower():
        return False
    if bare.isupper():
        return False

    # hard glyph markers that never appear in real English words
    if any(ch in str(token) for ch in "[]~<>{}|"):
        return True

    has_vowel = any(c in "aeiouAEIOU" for c in bare)

    if not has_vowel:
        return True

    # internal capitals (eqjSuk, bUnkSj) or known soup digraphs
    if any(c.isupper() for c in bare[1:]):
        return True

    return any(m in token for m in _MARKERS)
