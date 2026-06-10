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

# ── Design system — sleep-well-creatives: night blues, cream paper, gold ──────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Space+Grotesk:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

:root {
  --night:      #010d6e;
  --night-deep: #010940;
  --navy:       #002e77;
  --blue:       #2575f6;
  --blue-dim:   #0042af;
  --soft:       #94b8f2;
  --ice:        #eef4ff;
  --cream:      #fef1d0;
  --cream-2:    #fde7af;
  --gold:       #d4c500;
  --ink:        #0a1240;
  --serif: 'Instrument Serif', Georgia, serif;
  --sans:  'Space Grotesk', Arial, sans-serif;
  --mono:  'Space Mono', monospace;
}

html, body, [class*="css"], .stApp {
  font-family: var(--sans) !important;
  background: radial-gradient(120% 90% at 50% 0%, var(--navy) 0%, var(--night) 55%, var(--night-deep) 100%) fixed !important;
  color: var(--cream) !important;
}

#MainMenu, footer, header { visibility: hidden !important; }

.block-container {
  padding: 24px 56px 24px !important;
  max-width: 1500px !important;
}

/* ── top bar ── */
.topbar {
  display: flex; align-items: center; gap: 12px;
  padding: 0 0 16px; border-bottom: 1px solid rgba(148,184,242,0.25);
  margin-bottom: 20px;
}
.logo-mark { color: var(--gold); font-size: 20px; }
.logo-name { font-size: 17px; letter-spacing: 0.04em; color: var(--ice); }
.logo-name span { font-weight: 600; color: var(--soft); }
.topbar-right {
  margin-left: auto; font-family: var(--mono); font-size: 10px;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--soft);
}

/* ── hero ── */
.hero { text-align: center; padding: 26px 0 6px; }
.hero-eyebrow {
  display: inline-block;
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--soft);
  margin-bottom: 18px;
}
.hero-title {
  font-family: var(--serif); font-weight: 400;
  font-size: clamp(40px, 6vw, 64px); letter-spacing: 0; line-height: 1.08;
  color: var(--ice);
}
.hero-title em { font-style: italic; color: var(--gold); }
.hero-sub {
  margin: 16px auto 0; max-width: 560px;
  color: var(--soft); font-size: 15px; font-weight: 300; line-height: 1.7;
}

