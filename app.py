import io
import os
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

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Main container */
.block-container {
    padding: 3rem 4rem 5rem !important;
    max-width: 1080px !important;
}

/* ── Hero ── */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 14px;
    background: rgba(79, 126, 247, 0.10);
    border: 1px solid rgba(79, 126, 247, 0.25);
    border-radius: 100px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #4f7ef7;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -2px;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #999 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 14px;
}

.hero-sub {
    font-size: 15px;
    color: #777;
    line-height: 1.65;
    max-width: 480px;
    margin-bottom: 28px;
}

/* ── Pipeline steps ── */
.pipeline {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 40px;
}

.p-step {
    padding: 5px 13px;
    background: #111;
    border: 1px solid #1f1f1f;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #888;
}

.p-step.active { color: #4f7ef7; border-color: rgba(79,126,247,0.3); background: rgba(79,126,247,0.06); }
.p-step.done   { color: #22c55e; border-color: rgba(34,197,94,0.3);  background: rgba(34,197,94,0.05);  }

.p-arrow { color: #2a2a2a; font-size: 14px; font-weight: 300; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #1e1e1e !important;
    border-radius: 14px !important;
    background: #0c0c0c !important;
    transition: border-color 0.2s !important;
    padding: 4px !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(79,126,247,0.5) !important;
}

[data-testid="stFileUploaderDropzone"] {
    padding: 28px 24px !important;
    background: transparent !important;
    border: none !important;
}

section[data-testid="stFileUploaderDropzone"] p {
    color: #555 !important;
    font-size: 13px !important;
}

/* ── Info box ── */
[data-testid="stInfo"] {
    background: rgba(79,126,247,0.05) !important;
    border: 1px solid rgba(79,126,247,0.15) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    color: #888 !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div { border-radius: 4px !important; overflow: hidden; }
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #4f7ef7 0%, #7c3aed 100%) !important;
    border-radius: 4px !important;
    transition: width 0.4s ease !important;
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
    background: #4f7ef7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 9px 18px !important;
    letter-spacing: 0.1px !important;
    transition: opacity 0.15s, transform 0.1s !important;
    box-shadow: 0 2px 12px rgba(79,126,247,0.25) !important;
}

[data-testid="stDownloadButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #1a1a1a !important;
}

/* ── Select box ── */
[data-testid="stSelectbox"] > div > div {
    background: #0f0f0f !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #ccc !important;
    font-size: 13px !important;
}

/* ── Text input ── */
[data-testid="stTextInput"] input {
    background: #0f0f0f !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #ccc !important;
    font-size: 13px !important;
    padding: 9px 14px !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: rgba(79,126,247,0.5) !important;
    box-shadow: 0 0 0 3px rgba(79,126,247,0.08) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0f0f0f !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 10px !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #1a1a1a !important;
    margin: 28px 0 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #4f7ef7 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def stat_card(label, value, color="#e0e0e0", sublabel=None):
    sub = f'<div style="font-size:11px;color:#444;margin-top:4px">{sublabel}</div>' if sublabel else ""
    return f"""
    <div style="
        background:#0f0f0f;
        border:1px solid #1a1a1a;
        border-top:2px solid {color};
        border-radius:12px;
        padding:22px 24px;
    ">
        <div style="font-size:2.6rem;font-weight:800;letter-spacing:-2px;color:{color};line-height:1">{value}</div>
        <div style="font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:#444;margin-top:8px">{label}</div>
        {sub}
    </div>
    """


def section_label(title, count=None):
    badge = ""
    if count is not None:
        badge = f"""<span style="
            display:inline-flex;align-items:center;justify-content:center;
            min-width:22px;height:22px;padding:0 7px;
            background:rgba(79,126,247,0.10);border:1px solid rgba(79,126,247,0.22);
            border-radius:100px;font-size:11px;font-weight:700;color:#4f7ef7;
            margin-left:8px">{count}</span>"""
    return f"""
    <div style="display:flex;align-items:center;margin-bottom:14px">
        <span style="font-size:11px;font-weight:700;text-transform:uppercase;
            letter-spacing:0.9px;color:#444">{title}</span>{badge}
    </div>
    """


# ── Hero ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-badge">⬡ &nbsp;PDF Extraction Pipeline</div>
<div class="hero-title">CODEDPipeline</div>
<div class="hero-sub">Upload a government statistical report — the pipeline finds every table, cleans it, and hands you clean CSVs.</div>
<div class="pipeline">
    <div class="p-step">PDF</div>
    <div class="p-arrow">›</div>
    <div class="p-step">Camelot Extract</div>
    <div class="p-arrow">›</div>
    <div class="p-step">Clean + Dedupe</div>
    <div class="p-arrow">›</div>
    <div class="p-step">Detect Headers</div>
    <div class="p-arrow">›</div>
    <div class="p-step">Validate</div>
    <div class="p-arrow">›</div>
    <div class="p-step done">CSV Export</div>
</div>
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "Drop your PDF here, or click to browse",
    type=["pdf"],
    label_visibility="visible",
)

if uploaded is None:
    st.markdown("""
    <div style="margin-top:16px;padding:14px 18px;background:#0c0c0c;border:1px solid #1a1a1a;
        border-radius:10px;font-size:13px;color:#555;line-height:1.7">
        <strong style="color:#777">Supported:</strong> Bordered / lattice tables — DES district statistical reports, census data, government annexures.<br>
        <strong style="color:#777">Not supported:</strong> Scanned PDFs or stream-style tables without visible borders.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Pipeline ───────────────────────────────────────────────────────────────────

with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp.write(uploaded.getvalue())
    pdf_path = tmp.name

try:
    with st.spinner("Parsing PDF…"):
        from backend.app.extract.table_extractor import extract_tables
        tables = extract_tables(pdf_path)

    if not tables:
        st.error("No tables found. The PDF must contain bordered (lattice) tables.")
        st.stop()

    from backend.app.cleaning.header_builder import apply_headers
    from backend.app.cleaning.header_detector import detect_header_rows
    from backend.app.cleaning.header_postprocessor import clean_headers
    from backend.app.cleaning.universal_cleaner import clean_dataframe
    from backend.app.standardization.metadata_builder import build_metadata
    from backend.app.standardization.table_name_extractor import extract_table_name
    from backend.app.validation.table_validator import validate_table

    prog = st.progress(0, text=f"Processing 0 / {len(tables)} tables…")
    catalog, failed, table_dfs = [], [], {}

    for i, table in enumerate(tables):
        prog.progress(
            (i + 1) / len(tables),
            text=f"Table {table['table_id']} / {len(tables)}  ·  page {table['page']}",
        )
        try:
            with redirect_stdout(io.StringIO()):
                df = clean_dataframe(table["dataframe"])
                h  = detect_header_rows(df)
                nm = extract_table_name(df, h)
                df = apply_headers(df, h)
                df = clean_headers(df)
            status = validate_table(df)
            if status["passed"]:
                catalog.append(build_metadata(table["table_id"], nm, table["page"], df))
                table_dfs[table["table_id"]] = df
            else:
                failed.append({"table": table["table_id"], "page": table["page"], "reason": status["reason"]})
        except Exception as e:
            failed.append({"table": table["table_id"], "page": table["page"], "reason": str(e)})

    prog.empty()

    # ── Stats ──────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(stat_card("Total Tables", len(tables), "#888"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Extracted", len(catalog), "#22c55e"), unsafe_allow_html=True)
    with c3:
        clr = "#f87171" if failed else "#22c55e"
        st.markdown(stat_card("Failed", len(failed), clr), unsafe_allow_html=True)

    if not catalog:
        st.warning("All tables failed validation.")
        st.stop()

    # ── Build ZIP ──────────────────────────────────────────────────────────────
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for tid, df in table_dfs.items():
            zf.writestr(f"table_{tid}.csv", df.to_csv(index=False))
        zf.writestr("table_catalog.csv", pd.DataFrame(catalog).to_csv(index=False))
    zip_buf.seek(0)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Catalog header row ─────────────────────────────────────────────────────
    lc, rc = st.columns([5, 1])
    with lc:
        st.markdown(section_label("Extracted Tables", len(catalog)), unsafe_allow_html=True)
    with rc:
        st.download_button(
            "⬇ All CSVs",
            zip_buf,
            file_name=f"{uploaded.name.replace('.pdf','')}_tables.zip",
            mime="application/zip",
            use_container_width=True,
        )

    # ── Search ─────────────────────────────────────────────────────────────────
    search = st.text_input(
        "search",
        placeholder="🔍  Filter by table name or ID…",
        label_visibility="collapsed",
    )

    catalog_df = pd.DataFrame(catalog)
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
            "table_id":   st.column_config.NumberColumn("#",     width=60),
            "table_name": st.column_config.TextColumn("Name",   width="large"),
            "page":       st.column_config.NumberColumn("Page", width=70),
            "rows":       st.column_config.NumberColumn("Rows", width=70),
            "columns":    st.column_config.NumberColumn("Cols", width=70),
        },
    )

    # ── Preview ────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(section_label("Preview & Download"), unsafe_allow_html=True)

    options = {
        f"#{r.table_id}  ·  {r.table_name}  (p. {r.page})": r.table_id
        for r in pd.DataFrame(catalog).itertuples()
    }
    selected = st.selectbox("table", list(options.keys()), label_visibility="collapsed")

    if selected:
        tid = options[selected]
        df_preview = table_dfs[tid]

        st.markdown(
            f'<div style="font-size:11px;color:#444;margin-bottom:8px">'
            f'{len(df_preview)} rows · {len(df_preview.columns)} columns</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df_preview, use_container_width=True, hide_index=True)

        st.download_button(
            f"⬇  Download table_{tid}.csv",
            df_preview.to_csv(index=False),
            file_name=f"table_{tid}.csv",
            mime="text/csv",
        )

    # ── Failed ─────────────────────────────────────────────────────────────────
    if failed:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.expander(f"⚠  {len(failed)} tables failed validation", expanded=False):
            st.dataframe(
                pd.DataFrame(failed),
                use_container_width=True,
                hide_index=True,
            )

finally:
    os.unlink(pdf_path)
