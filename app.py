import io
import os
import sys
import tempfile
import warnings
import zipfile
from contextlib import redirect_stdout

import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="CODEDPipeline",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1100px; }
    .stMetric { background: #f7f8fa; border-radius: 8px; padding: 12px 16px; }
    div[data-testid="stDownloadButton"] button { width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown("## ⬡ CODEDPipeline")
st.caption("Extract statistical tables from government PDF reports — clean CSVs, ready to use.")
st.divider()

uploaded = st.file_uploader(
    "Upload a PDF",
    type=["pdf"],
    help="Works best with DES district statistical reports (bordered/lattice tables)",
)

if uploaded is None:
    st.info("Upload a PDF above to start. The pipeline uses Camelot lattice extraction — bordered tables only.")
    st.stop()

with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp.write(uploaded.getvalue())
    pdf_path = tmp.name

try:
    with st.spinner("Parsing PDF and detecting tables…"):
        from backend.app.extract.table_extractor import extract_tables
        tables = extract_tables(pdf_path)

    if not tables:
        st.error("No tables found. PDF must have bordered (lattice) tables — scanned/image PDFs are not supported.")
        st.stop()

    from backend.app.cleaning.header_builder import apply_headers
    from backend.app.cleaning.header_detector import detect_header_rows
    from backend.app.cleaning.header_postprocessor import clean_headers
    from backend.app.cleaning.universal_cleaner import clean_dataframe
    from backend.app.standardization.metadata_builder import build_metadata
    from backend.app.standardization.table_name_extractor import extract_table_name
    from backend.app.validation.table_validator import validate_table

    prog = st.progress(0, text=f"Found {len(tables)} tables — running pipeline…")

    catalog, failed, table_dfs = [], [], {}

    for i, table in enumerate(tables):
        prog.progress(
            (i + 1) / len(tables),
            text=f"Table {table['table_id']} / {len(tables)}  (page {table['page']})",
        )
        try:
            with redirect_stdout(io.StringIO()):
                df = clean_dataframe(table["dataframe"])
                h = detect_header_rows(df)
                name = extract_table_name(df, h)
                df = apply_headers(df, h)
                df = clean_headers(df)

            status = validate_table(df)
            if status["passed"]:
                catalog.append(build_metadata(table["table_id"], name, table["page"], df))
                table_dfs[table["table_id"]] = df
            else:
                failed.append({"table": table["table_id"], "page": table["page"], "reason": status["reason"]})
        except Exception as e:
            failed.append({"table": table["table_id"], "page": table["page"], "reason": str(e)})

    prog.empty()

    # ── Stats ──────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Total tables", len(tables))
    c2.metric("Extracted", len(catalog))
    c3.metric("Failed", len(failed))
    st.divider()

    if not catalog:
        st.warning("All tables failed validation.")
        st.stop()

    # ── Build ZIP ──────────────────────────────────────────────
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for tid, df in table_dfs.items():
            zf.writestr(f"table_{tid}.csv", df.to_csv(index=False))
        zf.writestr("table_catalog.csv", pd.DataFrame(catalog).to_csv(index=False))
    zip_buf.seek(0)

    # ── Catalog ────────────────────────────────────────────────
    hdr, dl_col = st.columns([4, 1])
    hdr.markdown("### Extracted Tables")
    dl_col.download_button(
        "⬇ Download All (ZIP)",
        zip_buf,
        file_name=f"{uploaded.name.replace('.pdf', '')}_tables.zip",
        mime="application/zip",
        use_container_width=True,
    )

    catalog_df = pd.DataFrame(catalog)

    search = st.text_input("Filter", placeholder="Search by table name or ID…", label_visibility="collapsed")
    if search:
        mask = (
            catalog_df["table_name"].str.contains(search, case=False, na=False)
            | catalog_df["table_id"].astype(str).str.contains(search)
        )
        catalog_df = catalog_df[mask]

    st.dataframe(
        catalog_df[["table_id", "table_name", "page", "rows", "columns"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "table_id":   st.column_config.NumberColumn("#",         width=60),
            "table_name": st.column_config.TextColumn("Name",        width="large"),
            "page":       st.column_config.NumberColumn("Page",      width=70),
            "rows":       st.column_config.NumberColumn("Rows",      width=70),
            "columns":    st.column_config.NumberColumn("Cols",      width=70),
        },
    )

    # ── Preview ────────────────────────────────────────────────
    st.divider()
    st.markdown("### Preview / Download")

    options = {
        f"Table {r.table_id}  ·  {r.table_name}  (p. {r.page})": r.table_id
        for r in pd.DataFrame(catalog).itertuples()
    }
    selected = st.selectbox("Select a table", list(options.keys()), label_visibility="collapsed")

    if selected:
        tid = options[selected]
        df_preview = table_dfs[tid]
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        st.download_button(
            f"⬇ table_{tid}.csv",
            df_preview.to_csv(index=False),
            file_name=f"table_{tid}.csv",
            mime="text/csv",
        )

    # ── Failed ─────────────────────────────────────────────────
    if failed:
        with st.expander(f"⚠ {len(failed)} tables failed validation", expanded=False):
            st.dataframe(pd.DataFrame(failed), use_container_width=True, hide_index=True)

finally:
    os.unlink(pdf_path)
