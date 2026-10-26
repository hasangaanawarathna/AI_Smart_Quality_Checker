import html

import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
        :root{--ink:#eaf2ff;--muted:#8fa3bd;--line:rgba(132,166,207,.16);--cyan:#38d9c5;--blue:#4f8cff}
        html,body,[class*="css"]{font-family:"DM Sans",sans-serif}h1,h2,h3,.brand strong{font-family:"Manrope",sans-serif!important}
        .stApp{background:radial-gradient(circle at 76% -10%,rgba(48,113,221,.24),transparent 32rem),radial-gradient(circle at 15% 90%,rgba(27,190,170,.08),transparent 30rem),#07111f;color:var(--ink)}
        [data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"]{background:rgba(6,17,31,.96);border-right:1px solid var(--line)}
        [data-testid="stSidebar"] [data-testid="stRadio"] label{padding:.66rem .72rem;margin:.12rem 0;border-radius:10px;transition:background .18s ease}[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(79,140,255,.09)}
        .block-container{max-width:1380px;padding:2.3rem 2.4rem 4rem}.brand{display:flex;align-items:center;gap:.8rem;color:#f7fbff;margin:.25rem 0}
        .brand-mark{display:grid;place-items:center;width:42px;height:42px;flex:0 0 42px;border-radius:13px;background:linear-gradient(135deg,var(--cyan),var(--blue));box-shadow:0 8px 24px rgba(65,148,255,.24);color:#05131f;font-weight:900}.brand strong{font-size:1rem;line-height:1.15;letter-spacing:-.02em}
        .eyebrow{color:var(--cyan);font-size:.73rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.page-header{margin:.15rem 0 1.65rem}.page-header h1{margin:.32rem 0 .35rem;color:#f6f9ff;font-size:clamp(1.9rem,3vw,2.65rem);letter-spacing:-.045em}.page-header p{margin:0;color:var(--muted);font-size:1rem}
        .hero{position:relative;overflow:hidden;padding:1.6rem 1.75rem;margin-bottom:1.25rem;border:1px solid rgba(91,151,255,.24);border-radius:18px;background:linear-gradient(120deg,rgba(20,52,91,.96),rgba(11,29,52,.9));box-shadow:0 20px 50px rgba(0,0,0,.19)}.hero:after{content:"";position:absolute;right:-4rem;top:-7rem;width:18rem;height:18rem;border-radius:50%;background:rgba(56,217,197,.08)}.hero h2{margin:.35rem 0;font-size:1.42rem;color:#fff}.hero p{max-width:690px;margin:0;color:#adc0d8}
        .metric-card{min-height:128px;padding:1.05rem 1.15rem;border:1px solid var(--line);border-radius:15px;background:linear-gradient(145deg,rgba(18,42,72,.88),rgba(10,27,48,.9));box-shadow:0 12px 32px rgba(0,0,0,.14);transition:transform .18s ease,border-color .18s ease}.metric-card:hover{transform:translateY(-2px);border-color:rgba(79,140,255,.38)}.metric-card span,.metric-card small{display:block;color:var(--muted)}.metric-card span{font-size:.86rem;font-weight:600}.metric-card strong{display:block;margin:.35rem 0 .25rem;color:#fff;font-family:"Manrope";font-size:1.9rem}.metric-card small{font-size:.76rem}
        .pipeline{display:flex;align-items:center;gap:.85rem;padding:.78rem;margin:.55rem 0;background:rgba(12,31,55,.76);border:1px solid var(--line);border-radius:12px}.pipeline>b{display:grid;place-items:center;min-width:32px;height:32px;border-radius:10px;color:#07111f;background:linear-gradient(135deg,var(--cyan),#74eddf)}.pipeline strong,.pipeline span{display:block}.pipeline strong{color:#eaf2ff;font-size:.9rem}.pipeline span{color:var(--muted);font-size:.77rem}
        .notice{padding:.9rem 1rem;margin-bottom:1rem;color:#c7ddf7;background:rgba(30,71,116,.32);border:1px solid rgba(72,139,218,.24);border-radius:11px}.status-pill{display:inline-block;padding:.32rem .68rem;margin-bottom:1rem;border-radius:999px;color:#ffd483;background:rgba(161,106,20,.22);border:1px solid rgba(255,190,75,.25);font-size:.76rem;font-weight:700}
        .empty-state{padding:1.3rem;text-align:center;border:1px dashed rgba(128,160,200,.27);border-radius:13px;color:var(--muted);background:rgba(9,25,45,.42)}.empty-state b{display:block;margin-bottom:.25rem;color:#dce8f7}.section-label{margin:1.35rem 0 .65rem;color:#eaf2ff;font:700 1.02rem "Manrope"}
        .stButton>button,.stDownloadButton>button{min-height:2.75rem;border-radius:10px;font-weight:700}[data-testid="stFileUploaderDropzone"]{padding:1.5rem;background:rgba(11,33,58,.72);border:1px dashed rgba(80,157,224,.52);border-radius:14px}[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;overflow:hidden}[data-testid="stMetric"]{padding:1rem;border:1px solid var(--line);border-radius:12px;background:rgba(13,31,54,.7)}[data-baseweb="tab-list"]{gap:.35rem}[data-baseweb="tab"]{border-radius:9px 9px 0 0;padding-left:1rem;padding-right:1rem}hr{border-color:var(--line)!important}
        @media(max-width:700px){.block-container{padding:1.3rem 1rem 3rem}.hero{padding:1.25rem}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title, subtitle, eyebrow="QUALITY OPERATIONS"):
    st.markdown(
        f'<div class="page-header"><div class="eyebrow">{html.escape(eyebrow)}</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def render_empty(title, message):
    st.markdown(
        f'<div class="empty-state"><b>{html.escape(title)}</b>{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )
