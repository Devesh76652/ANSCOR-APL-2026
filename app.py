import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from datetime import datetime
import io
from collections import defaultdict

# Page Configuration
st.set_page_config(
    page_title="APL 2026 - Cricket Scorer", 
    page_icon="🏏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub repo path
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"

# Team Database
TEAM_DB = {
    "Capital Chellengers": {
        "remote": GITHUB_RAW_BASE + "CapitalChellengers.jpeg",
        "squad": ["Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"],
    },
    "Black panther": {
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"],
    },
    "Super Kings": {
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"],
    },
    "Power Hitter": {
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"],
    },
    "Royal Warriors XI": {
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"],
    },
    "UnStoppable": {
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"],
    }
}

# Initialize session state
if 'player_stats' not in st.session_state:
    st.session_state.player_stats = {}
if 'commentary_store' not in st.session_state:
    st.session_state.commentary_store = []
if 'scheduled_matches' not in st.session_state:
    st.session_state.scheduled_matches = []
if 'match_counter' not in st.session_state:
    st.session_state.match_counter = 0

def update_player_stats(player_name, runs=0, balls=0, fours=0, sixes=0, wicket=False, overs=0, runs_conceded=0):
    if not player_name:
        return
    if player_name not in st.session_state.player_stats:
        st.session_state.player_stats[player_name] = {
            "matches": 0, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
            "wickets": 0, "overs": 0, "runs_conceded": 0, "fifties": 0, "hundreds": 0
        }
    stats = st.session_state.player_stats[player_name]
    if runs > 0 or balls > 0:
        stats["runs"] += runs
        stats["balls"] += balls
        stats["fours"] += fours
        stats["sixes"] += sixes
        if runs >= 50:
            stats["fifties"] += 1
        if runs >= 100:
            stats["hundreds"] += 1
    if wicket:
        stats["wickets"] += 1
    if overs > 0:
        stats["overs"] += overs
        stats["runs_conceded"] += runs_conceded

def add_commentary(description):
    st.session_state.commentary_store.insert(0, {
        "text": description,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    while len(st.session_state.commentary_store) > 20:
        st.session_state.commentary_store.pop()

def get_top_batsmen():
    batsmen = []
    for name, stats in st.session_state.player_stats.items():
        if stats["runs"] > 0:
            avg = stats["runs"] / stats["matches"] if stats["matches"] > 0 else 0
            sr = (stats["runs"] * 100 / stats["balls"]) if stats["balls"] > 0 else 0
            batsmen.append({
                "Player": name[:15], "M": stats["matches"], "Runs": stats["runs"],
                "Balls": stats["balls"], "4s": stats["fours"], "6s": stats["sixes"],
                "SR": f"{sr:.1f}", "Avg": f"{avg:.1f}"
            })
    return sorted(batsmen, key=lambda x: x["Runs"], reverse=True)[:10]

def get_top_bowlers():
    bowlers = []
    for name, stats in st.session_state.player_stats.items():
        if stats["wickets"] > 0:
            econ = stats["runs_conceded"] / stats["overs"] if stats["overs"] > 0 else 0
            bowlers.append({
                "Player": name[:15], "M": stats["matches"], "Wkts": stats["wickets"],
                "Overs": f"{stats['overs']:.1f}", "Runs": stats["runs_conceded"],
                "Econ": f"{econ:.2f}"
            })
    return sorted(bowlers, key=lambda x: x["Wkts"], reverse=True)[:10]

def init_innings():
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0, "penalty": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0},
        "all_batsmen": [], "all_bowlers": [], "undo_stack": [],
        "awaiting_batsman": False, "awaiting_bowler": False
    }

def ensure_match(m):
    if not isinstance(m, dict):
        return {"id": "Match", "team_1": "Team 1", "team_2": "Team 2", "total_overs": 4, "current_innings": 1,
                "innings_1": init_innings(), "innings_2": init_innings()}
    if "innings_1" not in m:
        m["innings_1"] = init_innings()
    if "innings_2" not in m:
        m["innings_2"] = init_innings()
    return m

def get_match_result(m):
    d1, d2 = m["innings_1"], m["innings_2"]
    if d1["b1"]["name"] == "":
        return "Awaiting lineup"
    total_balls = m["total_overs"] * 6
    if m["current_innings"] == 1:
        if d1["balls"] >= total_balls or d1["wickets"] >= 10:
            return f"Innings 1: {d1['runs']}/{d1['wickets']}"
        return f"{m['team_1']} batting - {d1['runs']}/{d1['wickets']}"
    target = d1["runs"] + 1
    if d2["runs"] >= target:
        return f"{m['team_2']} won by {10 - d2['wickets']} wickets"
    if d2["balls"] >= total_balls or d2["wickets"] >= 10:
        if d2["runs"] < d1["runs"]:
            return f"{m['team_1']} won by {d1['runs'] - d2['runs']} runs"
        return "Match Tied"
    runs_needed = target - d2['runs']
    balls_left = total_balls - d2['balls']
    return f"{m['team_2']} needs {runs_needed} runs from {balls_left} balls"

def generate_pdf(m):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "APL 2026 - Match Scorecard", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"{m['team_1']} vs {m['team_2']} ({m['total_overs']} overs)", ln=True, align="C")
        pdf.cell(0, 8, get_match_result(m), ln=True, align="C")
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue()
    except:
        return b""