/* ── the solver: person + rubik's cube (pure CSS) ── */
.solver-box {
  position: relative; border-radius: 14px;
  border: 1px solid rgba(148,184,242,0.25);
  background: rgba(238,244,255,0.03);
  padding: 44px 64px; margin: 8px 0; min-height: 360px;
  display: flex; align-items: center; justify-content: space-between; gap: 40px;
}
.scan-left { position: relative; text-align: left; max-width: 400px; }
.scan-title { font-family: var(--serif); font-size: 28px; color: var(--ice); }
.scan-msg {
  font-family: var(--mono); font-size: 10px;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold);
  margin-top: 12px; min-height: 14px;
}
.scan-msg::after { content: '▍'; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.scan-sub { color: var(--soft); font-size: 10px; margin-top: 6px; font-family: var(--mono); letter-spacing: 0.08em; }
.scan-bar {
  position: relative; height: 3px; border-radius: 2px;
  background: rgba(148,184,242,0.25);
  margin: 22px 0 0; max-width: 320px; overflow: hidden;
}
.scan-bar > div {
  height: 100%; background: var(--gold); border-radius: 2px;
  transition: width .25s ease;
}
.scan-bar.indet > div {
  width: 35% !important; animation: slide 1.2s ease-in-out infinite alternate;
}
@keyframes slide { from { margin-left: 0; } to { margin-left: 65%; } }

.solver { position: relative; width: 280px; height: 240px; flex-shrink: 0; }
.person { position: absolute; inset: 0; width: 100%; height: auto; opacity: 0.9; }
.arm { transform-origin: 120px 84px; }
.arm-l { animation: arm-wiggle 2.4s ease-in-out infinite; }
.arm-r { animation: arm-wiggle 2.4s ease-in-out infinite reverse; }
@keyframes arm-wiggle { 0%,100% { transform: rotate(0deg); } 50% { transform: rotate(4deg); } }

.cube-stage {
  position: absolute; left: 50%; top: 96px;
  width: 72px; height: 72px; margin-left: -36px;
  perspective: 700px;
}
.cube-rotor {
  position: absolute; inset: 0; transform-style: preserve-3d;
  animation: cube-spin 9s linear infinite;
}
@keyframes cube-spin {
  from { transform: rotateX(-24deg) rotateY(0deg); }
  to   { transform: rotateX(-24deg) rotateY(360deg); }
}
.slice {
  position: absolute; left: 0; width: 72px; height: 24px;
  transform-style: preserve-3d;
}
.slice-top { top: 0;    animation: twist-a 7.2s cubic-bezier(.7,0,.2,1) infinite; }
.slice-mid { top: 24px; animation: twist-b 7.2s cubic-bezier(.7,0,.2,1) infinite; }
.slice-bot { top: 48px; animation: twist-c 7.2s cubic-bezier(.7,0,.2,1) infinite; }
/* sequential layer moves, like solving */
@keyframes twist-a { 0%,8% {transform:rotateY(0)} 16%,100% {transform:rotateY(90deg)} }
@keyframes twist-b { 0%,36% {transform:rotateY(0)} 46%,100% {transform:rotateY(-90deg)} }
@keyframes twist-c { 0%,66% {transform:rotateY(0)} 76%,100% {transform:rotateY(90deg)} }
.slice-face {
  position: absolute; width: 72px; height: 24px;
  display: flex; flex-direction: column;
  background: var(--night-deep);
}
.sf-0 { transform: rotateY(0deg)   translateZ(36px); }
.sf-1 { transform: rotateY(90deg)  translateZ(36px); }
.sf-2 { transform: rotateY(180deg) translateZ(36px); }
.sf-3 { transform: rotateY(270deg) translateZ(36px); }
.sf-up { width: 72px; height: 72px; transform: rotateX(90deg) translateZ(12px); }
.sticker-row { display: flex; flex: 1; gap: 2px; padding: 1px; height: 100%; }
.sf-up .sticker-row { height: 33.3%; }
.sticker { flex: 1; border-radius: 3px; display: block; }
.cube-shadow {
  position: absolute; left: 50%; top: 188px; width: 110px; height: 16px;
  margin-left: -55px; border-radius: 50%;
  background: radial-gradient(ellipse, rgba(1,9,64,0.9) 0%, transparent 70%);
}

/* ── book spread (results) ── */
.book {
  position: relative; display: flex; border-radius: 10px;
  background: var(--night-deep); padding: 12px; margin: 4px 0 18px;
  box-shadow: 0 30px 60px rgba(1,9,64,0.5), inset 0 0 0 1px rgba(148,184,242,0.18);
}
.bpage {
  background: linear-gradient(135deg, var(--cream) 0%, var(--cream-2) 100%);
  color: var(--ink); padding: 30px 34px; flex: 1;
}
.bpage-l { border-radius: 6px 0 0 6px; border-right: 1px solid rgba(10,18,64,0.18); }
.bpage-r { border-radius: 0 6px 6px 0; }
.bk-kicker {
  font-family: var(--mono); font-size: 10px; text-transform: uppercase;
  letter-spacing: 0.22em; color: var(--blue-dim);
}
.bk-title {
  font-family: var(--serif); font-style: italic; font-weight: 400;
  font-size: 44px; line-height: 1; margin: 10px 0 8px; color: var(--ink);
}
.bk-sub { font-size: 13px; font-weight: 300; color: rgba(10,18,64,0.7); max-width: 320px; }
.bk-stats { display: flex; gap: 30px; margin-top: 8px; }
.bk-stat .v { font-family: var(--serif); font-size: 38px; line-height: 1.1; color: var(--ink); }
.bk-stat .v.good { color: var(--blue-dim); }
.bk-stat .v.bad { color: #a4541b; }
.bk-stat .k {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.16em;
  text-transform: uppercase; color: rgba(10,18,64,0.6); margin-top: 2px;
}

/* ── widgets, recoloured to the palette ── */
.stTextInput input, .stSelectbox div[data-baseweb] {
  background: rgba(238,244,255,0.06) !important;
  border-color: rgba(148,184,242,0.35) !important;
  color: var(--ice) !important; font-family: var(--mono) !important; font-size: 12px !important;
}
.stDownloadButton button, .stButton button {
  background: var(--cream) !important; color: var(--ink) !important;
  border: 1px solid var(--cream) !important; border-radius: 6px !important;
  font-family: var(--mono) !important; font-weight: 700 !important; font-size: 12px !important;
  letter-spacing: 0.06em !important;
}
.stDownloadButton button:hover, .stButton button:hover {
  background: var(--gold) !important; border-color: var(--gold) !important;
}
div[data-testid="stFileUploader"] {
  border: 1px dashed rgba(254,241,208,0.35); border-radius: 14px;
  background: rgba(238,244,255,0.03); padding: 6px;
}
div[data-testid="stFileUploader"]:hover { border-color: var(--gold); }
div[data-testid="stFileUploader"] section { background: transparent !important; }
div[data-testid="stFileUploader"] section button {
  background: var(--cream) !important; color: var(--ink) !important; border-radius: 6px !important;
  font-weight: 600 !important;
}
div[data-testid="stDataFrame"] {
  border: 1px solid rgba(148,184,242,0.25); border-radius: 8px;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 4px; background: transparent;
  border-bottom: 1px solid rgba(148,184,242,0.25);
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--mono) !important; font-size: 11px !important;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--soft) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--gold) !important; border-bottom: 2px solid var(--gold) !important;
}
hr { border-color: rgba(148,184,242,0.25) !important; margin: 10px 0 !important; }
.note {
  border-top: 1px solid rgba(148,184,242,0.3);
  padding: 14px 4px 0; color: var(--soft); font-size: 13px;
  font-weight: 300; line-height: 1.7; max-width: 720px; margin: 18px auto 0;
}
.note strong { color: var(--ice); font-weight: 500; }

