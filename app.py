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

# ── Design System ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --red:      #C8102E;
  --red-hi:   #E0142F;
  --red-dim:  rgba(200,16,46,0.12);
  --red-rim:  rgba(200,16,46,0.28);
  --white:    #F2EDE8;
  --white2:   #C8C0BC;
  --bg:       #080808;
  --surf:     #0E0E0E;
  --card:     #111111;
  --border:   #1C1C1C;
  --muted:    #484848;
  --mono:     'JetBrains Mono', monospace;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'Space Grotesk', -apple-system, sans-serif !important;
  background: var(--bg) !important;
  color: var(--white) !important;
}

#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
  padding: 0 80px 80px !important;
  max-width: 100% !important;
}

/* ── Hero band ── */
.hero {
  margin-left: -80px;
  margin-right: -80px;
  padding: 72px 80px 60px;
  border-bottom: 1px solid var(--border);
  background:
    radial-gradient(ellipse 60% 40% at 80% 50%, rgba(200,16,46,0.06) 0%, transparent 70%),
    var(--bg);
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 13px 5px 10px;
  border: 1px solid var(--red-rim);
  border-radius: 3px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: 28px;
}

.hero-eyebrow-dot {
  width: 6px; height: 6px;
  background: var(--red);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

.hero-title {
  font-size: clamp(52px, 6vw, 80px);
  font-weight: 700;
  letter-spacing: -3px;
  line-height: 0.95;
  color: var(--white);
  margin-bottom: 6px;
}

.hero-title-red {
  color: var(--red);
  display: block;
}

.hero-divline {
  width: 48px;
  height: 2px;
  background: var(--red);
  margin: 22px 0;
}

.hero-sub {
  font-size: 15px;
  font-weight: 400;
  color: var(--muted);
  line-height: 1.65;
  max-width: 420px;
  margin-bottom: 40px;
}

/* ── Pipeline steps ── */
.pipeline-row {
  display: flex;
  align-items: center;
  gap: 0;
}

.p-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--muted);
  border: 1px solid var(--border);
  background: var(--card);
}

.p-node:first-child { border-radius: 4px 0 0 4px; }
.p-node:last-child  { border-radius: 0 4px 4px 0; }

.p-node.done {
  color: var(--red);
  border-color: var(--red-rim);
  background: var(--red-dim);
}

.p-sep {
  width: 1px;
  height: 100%;
  background: var(--border);
}

.p-connector {
  width: 20px;
  height: 1px;
  background: var(--border);
}

/* ── Main content area ── */
.content {
  padding: 0 80px 80px;
  max-width: 1240px;
}

/* ── Upload section ── */
.upload-section {
  padding: 48px 0 32px;
}

.section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 16px;
}

[data-testid="stFileUploader"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-left: 3px solid var(--red) !important;
  border-radius: 0 6px 6px 0 !important;
  transition: border-color 0.2s, background 0.2s !important;
}

[data-testid="stFileUploader"]:hover {
  background: #141414 !important;
  border-color: var(--red-rim) !important;
  border-left-color: var(--red) !important;
}

[data-testid="stFileUploaderDropzone"] {
  padding: 32px 28px !important;
  background: transparent !important;
  border: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] p,