@st.cache_resource
def get_db():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db = get_db()

# CSS
st.markdown("""
    <style>
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        width: 100%;
    }
    .score-card {
        background: linear-gradient(135deg, #1E3A8A, #0F172A);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        position: relative;
    }
    .score-big {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
    }
    .info-box {
        background: #1E293B;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid #334155;
    }
    .ball {
        display: inline-block;
        width: 36px;
        height: 36px;
        line-height: 36px;
        text-align: center;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
    }
    .run-ball { background: #475569; color: white; }
    .four-ball { background: #10B981; color: white; }
    .six-ball { background: #10B981; color: white; }
    .wicket-ball { background: #EF4444; color: white; }
    .extra-ball { background: #F59E0B; color: white; }
    .live-badge {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #EF4444;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        animation: pulse 1s infinite;
    }
    .finished-badge {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #6B7280;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    .team-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .team-logo-small {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        border: 2px solid #3B82F6;
        object-fit: cover;
    }
    .commentary-box {
        background: #0F172A;
        border-radius: 10px;
        padding: 10px;
        max-height: 250px;
        overflow-y: auto;
    }
    .commentary-item {
        padding: 6px;
        margin: 4px 0;
        border-left: 3px solid #3B82F6;
        background: #1E293B;
        border-radius: 5px;
        font-size: 12px;
    }
    .team-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin: 8px;
    }
    .schedule-card {
        background: #1E293B;
        border-radius: 10px;
        padding: 10px;
        margin: 8px 0;
        border-left: 3px solid #3B82F6;
    }
    @media (max-width: 768px) {
        .team-logo-small { width: 35px; height: 35px; }
        .score-big { font-size: 1.8rem; }
        .ball { width: 30px; height: 30px; line-height: 30px; font-size: 12px; }
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏏 APL 2026")
    st.markdown("---")
    commentary_on = st.toggle("📝 Commentary", value=True)
    st.markdown("---")
    role = st.radio("Access:", ["👤 Player View", "⚡ Scorer Panel"])
    is_admin = False
    if role == "⚡ Scorer Panel":
        pwd = st.text_input("Password:", type="password", key="admin_pwd")
        if pwd == "anscor2026":
            is_admin = True
            st.success("✅ Admin Access")
        elif pwd:
            st.error("Wrong Password")
    if st.session_state.scheduled_matches:
        st.markdown(f"📅 {len(st.session_state.scheduled_matches)} Scheduled")

# Tabs
tabs = st.tabs(["🏏 Live", "📊 Analytics", "👤 Players", "🏆 Rankings", "📅 Schedule", "👥 Teams"])
tab_live, tab_analytics, tab_players, tab_rankings, tab_schedule, tab_teams = tabs

# Teams Tab
with tab_teams:
    st.markdown("### Tournament Teams")
    cols = st.columns(3)
    for idx, (name, data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            st.image(data["remote"], width=100)
            st.markdown(f"**{name}**")
            if st.button(f"View Squad", key=f"team_squad_{idx}"):
                with st.expander(f"{name} Squad", expanded=True):
                    for p in data["squad"]:
                        st.markdown(f"• {p}")

# Schedule Tab
with tab_schedule:
    st.markdown("### Match Schedule")
    if is_admin:
        with st.expander("➕ Schedule New Match", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                match_id = st.text_input("Match ID:", key="sch_match_id")
                t1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="sch_t1")
                s_date = st.date_input("Date:", key="sch_date")
            with col2:
                venue = st.text_input("Venue:", key="sch_venue")
                t2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="sch_t2")
                s_time = st.time_input("Time:", key="sch_time")
            if st.button("📅 Schedule", key="schedule_btn"):
                if match_id and t1 != t2:
                    st.session_state.scheduled_matches.append({
                        "id": match_id, "team1": t1, "team2": t2,
                        "date": s_date.strftime("%Y-%m-%d"), "time": s_time.strftime("%H:%M"), "venue": venue
                    })
                    st.success(f"Scheduled {match_id}!")
                    st.rerun()
    if st.session_state.scheduled_matches:
        for m in st.session_state.scheduled_matches:
            st.markdown(f"""
                <div class="schedule-card">
                    <strong>{m['id']}</strong><br>
                    {m['team1']} vs {m['team2']}<br>
                    📍 {m['venue']} | 📅 {m['date']} 🕐 {m['time']}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No matches scheduled")

# Rankings Tab
with tab_rankings:
    st.markdown("### Player Rankings")
    r1, r2 = st.tabs(["🏏 Top Batsmen", "🎯 Top Bowlers"])
    with r1:
        bats = get_top_batsmen()
        if bats:
            st.dataframe(pd.DataFrame(bats), use_container_width=True, hide_index=True)
        else:
            st.info("No batting stats yet")
    with r2:
        bowl = get_top_bowlers()
        if bowl:
            st.dataframe(pd.DataFrame(bowl), use_container_width=True, hide_index=True)
        else:
            st.info("No bowling stats yet")

# Players Tab
with tab_players:
    st.markdown("### Player Profiles")
    all_players = []
    for team in TEAM_DB.values():
        all_players.extend(team["squad"])
    search = st.selectbox("Search:", sorted(all_players), key="player_search")
    if search:
        stats = st.session_state.player_stats.get(search, {})
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div style="background:#1E293B; border-radius:12px; padding:15px; text-align:center;">
                    <div style="width:60px; height:60px; background:#3B82F6; border-radius:50%; margin:0 auto; display:flex; align-items:center; justify-content:center;">
                        <span style="font-size:1.5rem; color:white;">{search[0]}</span>
                    </div>
                    <h4>{search}</h4>
                    <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:8px; margin-top:10px;">
                        <div style="background:#0F172A; padding:8px; border-radius:8px;">
                            <div style="font-size:1.2rem; font-weight:800; color:#3B82F6;">{stats.get('matches',0)}</div>
                            <div>Matches</div>
                        </div>
                        <div style="background:#0F172A; padding:8px; border-radius:8px;">
                            <div style="font-size:1.2rem; font-weight:800; color:#3B82F6;">{stats.get('runs',0)}</div>
                            <div>Runs</div>
                        </div>
                        <div style="background:#0F172A; padding:8px; border-radius:8px;">
                            <div style="font-size:1.2rem; font-weight:800; color:#3B82F6;">{stats.get('wickets',0)}</div>
                            <div>Wickets</div>
                        </div>
                        <div style="background:#0F172A; padding:8px; border-radius:8px;">
                            <div style="font-size:1.2rem; font-weight:800; color:#3B82F6;">{stats.get('fours',0)}</div>
                            <div>4s</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="background:#1E293B; border-radius:12px; padding:15px;">
                    <h4>Batting</h4>
                    <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:8px;">
                        <div><small>Balls</small><br><b>{stats.get('balls',0)}</b></div>
                        <div><small>6s</small><br><b>{stats.get('sixes',0)}</b></div>
                        <div><small>50s</small><br><b>{stats.get('fifties',0)}</b></div>
                    </div>
                    <h4>Bowling</h4>
                    <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:8px;">
                        <div><small>Overs</small><br><b>{stats.get('overs',0):.1f}</b></div>
                        <div><small>Runs</small><br><b>{stats.get('runs_conceded',0)}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Analytics Tab
with tab_analytics:
    st.markdown("### Match Analytics")
    if db["matches"]:
        match_sel = st.selectbox("Select Match:", list(db["matches"].keys()), key="analytics_match")
        m = ensure_match(db["matches"][match_sel])
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Runs", m["innings_1"]["runs"] + m["innings_2"]["runs"])
        with c2:
            st.metric("Total Wickets", m["innings_1"]["wickets"] + m["innings_2"]["wickets"])
        with c3:
            fours = m["innings_1"]["b1"]["fours"] + m["innings_1"]["b2"]["fours"]
            st.metric("Total Fours", fours)
        with c4:
            sixes = m["innings_1"]["b1"]["sixes"] + m["innings_1"]["b2"]["sixes"]
            st.metric("Total Sixes", sixes)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Innings 1: {m['team_1']}")
            st.metric("Score", f"{m['innings_1']['runs']}/{m['innings_1']['wickets']}")
            if m["innings_1"]["over_history"]:
                st.dataframe(pd.DataFrame(m["innings_1"]["over_history"]), use_container_width=True)
        with col2:
            st.subheader(f"Innings 2: {m['team_2']}")
            st.metric("Score", f"{m['innings_2']['runs']}/{m['innings_2']['wickets']}")
            if m["innings_2"]["over_history"]:
                st.dataframe(pd.DataFrame(m["innings_2"]["over_history"]), use_container_width=True)
        st.success(get_match_result(m))
    else:
        st.info("No matches played")

# Live Tab
with tab_live:
    if is_admin:
        with st.expander("⚙️ New Match", expanded=not db["active_match_id"]):
            c1, c2, c3 = st.columns(3)
            with c1:
                mid = st.text_input("Match ID:", "Match_001", key="new_mid")
            with c2:
                tm1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="new_t1")
            with c3:
                tm2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="new_t2")
            c4, c5 = st.columns(2)
            with c4:
                ovrs = st.number_input("Overs:", 1, 10, 4, key="new_overs")
            with c5:
                if st.button("🚀 Create", key="create_match"):
                    if mid and tm1 != tm2:
                        with db["lock"]:
                            db["matches"][mid] = {
                                "id": mid, "team_1": tm1, "team_2": tm2,
                                "total_overs": ovrs, "current_innings": 1,
                                "innings_1": init_innings(), "innings_2": init_innings()
                            }
                            db["active_match_id"] = mid
                        st.rerun()
        if db["matches"]:
            curr = db["active_match_id"] if db["active_match_id"] else list(db["matches"].keys())[0]
            sel = st.selectbox("Active:", list(db["matches"].keys()), index=list(db["matches"].keys()).index(curr), key="active_sel")
            ca, cb = st.columns(2)
            with ca:
                if st.button("🎯 Set Active", key="set_active"):
                    db["active_match_id"] = sel
                    st.rerun()
            with cb:
                if db["active_match_id"] and db["active_match_id"] in db["matches"]:
                    am = ensure_match(db["matches"][db["active_match_id"]])
                    if am["current_innings"] == 1 and am["innings_1"]["b1"]["name"]:
                        if st.button("➡️ Innings 2", key="switch_innings"):
                            with db["lock"]:
                                am["current_innings"] = 2
                            st.rerun()
    if not db["active_match_id"] or db["active_match_id"] not in db["matches"]:
        st.info("No active match. Create one above.")
    else:
        match = ensure_match(db["matches"][db["active_match_id"]])
        inn = match["innings_1"] if match["current_innings"] == 1 else match["innings_2"]
        batting = match["team_1"] if match["current_innings"] == 1 else match["team_2"]
        bowling = match["team_2"] if match["current_innings"] == 1 else match["team_1"]
        target = match["innings_1"]["runs"] + 1 if match["current_innings"] == 2 else None
        total_balls = match["total_overs"] * 6
        if match["current_innings"] == 1:
            innings_complete = (inn["balls"] >= total_balls or inn["wickets"] >= 10)
        else:
            innings_complete = (inn["balls"] >= total_balls or inn["wickets"] >= 10 or (target and inn["runs"] >= target))
        if inn["b1"]["name"] == "" and is_admin:
            with st.form("setup_form"):
                st.warning(f"Setup {batting} Batting")
                col1, col2, col3 = st.columns(3)
                with col1:
                    striker = st.selectbox("Striker:", TEAM_DB[batting]["squad"], key="striker_sel")
                with col2:
                    non_striker = st.selectbox("Non-Striker:", TEAM_DB[batting]["squad"], key="non_striker_sel")
                with col3:
                    bowler = st.selectbox("Bowler:", TEAM_DB[bowling]["squad"], key="bowler_sel")
                if st.form_submit_button("🚀 Start Match"):
                    with db["lock"]:
                        inn["b1"]["name"] = striker
                        inn["b2"]["name"] = non_striker
                        inn["bowler"]["name"] = bowler
                    st.rerun()
        elif inn["b1"]["name"]:
            overs_done = inn["balls"] // 6
            balls_in = inn["balls"] % 6
            crr = inn["runs"] / (inn["balls"]/6) if inn["balls"] > 0 else 0
            status_badge = '<span class="finished-badge">FINISHED</span>' if innings_complete else '<span class="live-badge">LIVE</span>'
            # Score Display
            st.markdown(f"""
                <div class="score-card">
                    {status_badge}
                    <div class="team-header">
                        <div style="text-align:center;">
                            <img src="{TEAM_DB[batting]['remote']}" class="team-logo-small">
                            <div style="font-size:10px;">{batting[:12]}</div>
                        </div>
                        <div style="text-align:center;">
                            <div class="score-big">{inn['runs']}-{inn['wickets']}</div>
                            <div>{overs_done}.{balls_in}/{match['total_overs']} | CRR: {crr:.2f}</div>
                        </div>
                        <div style="text-align:center;">
                            <img src="{TEAM_DB[bowling]['remote']}" class="team-logo-small">
                            <div style="font-size:10px;">{bowling[:12]}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if target:
                runs_needed = target - inn['runs']
                balls_left = total_balls - inn['balls']
                req_rate = runs_needed / (balls_left/6) if balls_left > 0 else 0
                if inn['runs'] >= target:
                    st.success(f"Target Achieved! {batting} wins!")
                else:
                    st.info(f"Target: {target} | Need {runs_needed} off {balls_left} | RR: {req_rate:.2f}")
            if is_admin:
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    st.markdown(f"""
                        <div class="info-box">
                            <b>🏏 BATTING</b><br>
                            {'👉 ' if inn['b1']['strike'] else ''}{inn['b1']['name'][:15]}: <b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}<br>
                            {'👉 ' if inn['b2']['strike'] else ''}{inn['b2']['name'][:15]}: <b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}
                        </div>
                        <div class="info-box">
                            <b>🥎 BOWLER</b><br>
                            {inn['bowler']['name'][:15]}: {inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6}) | Econ: {inn['bowler']['runs']/(inn['bowler']['balls']/6) if inn['bowler']['balls']>0 else 0:.2f}
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("**📦 CURRENT OVER**")
                    if inn["this_over"]:
                        html = ""
                        for b in inn["this_over"]:
                            if b in [4,6]:
                                html += f'<span class="ball four-ball">{b}</span>'
                            elif b == "W":
                                html += f'<span class="ball wicket-ball">{b}</span>'
                            elif b in ["WD","NB"]:
                                html += f'<span class="ball extra-ball">{b}</span>'
                            else:
                                html += f'<span class="ball run-ball">{b}</span>'
                        st.markdown(html, unsafe_allow_html=True)
                    else:
                        st.caption("No deliveries")
                    if inn["over_history"]:
                        st.markdown("**📊 RECENT OVERS**")
                        for ov in inn["over_history"][-3:]:
                            st.caption(f"Over {ov['Over']}: {ov['Bowler'][:10]} - {ov['Timeline']}")
                    st.info(get_match_result(match))
                with col_right:
                    st.markdown("### 🎛️ SCORING")
                    def add_ball(runs, extra=0, legal=True, wicket=False, symbol=None):
                        with db["lock"]:
                            if "undo_stack" not in inn:
                                inn["undo_stack"] = []
                            inn["undo_stack"].append(copy.deepcopy({
                                "runs": inn["runs"], "wickets": inn["wickets"], "balls": inn["balls"],
                                "extras": inn["extras"], "this_over": list(inn["this_over"]),
                                "b1": copy.deepcopy(inn["b1"]), "b2": copy.deepcopy(inn["b2"]),
                                "bowler": copy.deepcopy(inn["bowler"])
                            }))
                            striker = inn["b1"] if inn["b1"]["strike"] else inn["b2"]
                            inn["runs"] += runs
                            inn["extras"] += extra
                            inn["bowler"]["runs"] += runs
                            if runs > 0 and not wicket and striker["name"]:
                                update_player_stats(striker["name"], runs=runs, balls=1,
                                                  fours=1 if runs==4 else 0, sixes=1 if runs==6 else 0)
                            if wicket:
                                inn["wickets"] += 1
                                inn["bowler"]["wickets"] += 1
                                if inn["bowler"]["name"]:
                                    update_player_stats(inn["bowler"]["name"], wicket=True, overs=0.166 if legal else 0, runs_conceded=runs)
                                if striker["name"]:
                                    update_player_stats(striker["name"], balls=1)
                            if legal:
                                inn["balls"] += 1
                                inn["bowler"]["balls"] += 1
                                if not wicket and striker["name"]:
                                    striker["balls"] += 1
                                    striker["runs"] += (runs - extra)
                                inn["this_over"].append(symbol if symbol else runs)
                                if commentary_on:
                                    if wicket:
                                        add_commentary(f"OUT! {striker['name']} ({striker['runs']}) b {inn['bowler']['name']}")
                                    elif runs == 6:
                                        add_commentary(f"SIX! {striker['name']} launches it!")
                                    elif runs == 4:
                                        add_commentary(f"FOUR! {striker['name']} finds the gap!")
                                    elif runs > 0:
                                        add_commentary(f"{runs} run{'s' if runs>1 else ''} - {striker['name']}")
                                    else:
                                        add_commentary(f"Dot ball! {striker['name']} defends")
                            else:
                                inn["this_over"].append(symbol)
                                if commentary_on:
                                    add_commentary(f"{symbol} - Extra run")
                            if legal and (runs % 2 == 1) and not wicket:
                                inn["b1"]["strike"] = not inn["b1"]["strike"]
                                inn["b2"]["strike"] = not inn["b2"]["strike"]
                            legal_balls = [b for b in inn["this_over"] if b not in ['WD','NB']]
                            if len(legal_balls) == 6:
                                inn["awaiting_bowler"] = True
                            if wicket and inn["wickets"] < 10:
                                inn["awaiting_batsman"] = True
                    if inn["awaiting_batsman"]:
                        st.warning("⚠️ New Batsman")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen"]]
                        avail = [p for p in TEAM_DB[batting]["squad"] if p not in used]
                        if not avail:
                            avail = TEAM_DB[batting]["squad"]
                        new_bat = st.selectbox("Select:", avail, key="new_bat")
                        if st.button("✅ Confirm", key="confirm_bat"):
                            with db["lock"]:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True}
                                else:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False}
                                inn["awaiting_batsman"] = False
                                if commentary_on:
                                    add_commentary(f"👤 New batsman: {new_bat}")
                            st.rerun()
                    elif inn["awaiting_bowler"]:
                        st.success("🔄 Over Complete!")
                        new_bowl = st.selectbox("Select Bowler:", TEAM_DB[bowling]["squad"], key="new_bowl")
                        if st.button("✅ Next Over", key="next_over"):
                            with db["lock"]:
                                if inn["bowler"]["name"]:
                                    inn["all_bowlers"].append(copy.deepcopy(inn["bowler"]))
                                inn["over_history"].append({
                                    "Over": len(inn["over_history"]) + 1,
                                    "Bowler": inn["bowler"]["name"],
                                    "Score": f"{inn['runs']}/{inn['wickets']}",
                                    "Timeline": ", ".join(map(str, inn["this_over"]))
                                })
                                inn["this_over"] = []
                                inn["bowler"] = {"name": new_bowl, "runs": 0, "wickets": 0, "balls": 0}
                                inn["awaiting_bowler"] = False
                                if commentary_on:
                                    add_commentary(f"🔄 New over! {new_bowl} to bowl")
                            st.rerun()
                    elif not innings_complete:
                        if target and inn["runs"] >= target:
                            st.success("Target Achieved!")
                        else:
                            st.markdown("**RUNS**")
                            r1, r2, r3, r4 = st.columns(4)
                            with r1:
                                if st.button("0", key="r0"): add_ball(0); st.rerun()
                                if st.button("1", key="r1"): add_ball(1); st.rerun()
                            with r2:
                                if st.button("2", key="r2"): add_ball(2); st.rerun()
                                if st.button("3", key="r3"): add_ball(3); st.rerun()
                            with r3:
                                if st.button("4", key="r4"):
                                    add_ball(4)
                                    if inn["b1"]["strike"]: inn["b1"]["fours"] += 1
                                    else: inn["b2"]["fours"] += 1
                                    st.rerun()
                                if st.button("6", key="r6"):
                                    add_ball(6)
                                    if inn["b1"]["strike"]: inn["b1"]["sixes"] += 1
                                    else: inn["b2"]["sixes"] += 1
                                    st.rerun()
                            with r4:
                                if st.button("WD", key="wd"): add_ball(1, 1, False, symbol="WD"); st.rerun()
                                if st.button("NB", key="nb"): add_ball(1, 1, False, symbol="NB"); st.rerun()
                            st.markdown("---")
                            a1, a2, a3 = st.columns(3)
                            with a1:
                                if st.button("OUT", type="primary", key="out_btn"):
                                    add_ball(0, 0, True, True, "W")
                                    st.rerun()
                            with a2:
                                if inn["undo_stack"]:
                                    if st.button("UNDO", key="undo_btn"):
                                        with db["lock"]:
                                            prev = inn["undo_stack"].pop()
                                            for k in ["runs","wickets","balls","extras","this_over","b1","b2","bowler"]:
                                                inn[k] = prev[k]
                                        st.rerun()
                            with a3:
                                if st.button("SWAP", key="swap_btn"):
                                    with db["lock"]:
                                        inn["b1"]["strike"] = not inn["b1"]["strike"]
                                        inn["b2"]["strike"] = not inn["b2"]["strike"]
                                    st.rerun()
                    else:
                        st.success("Innings Complete!")
                        if match["current_innings"] == 1:
                            if st.button("Start Innings 2", type="primary", key="start_inn2"):
                                with db["lock"]:
                                    match["current_innings"] = 2
                                    if commentary_on:
                                        add_commentary(f"Second innings! {match['team_2']} needs {match['innings_1']['runs']+1} to win")
                                st.rerun()
                    with st.expander("⚙️ Admin", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            etype = st.selectbox("Type", ["Extras", "Penalty"], key="etype")
                        with col2:
                            eruns = st.number_input("Runs", 1, 20, 1, key="eruns")
                        if st.button("➕ Add", key="add_runs"):
                            with db["lock"]:
                                inn["runs"] += eruns
                                if etype == "Extras":
                                    inn["extras"] += eruns
                                    inn["this_over"].append(f"+{eruns}Ex")
                                else:
                                    inn["penalty"] = inn.get("penalty",0) + eruns
                                    inn["this_over"].append(f"+{eruns}Pen")
                            st.rerun()
                    st.markdown("---")
                    if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                        pdf_data = generate_pdf(match)
                        if pdf_data:
                            st.download_button("📥 PDF", pdf_data, f"match_{match['id']}.pdf", use_container_width=True, key="pdf_download")
            else:
                # Player View
                st.markdown(f"""
                    <div class="info-box">
                        <b>🏏 BATTING</b><br>
                        {inn['b1']['name'][:18]}: {inn['b1']['runs']}({inn['b1']['balls']}) {'*' if inn['b1']['strike'] else ''}<br>
                        {inn['b2']['name'][:18]}: {inn['b2']['runs']}({inn['b2']['balls']}) {'*' if inn['b2']['strike'] else ''}
                    </div>
                    <div class="info-box">
                        <b>🥎 BOWLER</b><br>
                        {inn['bowler']['name'][:18]}: {inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6})
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("**📦 CURRENT OVER**")
                if inn["this_over"]:
                    html = ""
                    for b in inn["this_over"]:
                        if b in [4,6]:
                            html += f'<span class="ball four-ball">{b}</span>'
                        elif b == "W":
                            html += f'<span class="ball wicket-ball">{b}</span>'
                        elif b in ["WD","NB"]:
                            html += f'<span class="ball extra-ball">{b}</span>'
                        else:
                            html += f'<span class="ball run-ball">{b}</span>'
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    st.caption("No deliveries")
                if inn["over_history"]:
                    st.markdown("**📊 RECENT OVERS**")
                    for ov in inn["over_history"][-5:]:
                        st.caption(f"Over {ov['Over']}: {ov['Bowler']} - {ov['Timeline']}")
                if inn["all_batsmen"]:
                    st.markdown("**📋 FALLEN WICKETS**")
                    for w in inn["all_batsmen"][-5:]:
                        st.caption(f"• {w['name']} - {w['runs']}({w['balls']})")
                st.info(get_match_result(match))
                if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                    pdf_data = generate_pdf(match)
                    if pdf_data:
                        st.download_button("📥 PDF", pdf_data, f"match_{match['id']}.pdf", use_container_width=True, key="pdf_player")
            if commentary_on and st.session_state.commentary_store:
                st.markdown("---")
                st.markdown("### 📝 Commentary")
                st.markdown('<div class="commentary-box">', unsafe_allow_html=True)
                for c in st.session_state.commentary_store[:10]:
                    st.markdown(f'<div class="commentary-item"><small>{c["time"]}</small><br>{c["text"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
