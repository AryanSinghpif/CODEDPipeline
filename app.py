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
    page_title="DataGen",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system — GitHub dark / radar green ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg:      #000000;
  --bg2:     #0d0a12;
  --card:    #0d0a12;
  --border:  #221c2c;
  --border2: #322940;
  --text:    #f2edf7;
  --text2:   #9b8fae;
  --muted:   #6f6480;
  --green:   #ff4fd8;
  --green-hi:#ff7ce4;
  --green-dk:#b026c9;
  --green-dim: rgba(255,79,216,0.10);
  --green-rim: rgba(255,79,216,0.35);
  --mono: 'JetBrains Mono', monospace;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
  padding: 24px 56px 24px !important;
  max-width: 1500px !important;
}

/* ── top bar ── */
.topbar {
  display: flex; align-items: center; gap: 14px;
  padding: 0 0 16px; border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}
.logo-mark {
  width: 30px; height: 30px; border-radius: 50%;
  background: radial-gradient(circle at 50% 35%, var(--green-dk), #2a0a33 70%);
  border: 1px solid var(--green-rim);
  box-shadow: 0 0 18px rgba(255,79,216,0.35);
}
.logo-name { font-weight: 800; font-size: 18px; letter-spacing: -0.3px; }
.logo-name span { color: var(--green); }
.topbar-tag {
  font-family: var(--mono); font-size: 10px; letter-spacing: 2px;
  text-transform: uppercase; color: var(--text2);
  border: 1px solid var(--border2); border-radius: 999px;
  padding: 4px 12px; margin-left: 8px;
}
.topbar-right { margin-left: auto; font-family: var(--mono); font-size: 10px;
  letter-spacing: 2px; text-transform: uppercase; color: var(--muted); }

/* ── hero (pre-upload) ── */
.hero { text-align: center; padding: 26px 0 6px; }
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 10px; letter-spacing: 3px;
  text-transform: uppercase; color: var(--green);
  background: var(--green-dim); border: 1px solid var(--green-rim);
  border-radius: 4px; padding: 5px 14px; margin-bottom: 18px;
}
.hero-title {
  font-size: 54px; font-weight: 800; letter-spacing: -2px; line-height: 1.04;
  color: var(--text);
}
.hero-sub {
  margin: 14px auto 0; max-width: 620px;
  color: var(--text2); font-size: 15px; line-height: 1.6;
}

/* ── radar grid backdrop ── */
.radar-wrap { position: relative; margin: 26px auto 0; width: 320px; height: 150px; overflow: hidden; }
.radar-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,79,216,0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,79,216,0.12) 1px, transparent 1px);
  background-size: 26px 26px;
  mask-image: radial-gradient(ellipse at 50% 100%, black 30%, transparent 75%);
}
.radar-dome {
  position: absolute; left: 50%; bottom: -90px; transform: translateX(-50%);
  width: 180px; height: 180px; border-radius: 50%;
  background: radial-gradient(circle at 50% 30%, rgba(255,79,216,0.45), rgba(13,40,22,0.9) 70%);
  border: 1px solid var(--green-rim);
  box-shadow: 0 0 60px rgba(255,79,216,0.35);
}

