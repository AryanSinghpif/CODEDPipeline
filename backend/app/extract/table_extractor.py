import re

import camelot

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def _is_crushed(df):
    """
    Lattice on tables without horizontal row separators merges many
    rows into one cell. Detect: a meaningful share of cells holding
    multi-line content.
    """

    if df.empty:
        return True

    cells = df.astype(str).values.flatten()

    if len(cells) == 0:
        return True

    multiline = sum(1 for c in cells if c.count("\n") >= 2)

    return multiline / len(cells) > 0.25


NUMERIC_FRAGMENT = re.compile(r"^-?[\d,]+(\.\d+)?%?$")


def _repair_crushed_header_rows(df):
    """
    Camelot sometimes crams an entire header row into one cell
    ("S. No.\nName of Ministry\nReceipts\n...") leaving the other
    cells empty — the row had no vertical separators. Split the
    fragments and distribute them across the columns so headers
    survive cleaning.
    """

    ncols = df.shape[1]

    for i in range(min(8, len(df))):

        row = [str(v).strip() for v in df.iloc[i].tolist()]
        non_empty = [(j, v) for j, v in enumerate(row) if v]

        if len(non_empty) != 1:
            continue

        col, value = non_empty[0]
        fragments = [f.strip() for f in value.split("\n") if f.strip()]

        if len(fragments) < 3:
            continue

        # headers are text; a crushed DATA column is mostly numbers
        numeric = sum(1 for f in fragments if NUMERIC_FRAGMENT.match(f))

        if numeric / len(fragments) > 0.3:
            continue

        slots = ncols - col

        if slots < 2:
            continue

        placed = fragments[:slots - 1]
        placed.append(" ".join(fragments[slots - 1:]))

        for k, frag in enumerate(placed):
            df.iat[i, col + k] = frag

    return df


def _extract_caption(plumber_pdf, page_num, bbox):
    """
    Grab the text lines printed just above the table on the page —
    usually the table title/caption.
    """

    if plumber_pdf is None or bbox is None:
        return None

    try:
        page = plumber_pdf.pages[page_num - 1]

        # camelot bbox is (x1, y1, x2, y2) in PDF coords (y from bottom);
        # pdfplumber uses top-down coords.
        table_top = page.height - max(bbox[1], bbox[3])

        if table_top <= 0:
            return None

        region = page.crop((0, max(0, table_top - 90), page.width, table_top))
        text = region.extract_text() or ""

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        if not lines:
            return None

        # caption is the line(s) closest to the table
        return " ".join(lines[-2:])[:300]

    except Exception:
        return None


def _read(pdf_path, pages, flavor):

    try:
        return camelot.read_pdf(pdf_path, pages=pages, flavor=flavor)
    except Exception:
        return []


def _read_resilient(pdf_path, page_list, flavor):
    """
    camelot raises (e.g. "max() arg is an empty sequence") on blank or
    vector-only pages, aborting the whole multi-page call. Try the chunk
    first; on failure fall back to page-by-page so one bad page cannot
    sink its 39 neighbours.
    """

    try:
        return list(
            camelot.read_pdf(
                pdf_path, pages=",".join(page_list), flavor=flavor
            )
        )
    except Exception:
        pass

    tables = []

    for p in page_list:
        try:
            tables.extend(
                camelot.read_pdf(pdf_path, pages=p, flavor=flavor)
            )
        except Exception:
            continue

    return tables


def extract_tables(pdf_path):

    plumber_pdf = None

    if pdfplumber is not None:
        try:
            plumber_pdf = pdfplumber.open(pdf_path)
        except Exception:
            plumber_pdf = None

    total_pages = None

    if plumber_pdf is not None:
        total_pages = len(plumber_pdf.pages)

    kept = []
    good_lattice_pages = set()

    for table in _read(pdf_path, "all", "lattice"):

        try:
            page = int(table.page)
            df = table.df
        except Exception:
            continue

        if _is_crushed(df):
            continue

        good_lattice_pages.add(page)
        kept.append({
            "page": page,
            "dataframe": _repair_crushed_header_rows(df),
            "bbox": getattr(table, "_bbox", None),
            "flavor": "lattice",
        })

    # Stream fallback: pages where lattice found nothing usable
    # (borderless tables, or tables without row separator lines).
    if total_pages is not None:

        missing = [
            str(p)
            for p in range(1, total_pages + 1)
            if p not in good_lattice_pages
        ]

        for chunk_start in range(0, len(missing), 40):

            chunk_pages = missing[chunk_start:chunk_start + 40]

            for table in _read_resilient(pdf_path, chunk_pages, "stream"):

                try:
                    page = int(table.page)
                    df = table.df

                    report = table.parsing_report
                    accuracy = report.get("accuracy", 0)
                    whitespace = report.get("whitespace", 100)
                except Exception:
                    continue

                # stream "finds" pseudo-tables on prose pages;
                # keep only confident, dense ones
                if accuracy < 80 or whitespace > 60:
                    continue

                if len(df) < 4 or len(df.columns) < 3:
                    continue

                kept.append({
                    "page": page,
                    "dataframe": df,
                    "bbox": getattr(table, "_bbox", None),
                    "flavor": "stream",
                })

    kept.sort(key=lambda t: t["page"])

    results = []

    for i, t in enumerate(kept):

        results.append({
            "table_id": i + 1,
            "page": t["page"],
            "dataframe": t["dataframe"],
            "caption": _extract_caption(plumber_pdf, t["page"], t["bbox"]),
            "flavor": t["flavor"],
        })

    if plumber_pdf is not None:
        try:
            plumber_pdf.close()
        except Exception:
            pass

    return results
