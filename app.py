import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from typing import TypedDict
import traceback

# Constants
BALLS_PER_OVER = 6
MAX_WICKETS = 10
DEFAULT_OVERS = 4
ADMIN_PASSWORD = "anscor2026"

# Page Configuration
st.set_page_config(
    page_title="APL 2026 - Cricket Scoring System",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Background auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

# Team Database
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"

TEAM_DB = {
    "Capital Chellengers": {
        "squad": ["Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"]
    },
    "Black panther": {
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"]
    },
    "Super Kings": {
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"]
    },
    "Power Hitter": {
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"]
    },
    "Royal Warriors XI": {
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"]
    },
    "UnStoppable": {
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"]
    }
}

DISMISSAL_TYPES = ["Bowled", "Caught", "LBW", "Run Out", "Stumped", "Hit Wicket"]

# Custom CSS - Fixed layout and alignment
st.markdown("""
    <style>
    /* Main container - fixed width and centering */
    .main .block-container {
        padding: 1rem 1rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* Score card styling */
    .score-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #ff6b6b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .score-box h1 {
        font-size: 2.5rem !important;
        margin: 5px 0;
        font-weight: bold;
        color: #ff6b6b;
    }
    
    .score-box h2 {
        font-size: 1rem !important;
        margin: 5px 0;
    }
    
    .score-box h3 {
        font-size: 0.9rem !important;
        margin: 5px 0;
        color: #ddd;
    }
    
    .status-badge {
        position: absolute;
        top: 8px;
        right: 12px;
        background: #ff6b6b;
        color: white;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    /* Mobile card styling */
    .info-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        color: white;
        border: 1px solid #ff6b6b;
    }
    
    .info-card h4 {
        font-size: 0.85rem;
        margin-bottom: 8px;
        color: #ff6b6b;
    }
    
    /* Button styling - compact */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 5px 12px;
        font-size: 0.8rem;
        font-weight: 500;
        transition: all 0.2s;
        width: 100%;
        white-space: nowrap;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(255,107,107,0.3);
    }
    
    /* Metric styling - compact */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #ff6b6b;
    }
    
    div[data-testid="stMetric"] label {
        color: #ddd !important;
        font-size: 0.75rem !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #ff6b6b !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    
    /* Tab styling - fixed */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: #1e3c72;
        padding: 6px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 4px 15px;
        font-size: 0.8rem;
        font-weight: 500;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: #ff6b6b !important;
        color: white !important;
    }
    
    /* Dataframe styling - compact */
    .stDataFrame {
        background: #1e3c72;
        border-radius: 8px;
        border: 1px solid #ff6b6b;
    }
    
    /* Expander styling - compact */
    .streamlit-expanderHeader {
        background: #1e3c72;
        border-radius: 6px;
        color: white;
        font-size: 0.85rem;
        padding: 6px;
    }
    
    /* Selectbox styling */
    .stSelectbox div {
        background: #1e3c72;
        color: white;
    }
    
    /* Alert boxes - compact */
    .stAlert {
        border-radius: 6px;
        font-size: 0.8rem;
        padding: 6px;
        margin-bottom: 10px;
    }
    
    /* Row spacing - compact */
    .row-widget {
        margin-bottom: 6px;
    }
    
    hr {
        margin: 10px 0;
        border-color: #ff6b6b;
    }
    
    /* Ball bubble styling */
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    /* Team card */
    .team-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid #ff6b6b;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .team-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255,107,107,0.2);
    }
    
    .team-card h3 {
        color: #ff6b6b;
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .ball-bubble {
            width: 28px;
            height: 28px;
            font-size: 0.75rem;
        }
        
        .stButton > button {
            padding: 3px 8px;
            font-size: 0.7rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Type definitions
class BatsmanStats(TypedDict):
    name: str
    runs: int
    balls: int
    fours: int
    sixes: int
    strike: bool
    status: str
    dismissal_type: Optional[str]

class BowlerStats(TypedDict):
    name: str
    runs: int
    wickets: int
    balls: int
    maidens: int

class InningsData(TypedDict):
    runs: int
    wickets: int
    balls: int
    extras: int
    penalty: int
    this_over: List[str]
    over_history: List[Dict]
    b1: BatsmanStats
    b2: BatsmanStats
    bowler: BowlerStats
    all_batsmen_history: List[BatsmanStats]
    all_bowlers_history: List[BowlerStats]
    undo_stack: List[Dict]
    awaiting_batsman: bool
    awaiting_bowler: bool
    commentary: List[str]

class MatchData(TypedDict):
    id: str
    team_1: str
    team_2: str
    total_overs: int
    current_innings: int
    match_complete: bool
    innings_1: InningsData
    innings_2: InningsData
    created_at: str
    winner: Optional[str]
    win_margin: Optional[str]

def init_blank_innings() -> InningsData:
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0, "penalty": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "Not Out", "dismissal_type": None},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out", "dismissal_type": None},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [], "all_bowlers_history": [], "undo_stack": [],
        "awaiting_batsman": False, "awaiting_bowler": False, "commentary": []
    }

def ensure_innings_keys(inn: Dict) -> InningsData:
    if not isinstance(inn, dict):
        inn = init_blank_innings()
    defaults = init_blank_innings()
    for k, v in defaults.items():
        if k not in inn:
            inn[k] = v
    for player_key in ["b1", "b2", "bowler"]:
        if player_key in inn and not isinstance(inn[player_key], dict):
            inn[player_key] = copy.deepcopy(defaults[player_key])
    return inn

def ensure_match_keys(m: Dict) -> MatchData:
    if not isinstance(m, dict):
        m = {"id": "Match", "team_1": "Team 1", "team_2": "Team 2", "total_overs": DEFAULT_OVERS, "current_innings": 1, "match_complete": False, "innings_1": init_blank_innings(), "innings_2": init_blank_innings(), "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None}
    for key in ["innings_1", "innings_2"]:
        if key not in m:
            m[key] = init_blank_innings()
        m[key] = ensure_innings_keys(m[key])
    for key in ["total_overs", "current_innings", "match_complete"]:
        if key not in m:
            m[key] = DEFAULT_OVERS if key == "total_overs" else 1 if key == "current_innings" else False
    if "id" not in m:
        m["id"] = "Match"
    if "created_at" not in m:
        m["created_at"] = datetime.now().isoformat()
    return m

def is_innings_complete(inn: InningsData, total_overs: int) -> bool:
    return (inn["balls"] >= total_overs * BALLS_PER_OVER) or (inn["wickets"] >= 10)

def get_match_result(m: MatchData) -> str:
    m = ensure_match_keys(m)
    if m.get("winner"):
        return f"🏆 {m['winner']} ({m.get('win_margin', '')})"
    d1, d2 = m["innings_1"], m["innings_2"]
    if d1["b1"]["name"] == "":
        return "⚙️ Setup Required"
    if m["current_innings"] == 1:
        return f"🏏 Innings 1: {m['team_1']} batting"
    runs_i1, runs_i2, wickets_i2 = d1["runs"], d2["runs"], d2["wickets"]
    target = runs_i1 + 1
    if runs_i2 >= target:
        return f"🏆 {m['team_2']} won by {10 - wickets_i2} wickets!"
    if is_innings_complete(d2, m["total_overs"]):
        if runs_i2 < runs_i1:
            return f"🏆 {m['team_1']} won by {runs_i1 - runs_i2} runs!"
        elif runs_i2 == runs_i1:
            return "🤝 Match Tied!"
    runs_needed = target - runs_i2
    balls_rem = (m["total_overs"] * BALLS_PER_OVER) - d2["balls"]
    return f"🎯 {m['team_2']} needs {runs_needed} runs from {balls_rem} balls"

def clean_for_pdf(text: str) -> str:
    if not text:
        return ""
    import re
    text = re.sub(r'[^\x00-\x7F]+', '', str(text))
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf_bytes(m: MatchData) -> bytes:
    try:
        m = ensure_match_keys(m)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "APL 2026 - MATCH SCORECARD", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"{m['team_1']} vs {m['team_2']} ({m['total_overs']} overs)", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, get_match_result(m), ln=True, align="C")
        pdf.ln(5)
        for inn_num, inn_data, team in [(1, m["innings_1"], m["team_1"]), (2, m["innings_2"], m["team_2"])]:
            if inn_data["b1"]["name"]:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"INNINGS {inn_num}: {team}", ln=True)
                overs = f"{inn_data['balls']//6}.{inn_data['balls']%6}"
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, f"Score: {inn_data['runs']}/{inn_data['wickets']} ({overs} overs)", ln=True)
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(70, 6, "Batsman", 1)
                pdf.cell(25, 6, "Runs", 1, 0, "C")
                pdf.cell(25, 6, "Balls", 1, 0, "C")
                pdf.cell(30, 6, "Status", 1, 1, "C")
                pdf.set_font("Helvetica", "", 8)
                for b in [inn_data["b1"], inn_data["b2"]] + inn_data.get("all_batsmen_history", []):
                    if b["name"]:
                        pdf.cell(70, 5, b["name"][:30], 1)
                        pdf.cell(25, 5, str(b["runs"]), 1, 0, "C")
                        pdf.cell(25, 5, str(b["balls"]), 1, 0, "C")
                        pdf.cell(30, 5, b.get("status", "Out")[:20], 1, 1, "C")
        return pdf.output(dest='S').encode('latin-1', errors='replace')
    except:
        return b""

def add_commentary(inn_data: InningsData, message: str):
    if "commentary" not in inn_data:
        inn_data["commentary"] = []
    inn_data["commentary"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    if len(inn_data["commentary"]) > 100:
        inn_data["commentary"] = inn_data["commentary"][-100:]

def process_ball_input(inn_data: InningsData, runs_inc: int, extra_inc: int = 0, is_legal: bool = True, is_wicket: bool = False, symbol: Optional[str] = None, dismissal_type: Optional[str] = None):
    state_snap = copy.deepcopy({k: inn_data[k] for k in ["runs", "wickets", "balls", "extras", "penalty", "this_over", "over_history", "b1", "b2", "bowler", "all_batsmen_history", "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]})
    if "undo_stack" not in inn_data:
        inn_data["undo_stack"] = []
    inn_data["undo_stack"].append(state_snap)
    striker = inn_data["b1"] if inn_data["b1"]["strike"] else inn_data["b2"]
    inn_data["runs"] += runs_inc
    inn_data["extras"] += extra_inc
    inn_data["bowler"]["runs"] += runs_inc
    if is_wicket:
        inn_data["wickets"] += 1
        inn_data["bowler"]["wickets"] += 1
        striker["status"] = f"{dismissal_type or 'Out'} b {inn_data['bowler']['name']}"
        add_commentary(inn_data, f"WICKET! {striker['name']} ({striker['runs']} runs)")
    if is_legal:
        inn_data["balls"] += 1
        inn_data["bowler"]["balls"] += 1
        striker["balls"] += 1
        striker["runs"] += (runs_inc - extra_inc)
        if runs_inc == 4:
            striker["fours"] += 1
            add_commentary(inn_data, f"FOUR! {striker['name']}")
        elif runs_inc == 6:
            striker["sixes"] += 1
            add_commentary(inn_data, f"SIX! {striker['name']}")
        inn_data["this_over"].append(symbol or str(runs_inc))
    else:
        inn_data["this_over"].append(symbol)
    if is_legal and (runs_inc % 2 != 0) and not is_wicket:
        inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
        inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
    legal_balls = [b for b in inn_data["this_over"] if str(b) not in ['WD', 'NB']]
    if len(legal_balls) == BALLS_PER_OVER:
        inn_data["awaiting_bowler"] = True
    if is_wicket and inn_data["wickets"] < 10:
        inn_data["awaiting_batsman"] = True

@st.cache_resource
def get_tournament_database():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db_global = get_tournament_database()
lock = db_global["lock"]

@st.dialog("Team Squad", width="large")
def show_squad_popup(team_name: str):
    st.markdown(f"### {team_name}")
    st.markdown("---")
    squad = TEAM_DB[team_name]["squad"]
    cols = st.columns(4)
    for idx, player in enumerate(squad):
        with cols[idx % 4]:
            st.markdown(f"🏏 {player}")
    if st.button("Close", use_container_width=True):
        st.rerun()

def reset_match(match_id: str):
    with lock:
        if match_id in db_global["matches"]:
            db_global["matches"][match_id] = {"id": match_id, "team_1": db_global["matches"][match_id]["team_1"], "team_2": db_global["matches"][match_id]["team_2"], "total_overs": db_global["matches"][match_id]["total_overs"], "current_innings": 1, "match_complete": False, "innings_1": init_blank_innings(), "innings_2": init_blank_innings(), "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None}
            return True
    return False

def delete_match(match_id: str):
    with lock:
        if match_id in db_global["matches"]:
            if db_global["active_match_id"] == match_id:
                db_global["active_match_id"] = None
            del db_global["matches"][match_id]
            return True
    return False

# Sidebar - Compact
with st.sidebar:
    st.markdown("## 🏏 APL 2026")
    st.markdown("---")
    user_role = st.radio("Role:", ["👁️ Viewer", "⚡ Scorer"], horizontal=True)
    is_admin = False
    if user_role == "⚡ Scorer":
        password = st.text_input("Password:", type="password")
        if password == ADMIN_PASSWORD:
            is_admin = True
            st.success("✅ Admin")
        elif password:
            st.error("❌ Invalid")
    st.markdown("---")
    st.caption("© 2026 APL")

# Main Tabs
tab_live, tab_review, tab_teams = st.tabs(["🎮 LIVE MATCH", "📊 ARCHIVES", "🏆 TEAMS"])

# Teams Tab
with tab_teams:
    st.markdown("### Tournament Teams")
    cols = st.columns(3)
    for idx, (team_name, _) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            st.markdown(f'<div class="team-card"><h3>{team_name}</h3></div>', unsafe_allow_html=True)
            if st.button(f"View Squad", key=f"team_{idx}", use_container_width=True):
                show_squad_popup(team_name)

# Live Match Tab
with tab_live:
    # Admin controls - Compact
    if is_admin:
        with st.expander("⚙️ ADMIN CONTROLS", expanded=not bool(db_global["active_match_id"])):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**CREATE MATCH**")
                match_id = st.text_input("Match ID:", placeholder="Match_01", key="new_id")
                team1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="t1")
                team2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="t2")
                overs = st.number_input("Overs:", 1, 10, DEFAULT_OVERS, key="ov")
                if st.button("🚀 Create Match", use_container_width=True):
                    if match_id and team1 != team2:
                        with lock:
                            db_global["matches"][match_id] = {"id": match_id, "team_1": team1, "team_2": team2, "total_overs": overs, "current_innings": 1, "match_complete": False, "innings_1": init_blank_innings(), "innings_2": init_blank_innings(), "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None}
                            db_global["active_match_id"] = match_id
                        st.success(f"✅ {match_id} created")
                        st.rerun()
                    else:
                        st.error("Invalid: Different teams required")
            with col2:
                if db_global["matches"]:
                    st.markdown("**MANAGE MATCHES**")
                    matches = list(db_global["matches"].keys())
                    sel = st.selectbox("Select Match:", matches)
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Set Active", use_container_width=True):
                            db_global["active_match_id"] = sel
                            st.rerun()
                    with col_b:
                        if st.button("Reset", use_container_width=True):
                            if reset_match(sel):
                                st.success("Reset successful")
                                st.rerun()
                    with col_c:
                        if st.button("Delete", use_container_width=True):
                            if delete_match(sel):
                                st.success("Deleted")
                                st.rerun()
    
    # Live Match Display
    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("📢 No active match. Create one in Admin section.")
    else:
        m = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
        inn_key = "innings_1" if m["current_innings"] == 1 else "innings_2"
        inn = m[inn_key]
        bat_team = m["team_1"] if m["current_innings"] == 1 else m["team_2"]
        bowl_team = m["team_2"] if m["current_innings"] == 1 else m["team_1"]
        target = m["innings_1"]["runs"] + 1 if m["current_innings"] == 2 else None
        
        # Lineup Setup
        if inn["b1"]["name"] == "":
            if is_admin:
                st.warning(f"⚙️ Setup batting lineup for {bat_team}")
                with st.form("lineup"):
                    bat_squad = TEAM_DB[bat_team]["squad"]
                    bowl_squad = TEAM_DB[bowl_team]["squad"]
                    col1, col2, col3 = st.columns(3)
                    with col1: striker = st.selectbox("Striker:", bat_squad)
                    with col2: non_striker = st.selectbox("Non-Striker:", bat_squad)
                    with col3: bowler = st.selectbox("Opening Bowler:", bowl_squad)
                    if st.form_submit_button("🏏 Start Match", use_container_width=True):
                        with lock:
                            inn["b1"]["name"] = striker
                            inn["b2"]["name"] = non_striker
                            inn["bowler"]["name"] = bowler
                            add_commentary(inn, f"Match started! {bat_team} batting")
                        st.rerun()
            else:
                st.info("⏳ Waiting for scorer to start the match")
        else:
            # Calculate stats
            comp_ov = inn["balls"] // BALLS_PER_OVER
            rem_ball = inn["balls"] % BALLS_PER_OVER
            crr = (inn["runs"] / (comp_ov + rem_ball/BALLS_PER_OVER)) if (comp_ov + rem_ball/BALLS_PER_OVER) > 0 else 0
            innings_end = is_innings_complete(inn, m["total_overs"]) or (target and inn["runs"] >= target)
            status = "FINISHED" if innings_end else "LIVE"
            
            # Main Layout - 2 columns
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                # Score Box
                st.markdown(f"""
                    <div class="score-box" style="position:relative">
                        <span class="status-badge">{status}</span>
                        <h2>{bat_team} vs {bowl_team}</h2>
                        <h1>{inn['runs']} - {inn['wickets']}</h1>
                        <h3>Overs: {comp_ov}.{rem_ball} / {m['total_overs']} | Run Rate: {crr:.2f}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Target Info
                if target:
                    need = target - inn['runs']
                    balls_left = (m['total_overs'] * BALLS_PER_OVER) - inn['balls']
                    if need > 0:
                        st.warning(f"🎯 Target: {target} | Need {need} runs from {balls_left} balls")
                    else:
                        st.success(f"🏆 VICTORY! {bat_team} wins!")
                
                # Stats Row - Compact
                a, b, c, d = st.columns(4)
                with a: st.metric("Runs", inn['runs'])
                with b: st.metric("Wickets", inn['wickets'])
                with c: st.metric("Extras", inn['extras'] + inn.get('penalty', 0))
                with d: st.metric("Run Rate", f"{crr:.2f}")
                
                # Current Over Display
                st.markdown("**📦 Current Over**")
                if inn["this_over"]:
                    balls_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px;">'
                    for ball in inn["this_over"][-6:]:
                        color = "#ff6b6b" if ball in ["4","6"] else "#ef4444" if "W" in str(ball) else "#f59e0b" if any(x in str(ball) for x in ["WD","NB"]) else "#4a5568"
                        balls_html += f'<span class="ball-bubble" style="background:{color};color:white">{ball}</span>'
                    balls_html += '</div>'
                    st.markdown(balls_html, unsafe_allow_html=True)
                else:
                    st.caption("No deliveries yet")
                
                # Over History
                st.markdown("**📊 Over History**")
                if inn["over_history"]:
                    df = pd.DataFrame(inn["over_history"])
                    st.dataframe(df[["Over", "Bowler", "Score", "Timeline"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No overs recorded")
            
            with col_right:
                # Current Players Card
                st.markdown(f"""
                    <div class="info-card">
                        <h4>🏏 BATTING</h4>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span><b>{'👉 ' if inn['b1']['strike'] else ''}{inn['b1']['name']}</b></span>
                            <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']})</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span><b>{'👉 ' if inn['b2']['strike'] else ''}{inn['b2']['name']}</b></span>
                            <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']})</span>
                        </div>
                        <h4 style="margin-top: 10px;">🥎 BOWLING</h4>
                        <div style="display: flex; justify-content: space-between;">
                            <span><b>{inn['bowler']['name']}</b></span>
                            <span>W: {inn['bowler']['wickets']} | R: {inn['bowler']['runs']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Scoring Controls (Admin only)
                if is_admin and not innings_end:
                    if inn["awaiting_batsman"]:
                        st.error("☝️ Wicket! Select new batsman:")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen_history"]]
                        available = [p for p in TEAM_DB[bat_team]["squad"] if p not in used] or ["New Player"]
                        new_bat = st.selectbox("Batsman:", available, key="new_bat")
                        if st.button("✅ Confirm Batsman", use_container_width=True):
                            with lock:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen_history"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike", "dismissal_type": None}
                                else:
                                    inn["all_batsmen_history"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out", "dismissal_type": None}
                                inn["awaiting_batsman"] = False
                                add_commentary(inn, f"New batsman: {new_bat} comes to crease")
                            st.rerun()
                    
                    elif inn["awaiting_bowler"]:
                        st.success("🔄 Over complete! Select next bowler:")
                        next_bowler = st.selectbox("Bowler:", TEAM_DB[bowl_team]["squad"], key="new_bowl")
                        if st.button("✅ Confirm Bowler", use_container_width=True):
                            with lock:
                                if inn["bowler"]["name"]:
                                    inn["all_bowlers_history"].append(copy.deepcopy(inn["bowler"]))
                                inn["over_history"].append({"Over": len(inn["over_history"])+1, "Bowler": inn["bowler"]["name"], "Score": f"{inn['runs']}/{inn['wickets']}", "Timeline": ", ".join(map(str, inn["this_over"]))})
                                inn["this_over"] = []
                                inn["bowler"] = {"name": next_bowler, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn["awaiting_bowler"] = False
                                add_commentary(inn, f"New bowler: {next_bowler}")
                            st.rerun()
                    
                    else:
                        # Run buttons grid - 5x2 layout
                        st.markdown("**Run Scoring**")
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            if st.button("0", use_container_width=True):
                                with lock: process_ball_input(inn, 0, 0, True); st.rerun()
                        with col2:
                            if st.button("1", use_container_width=True):
                                with lock: process_ball_input(inn, 1, 0, True); st.rerun()
                        with col3:
                            if st.button("2", use_container_width=True):
                                with lock: process_ball_input(inn, 2, 0, True); st.rerun()
                        with col4:
                            if st.button("3", use_container_width=True):
                                with lock: process_ball_input(inn, 3, 0, True); st.rerun()
                        with col5:
                            if st.button("4", use_container_width=True):
                                with lock: process_ball_input(inn, 4, 0, True); st.rerun()
                        
                        col6, col7, col8, col9, col10 = st.columns(5)
                        with col6:
                            if st.button("6", use_container_width=True):
                                with lock: process_ball_input(inn, 6, 0, True); st.rerun()
                        with col7:
                            if st.button("WD", use_container_width=True):
                                with lock: process_ball_input(inn, 1, 1, False, symbol="WD"); st.rerun()
                        with col8:
                            if st.button("NB", use_container_width=True):
                                with lock: process_ball_input(inn, 1, 1, False, symbol="NB"); st.rerun()
                        with col9:
                            with st.popover("WICKET"):
                                st.markdown("**Dismissal Type**")
                                dismissal = st.selectbox("Type:", DISMISSAL_TYPES, key="wicket_type")
                                if st.button("Confirm Wicket", use_container_width=True):
                                    with lock: process_ball_input(inn, 0, 0, True, True, symbol="W", dismissal_type=dismissal); st.rerun()
                        with col10:
                            if st.button("SWAP", use_container_width=True):
                                with lock: 
                                    inn["b1"]["strike"], inn["b2"]["strike"] = inn["b2"]["strike"], inn["b1"]["strike"]
                                    add_commentary(inn, "Strike rotated")
                                st.rerun()
                        
                        # Utility buttons
                        col_u, col_e = st.columns(2)
                        with col_u:
                            if inn.get("undo_stack") and len(inn["undo_stack"]) > 0:
                                if st.button("↩️ Undo Last Ball", use_container_width=True):
                                    with lock:
                                        prev = inn["undo_stack"].pop()
                                        for k in prev:
                                            inn[k] = prev[k]
                                    st.rerun()
                        with col_e:
                            with st.popover("➕ Add Extras"):
                                st.markdown("**Extra Runs**")
                                extra_type = st.radio("Type:", ["Extra Run", "Penalty Run"], horizontal=True)
                                extra_runs = st.number_input("Runs:", 1, 10, 1)
                                if st.button("Add Runs", use_container_width=True):
                                    with lock:
                                        if "undo_stack" not in inn:
                                            inn["undo_stack"] = []
                                        inn["undo_stack"].append({"runs": inn["runs"], "extras": inn["extras"], "penalty": inn.get("penalty",0), "this_over": list(inn["this_over"])})
                                        inn["runs"] += extra_runs
                                        if extra_type == "Extra Run":
                                            inn["extras"] += extra_runs
                                            inn["this_over"].append(f"+{extra_runs}")
                                            add_commentary(inn, f"{extra_runs} extra runs added")
                                        else:
                                            inn["penalty"] = inn.get("penalty",0) + extra_runs
                                            inn["this_over"].append(f"Pen+{extra_runs}")
                                            add_commentary(inn, f"{extra_runs} penalty runs awarded")
                                    st.rerun()
                
                # Commentary Section
                with st.expander("📝 Ball-by-Ball Commentary", expanded=True):
                    if inn.get("commentary"):
                        for comment in inn["commentary"][-12:]:
                            st.caption(comment)
                    else:
                        st.caption("No commentary yet")
            
            # Export Section - Only PDF
            st.markdown("---")
            pdf_data = generate_pdf_bytes(m)
            if pdf_data and len(pdf_data) > 100:
                st.download_button(
                    label="📥 Download PDF Scorecard",
                    data=pdf_data,
                    file_name=f"APL_{m['id']}_Scorecard.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("📄 PDF will be available once match has data")

# Archives Tab
with tab_review:
    st.markdown("### Match Archives")
    if not db_global["matches"]:
        st.info("No matches played yet")
    else:
        sel_match = st.selectbox("Select Match:", list(db_global["matches"].keys()))
        m = ensure_match_keys(db_global["matches"][sel_match])
        
        result = get_match_result(m)
        if "🏆" in result:
            st.success(result)
        else:
            st.info(result)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Innings 1: {m['team_1']}**")
            d1 = m["innings_1"]
            if d1["b1"]["name"]:
                st.metric("Score", f"{d1['runs']}/{d1['wickets']}", f"{d1['balls']//6}.{d1['balls']%6} overs")
                if d1["over_history"]:
                    st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
            else:
                st.caption("Innings not played")
        
        with col2:
            st.markdown(f"**Innings 2: {m['team_2']}**")
            d2 = m["innings_2"]
            if d2["b1"]["name"]:
                st.metric("Score", f"{d2['runs']}/{d2['wickets']}", f"{d2['balls']//6}.{d2['balls']%6} overs")
                if d2["over_history"]:
                    st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
            else:
                st.caption("Innings not played")
        
        # PDF Export for archived match
        pdf_data = generate_pdf_bytes(m)
        if pdf_data and len(pdf_data) > 100:
            st.download_button(
                label="📥 Download Full Scorecard PDF",
                data=pdf_data,
                file_name=f"APL_{m['id']}_FullScorecard.pdf",
                mime="application/pdf",
                use_container_width=True
            )