/* ── upload scene: man at his desk, monitor = the app ── */
.scene {
  position: relative; width: 860px; height: 540px; margin: 0 auto;
}
.star { position: absolute; width: 3px; height: 3px; border-radius: 50%;
  background: var(--gold); animation: twinkle 3s ease-in-out infinite; }
@keyframes twinkle { 0%,100% { opacity: .15; } 50% { opacity: .95; } }
.scene-eyebrow {
  position: absolute; top: 0; left: 0; right: 0; text-align: center;
  font-family: var(--mono); font-size: 10px; letter-spacing: 0.24em;
  text-transform: uppercase; color: var(--soft);
}
.scene-eyebrow::before, .scene-eyebrow::after { content: ' • '; color: var(--blue); }
.desk {
  position: absolute; left: 90px; right: 90px; top: 442px; height: 10px;
  background: var(--cream); border-radius: 5px;
  box-shadow: 0 26px 40px rgba(1,9,64,0.65);
}
.desk-leg { position: absolute; top: 452px; width: 7px; height: 78px;
  background: linear-gradient(var(--cream-2), rgba(253,231,175,0.25)); }
.monitor {
  position: absolute; left: 50%; top: 56px; width: 470px; height: 330px;
  margin-left: -235px;
  border: 3px solid var(--cream); border-radius: 14px;
  background: rgba(1,9,64,0.55);
  box-shadow: 0 0 0 1px rgba(1,9,64,0.6), 0 24px 70px rgba(1,9,64,0.6),
              inset 0 0 60px rgba(37,117,246,0.12);
}
.monitor-stand { position: absolute; left: 50%; top: 386px; width: 14px; height: 44px;
  margin-left: -7px; background: var(--cream); }
.monitor-base { position: absolute; left: 50%; top: 428px; width: 130px; height: 9px;
  margin-left: -65px; background: var(--cream); border-radius: 5px; }