section[data-testid="stFileUploaderDropzone"] p {
  color: var(--muted) !important;
  font-size: 13px !important;
  font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Notes ── */
.note {
  margin-top: 14px;
  padding: 14px 18px 14px 20px;
  border-left: 2px solid var(--border);
  font-size: 12px;
  color: var(--muted);
  line-height: 1.7;
}

.note strong { color: #777; font-weight: 600; }

/* ── Progress ── */
[data-testid="stProgressBar"] > div {
  background: #1a1a1a !important;
  border-radius: 1px !important;
  height: 2px !important;
}

[data-testid="stProgressBar"] > div > div {
  background: var(--red) !important;
  border-radius: 1px !important;
  transition: width 0.5s ease !important;
}

[data-testid="stProgressBar"] p,
div[data-testid="stProgressBar"] + div {
  font-family: var(--mono) !important;
  font-size: 11px !important;
  color: var(--muted) !important;
}

/* ── Stat cards ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 40px 0;
}

.stat-card {
  padding: 28px 24px;
  background: var(--card);
  border: 1px solid var(--border);
  border-top: 2px solid;
  border-radius: 4px;
}

.stat-card.total  { border-top-color: var(--border); }
.stat-card.ok     { border-top-color: var(--red); }
.stat-card.fail   { border-top-color: #333; }
.stat-card.fail.nonzero { border-top-color: var(--red); }

.stat-num {
  font-size: 3.6rem;
  font-weight: 700;
  letter-spacing: -3px;
  line-height: 1;
  font-family: var(--mono);
}

.stat-card.total .stat-num  { color: var(--white2); }
.stat-card.ok    .stat-num  { color: var(--red); }
.stat-card.fail  .stat-num  { color: var(--muted); }
.stat-card.fail.nonzero .stat-num { color: var(--red); }

.stat-rule {
  width: 24px;
  height: 1px;
  background: var(--border);
  margin: 16px 0 12px;
}

.stat-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--muted);
}

.stat-sub {
  font-size: 11px;
  color: #333;
  margin-top: 4px;
  font-family: var(--mono);
}

/* ── Section header ── */
.sect {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.sect-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sect-name {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--muted);
}

.sect-count {
  padding: 2px 9px;
  background: var(--red-dim);
  border: 1px solid var(--red-rim);
  border-radius: 2px;
  font-size: 10px;
  font-weight: 700;
  color: var(--red);
  font-family: var(--mono);
}

/* ── Table ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  overflow: hidden !important;
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] button {
  background: var(--red) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 3px !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  letter-spacing: 0.8px !important;
  padding: 10px 20px !important;
  transition: background 0.15s, transform 0.1s !important;
  font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stDownloadButton"] button:hover {
  background: var(--red-hi) !important;
  transform: translateY(-1px) !important;
}

/* ── Text input ── */
[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  color: var(--white) !important;
  font-size: 13px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  padding: 10px 14px !important;
}

[data-testid="stTextInput"] input:focus {
  border-color: var(--red-rim) !important;
  box-shadow: 0 0 0 3px rgba(200,16,46,0.06) !important;
  outline: none !important;
}

[data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  color: var(--white) !important;
  font-size: 13px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: var(--red) !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-left: 3px solid var(--red) !important;
  border-radius: 0 4px 4px 0 !important;
}

/* ── HR ── */
hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 36px 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def stat_card(cls, value, label, sub=""):
    sub_html = f'<div class="stat-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="stat-card {cls}">
        <div class="stat-num">{value}</div>
        <div class="stat-rule"></div>
        <div class="stat-label">{label}</div>
        {sub_html}
    </div>"""


def sect_header(name, count=None):
    badge = f'<span class="sect-count">{count}</span>' if count is not None else ""
    return f"""
    <div class="sect">
        <div class="sect-title">
            <span class="sect-name">{name}</span>
            {badge}
        </div>
    </div>"""


# ── Hero ───────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">
        <div class="hero-eyebrow-dot"></div>
        District Extraction Engine
    </div>
    <div class="hero-title">
        CODED
        <span class="hero-title-red">Pipeline</span>
    </div>
    <div class="hero-divline"></div>
    <div class="hero-sub">
        Upload a government statistical report.
        The pipeline finds every table, cleans it,
        and hands you structured CSVs — ready to analyse.
    </div>
    <div class="pipeline-row">
        <div class="p-node">PDF</div>
        <div class="p-connector"></div>
        <div class="p-node">Camelot Extract</div>
        <div class="p-connector"></div>
        <div class="p-node">Clean + Dedupe</div>
        <div class="p-connector"></div>
        <div class="p-node">Header Detection</div>
        <div class="p-connector"></div>
        <div class="p-node">Validate</div>
        <div class="p-connector"></div>
        <div class="p-node done">&#10003; &nbsp;CSV Export</div>
    </div>
</div>
<div class="content">
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────

st.markdown('<div class="upload-section"><div class="section-label">Input</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop PDF here or click to browse",
    type=["pdf"],
    label_visibility="collapsed",
)

st.markdown('</div>', unsafe_allow_html=True)

if uploaded is None:
    st.markdown("""
    <div class="note">
        <strong>Supported</strong> — Bordered / lattice tables: DES district reports, census annexures, government statistical publications.<br>
        <strong>Not supported</strong> — Scanned PDFs, image-only files, or stream-style tables without visible cell borders.
    </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Run pipeline ───────────────────────────────────────────────────────────────

with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp.write(uploaded.getvalue())
    pdf_path = tmp.name

try:
    with st.spinner("Parsing PDF…"):
        from backend.app.extract.table_extractor import extract_tables
        tables = extract_tables(pdf_path)

    if not tables:
        st.error("No tables found. PDF must contain bordered (lattice) tables.")
        st.stop()

    from backend.app.cleaning.header_builder import apply_headers
    from backend.app.cleaning.header_detector import detect_header_rows
    from backend.app.cleaning.header_postprocessor import clean_headers
    from backend.app.cleaning.universal_cleaner import clean_dataframe
    from backend.app.standardization.metadata_builder import build_metadata
    from backend.app.standardization.table_name_extractor import extract_table_name
    from backend.app.validation.table_validator import validate_table

    prog = st.progress(0, text=f"0 / {len(tables)}")
    catalog, failed, table_dfs = [], [], {}

    for i, t in enumerate(tables):
        prog.progress(
            (i + 1) / len(tables),
            text=f"{i+1} / {len(tables)}  ·  table {t['table_id']}  ·  p.{t['page']}",
        )
        try:
            with redirect_stdout(io.StringIO()):
                df  = clean_dataframe(t["dataframe"])
                h   = detect_header_rows(df)
                nm  = extract_table_name(df, h)
                df  = apply_headers(df, h)
                df  = clean_headers(df)
            s = validate_table(df)
            if s["passed"]:
                catalog.append(build_metadata(t["table_id"], nm, t["page"], df))
                table_dfs[t["table_id"]] = df
            else:
                failed.append({"table": t["table_id"], "page": t["page"], "reason": s["reason"]})
        except Exception as e:
            failed.append({"table": t["table_id"], "page": t["page"], "reason": str(e)})

    prog.empty()

    # ── Stats ──────────────────────────────────────────────────────────────────
    fail_cls = "fail nonzero" if failed else "fail"
    st.markdown(f"""
    <div class="stats-row">
        {stat_card("total", len(tables),  "Total Tables",  f"{uploaded.name}")}
        {stat_card("ok",    len(catalog), "Extracted",     f"{round(len(catalog)/len(tables)*100)}% success rate")}
        {stat_card(fail_cls, len(failed), "Failed",        "validation" if failed else "clean run")}
    </div>
    """, unsafe_allow_html=True)

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

    # ── Catalog ────────────────────────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(sect_header("Extracted Tables", len(catalog)), unsafe_allow_html=True)

    lc, rc = st.columns([5, 1])
    with lc:
        search = st.text_input(
            "s", placeholder="Search by name or table ID…",
            label_visibility="collapsed",
        )
    with rc:
        st.download_button(
            "↓ All CSVs",
            zip_buf,
            file_name=f"{uploaded.name.replace('.pdf','')}_tables.zip",
            mime="application/zip",
            use_container_width=True,
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
    st.markdown(sect_header("Preview & Download"), unsafe_allow_html=True)

    options = {
        f"#{r.table_id}  ·  {r.table_name}  ·  p.{r.page}": r.table_id
        for r in pd.DataFrame(catalog).itertuples()
    }
    sel = st.selectbox("t", list(options.keys()), label_visibility="collapsed")

    if sel:
        tid     = options[sel]
        df_prev = table_dfs[tid]
        st.markdown(
            f'<div style="font-size:11px;color:var(--muted);margin-bottom:10px;font-family:var(--mono)">'
            f'{len(df_prev)} rows &nbsp;·&nbsp; {len(df_prev.columns)} columns</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df_prev, use_container_width=True, hide_index=True)
        st.download_button(
            f"↓ table_{tid}.csv",
            df_prev.to_csv(index=False),
            file_name=f"table_{tid}.csv",
            mime="text/csv",
        )

    # ── Failed ─────────────────────────────────────────────────────────────────
    if failed:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        with st.expander(f"{len(failed)} tables failed validation", expanded=False):
            st.dataframe(pd.DataFrame(failed), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

finally:
    os.unlink(pdf_path)
