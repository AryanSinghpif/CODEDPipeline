"""
Translate legacy Kruti Dev / Chanakya font-encoded Hindi text
(which Camelot extracts as ASCII soup like "ftyk", "';ksiqj")
into English.

The mapping was learned by pairing the Hindi district column with
the English "District" column across the source PDF, plus common
header / summary terms added manually.
"""

import re

# legacy-encoded Hindi -> English
LEGACY_MAP = {
    # header / common terms
    "ftyk": "District",
    "ftys": "District",
    "o\"kz": "Year",
    ";ksx": "Total",
    "dqy": "Total",
    "Ø- l-": "S.No",
    "Ø-l-": "S.No",
    "dz- l-": "S.No",
    # state
    "e/;izns'k": "Madhya Pradesh",
    # districts (Madhya Pradesh)
    "';ksiqj": "Sheopur",
    "eqjSuk": "Morena",
    "fHk.M": "Bhind",
    "Xokfy;j": "Gwalior",
    "nfr;k": "Datia",
    "f'koiqjh": "Shivpuri",
    "xquk": "Guna",
    "x quk": "Guna",
    "x uk q": "Guna",
    "x q uk": "Guna",
    "v'kksduxj": "Ashok Nagar",
    "Vhdex<+": "Tikamgarh",
    "Nrjiqj": "Chhatarpur",
    "fuokMh": "Nivari",
    "fuokM+h": "Nivari",
    "iUuk": "Panna",
    "lkxj": "Sagar",
    "Lkkxj": "Sagar",
    "neksg": "Damoh",
    "lruk": "Satna",
    "jhok": "Rewa",
    "mefj;k": "Umaria",
    "'kgMksy": "Shahadol",
    "vuqiiqj": "Anuppur",
    "lh/kh": "Sidhi",
    "flaxjkSyh": "Singrauli",
    "uhep": "Neemuch",
    "eanlkSj": "Mandsaur",
    "jryke": "Ratlam",
    "mTtSu": "Ujjain",
    "'kktkiqj": "Shajapur",
    "vkxj ekyok": "Agar Malwa",
    "nsokl": "Dewas",
    ">kcqvk": "Jhabua",
    "vyhjktiqj": "Alirajpur",
    "/kkj": "Dhar",
    "bUnkSj": "Indore",
    "cM+okuh": "Badwani",
    "[k.Mok": "Khandwa",
    "cqjgkuiqj": "Burhanpur",
    "[kjxkSu": "Khargaone",
    "jktx<+": "Rajgarh",
    "fofn'kk": "Vidisha",
    "Hkksiky": "Bhopal",
    "jk;lsu": "Raisen",
    "lhgksj": "Sehore",
    "cSrwy": "Betul",
    "gjnk": "Harda",
    "ueZnkiqje": "Narmadapuram",
    "dVuh": "Katni",
    "tcyiqj": "Jabalpur",
    "ujflagiqj": "Narsinghpur",
    "e.Myk": "Mandla",
    "fMaMksjh": "Dindori",
    "fNUnokM+k": "Chhindwara",
    "flouh": "Seoni",
    "ckyk?kkV": "Balaghat",
}

_QUOTE_FIXES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def _normalize(text):
    text = str(text).translate(_QUOTE_FIXES)
    return re.sub(r"\s+", " ", text).strip()


# case-insensitive, whitespace-insensitive secondary index
_LOOSE_MAP = {
    re.sub(r"\s+", "", k).lower(): v for k, v in LEGACY_MAP.items()
}


def translate_text(text):
    """Return English translation if known, else the original text."""
    norm = _normalize(text)
    if not norm:
        return text
    if norm in LEGACY_MAP:
        return LEGACY_MAP[norm]
    loose = re.sub(r"\s+", "", norm).lower()
    if loose in _LOOSE_MAP:
        return _LOOSE_MAP[loose]
    return text


def translate_dataframe(df):
    """Translate legacy-Hindi cells in all text columns; unknown text is kept as-is."""
    # iterate positionally — df[col] breaks on duplicate column names
    for i in range(df.shape[1]):
        if df.iloc[:, i].dtype == object:
            df.iloc[:, i] = df.iloc[:, i].map(translate_text)
    return df
