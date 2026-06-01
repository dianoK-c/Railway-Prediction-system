"""
app.py  -  RailTrack  (with Authentication)
Design: Warm editorial, industrial precision
Fonts:  DM Serif Display + DM Sans + DM Mono
Colors: Cream #F7F3EE, Charcoal #1C1917, Amber #D97706, Blue #3B5BDB
Run:  streamlit run app.py
"""

import datetime, time, sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from stations import STATIONS, station_names, get_station
from distance import distance_between, bearing
from eta import physics_eta_minutes, compute_arrival_time, compute_delay_minutes
from ml_model import predict_eta, train_model, append_history
from simulation import simulate_journey

# ── NEW: import the auth module ────────────────────────────────────────────────
from auth import require_auth, show_user_pill, save_journey, AUTH_CSS, logout_user

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the very first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="RailTrack", page_icon="🚂",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  (original RailTrack styles — unchanged)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=DM+Mono:wght@400;500&display=swap');
*::before,*::after{box-sizing:border-box}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;background:#F7F3EE!important;color:#1C1917}
.main .block-container{padding:0 2.5rem 4rem!important;max-width:1200px}
[data-testid="stSidebar"]{background:#1C1917!important;border-right:none!important}
[data-testid="stSidebar"]>div:first-child{padding-top:0!important}
[data-testid="stSidebar"]{color:#E7E5E4!important;font-family:'DM Sans',sans-serif!important}
[data-testid="stSidebar"] .stSelectbox>div>div,[data-testid="stSidebar"] .stNumberInput>div>div>input,[data-testid="stSidebar"] .stTextInput>div>div>input{background:#292524!important;border:1px solid #44403C!important;color:#E7E5E4!important;border-radius:6px!important}
[data-testid="stSidebar"] label{color:#A8A29E!important;font-size:.71rem!important;font-weight:600!important;letter-spacing:.09em!important;text-transform:uppercase!important}
h1,h2,h3{font-family:'DM Serif Display',serif!important;color:#1C1917!important}
.rt-topbar{background:#1C1917;margin:0 -2.5rem 0 -2.5rem;padding:1rem 2.5rem;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #D97706;margin-bottom:2rem}
.rt-brand{display:flex;align-items:baseline;gap:.7rem}
.rt-logo{font-family:'DM Serif Display',serif;font-size:1.5rem;color:#FAFAF9;letter-spacing:-.01em}
.rt-badge{font-size:.6rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#D97706;background:rgba(217,119,6,.12);border:1px solid rgba(217,119,6,.3);padding:2px 8px;border-radius:4px}
.rt-route{font-family:'DM Mono',monospace;font-size:.76rem;color:#78716C;letter-spacing:.04em}
.rt-clock{font-family:'DM Mono',monospace;font-size:.76rem;color:#57534E}
.rt-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.8rem}
.rt-stat{background:#fff;border:1px solid #E7E5E4;border-radius:10px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;transition:box-shadow .2s}
.rt-stat::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--c,#3B5BDB)}
.rt-stat:hover{box-shadow:0 4px 20px rgba(28,25,23,.07)}
.rt-stat-label{font-size:.66rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#78716C;margin-bottom:.5rem}
.rt-stat-val{font-family:'DM Serif Display',serif;font-size:2rem;color:#1C1917;line-height:1}
.rt-stat-sub{font-size:.73rem;color:#A8A29E;margin-top:.25rem}
.rt-result{background:#1C1917;border-radius:14px;padding:2rem 2.2rem;position:relative;overflow:hidden}
.rt-result::after{content:'';position:absolute;bottom:-50px;right:-50px;width:200px;height:200px;background:radial-gradient(circle,rgba(217,119,6,.18) 0%,transparent 70%);border-radius:50%;pointer-events:none}
.rt-result-route{font-family:'DM Mono',monospace;font-size:.7rem;color:#57534E;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem}
.rt-result-time{font-family:'DM Serif Display',serif;font-size:3.8rem;color:#FAFAF9;line-height:1;letter-spacing:-.02em;margin-bottom:.35rem}
.rt-result-sub{font-size:.85rem;color:#78716C;margin-bottom:1.2rem}
.rt-result-row{display:flex;align-items:center;gap:.75rem;flex-wrap:wrap}
.rt-detail{font-size:.8rem;color:#57534E}
.badge{display:inline-flex;align-items:center;gap:.3rem;padding:.28rem .8rem;border-radius:100px;font-size:.69rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase}
.badge-on-time{background:#ECFDF5;color:#059669;border:1.5px solid #A7F3D0}
.badge-delayed{background:#FEF2F2;color:#DC2626;border:1.5px solid #FECACA}
.badge-early{background:#EFF6FF;color:#3B5BDB;border:1.5px solid #BFDBFE}
.rt-sched{background:#fff;border:1px solid #E7E5E4;border-radius:14px;padding:1.4rem 1.6rem;height:100%}
.rt-sched-title{font-size:.66rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#78716C;margin-bottom:.9rem;padding-bottom:.6rem;border-bottom:1px solid #F5F5F4}
.rt-sched-row{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;font-size:.85rem;border-bottom:1px solid #F5F5F4}
.rt-sched-row:last-child{border-bottom:none}
.rt-sched-k{color:#78716C}
.rt-sched-v{font-family:'DM Mono',monospace;font-weight:500;color:#1C1917;font-size:.8rem}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:2px solid #E7E5E4!important;gap:0!important;padding-bottom:0!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;border:none!important;border-bottom:2px solid transparent!important;border-radius:0!important;color:#78716C!important;font-family:'DM Sans',sans-serif!important;font-size:.84rem!important;font-weight:500!important;padding:.55rem 1.2rem!important;margin-bottom:-2px!important}
.stTabs [data-baseweb="tab"]:hover{color:#1C1917!important}
.stTabs [aria-selected="true"]{color:#1C1917!important;border-bottom-color:#D97706!important;font-weight:600!important}
[data-testid="stTabsContent"]{padding-top:1.8rem!important}
.rt-sect{font-family:'DM Serif Display',serif;font-size:1.2rem;color:#1C1917;margin-bottom:.8rem;display:flex;align-items:center;gap:.7rem}
.rt-sect-line{flex:1;height:1px;background:#E7E5E4}
.stButton>button{background:#1C1917!important;color:#FAFAF9!important;border:none!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-size:.84rem!important;font-weight:600!important;padding:.58rem 1.5rem!important;transition:all .18s!important}
.stButton>button:hover{background:#292524!important;transform:translateY(-1px)!important;box-shadow:0 4px 14px rgba(28,25,23,.2)!important}
[data-testid="stSidebar"] .stButton>button{background:#D97706!important}
[data-testid="stSidebar"] .stButton>button:hover{background:#B45309!important}
[data-testid="metric-container"]{background:#fff!important;border:1px solid #E7E5E4!important;border-radius:10px!important;padding:1.1rem 1.4rem!important;box-shadow:none!important}
[data-testid="stMetricLabel"]{font-size:.66rem!important;font-weight:600!important;letter-spacing:.1em!important;text-transform:uppercase!important;color:#78716C!important}
[data-testid="stMetricValue"]{font-family:'DM Serif Display',serif!important;font-size:1.9rem!important;color:#1C1917!important}
.stProgress>div>div{background:#D97706!important;border-radius:100px!important}
.stProgress>div{background:#F5F5F4!important;border-radius:100px!important;height:5px!important}
.rt-sim-box{background:#fff;border:1px solid #E7E5E4;border-radius:10px;padding:1.1rem 1.4rem;font-family:'DM Mono',monospace;font-size:.8rem;color:#44403C;line-height:1.8}
.rt-sim-box strong{color:#1C1917}
.rt-amber{color:#D97706;font-weight:600}
[data-testid="stSidebar"] input {color: white !important;background-color: #2b2b2b !important;}
[data-testid="stSidebar"] .stNumberInput input {color: white !important;}
.rt-info{background:#FFFBEB;border:1px solid #FDE68A;border-left:3px solid #D97706;border-radius:8px;padding:.9rem 1.1rem;font-size:.85rem;color:#78350F;margin:.8rem 0}
.rt-info-blue{background:#EFF6FF;border:1px solid #BFDBFE;border-left:3px solid #3B5BDB;border-radius:8px;padding:.9rem 1.1rem;font-size:.83rem;color:#1E3A5F;margin:.6rem 0}
.rt-success{background:#ECFDF5;border:1px solid #A7F3D0;border-left:3px solid #059669;border-radius:8px;padding:.9rem 1.1rem;font-size:.85rem;color:#065F46;margin:.8rem 0}
.rt-model-card{background:#fff;border:1px solid #E7E5E4;border-radius:12px;padding:1.4rem}
.rt-model-row{display:flex;justify-content:space-between;align-items:center;padding:.42rem 0;font-size:.84rem;border-bottom:1px solid #F5F5F4}
.rt-model-row:last-child{border-bottom:none}
.rt-model-k{color:#78716C}
.rt-model-v{font-family:'DM Mono',monospace;font-weight:500;font-size:.79rem;color:#1C1917}
.rt-code{background:#1C1917;color:#A8A29E;border-radius:8px;padding:1rem 1.2rem;font-family:'DM Mono',monospace;font-size:.78rem;line-height:1.8;margin:.6rem 0}
.kw{color:#D97706}.num{color:#93C5FD}.cm{color:#57534E}
.sb-head{background:#111110;margin:-1rem -1rem 1.2rem;padding:1.5rem 1.2rem 1.1rem;border-bottom:1px solid #292524}
.sb-logo{font-family:'DM Serif Display',serif;font-size:1.35rem;color:#FAFAF9}
.sb-tag{font-size:.66rem;color:#57534E;letter-spacing:.07em;text-transform:uppercase;margin-top:.2rem}
.sb-pill{display:inline-block;background:rgba(217,119,6,.14);border:1px solid rgba(217,119,6,.28);color:#D97706;font-size:.62rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;padding:2px 8px;border-radius:100px;margin-top:.5rem}
.sb-sect{font-size:.62rem!important;font-weight:700!important;letter-spacing:.15em!important;text-transform:uppercase!important;color:#57534E!important;margin:1.1rem 0 .5rem!important;padding-bottom:.35rem!important;border-bottom:1px solid #292524!important;display:block}

/* ── NEW: user pill in top-bar ── */
.user-pill{display:inline-flex;align-items:center;gap:.45rem;background:rgba(217,119,6,.1);border:1px solid rgba(217,119,6,.28);border-radius:100px;padding:.28rem .85rem;font-size:.72rem;font-weight:600;color:#D97706;letter-spacing:.05em}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── NEW: Inject auth CSS + authentication gate ─────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(AUTH_CSS, unsafe_allow_html=True)

# If the user is not logged in, show the login/register page and stop here.
# Nothing below this point renders until the user is authenticated.
if not require_auth():
    st.stop()

# Shortcut to the current logged-in user's data
current_user = st.session_state["user"]   # dict: name, phone, joined, journey_history

# ══════════════════════════════════════════════════════════════════════════════
# TRAIN PRESETS  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
TRAIN_PRESETS = {
    "12951 - Mumbai Rajdhani":  {"speed": 130, "origin": "Mumbai CST",      "dest": "New Delhi"},
    "12009 - Shatabdi Express": {"speed": 150, "origin": "Mumbai Dadar",     "dest": "Pune Junction"},
    "22222 - Duronto Express":  {"speed": 140, "origin": "Kolkata Howrah",   "dest": "New Delhi"},
    "12658 - Chennai Mail":     {"speed": 110, "origin": "Chennai Central",  "dest": "Bangalore City"},
    "12724 - AP Express":       {"speed": 100, "origin": "Hyderabad Deccan", "dest": "Visakhapatnam"},
    "Custom Train":             {"speed":  80, "origin": "Mumbai CST",       "dest": "Pune Junction"},
}

def fmt_eta(minutes):
    if minutes == float("inf"): return "inf"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m" if h else f"{m} min"

def status_badge(delay_min):
    if delay_min > 5:    return f'<span class="badge badge-delayed">Delayed +{delay_min:.0f} min</span>'
    elif delay_min < -2: return f'<span class="badge badge-early">Early {abs(delay_min):.0f} min</span>'
    return '<span class="badge badge-on-time">On Time</span>'

@st.cache_resource(show_spinner="Loading model...")
def get_model_metrics(): return train_model()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  (unchanged except for the logout button at the bottom)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('''<div class="sb-head"><div class="sb-logo">RailTrack</div><div class="sb-tag">ETA Prediction System</div><div class="sb-pill">ML Powered</div></div>''', unsafe_allow_html=True)
    st.markdown('<span class="sb-sect">Train</span>', unsafe_allow_html=True)
    preset_name = st.selectbox("Preset", list(TRAIN_PRESETS.keys()), index=0, label_visibility="collapsed")
    preset = TRAIN_PRESETS[preset_name]
    train_id = st.text_input("Train ID", value="MY-TRAIN-001") if preset_name == "Custom Train" else preset_name.split("-")[0].strip()
    st.markdown('<span class="sb-sect">Current Position</span>', unsafe_allow_html=True)
    origin_choice = st.selectbox("Departed from", station_names(), index=station_names().index(preset["origin"]))
    origin_data = get_station(origin_choice)
    c1, c2 = st.columns(2)
    cur_lat = c1.number_input("Lat", value=float(origin_data["lat"]), format="%.4f")
    cur_lon = c2.number_input("Lon", value=float(origin_data["lon"]), format="%.4f")
    speed = st.slider("Speed (km/h)", 0, 350, int(preset["speed"]), step=5)
    st.markdown('<span class="sb-sect">Destination</span>', unsafe_allow_html=True)
    dest_choice = st.selectbox("Next station", station_names(), index=station_names().index(preset["dest"]))
    dest_data = get_station(dest_choice)
    scheduled_str = st.text_input("Scheduled arrival", value=(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%H:%M"))
    delay_input = st.number_input("Known delay (min)", -30.0, 120.0, 0.0, step=1.0)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Calculate ETA", use_container_width=True)

    # ── NEW: show who is logged in + logout button ─────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="sb-sect">Logged in as</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:#1a1917;border:1px solid #292524;border-radius:8px;'
        f'padding:.7rem 1rem;font-size:.8rem;color:#D97706;font-family:\'DM Mono\',monospace;">'
        f'👤 {current_user["name"]}<br>'
        f'<span style="color:#57534E;font-size:.7rem;">{current_user["phone"]}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(" Logout", use_container_width=True, key="sidebar_logout"):
        logout_user()
        st.rerun()
    # ── end NEW ────────────────────────────────────────────────────────────

    st.markdown(f'''<div style="margin-top:1.2rem;padding:.8rem;background:#111110;border-radius:8px;font-size:.67rem;color:#44403C;line-height:1.7;"><span style="color:#57534E;font-size:.61rem;letter-spacing:.1em;text-transform:uppercase;font-weight:600;">System</span><br>Algorithm: Linear Regression<br>Features: dist, speed, delay<br>Stations: {len(STATIONS)} registered</div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPUTED VALUES  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
dist_km   = distance_between((cur_lat, cur_lon), (dest_data["lat"], dest_data["lon"]))
phys_eta  = physics_eta_minutes(dist_km, speed)
ml_eta    = predict_eta(dist_km, speed, delay_input)
avg_eta   = (phys_eta + ml_eta) / 2 if phys_eta != float("inf") else ml_eta
now        = datetime.datetime.now()
arrival_dt = compute_arrival_time(avg_eta, now)
try:
    h_s, m_s = map(int, scheduled_str.split(":"))
    sched_dt = now.replace(hour=h_s, minute=m_s, second=0, microsecond=0)
    if sched_dt < now: sched_dt += datetime.timedelta(days=1)
    delay_computed = compute_delay_minutes(sched_dt, arrival_dt)
except Exception:
    sched_dt = None; delay_computed = delay_input
train_bearing = bearing(cur_lat, cur_lon, dest_data["lat"], dest_data["lon"])

# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR  — now shows the logged-in user's name on the right
# ══════════════════════════════════════════════════════════════════════════════
top_left, top_right = st.columns([4, 1])

with top_left:
    st.markdown(f'''
    <div class="rt-topbar">
        <div class="rt-brand">
            <span class="rt-logo">RailTrack</span>
            <span class="rt-badge">ETA Engine</span>
            <span class="rt-route">{origin_choice.split()[0]} to {dest_choice.split()[0]}</span>
        </div>
        <div class="rt-clock">
            Train {train_id} &middot; {now.strftime('%d %b %Y, %H:%M')}
            &nbsp;&nbsp;
            <span class="user-pill">👤 {current_user["name"]}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS  (original content — unchanged except tab_hist which now also
#             calls save_journey() to write to users.json)
# ══════════════════════════════════════════════════════════════════════════════
tab_pred, tab_sim, tab_map, tab_hist, tab_ml = st.tabs(
    ["Prediction", "Live Simulation", "Route Map", "History", "Model"]
)

# ── Tab: Prediction ────────────────────────────────────────────────────────────
with tab_pred:
    delay_color = "#DC2626" if delay_computed > 5 else ("#059669" if delay_computed < -2 else "#D97706")
    delay_sign  = f"+{delay_computed:.0f}" if delay_computed > 0 else f"{delay_computed:.0f}"
    st.markdown(f'''<div class="rt-stats">
        <div class="rt-stat" style="--c:#3B5BDB"><div class="rt-stat-label">Distance Remaining</div><div class="rt-stat-val">{dist_km:.1f}</div><div class="rt-stat-sub">kilometres</div></div>
        <div class="rt-stat" style="--c:#D97706"><div class="rt-stat-label">Current Speed</div><div class="rt-stat-val">{speed}</div><div class="rt-stat-sub">km per hour</div></div>
        <div class="rt-stat" style="--c:#78716C"><div class="rt-stat-label">Physics ETA</div><div class="rt-stat-val">{fmt_eta(phys_eta)}</div><div class="rt-stat-sub">kinematics baseline</div></div>
        <div class="rt-stat" style="--c:#059669"><div class="rt-stat-label">ML-Enhanced ETA</div><div class="rt-stat-val">{fmt_eta(ml_eta)}</div><div class="rt-stat-sub">model prediction</div></div>
    </div>''', unsafe_allow_html=True)
    col_r, col_s = st.columns([3, 2], gap="medium")
    with col_r:
        sched_show = sched_dt.strftime('%H:%M') if sched_dt else "--"
        st.markdown(f'''<div class="rt-result">
            <div class="rt-result-route">{origin_choice} &rarr; {dest_choice}</div>
            <div class="rt-result-time">{arrival_dt.strftime('%H:%M')}</div>
            <div class="rt-result-sub">Predicted arrival &middot; {arrival_dt.strftime('%d %b %Y')} &middot; ETA {fmt_eta(avg_eta)}</div>
            <div class="rt-result-row">{status_badge(delay_computed)}<span class="rt-detail">Bearing {train_bearing:.0f}&deg;</span><span class="rt-detail">&middot;</span><span class="rt-detail">Physics + ML averaged</span></div>
        </div>''', unsafe_allow_html=True)
    with col_s:
        st.markdown(f'''<div class="rt-sched">
            <div class="rt-sched-title">Schedule</div>
            <div class="rt-sched-row"><span class="rt-sched-k">Scheduled</span><span class="rt-sched-v">{sched_show}</span></div>
            <div class="rt-sched-row"><span class="rt-sched-k">Predicted</span><span class="rt-sched-v">{arrival_dt.strftime('%H:%M')}</span></div>
            <div class="rt-sched-row"><span class="rt-sched-k">Variance</span><span class="rt-sched-v" style="color:{delay_color}">{delay_sign} min</span></div>
            <div class="rt-sched-row"><span class="rt-sched-k">Now</span><span class="rt-sched-v">{now.strftime('%H:%M:%S')}</span></div>
            <div class="rt-sched-row"><span class="rt-sched-k">Known delay</span><span class="rt-sched-v">{delay_input:+.0f} min</span></div>
        </div>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="rt-sect">Speed Sensitivity <div class="rt-sect-line"></div></div><p style="font-size:.82rem;color:#78716C;margin-bottom:1rem;">How would ETA change at different speeds?</p>', unsafe_allow_html=True)
    speeds_r = np.linspace(max(10, speed * 0.4), min(350, speed * 1.65), 90)
    etas_p   = [physics_eta_minutes(dist_km, s) for s in speeds_r]
    etas_m   = [predict_eta(dist_km, s, delay_input) for s in speeds_r]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=speeds_r, y=etas_p, name="Physics ETA", line=dict(color="#3B5BDB", width=2.5), fill="tozeroy", fillcolor="rgba(59,91,219,0.06)"))
    fig.add_trace(go.Scatter(x=speeds_r, y=etas_m, name="ML ETA", line=dict(color="#D97706", width=2.5, dash="dot")))
    fig.add_vline(x=speed, line_color="#1C1917", line_dash="dash", line_width=1.5, annotation_text=f"  {speed} km/h", annotation_font=dict(color="#1C1917", size=11, family="DM Mono"))
    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFAF9", font=dict(family="DM Sans", color="#44403C", size=11),
        legend=dict(bgcolor="rgba(255,255,255,.9)", bordercolor="#E7E5E4", borderwidth=1, font=dict(size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Speed (km/h)", gridcolor="#F5F5F4", linecolor="#E7E5E4", tickfont=dict(family="DM Mono", size=10)),
        yaxis=dict(title="ETA (minutes)", gridcolor="#F5F5F4", linecolor="#E7E5E4", tickfont=dict(family="DM Mono", size=10)),
        margin=dict(l=10,r=10,t=40,b=10), height=300)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Tab: Live Simulation ───────────────────────────────────────────────────────
with tab_sim:
    st.markdown('<div class="rt-sect">Journey Simulation <div class="rt-sect-line"></div></div><p style="font-size:.82rem;color:#78716C;margin-bottom:1.2rem;">Watch the train move step-by-step with live ETA updates.</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    sim_steps = c1.slider("Simulation steps", 10, 50, 20)
    tick_ms   = c2.slider("Tick speed (ms)", 100, 1500, 600)
    if st.button("Start Simulation", use_container_width=True):
        snaps = simulate_journey(origin_lat=origin_data["lat"], origin_lon=origin_data["lon"],
            dest_lat=dest_data["lat"], dest_lon=dest_data["lon"],
            total_distance_km=dist_km, avg_speed_kmh=float(speed), n_steps=sim_steps)
        prog = st.progress(0.0, text="Departing...")
        status_ph = st.empty(); chart_ph = st.empty()
        eta_h, spd_h, step_h = [], [], []
        for snap in snaps:
            prog.progress(min(snap.step / sim_steps, 1.0), text=f"Step {snap.step}/{sim_steps}")
            eta_h.append(snap.eta_minutes); spd_h.append(snap.speed_kmh); step_h.append(snap.step)
            status_ph.markdown(f'''<div class="rt-sim-box"><strong>Step {snap.step} of {sim_steps}</strong><br>
                Position &nbsp; <span class="rt-amber">{snap.lat:.4f}N, {snap.lon:.4f}E</span><br>
                Speed &nbsp;&nbsp;&nbsp;&nbsp; <span class="rt-amber">{snap.speed_kmh} km/h</span> &middot; Remaining <span class="rt-amber">{snap.distance_remaining_km:.1f} km</span><br>
                ETA &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span class="rt-amber">{fmt_eta(snap.eta_minutes)}</span> &middot; Elapsed {fmt_eta(snap.elapsed_minutes)}</div>''', unsafe_allow_html=True)
            fig_live = go.Figure()
            fig_live.add_trace(go.Scatter(x=step_h, y=eta_h, name="ETA", line=dict(color="#3B5BDB", width=2.5), fill="tozeroy", fillcolor="rgba(59,91,219,0.07)"))
            fig_live.add_trace(go.Scatter(x=step_h, y=spd_h, name="Speed", line=dict(color="#D97706", width=2, dash="dot"), yaxis="y2"))
            fig_live.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FAFAF9", font=dict(family="DM Sans", color="#44403C", size=11),
                yaxis=dict(title="ETA (min)", gridcolor="#F5F5F4", tickfont=dict(family="DM Mono", size=10)),
                yaxis2=dict(title="Speed (km/h)", overlaying="y", side="right", tickfont=dict(family="DM Mono", size=10)),
                legend=dict(bgcolor="rgba(255,255,255,.9)", bordercolor="#E7E5E4", borderwidth=1, orientation="h", yanchor="bottom", y=1.02),
                xaxis=dict(title="Step", gridcolor="#F5F5F4", tickfont=dict(family="DM Mono", size=10)),
                margin=dict(l=10,r=10,t=40,b=10), height=260)
            chart_ph.plotly_chart(fig_live, use_container_width=True, config={"displayModeBar": False})
            time.sleep(tick_ms / 1000.0)
        prog.progress(1.0, text="Arrived")
        st.markdown('<div class="rt-success">Simulation complete - train has arrived at destination.</div>', unsafe_allow_html=True)

# ── Tab: Route Map ─────────────────────────────────────────────────────────────
with tab_map:
    st.markdown('<div class="rt-sect">Route Map <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium
        mid_lat = (cur_lat + dest_data["lat"]) / 2
        mid_lon = (cur_lon + dest_data["lon"]) / 2
        m = folium.Map(location=[mid_lat, mid_lon], zoom_start=6, tiles="CartoDB positron")
        for sname, sdata in STATIONS.items():
            folium.CircleMarker(location=[sdata["lat"], sdata["lon"]], radius=4, color="#3B5BDB",
                fill=True, fill_color="#3B5BDB", fill_opacity=0.45, tooltip=f"{sname} [{sdata['code']}]", weight=1).add_to(m)
        folium.Marker([origin_data["lat"], origin_data["lon"]], tooltip=f"Origin: {origin_choice}", icon=folium.Icon(color="blue", icon="circle", prefix="fa")).add_to(m)
        folium.Marker([dest_data["lat"], dest_data["lon"]], tooltip=f"Destination: {dest_choice}", icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)
        folium.Marker([cur_lat, cur_lon], tooltip=f"Train {train_id} - {speed} km/h", icon=folium.DivIcon(html='<div style="font-size:20px">🚂</div>', icon_size=(28, 28))).add_to(m)
        folium.PolyLine([[cur_lat, cur_lon], [dest_data["lat"], dest_data["lon"]]], color="#D97706", weight=3, opacity=0.85, dash_array="10 5").add_to(m)
        st_folium(m, width="100%", height=480)
    except ImportError:
        st.markdown('<div class="rt-info">Install folium and streamlit-folium for an interactive map.</div>', unsafe_allow_html=True)
        all_lats=[s["lat"] for s in STATIONS.values()]; all_lons=[s["lon"] for s in STATIONS.values()]; all_names=list(STATIONS.keys())
        fig_map=go.Figure()
        fig_map.add_trace(go.Scattergeo(lat=all_lats,lon=all_lons,text=all_names,mode="markers",marker=dict(size=6,color="#3B5BDB",opacity=0.55),name="Stations"))
        fig_map.add_trace(go.Scattergeo(lat=[cur_lat,dest_data["lat"]],lon=[cur_lon,dest_data["lon"]],text=[f"Train {train_id}",dest_choice],mode="lines+markers",line=dict(width=3,color="#D97706"),marker=dict(size=11,color=["#D97706","#DC2626"]),name="Route"))
        fig_map.update_geos(showland=True,landcolor="#F7F3EE",showocean=True,oceancolor="#EBF5FB",showcountries=True,countrycolor="#E7E5E4",showcoastlines=True,coastlinecolor="#E7E5E4",projection_type="natural earth",center=dict(lat=(cur_lat+dest_data["lat"])/2,lon=(cur_lon+dest_data["lon"])/2))
        fig_map.update_layout(paper_bgcolor="#FFFFFF",geo_bgcolor="#FFFFFF",font=dict(color="#44403C",family="DM Sans"),margin=dict(l=0,r=0,t=0,b=0),height=440,legend=dict(bgcolor="#FFFFFF",bordercolor="#E7E5E4"))
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})

# ── Tab: History ───────────────────────────────────────────────────────────────
with tab_hist:
    st.markdown('<div class="rt-sect">Journey History <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
    from ml_model import HISTORY_PATH
    if HISTORY_PATH.exists():
        df_hist = pd.read_csv(HISTORY_PATH).tail(500)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Records", f"{len(df_hist):,}")
        c2.metric("Avg ETA", f"{df_hist['actual_eta_minutes'].mean():.0f} min")
        c3.metric("Avg Speed", f"{df_hist['speed_kmh'].mean():.0f} km/h")
        st.markdown("<br>", unsafe_allow_html=True)
        fig_hist=go.Figure()
        fig_hist.add_trace(go.Histogram(x=df_hist["actual_eta_minutes"],nbinsx=40,marker_color="#3B5BDB",opacity=0.75))
        fig_hist.update_layout(paper_bgcolor="#FFFFFF",plot_bgcolor="#FAFAF9",font=dict(family="DM Sans",color="#44403C",size=11),xaxis=dict(title="Actual ETA (minutes)",gridcolor="#F5F5F4",tickfont=dict(family="DM Mono",size=10)),yaxis=dict(title="Count",gridcolor="#F5F5F4",tickfont=dict(family="DM Mono",size=10)),showlegend=False,margin=dict(l=10,r=10,t=20,b=10),height=260)
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        with st.expander("Raw data - last 500 records"):
            st.dataframe(df_hist, use_container_width=True, height=280)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="rt-sect" style="font-size:1rem;">Log This Journey <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
        with st.form("log_form"):
            actual_min = st.number_input("Actual arrival time (minutes from departure)", 0.0, 1440.0, float(round(avg_eta, 1)))
            if st.form_submit_button("Save journey"):
                # Save to ml_model history CSV (original behaviour)
                append_history(dist_km, float(speed), delay_input, actual_min)

                # ── NEW: also save to users.json linked to the logged-in user
                save_journey(
                    phone=current_user["phone"],
                    journey={
                        "from":         origin_choice,
                        "to":           dest_choice,
                        "eta_minutes":  round(avg_eta, 1),
                        "actual_min":   actual_min,
                        "distance_km":  round(dist_km, 1),
                        "speed_kmh":    speed,
                    }
                )
                st.markdown('<div class="rt-success">Journey saved to your account and model history.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="rt-info">No history yet. Log completed journeys here to improve ML accuracy over time.</div>', unsafe_allow_html=True)

    # ── NEW: show this user's personal journey history ─────────────────────
    user_journeys = current_user.get("journey_history", [])
    if user_journeys:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="rt-sect" style="font-size:1rem;">Your Journeys ({len(user_journeys)}) <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
        df_user = pd.DataFrame(user_journeys[::-1])   # newest first
        st.dataframe(df_user, use_container_width=True, height=220)

# ── Tab: Model ─────────────────────────────────────────────────────────────────
with tab_ml:
    st.markdown('<div class="rt-sect">Model Overview <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
    metrics = get_model_metrics()
    c1, c2, c3 = st.columns(3)
    c1.metric("Algorithm", "Linear Regression")
    c2.metric("MAE", f"{metrics['mae']} min")
    c3.metric("R2 Score", str(metrics['r2']))
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2], gap="large")
    with col_a:
        st.markdown('<div class="rt-sect" style="font-size:1rem;">Architecture <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
        st.markdown('''<div class="rt-model-card">
            <div class="rt-model-row"><span class="rt-model-k">Input features</span><span class="rt-model-v">distance_km, speed_kmh, delay_min</span></div>
            <div class="rt-model-row"><span class="rt-model-k">Target variable</span><span class="rt-model-v">actual_eta_minutes</span></div>
            <div class="rt-model-row"><span class="rt-model-k">Pre-processing</span><span class="rt-model-v">StandardScaler (mean=0, std=1)</span></div>
            <div class="rt-model-row"><span class="rt-model-k">Training samples</span><span class="rt-model-v">2,000 synthetic + logged journeys</span></div>
            <div class="rt-model-row"><span class="rt-model-k">Validation split</span><span class="rt-model-v">80/20 train-test, seed=42</span></div>
            <div class="rt-model-row"><span class="rt-model-k">Persistence</span><span class="rt-model-v">pickle: eta_model.pkl + scaler.pkl</span></div>
        </div>''', unsafe_allow_html=True)
        st.markdown('''<div class="rt-code"><span class="cm"># Prediction pipeline</span><br>X = [distance_km, speed_kmh, delay_minutes]<br>X_s = <span class="kw">StandardScaler</span>.transform(X)<br>eta = <span class="kw">LinearRegression</span>.predict(X_s)<br><br><span class="cm"># Combined ETA</span><br>final = (physics_eta + ml_eta) / <span class="num">2</span></div>''', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="rt-sect" style="font-size:1rem;">Feature Coefficients <div class="rt-sect-line"></div></div>', unsafe_allow_html=True)
        from ml_model import load_model as _lm
        _model, _ = _lm()
        coefs = _model.coef_
        fig_c = go.Figure(go.Bar(x=["Distance","Speed","Delay"],y=coefs,marker_color=["#654103","#DF920C","#D9CB06"],marker_line_width=0,text=[f"{c:.3f}" for c in coefs],textposition="outside",textfont=dict(family="DM Mono",size=10,color="#44403C")))
        fig_c.update_layout(paper_bgcolor="#FFFFFF",plot_bgcolor="#FAFAF9",font=dict(family="DM Sans",color="#44403C",size=11),yaxis=dict(title="Coefficient",gridcolor="#F5F5F4",tickfont=dict(family="DM Mono",size=10),zeroline=True,zerolinecolor="#E7E5E4"),xaxis=dict(tickfont=dict(family="DM Sans",size=11)),showlegend=False,margin=dict(l=10,r=10,t=20,b=10),height=500)
        st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<div class="rt-info-blue" style="font-size:.78rem;"><strong>How to read:</strong> Distance (+) = more km = more time. Speed (-) = faster = less time. Delay (+) = carries forward.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Retrain model"):
        with st.spinner("Training..."):
            new_m = train_model(force=True)
        st.markdown(f'<div class="rt-success">Retrained. MAE = {new_m["mae"]} min, R2 = {new_m["r2"]}, {new_m["n_samples"]:,} samples</div>', unsafe_allow_html=True)
        st.cache_resource.clear()

# ── Footer (unchanged) ─────────────────────────────────────────────────────────
st.markdown('''<div style="margin-top:3rem;padding-top:1.4rem;border-top:1px solid #E7E5E4;display:flex;justify-content:space-between;align-items:center;font-size:.73rem;color:#A8A29E;"><span>RailTrack &middot; Railway ETA Prediction</span><span style="font-family:'DM Mono',monospace;font-size:.7rem;">Linear Regression &middot; Haversine &middot; Streamlit</span></div>''', unsafe_allow_html=True)