.screen-title {
  font-family: var(--serif); font-size: 44px; letter-spacing: 0.16em;
  color: var(--ice); text-align: center; margin-top: 30px; line-height: 1;
}
.screen-title em { font-style: italic; color: var(--gold); }
.screen-sub {
  font-family: var(--mono); font-size: 9px; letter-spacing: 0.26em;
  text-transform: uppercase; color: var(--soft); text-align: center; margin-top: 10px;
}
.kbd { position: absolute; left: 50%; top: 420px; width: 150px; height: 10px;
  margin-left: -160px; background: var(--cream-2); border-radius: 4px; opacity: .85;
  transform: skewX(-18deg); }
.mug { position: absolute; left: 50%; top: 408px; width: 26px; height: 32px;
  margin-left: 218px; border: 3px solid var(--cream); border-radius: 3px 3px 8px 8px; }
.mug::after { content: ''; position: absolute; right: -12px; top: 6px; width: 10px;
  height: 13px; border: 3px solid var(--cream); border-radius: 0 6px 6px 0; border-left: 0; }
.steam { position: absolute; left: 50%; top: 384px; margin-left: 224px;
  font-family: var(--serif); color: var(--soft); font-size: 15px; opacity: .7;
  animation: steam 2.6s ease-in-out infinite; }
@keyframes steam { 0%,100% { transform: translateY(0); opacity:.25; }
  50% { transform: translateY(-7px); opacity:.8; } }
.tower { position: absolute; left: 50%; top: 452px; width: 52px; height: 78px;
  margin-left: 150px; border: 3px solid rgba(148,184,242,0.7); border-radius: 6px; }
.tower::before { content: ''; position: absolute; left: 9px; right: 9px; top: 10px;
  height: 3px; background: var(--gold); animation: twinkle 1.6s steps(2) infinite; }
.tower::after { content: ''; position: absolute; left: 9px; right: 9px; top: 20px;
  height: 3px; background: rgba(148,184,242,0.6); }
.sitter { position: absolute; left: 16px; top: 226px; width: 300px; height: 322px; }
.type-arm { transform-origin: 150px 120px; animation: typing 1.1s ease-in-out infinite; }
.type-arm.b { animation-delay: .55s; }
@keyframes typing { 0%,100% { transform: rotate(0deg); } 50% { transform: rotate(5deg); } }
.head-bob { transform-origin: 96px 66px; animation: bob 4s ease-in-out infinite; }
@keyframes bob { 0%,100% { transform: rotate(0deg); } 50% { transform: rotate(-3deg); } }

/* uploader pulled INSIDE the monitor screen */
div[data-testid="stFileUploader"] {
  margin-top: -388px; position: relative; z-index: 5;
  border: 1px dashed rgba(254,241,208,0.5) !important;
  background: rgba(1,13,110,0.35) !important;
}
.note { margin-top: 230px !important; }

/* ── morph: monitor collapses into the cube ── */
.ghost-monitor {
  position: absolute; left: 50%; top: 70px; width: 220px; height: 150px;
  margin-left: -110px; border: 3px solid var(--cream); border-radius: 10px;
  animation: collapse 1.5s cubic-bezier(.6,-0.1,.3,1) forwards;
}
.ghost-monitor::after { content: ''; position: absolute; left: 50%; bottom: -26px;
  width: 10px; height: 26px; margin-left: -5px; background: var(--cream); }
@keyframes collapse {
  0%   { transform: scale(1) rotate(0deg); opacity: .9; }
  70%  { transform: scale(.28) rotate(200deg); opacity: .7; }
  100% { transform: scale(.06) rotate(360deg); opacity: 0; }
}
.morph-in .cube-stage { animation: cube-arrive 1s ease-out .9s backwards; }
@keyframes cube-arrive { from { transform: scale(0) ; } to { transform: scale(1); } }

/* ── results pop-in ── */
.pop { animation: pop-in .6s cubic-bezier(.2,1.4,.4,1) backwards; }
.pop-2 { animation-delay: .15s; } .pop-3 { animation-delay: .3s; }
@keyframes pop-in { from { transform: scale(.7) translateY(16px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="logo-mark">⬡</div>
  <div class="logo-name">Data<span>Gen</span></div>
  <div class="topbar-right">District extraction engine</div>
</div>
""", unsafe_allow_html=True)


STICKERS = ["#D4C500", "#FEF1D0", "#94B8F2", "#2575F6", "#0042AF", "#EEF4FF"]


def _sticker_row(seed):
    cells = "".join(
        f'<span class="sticker" style="background:{STICKERS[(seed + c * 2) % 6]}"></span>'
        for c in range(3)
    )
    return f'<div class="sticker-row">{cells}</div>'


def _slice(pos):
    faces = "".join(
        f'<div class="slice-face sf-{f}">{_sticker_row(f + len(pos))}</div>'
        for f in range(4)
    )
    up = ""
    if pos == "top":
        up = (
            '<div class="slice-face sf-up">'
            + _sticker_row(1) + _sticker_row(3) + _sticker_row(5)
            + "</div>"
        )
    return f'<div class="slice slice-{pos}">{faces}{up}</div>'


def _cube_solver():
    person = """
    <svg class="person" viewBox="0 0 240 200" fill="none">
      <circle cx="120" cy="48" r="22" stroke="#94B8F2" stroke-width="4"/>
      <path d="M120 70 C 120 100, 118 112, 116 128" stroke="#94B8F2" stroke-width="4" stroke-linecap="round"/>
      <path d="M116 128 C 90 150, 70 156, 48 152 C 80 168, 160 168, 192 152 C 170 156, 142 150, 116 128"
        stroke="#94B8F2" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
      <path class="arm arm-l" d="M118 84 C 96 92, 84 100, 78 112" stroke="#FEF1D0" stroke-width="4" stroke-linecap="round"/>
      <path class="arm arm-r" d="M122 84 C 144 92, 156 100, 162 112" stroke="#FEF1D0" stroke-width="4" stroke-linecap="round"/>
    </svg>"""
    cube = (
        '<div class="cube-stage"><div class="cube-rotor">'
        + _slice("top") + _slice("mid") + _slice("bot")
        + "</div></div>"
    )
    return f'<div class="solver">{person}{cube}<div class="cube-shadow"></div></div>'


INTERACTIVE_CUBE = """
<style>
html,body{margin:0;background:transparent;overflow:hidden}
#wrap{width:100%;height:310px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;cursor:grab;user-select:none;-webkit-user-select:none}
#wrap:active{cursor:grabbing}
#persp{perspective:900px}
#cube{position:relative;width:150px;height:150px;transform-style:preserve-3d}
.cb{position:absolute;width:48px;height:48px;transform-style:preserve-3d}
.f{position:absolute;width:46px;height:46px;border-radius:5px;border:1px solid #010940}
#hint{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:0.24em;
  text-transform:uppercase;color:#94b8f2;margin-top:30px}
</style>
<div id="wrap">
  <div id="persp"><div id="cube"></div></div>
  <div id="hint">drag to rotate &mdash; solved</div>
</div>
<script>
const COLS={F:'#2575F6',B:'#0042AF',R:'#EEF4FF',L:'#94B8F2',U:'#D4C500',D:'#FEF1D0'};
const cube=document.getElementById('cube'),S=50;
for(let x=-1;x<=1;x++)for(let y=-1;y<=1;y++)for(let z=-1;z<=1;z++){
  const c=document.createElement('div');c.className='cb';
  c.style.transform=`translate3d(${x*S+51}px,${y*S+51}px,${z*S}px)`;
  const faces=[];
  if(z===1)faces.push(['rotateY(0deg)',COLS.F]);
  if(z===-1)faces.push(['rotateY(180deg)',COLS.B]);
  if(x===1)faces.push(['rotateY(90deg)',COLS.R]);
  if(x===-1)faces.push(['rotateY(-90deg)',COLS.L]);
  if(y===-1)faces.push(['rotateX(90deg)',COLS.U]);
  if(y===1)faces.push(['rotateX(-90deg)',COLS.D]);
  for(const[r,col]of faces){
    const f=document.createElement('div');f.className='f';
    f.style.background=col;f.style.transform=`${r} translateZ(24px)`;
    c.appendChild(f);
  }
  cube.appendChild(c);
}
let rx=-26,ry=-38,dragging=false,px=0,py=0,idle=true;
function render(){cube.style.transform=`rotateX(${rx}deg) rotateY(${ry}deg)`;}
render();
const wrap=document.getElementById('wrap');
wrap.addEventListener('pointerdown',e=>{dragging=true;idle=false;px=e.clientX;py=e.clientY;});
window.addEventListener('pointermove',e=>{
  if(!dragging)return;
  ry+=(e.clientX-px)*0.5;rx-=(e.clientY-py)*0.5;
  rx=Math.max(-90,Math.min(90,rx));
  px=e.clientX;py=e.clientY;render();
});
window.addEventListener('pointerup',()=>{dragging=false;
  setTimeout(()=>{idle=true},2500);});
(function spin(){if(idle&&!dragging){ry+=0.15;render();}requestAnimationFrame(spin);})();
</script>
"""


def scanner_html(title, msg, sub="", pct=None, morph=False):
    bar_cls = "scan-bar" if pct is not None else "scan-bar indet"
    width = f"{pct:.0f}%" if pct is not None else "35%"
    solver = _cube_solver()
    if morph:
        solver = solver.replace(
            'class="solver"', 'class="solver morph-in"'
        ).replace(
            '<div class="cube-stage">',
            '<div class="ghost-monitor"></div><div class="cube-stage">',
        )
    return f"""
    <div class="solver-box">
      <div class="scan-left">
        <div class="scan-title">{title}</div>
        <div class="scan-msg">{msg}</div>
        <div class="scan-sub">{sub}</div>
        <div class="{bar_cls}"><div style="width:{width}"></div></div>
      </div>
      {solver}
    </div>"""


# ── Stage previews (dev): ?stage=solve | ?stage=results ───────────────────────
_stage = st.query_params.get("stage")

if _stage == "solve":
    st.markdown(
        scanner_html("Solving your PDF…", "merging hierarchical headers",
                     "table 47 · page 92 · 47 / 186", pct=42, morph=True),
        unsafe_allow_html=True,
    )
    st.stop()

if _stage == "results":
    import streamlit.components.v1 as components
    L, Rcol = st.columns([1.25, 1])
    with L:
        st.markdown("""
        <div class="bpage bpage-l pop" style="border-radius:10px;border:none">
          <div class="bk-kicker">The Extraction</div>
          <div class="bk-title">Solved.</div>
          <div class="bk-sub">Every table in your report, pressed into clean pages.</div>
          <div class="bk-stats">
            <div class="bk-stat pop pop-2"><div class="v">186</div><div class="k">Tables found</div></div>
            <div class="bk-stat pop pop-2"><div class="v good">184</div><div class="k">Extracted</div></div>
            <div class="bk-stat pop pop-3"><div class="v bad">2</div><div class="k">Set aside</div></div>
            <div class="bk-stat pop pop-3"><div class="v">200</div><div class="k">Pages covered</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("↓ Download Excel", b"x", file_name="t.xlsx", use_container_width=True)
        with b2:
            st.download_button("↓ Download CSVs", b"x", file_name="t.zip", use_container_width=True)
    with Rcol:
        components.html(INTERACTIVE_CUBE, height=330)
    st.stop()

# ── Upload / hero ──────────────────────────────────────────────────────────────
uploaded = None
hero = st.empty()

SITTER_SVG = """
<svg class="sitter" viewBox="0 0 270 290" fill="none">
  <g class="head-bob">
    <circle cx="96" cy="58" r="20" stroke="#94B8F2" stroke-width="4"/>
    <path d="M108 44 C 116 36, 122 36, 128 40" stroke="#94B8F2" stroke-width="4" stroke-linecap="round"/>
  </g>
  <path d="M96 78 C 98 110, 100 128, 104 150" stroke="#94B8F2" stroke-width="4" stroke-linecap="round"/>
  <path class="type-arm" d="M100 96 C 124 104, 142 112, 158 116" stroke="#FEF1D0" stroke-width="4" stroke-linecap="round"/>
  <path class="type-arm b" d="M100 104 C 122 116, 140 124, 154 128" stroke="#FEF1D0" stroke-width="4" stroke-linecap="round"/>
  <path d="M104 150 C 126 158, 144 162, 158 164 L 158 208" stroke="#94B8F2" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M104 150 L 104 208" stroke="#94B8F2" stroke-width="4" stroke-linecap="round"/>
  <path d="M84 152 L 84 252 M 84 168 L 130 168 L 130 252" stroke="#FDE7AF" stroke-width="4" stroke-linecap="round"/>
  <path d="M66 252 L 148 252" stroke="#FDE7AF" stroke-width="4" stroke-linecap="round"/>
</svg>"""

STARS = "".join(
    f'<span class="star" style="left:{l}%;top:{t}px;animation-delay:{d}s"></span>'
    for l, t, d in [(6, 60, 0), (13, 150, 1.2), (22, 40, 2.1), (31, 110, .6),
                    (44, 30, 1.8), (58, 50, .3), (69, 120, 2.4), (78, 35, 1),
                    (87, 90, .9), (94, 170, 1.5), (50, 12, 2.7), (90, 290, 2)]
)

with hero.container():
    st.markdown(f"""
    <div class="scene">
      {STARS}
      <div class="scene-eyebrow">Government PDF → clean data</div>
      {SITTER_SVG}
      <div class="monitor">
        <div class="screen-title">Data<em>Gen</em></div>
        <div class="screen-sub">upload the data</div>
      </div>
      <div class="monitor-stand"></div>
      <div class="monitor-base"></div>
      <div class="kbd"></div>
      <div class="mug"></div><div class="steam">~</div>
      <div class="tower"></div>
      <div class="desk"></div>
      <div class="desk-leg" style="left:110px"></div>
      <div class="desk-leg" style="right:110px"></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="upl-inside">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.05, 1.1, 1.05])
    with c2:
        uploaded = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
        if uploaded is None:
            st.markdown("""
            <div class="note">
              <strong>Supported</strong> — bordered (lattice) and borderless (stream) tables:
              DES district reports, census annexures, statistical publications.<br>
              <strong>Not supported</strong> — scanned or image-only PDFs.
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
            scanner_html("Solving your PDF…", "locating tables",
                         f"{uploaded.name} · camelot lattice + stream",
                         morph=True),
            unsafe_allow_html=True,
        )

        from backend.app.extract.table_extractor import extract_tables
        tables = extract_tables(pdf_path)

        if not tables:
            stage.empty()
            st.error("No tables found in this PDF.")
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
                    "Solving your PDF…",
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
            scanner_html("Binding the book", "building excel workbook + csv bundle",
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

    # ── Results: stats left, interactive solved cube right ────────────────────
    import streamlit.components.v1 as components

    fail_cls = "bad" if failed else "good"
    pages_covered = len(table_dfs) and max(m["page"] for m in catalog)
    base = uploaded.name.replace(".pdf", "")

    L, Rcol = st.columns([1.25, 1])

    with L:
        st.markdown(f"""
        <div class="bpage bpage-l pop" style="border-radius:10px;border:none">
          <div class="bk-kicker">The Extraction</div>
          <div class="bk-title">Solved.</div>
          <div class="bk-sub">Every table in your report, pressed into clean pages.</div>
          <div class="bk-stats">
            <div class="bk-stat pop pop-2"><div class="v">{R["n_raw"]}</div><div class="k">Tables found</div></div>
            <div class="bk-stat pop pop-2"><div class="v good">{len(catalog)}</div><div class="k">Extracted</div></div>
            <div class="bk-stat pop pop-3"><div class="v {fail_cls}">{len(failed)}</div><div class="k">Set aside</div></div>
            <div class="bk-stat pop pop-3"><div class="v">{pages_covered}</div><div class="k">Pages covered</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("↓ Download Excel", R["xlsx"], file_name=f"{base}_tables.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
        with b2:
            st.download_button("↓ Download CSVs", R["zip"], file_name=f"{base}_tables.zip",
                               mime="application/zip", use_container_width=True)

    with Rcol:
        components.html(INTERACTIVE_CUBE, height=330)

    search = st.text_input("s", placeholder="Search by name or table ID…", label_visibility="collapsed")

    tab1, tab2, tab3 = st.tabs(["Index", "Preview", f"Set aside ({len(failed)})"])

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
