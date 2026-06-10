"""
Stitch multi-page continuation tables back together.

Long report tables (PLFS state matrices, DARPG GRAI grids) are printed
across consecutive pages, repeating the same title and/or the same
header row on every page. Camelot returns one table per page; this
module merges those fragments into one continuous table.
"""

import pandas as pd


def _named_frac(cols):

    cols = [str(c) for c in cols]

    return sum(not c.startswith("col_") for c in cols) / max(len(cols), 1)


def _continues(prev, cur):
    """cur is a continuation of prev if it is on the next page with the
    same shape, and shares either the extracted title or the header row."""

    if cur["page"] - prev["pages"][-1] != 1:
        return False

    a, b = prev["df"], cur["df"]

    if a.shape[1] != b.shape[1]:
        return False

    # same explicit title repeated on the next page
    if prev["name"] and cur["name"] and prev["name"] == cur["name"]:
        return True

    # identical, meaningfully-named header row repeated on the next page —
    # but only for substantial tables: small KPI strips often share a
    # generic year header (2022 / 2023 / Total) while being unrelated.
    cols_a = [str(c) for c in a.columns]
    cols_b = [str(c) for c in b.columns]

    if (
        cols_a == cols_b
        and _named_frac(cols_a) >= 0.5
        and len(a) >= 6
        and len(b) >= 2
    ):
        return True

    return False


def stitch_tables(items):
    """
    items: list of dicts with keys table_id, name, page, df —
    in page order. Returns the same structure with continuation
    fragments concatenated; each item gains a "pages" list.
    """

    out = []

    for it in items:

        it = dict(it)
        it.setdefault("pages", [it["page"]])

        if out and _continues(out[-1], it):

            prev = out[-1]
            prev["df"] = pd.concat(
                [prev["df"], it["df"]], ignore_index=True
            )
            prev["pages"].append(it["page"])

            if not prev["name"] and it["name"]:
                prev["name"] = it["name"]

        else:
            out.append(it)

    return out
