import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    :root{--navy:#071426;--blue:#2f80ff}.stApp{background:radial-gradient(circle at 80% 0%,#102a52 0,#071426 34%,#050d19 100%)}
    [data-testid="stSidebar"]{background:#071426;border-right:1px solid #1c3555}.block-container{max-width:1400px;padding-top:2rem}
    .brand{display:flex;align-items:center;gap:.75rem;color:#f8fbff;font-size:1.05rem;line-height:1.15;margin-bottom:.5rem}.brand div{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,#2997ff,#6c5cff);font-size:1.3rem}
    .page-header{margin-bottom:1.6rem}.page-header h1{font-size:2rem;margin:0;color:#f7fbff}.page-header p{margin:.35rem 0 0;color:#94a9c4}
    .metric-card{min-height:125px;padding:1.1rem 1.2rem;border:1px solid #24466d;border-radius:14px;background:linear-gradient(145deg,rgba(20,46,79,.95),rgba(10,27,50,.95));box-shadow:0 10px 28px rgba(0,0,0,.18)}
    .metric-card span,.metric-card small{display:block;color:#9bb0ca}.metric-card strong{display:block;margin:.35rem 0;color:#fff;font-size:1.75rem}
    .pipeline{display:flex;align-items:center;gap:.8rem;padding:.75rem;margin:.5rem 0;background:#0d203a;border:1px solid #1d3b60;border-radius:11px}.pipeline>b{display:grid;place-items:center;min-width:30px;height:30px;border-radius:50%;color:#fff;background:#247ef2}.pipeline strong,.pipeline span{display:block}.pipeline span{color:#8da2bd;font-size:.82rem}
    .notice{padding:.85rem 1rem;margin-bottom:1rem;color:#b9d4f5;background:#0d2544;border-left:3px solid #2f80ff;border-radius:7px}.status-pill{display:inline-block;padding:.3rem .65rem;margin-bottom:1rem;border-radius:999px;color:#ffcc73;background:#4b3512;font-size:.8rem;font-weight:700}
    .stButton>button,.stDownloadButton>button{border-radius:9px;font-weight:650}[data-testid="stFileUploaderDropzone"]{background:#0c203b;border:1px dashed #3d74ac;border-radius:13px}[data-testid="stDataFrame"]{border:1px solid #203c5d;border-radius:10px;overflow:hidden}
    </style>""", unsafe_allow_html=True)

def render_header(title, subtitle):
    st.markdown(f'<div class="page-header"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
