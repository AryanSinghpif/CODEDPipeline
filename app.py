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
  --gold:       #e6c35c;
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

/* ── upload hero: sleep-well first page ── */
.night {
  position: relative; width: 100%; height: 560px; margin: 0 auto;
  overflow: hidden; border-radius: 0 0 18px 18px;
}
.star { position: absolute; width: 3px; height: 3px; border-radius: 50%;
  background: var(--gold); animation: twinkle 3s ease-in-out infinite; }
@keyframes twinkle { 0%,100% { opacity: .1; } 50% { opacity: .95; } }
.aurora {
  position: absolute; left: -10%; right: -10%; top: 270px; height: 170px;
  background:
    radial-gradient(50% 90% at 30% 50%, rgba(148,184,242,0.30), transparent 70%),
    radial-gradient(45% 80% at 70% 40%, rgba(37,117,246,0.28), transparent 70%),
    radial-gradient(60% 100% at 50% 60%, rgba(238,244,255,0.14), transparent 75%);
  filter: blur(14px);
  animation: aurora-drift 9s ease-in-out infinite alternate;
}
@keyframes aurora-drift {
  from { transform: translateX(-26px) scaleY(1); }
  to   { transform: translateX(26px) scaleY(1.18); }
}
.moon-emblem {
  position: absolute; left: 50%; top: 18px; transform: translateX(-50%);
  width: 44px; height: 58px; border: 2px solid var(--cream);
  border-radius: 50% / 42%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: inset 0 0 0 3px var(--night), inset 0 0 0 4px rgba(254,241,208,0.6);
}
.moon-emblem span { color: var(--cream); font-size: 18px; line-height: 1;
  transform: rotate(-22deg); }
.night-eyebrow {
  position: absolute; top: 118px; left: 0; right: 0; text-align: center;
  font-family: var(--mono); font-size: 11px; letter-spacing: 0.3em;
  text-transform: uppercase; color: var(--ice);
}
.night-eyebrow b { color: var(--soft); font-weight: 400; padding: 0 14px; }
.night-title {
  position: absolute; top: 148px; left: 0; right: 0; text-align: center;
  font-family: var(--serif); font-weight: 400;
  font-size: 76px; letter-spacing: 0.30em; text-indent: 0.30em;
  color: var(--ice); line-height: 1.1;
  text-shadow: 0 0 40px rgba(238,244,255,0.25);
  animation: title-in 2.2s ease-out backwards;
}
@keyframes title-in { from { opacity: 0; letter-spacing: 0.5em; }
  to { opacity: 1; letter-spacing: 0.30em; } }
.night-title em { font-style: italic; color: var(--gold); }
.dunes { position: absolute; left: 0; right: 0; bottom: 0; height: 240px; }
.dunes svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.figure {
  position: absolute; left: 50%; bottom: 116px; width: 46px; height: 110px;
  transform: translateX(-50%);
}
.scroll-hint {
  position: absolute; left: 0; right: 0; bottom: 14px; text-align: center;
  font-family: var(--sans); font-size: 12px; color: var(--blue);
  letter-spacing: 0.02em;
}
.grain { position: absolute; inset: 0; opacity: 0.5; pointer-events: none;
  mix-blend-mode: overlay; }

/* uploader floats over the night scene, under the title */
div[data-testid="stFileUploader"] {
  margin-top: -270px; position: relative; z-index: 6;
  border: 1px dashed rgba(254,241,208,0.55) !important;
  background: rgba(1,9,64,0.55) !important;
  backdrop-filter: blur(3px);
}
.note { margin-top: 140px !important; border-top: none !important;
  text-align: center; }

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


STICKERS = ["#E6C35C", "#FEF1D0", "#94B8F2", "#2575F6", "#0042AF", "#EEF4FF"]


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