/* ── scanner / loading ── */
.scan-box {
  position: relative; border: 1px solid var(--border2); border-radius: 10px;
  background: var(--bg2); padding: 48px 64px;
  overflow: hidden; margin: 8px 0;
  display: flex; align-items: center; justify-content: space-between;
  gap: 40px; min-height: 340px;
}
.scan-left { position: relative; text-align: left; max-width: 380px; }
.scan-box::before {
  content: ''; position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,79,216,0.10) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,79,216,0.10) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(ellipse at 50% 50%, black 20%, transparent 80%);
}
/* ── plasma orb (AI-assistant style) ── */
.orb {
  position: relative; width: 230px; height: 230px; margin: 0 auto;
  flex-shrink: 0;
  border-radius: 50%; overflow: hidden;
  background: radial-gradient(circle at 38% 32%,
    #ffffff 0%, #ffc2ef 16%, #ff7ce4 38%, #ff4fd8 58%, #b026c9 78%, #4a0d5c 100%);
  box-shadow:
    0 0 30px rgba(255,79,216,0.85),
    0 0 90px rgba(255,79,216,0.45),
    0 0 160px rgba(139,92,246,0.30);
  animation: breathe 3.2s ease-in-out infinite;
}
.orb .ribbon1, .orb .ribbon2 {
  position: absolute; inset: -35%; border-radius: 50%;
}
.orb .ribbon1 {
  background: conic-gradient(from 0deg,
    transparent 0%, rgba(255,255,255,0.95) 8%, transparent 22%,
    rgba(139,92,246,0.75) 45%, transparent 60%,
    rgba(255,255,255,0.7) 78%, transparent 92%);
  filter: blur(10px);
  animation: swirl 4.5s linear infinite;
}
.orb .ribbon2 {
  background: conic-gradient(from 140deg,
    transparent 0%, rgba(255,194,239,0.9) 12%, transparent 30%,
    rgba(255,255,255,0.8) 55%, transparent 70%);
  filter: blur(14px);
  animation: swirl 7s linear infinite reverse;
}
.orb .sheen {
  position: absolute; inset: 0; border-radius: 50%;
  background: radial-gradient(circle at 36% 26%,
    rgba(255,255,255,0.9), transparent 40%);
  mix-blend-mode: screen;
}
@keyframes swirl { to { transform: rotate(360deg); } }
@keyframes breathe {
  0%, 100% { transform: scale(1);    filter: hue-rotate(0deg); }
  50%      { transform: scale(1.06); filter: hue-rotate(-18deg); }
}
.scan-pulse {
  position: absolute; left: 50%; top: 50%; width: 110px; height: 110px;
  transform: translate(-50%, -82%); border-radius: 50%;
  border: 1px solid var(--green-rim);
  animation: pulse 2s ease-out infinite;
}
@keyframes pulse {
  0%   { opacity: .7; transform: translate(-50%,-82%) scale(1); }
  100% { opacity: 0;  transform: translate(-50%,-82%) scale(2.2); }
}
.scan-title { position: relative; font-weight: 600; font-size: 14px; }
.scan-msg {
  position: relative; font-family: var(--mono); font-size: 10px;
  letter-spacing: 1.5px; text-transform: uppercase; color: var(--green);
  margin-top: 10px; min-height: 14px;
}
.scan-msg::after { content: '▍'; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.scan-sub { position: relative; color: var(--muted); font-size: 10px; margin-top: 6px;
  font-family: var(--mono); }
.scan-bar {
  position: relative; height: 3px; border-radius: 2px; background: var(--border);
  margin: 22px 0 0; max-width: 320px; overflow: hidden;
}
.scan-bar > div {
  height: 100%; background: linear-gradient(90deg, var(--green-dk), var(--green-hi));
  border-radius: 2px; box-shadow: 0 0 12px rgba(255,79,216,0.6);
  transition: width .25s ease;
}
.scan-bar.indet > div {
  width: 35% !important; animation: slide 1.2s ease-in-out infinite alternate;
}
@keyframes slide { from { margin-left: 0; } to { margin-left: 65%; } }

/* ── stat chips ── */
.stats { display: flex; gap: 12px; margin: 4px 0 14px; }
.stat {
  flex: 1; background: var(--bg2); border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 16px;
}
.stat .v { font-size: 24px; font-weight: 800; letter-spacing: -1px; }
.stat .v.green { color: var(--green); }
.stat .v.red { color: #f85149; }
.stat .k { font-family: var(--mono); font-size: 9px; letter-spacing: 2px;
  text-transform: uppercase; color: var(--muted); margin-top: 2px; }

/* ── widgets ── */
.stTextInput input, .stSelectbox div[data-baseweb] {
  background: var(--bg2) !important; border-color: var(--border2) !important;
  color: var(--text) !important; font-family: var(--mono) !important; font-size: 12px !important;
}
.stDownloadButton button, .stButton button {
  background: #fff !important; color: #0d1117 !important;
  border: 1px solid #fff !important; border-radius: 6px !important;
  font-weight: 600 !important; font-size: 13px !important;
}
.stDownloadButton button:hover { background: var(--green-hi) !important; border-color: var(--green-hi) !important; }
div[data-testid="stFileUploader"] {
  border: 1px dashed var(--border2); border-radius: 10px; background: var(--bg2);
  padding: 6px;
}
div[data-testid="stFileUploader"] section { background: transparent !important; }
div[data-testid="stFileUploader"] section button {
  background: #fff !important; color: #0d1117 !important; border-radius: 6px !important;
  font-weight: 600 !important;
}
div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 8px; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono) !important; font-size: 11px !important;
  letter-spacing: 1.5px; text-transform: uppercase; color: var(--text2) !important;
}
.stTabs [aria-selected="true"] { color: var(--green) !important; border-bottom: 2px solid var(--green) !important; }
hr { border-color: var(--border) !important; margin: 10px 0 !important; }
.note {
  border: 1px solid var(--border); border-left: 3px solid var(--green);
  border-radius: 0 8px 8px 0; background: var(--bg2);
  padding: 14px 18px; color: var(--text2); font-size: 13px; line-height: 1.7;
  max-width: 760px; margin: 18px auto 0;
}
.note strong { color: var(--text); }
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="logo-mark"></div>
  <div class="logo-name">Data<span>Gen</span></div>
  <div class="topbar-tag">Release</div>
  <div class="topbar-right">District Extraction Engine</div>
</div>
""", unsafe_allow_html=True)


def scanner_html(title, msg, sub="", pct=None):
    bar_cls = "scan-bar" if pct is not None else "scan-bar indet"
    width = f"{pct:.0f}%" if pct is not None else "35%"
    return f"""
    <div class="scan-box">
      <div class="scan-left">
        <div class="scan-title">{title}</div>
        <div class="scan-msg">{msg}</div>
        <div class="scan-sub">{sub}</div>
        <div class="{bar_cls}"><div style="width:{width}"></div></div>
      </div>
      <div class="orb"><div class="ribbon1"></div><div class="ribbon2"></div><div class="sheen"></div></div>
    </div>"""


# ── Upload / hero ──────────────────────────────────────────────────────────────
uploaded = None
hero = st.empty()

with hero.container():
    st.markdown("""
    <div class="hero">
      <div class="orb" style="width:84px;height:84px;margin-bottom:24px">
        <div class="ribbon1"></div><div class="ribbon2"></div><div class="sheen"></div>
      </div>
      <div class="hero-eyebrow">● &nbsp;DataGen — district report extraction</div>
      <div class="hero-title">Every table in your PDF.<br>Cleaned. Translated. Excel-ready.</div>
      <div class="hero-sub">Upload a government statistical report — the pipeline finds every
      bordered table, merges hierarchical headers, translates legacy Hindi, and hands you
      structured CSVs and a multi-sheet Excel workbook.</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        uploaded = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
        if uploaded is None:
            st.markdown("""
            <div class="note">
              <strong>Supported</strong> — bordered / lattice tables: DES district reports, census
              annexures, statistical publications.<br>
              <strong>Not supported</strong> — scanned or image-only PDFs, borderless stream tables.
            </div>""", unsafe_allow_html=True)

if uploaded is None:
    st.stop()

hero.empty()

# ── Run pipeline ───────────────────────────────────────────────────────────────
with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    tmp.write(uploaded.getvalue())
    pdf_path = tmp.name

stage = st.empty()

try:
    if "results" not in st.session_state or st.session_state.get("pdf_name") != uploaded.name:

        stage.markdown(
            scanner_html("Scanning PDF", "locating lattice tables",
                         f"{uploaded.name} · camelot lattice engine"),
            unsafe_allow_html=True,
        )

        from backend.app.extract.table_extractor import extract_tables
        tables = extract_tables(pdf_path)

        if not tables:
            stage.empty()
            st.error("No tables found. PDF must contain bordered (lattice) tables.")
            st.stop()

        from backend.app.cleaning.header_builder import apply_headers
        from backend.app.cleaning.header_detector import detect_header_rows
        from backend.app.cleaning.header_postprocessor import clean_headers
        from backend.app.cleaning.universal_cleaner import clean_dataframe
        from backend.app.export.excel_exporter import build_workbook
        from backend.app.standardization.metadata_builder import build_metadata
        from backend.app.standardization.table_name_extractor import extract_table_name
        from backend.app.translation.hindi_translator import translate_dataframe
        from backend.app.validation.table_validator import validate_table

        MSGS = [
            "removing empty rows + garbage",
            "detecting header depth",
            "merging hierarchical headers",
            "translating legacy hindi",
            "validating structure",
            "naming tables from pdf titles",
        ]

        catalog, failed, table_dfs = [], [], {}
        for i, t in enumerate(tables):
            stage.markdown(
                scanner_html(
                    "Processing tables",
                    MSGS[i % len(MSGS)],
                    f"table {t['table_id']} · page {t['page']} · {i + 1} / {len(tables)}",
                    pct=100 * (i + 1) / len(tables),
                ),
                unsafe_allow_html=True,
            )
            try:
                with redirect_stdout(io.StringIO()):
                    df = clean_dataframe(t["dataframe"])
                    h = detect_header_rows(df)
                    nm = extract_table_name(df, h, t.get("caption"))
                    df = apply_headers(df, h)
                    df = translate_dataframe(df)
                    df = clean_headers(df)
                s = validate_table(df)
                if s["passed"]:
                    catalog.append(build_metadata(t["table_id"], nm, t["page"], df))
                    table_dfs[t["table_id"]] = df
                else:
                    failed.append({"table": t["table_id"], "page": t["page"], "reason": s["reason"]})
            except Exception as e:
                failed.append({"table": t["table_id"], "page": t["page"], "reason": str(e)})

        if not table_dfs:
            stage.empty()
            st.warning("All tables failed validation.")
            st.stop()

        stage.markdown(
            scanner_html("Packaging", "building excel workbook + csv bundle",
                         f"{len(table_dfs)} tables", pct=100),
            unsafe_allow_html=True,
        )

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for tid, df in table_dfs.items():
                zf.writestr(f"table_{tid}.csv", df.to_csv(index=False))
            zf.writestr("table_catalog.csv", pd.DataFrame(catalog).to_csv(index=False))
        zip_buf.seek(0)

        xlsx_buf = build_workbook(table_dfs, catalog)

        st.session_state["results"] = {
            "catalog": catalog, "failed": failed, "table_dfs": table_dfs,
            "zip": zip_buf.getvalue(), "xlsx": xlsx_buf.getvalue(),
            "n_raw": len(tables),
        }
        st.session_state["pdf_name"] = uploaded.name

    stage.empty()
    R = st.session_state["results"]
    catalog, failed, table_dfs = R["catalog"], R["failed"], R["table_dfs"]

    # ── Results (single viewport) ──────────────────────────────────────────────
    fail_cls = "red" if failed else "green"
    st.markdown(f"""
    <div class="stats">
      <div class="stat"><div class="v">{R["n_raw"]}</div><div class="k">Tables detected</div></div>
      <div class="stat"><div class="v green">{len(catalog)}</div><div class="k">Passed</div></div>
      <div class="stat"><div class="v {fail_cls}">{len(failed)}</div><div class="k">Failed</div></div>
      <div class="stat"><div class="v">{len(table_dfs) and max(m["page"] for m in catalog)}</div><div class="k">Pages covered</div></div>
    </div>
    """, unsafe_allow_html=True)

    base = uploaded.name.replace(".pdf", "")
    s1, s2, s3 = st.columns([4, 1, 1])
    with s1:
        search = st.text_input("s", placeholder="Search by name or table ID…", label_visibility="collapsed")
    with s2:
        st.download_button("↓ Excel", R["xlsx"], file_name=f"{base}_tables.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)
    with s3:
        st.download_button("↓ All CSVs", R["zip"], file_name=f"{base}_tables.zip",
                           mime="application/zip", use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["Catalog", "Preview", f"Failed ({len(failed)})"])

    with tab1:
        catalog_df = pd.DataFrame(catalog)
        if search:
            mask = (
                catalog_df["table_name"].str.contains(search, case=False, na=False)
                | catalog_df["table_id"].astype(str).str.contains(search)
            )
            catalog_df = catalog_df[mask]
        st.dataframe(
            catalog_df[["table_id", "table_name", "page", "rows", "columns"]],
            use_container_width=True, hide_index=True, height=330,
            column_config={
                "table_id": st.column_config.NumberColumn("#", width=60),
                "table_name": st.column_config.TextColumn("Name", width="large"),
                "page": st.column_config.NumberColumn("Page", width=70),
                "rows": st.column_config.NumberColumn("Rows", width=70),
                "columns": st.column_config.NumberColumn("Cols", width=70),
            },
        )

    with tab2:
        options = {
            f"#{m['table_id']}  ·  {m['table_name']}  ·  p.{m['page']}": m["table_id"]
            for m in catalog
        }
        pc1, pc2 = st.columns([5, 1])
        with pc1:
            sel = st.selectbox("t", list(options.keys()), label_visibility="collapsed")
        tid = options[sel]
        df_prev = table_dfs[tid]
        with pc2:
            st.download_button(f"↓ CSV", df_prev.to_csv(index=False),
                               file_name=f"table_{tid}.csv", mime="text/csv",
                               use_container_width=True)
        st.dataframe(df_prev, use_container_width=True, hide_index=True, height=300)

    with tab3:
        if failed:
            st.dataframe(pd.DataFrame(failed), use_container_width=True, hide_index=True, height=300)
        else:
            st.markdown('<div class="scan-sub" style="padding:20px">No failures — every table passed validation.</div>',
                        unsafe_allow_html=True)

finally:
    os.unlink(pdf_path)