HERO_GSAP = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Space+Mono&display=swap');
html,body{margin:0;overflow:hidden;height:100%;
  background:radial-gradient(120% 100% at 50% 0%,#002e77 0%,#010d6e 55%,#010940 100%)}
#sky{position:absolute;inset:0;overflow:hidden}
.s{position:absolute;border-radius:50%;background:#fef1d0;
  box-shadow:0 0 6px rgba(254,241,208,.9)}
.s.g{background:#e6c35c;box-shadow:0 0 8px rgba(230,195,92,.9)}
.ov{position:absolute;left:0;right:0;text-align:center;pointer-events:none;z-index:2}
#eye{top:96px;font-family:'Space Mono',monospace;font-size:11px;
  letter-spacing:.3em;text-transform:uppercase;color:#eef4ff}
#eye b{color:#94b8f2;font-weight:400;padding:0 12px}
#title{top:126px;font-family:'Instrument Serif',Georgia,serif;font-size:60px;
  color:#eef4ff;letter-spacing:.22em;text-indent:.22em;
  text-shadow:0 0 50px rgba(238,244,255,.3)}
#tsub{top:206px;font-family:'Instrument Serif',Georgia,serif;font-style:italic;
  font-size:19px;color:#94b8f2;letter-spacing:.02em}
#title em{font-style:italic;color:#e6c35c}
#hint{bottom:16px;font-family:'Space Mono',monospace;font-size:10px;
  letter-spacing:.2em;color:#2575f6;text-transform:uppercase}
</style>
<div id="sky"></div>
<div class="ov" id="eye"><b>&#9679;</b>GOVERNMENT PDF &rarr; CLEAN DATA<b>&#9679;</b></div>
<div class="ov" id="title">DATA<em>GEN</em></div>
<div class="ov" id="tsub">Every table in your report &mdash; solved, page by page.</div>
<div class="ov" id="hint">&#8964; drop a pdf to begin</div>
__GSAP_JS__
<script>
const sky=document.getElementById('sky'),W=innerWidth,H=560;
for(let i=0;i<70;i++){
  const s=document.createElement('div');
  s.className='s'+(Math.random()<.4?' g':'');
  const sz=1.5+Math.random()*2.5;
  s.style.width=s.style.height=sz+'px';
  s.style.left=Math.random()*100+'%';
  s.style.top='-20px';
  sky.appendChild(s);
  gsap.to(s,{y:H+60,x:'+='+(Math.random()*80-40),duration:3+Math.random()*6,
    delay:Math.random()*8,repeat:-1,ease:'none'});
  gsap.to(s,{opacity:.15+Math.random()*.3,duration:.6+Math.random(),
    repeat:-1,yoyo:true,ease:'sine.inOut'});
}
gsap.from('#title',{opacity:0,letterSpacing:'.4em',duration:2.2,ease:'power3.out'});
gsap.from('#tsub',{opacity:0,y:10,duration:1.6,delay:.7,ease:'power2.out'});
gsap.from('#eye',{opacity:0,y:-12,duration:1.4,delay:.4,ease:'power2.out'});
gsap.to('#eye b',{opacity:.15,duration:1,repeat:-1,yoyo:true,ease:'sine.inOut'});
gsap.to('#hint',{y:5,duration:1.1,repeat:-1,yoyo:true,ease:'sine.inOut'});
</script>
"""

INTERACTIVE_CUBE = """
<style>
html,body{margin:0;background:transparent;overflow:hidden}
#wrap{width:100%;height:310px;display:flex;flex-direction:column;align-items:center;
  justify-content:center;cursor:grab;user-select:none;-webkit-user-select:none}
#wrap:active{cursor:grabbing}
#persp{perspective:900px}
#cube{position:relative;width:150px;height:150px;transform-style:preserve-3d}
.cb{position:absolute;width:48px;height:48px;transform-style:preserve-3d}
.f{position:absolute;width:46px;height:46px;border-radius:5px;border:1px solid #010d6e}
#hint{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:0.24em;
  text-transform:uppercase;color:#94b8f2;margin-top:30px}
</style>
<div id="wrap">
  <div id="persp"><div id="cube"></div></div>
  <div id="hint">drag to rotate &mdash; solved</div>
</div>
<script>
const COLS={F:'#2575F6',B:'#0042AF',R:'#EEF4FF',L:'#94B8F2',U:'#E6C35C',D:'#FEF1D0'};
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

STARS = "".join(
    f'<span class="star" style="left:{l}%;top:{t}px;animation-delay:{d}s;'
    f'width:{s}px;height:{s}px"></span>'
    for l, t, d, s in [(5, 70, 0, 3), (11, 160, 1.2, 2), (17, 45, 2.1, 3),
                       (24, 120, .6, 2), (31, 60, 1.8, 3), (38, 170, .3, 2),
                       (45, 40, 2.4, 2), (52, 100, 1, 3), (59, 55, .9, 2),
                       (66, 150, 1.5, 3), (73, 70, 2.7, 2), (80, 130, 2, 3),
                       (87, 50, .4, 2), (93, 110, 1.7, 3), (97, 200, .8, 2),
                       (8, 260, 2.3, 2), (90, 270, 1.1, 2), (50, 15, 2.9, 2)]
)

DUNES_SVG = """
<svg viewBox="0 0 1400 240" preserveAspectRatio="none" fill="none">
  <path d="M0 150 C 180 90, 320 90, 470 140 C 600 183, 800 183, 930 140
           C 1080 90, 1220 90, 1400 150 L 1400 240 L 0 240 Z" fill="#0A0A14"/>
  <path d="M0 168 C 200 116, 360 112, 520 156 C 660 194, 760 194, 890 156
           C 1050 112, 1210 116, 1400 168 L 1400 240 L 0 240 Z" fill="#F3EBD8"/>
  <path d="M60 200 C 130 184, 210 184, 280 202 C 220 214, 130 214, 60 200 Z" fill="#0A0A14"/>
  <path d="M420 214 C 500 196, 600 196, 690 212 C 600 228, 490 228, 420 214 Z" fill="#0A0A14"/>
  <path d="M860 204 C 940 188, 1030 188, 1110 204 C 1030 220, 930 220, 860 204 Z" fill="#0A0A14"/>
  <path d="M1180 196 C 1240 184, 1310 186, 1360 198 C 1300 210, 1230 208, 1180 196 Z" fill="#0A0A14"/>
  <path d="M0 226 C 300 208, 1100 208, 1400 226 L 1400 240 L 0 240 Z" fill="#E9DFC6"/>
</svg>"""

FIGURE_SVG = """
<svg class="figure" viewBox="0 0 46 110" fill="none">
  <circle cx="23" cy="10" r="8" fill="#0A0A14"/>
  <path d="M23 16 C 12 22, 10 52, 13 78 L 33 78 C 36 52, 34 22, 23 16 Z" fill="#0A0A14"/>
  <path d="M16 78 L 16 102 M 30 78 L 30 102" stroke="#0A0A14" stroke-width="5" stroke-linecap="round"/>
  <path d="M14 30 C 10 42, 10 54, 12 64 M 32 30 C 36 42, 36 54, 34 64"
    stroke="#0A0A14" stroke-width="4" stroke-linecap="round"/>
</svg>"""

GRAIN_SVG = """
<svg class="grain" width="100%" height="100%">
  <filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2"/>
  <feColorMatrix type="saturate" values="0"/><feComponentTransfer>
  <feFuncA type="linear" slope="0.10"/></feComponentTransfer></filter>
  <rect width="100%" height="100%" filter="url(#g)"/>
</svg>"""

def _gsap_tag():
    from pathlib import Path as _P
    local = _P(__file__).parent / "static" / "gsap.min.js"
    if local.exists():
        return "<script>" + local.read_text() + "</script>"
    return ('<script src="https://cdnjs.cloudflare.com/ajax/libs/'
            'gsap/3.12.5/gsap.min.js"></script>')


with hero.container():
    import streamlit.components.v1 as components
    components.html(HERO_GSAP.replace("__GSAP_JS__", _gsap_tag()), height=560)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    with c2:
        uploaded = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
        if uploaded is None:
            st.markdown("""
            <div class="note">
              <strong>Supported</strong> — bordered (lattice) and borderless (stream) tables:
              DES district reports, census annexures, statistical publications.
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
