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
import io

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
    initial_sidebar_state="expanded"
)

# Team Database with logo URLs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"

TEAM_DB = {
    "Capital Chellengers": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/CapitalChellengers.jpeg",
        "squad": ["Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"]
    },
    "Black panther": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/Blackpanther.jpeg",
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"]
    },
    "Super Kings": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/SuperKings.jpeg",
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"]
    },
    "Power Hitter": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/PowerHitter.jpeg",
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"]
    },
    "Royal Warriors XI": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/RoyalWarriorsXl.jpeg",
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"]
    },
    "UnStoppable": {
        "logo": "https://raw.githubusercontent.com/Anscortournament/APL/main/UnStoppable.jpeg",
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"]
    }
}

DISMISSAL_TYPES = ["Bowled", "Caught", "LBW", "Run Out", "Stumped", "Hit Wicket"]

# CSS Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .score-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        position: relative;
    }
    
    .score-box h1 {
        font-size: 3rem !important;
        margin: 10px 0;
        font-weight: 800;
        color: #ffd700;
    }
    
    .status-badge {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #ff6b6b;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    .mobile-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        color: white;
    }
    
    .mobile-card h3 {
        font-size: 1rem;
        margin-bottom: 10px;
        color: #ffd700;
    }
    
    .team-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .team-card:hover {
        transform: translateY(-3px);
    }
    
    .team-card h3 {
        color: white;
        margin: 10px 0 0 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30,60,114,0.4);
    }
    
    div[data-testid="stMetric"] {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    div[data-testid="stMetric"] div {
        color: #1e3c72 !important;
        font-weight: bold !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f0f0f0;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        color: white !important;
    }
    
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .team-logo {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ffd700;
    }
    
    @media (max-width: 768px) {
        .ball-bubble {
            width: 32px;
            height: 32px;
            font-size: 0.75rem;
        }
        
        .team-logo {
            width: 40px;
            height: 40px;
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
    return inn

def ensure_match_keys(m: Dict) -> MatchData:
    if not isinstance(m, dict):
        m = {"id": "Match", "team_1": "Team 1", "team_2": "Team 2", "total_overs": DEFAULT_OVERS, "current_innings": 1, "match_complete": False, "innings_1": init_blank_innings(), "innings_2": init_blank_innings(), "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None}
    for key in ["innings_1", "innings_2"]:
        if key not in m:
            m[key] = init_blank_innings()
        m[key] = ensure_innings_keys(m[key])
    if "current_innings" not in m:
        m["current_innings"] = 1
    if "total_overs" not in m:
        m["total_overs"] = DEFAULT_OVERS
    if "id" not in m:
        m["id"] = "Match"
    return m

def is_innings_complete(inn: InningsData, total_overs: int) -> bool:
    return (inn["balls"] >= total_overs * BALLS_PER_OVER) or (inn["wickets"] >= 10)

def get_match_result(m: MatchData) -> str:
    m = ensure_match_keys(m)
    if m.get("winner"):
        return f"🏆 WINNER: {m['winner']} ({m.get('win_margin', '')})"
    d1, d2 = m["innings_1"], m["innings_2"]
    if d1["b1"]["name"] == "":
        return "⚙️ Setup Required"
    if m["current_innings"] == 1:
        if is_innings_complete(d1, m["total_overs"]):
            return f"📊 Innings 1 Complete: {d1['runs']}/{d1['wickets']}"
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

def generate_pdf_bytes(m: MatchData) -> bytes:
    """Generate PDF scorecard"""
    try:
        m = ensure_match_keys(m)
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "APL 2026 - MATCH SCORECARD", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"{m['team_1']} vs {m['team_2']}", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Match ID: {m['id']} | Overs: {m['total_overs']}", ln=True, align="C")
        pdf.ln(5)
        
        # Result
        result = get_match_result(m)
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 8, result, ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # Innings 1
        d1 = m["innings_1"]
        if d1["b1"]["name"]:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"INNINGS 1: {m['team_1']}", ln=True)
            overs = f"{d1['balls']//6}.{d1['balls']%6}"
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 6, f"Score: {d1['runs']}/{d1['wickets']} ({overs} overs)", ln=True)
            pdf.ln(4)
            
            # Batting
            pdf.set_font("Arial", "B", 9)
            pdf.cell(70, 6, "Batsman", 1)
            pdf.cell(25, 6, "Runs", 1, 0, "C")
            pdf.cell(25, 6, "Balls", 1, 0, "C")
            pdf.cell(20, 6, "4s", 1, 0, "C")
            pdf.cell(20, 6, "6s", 1, 0, "C")
            pdf.cell(30, 6, "Status", 1, 1, "C")
            
            pdf.set_font("Arial", "", 8)
            for b in [d1["b1"], d1["b2"]] + d1.get("all_batsmen_history", []):
                if b["name"]:
                    pdf.cell(70, 5, b["name"][:30], 1)
                    pdf.cell(25, 5, str(b["runs"]), 1, 0, "C")
                    pdf.cell(25, 5, str(b["balls"]), 1, 0, "C")
                    pdf.cell(20, 5, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(20, 5, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(30, 5, b.get("status", "Out")[:20], 1, 1, "C")
            pdf.ln(4)
        
        # Innings 2
        d2 = m["innings_2"]
        if d2["b1"]["name"]:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"INNINGS 2: {m['team_2']}", ln=True)
            overs = f"{d2['balls']//6}.{d2['balls']%6}"
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 6, f"Score: {d2['runs']}/{d2['wickets']} ({overs} overs)", ln=True)
            pdf.ln(4)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(70, 6, "Batsman", 1)
            pdf.cell(25, 6, "Runs", 1, 0, "C")
            pdf.cell(25, 6, "Balls", 1, 0, "C")
            pdf.cell(20, 6, "4s", 1, 0, "C")
            pdf.cell(20, 6, "6s", 1, 0, "C")
            pdf.cell(30, 6, "Status", 1, 1, "C")
            
            pdf.set_font("Arial", "", 8)
            for b in [d2["b1"], d2["b2"]] + d2.get("all_batsmen_history", []):
                if b["name"]:
                    pdf.cell(70, 5, b["name"][:30], 1)
                    pdf.cell(25, 5, str(b["runs"]), 1, 0, "C")
                    pdf.cell(25, 5, str(b["balls"]), 1, 0, "C")
                    pdf.cell(20, 5, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(20, 5, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(30, 5, b.get("status", "Out")[:20], 1, 1, "C")
        
        return pdf.output(dest='S').encode('latin-1', errors='replace')
    except Exception as e:
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
    st.markdown(f"### {team_name} Squad")
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
            db_global["matches"][match_id]["innings_1"] = init_blank_innings()
            db_global["matches"][match_id]["innings_2"] = init_blank_innings()
            db_global["matches"][match_id]["current_innings"] = 1
            db_global["matches"][match_id]["winner"] = None
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

# Sidebar
with st.sidebar:
    st.markdown("## 🏏 APL 2026")
    st.markdown("---")
    user_role = st.radio("Role:", ["👁️ Viewer", "⚡ Scorer"])
    is_admin = False
    if user_role == "⚡ Scorer":
        password = st.text_input("Password:", type="password")
        if password == ADMIN_PASSWORD:
            is_admin = True
            st.success("✅ Admin Access")
        elif password:
            st.error("❌ Invalid")
    st.markdown("---")
    st.caption("© 2026 APL Tournament")

# Main Tabs
tab_live, tab_review, tab_teams = st.tabs(["🎮 LIVE MATCH", "📊 ARCHIVES", "🏆 TEAMS"])

# Teams Tab
with tab_teams:
    st.markdown("### 🏆 Tournament Teams")
    cols = st.columns(3)
    for idx, (team_name, team_data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="team-card">
                    <img src="{team_data['logo']}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover;">
                    <h3>{team_name}</h3>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"View Squad", key=f"team_{idx}", use_container_width=True):
                show_squad_popup(team_name)

# Live Match Tab
with tab_live:
    # Admin controls
    if is_admin:
        with st.expander("⚙️ ADMIN CONTROLS", expanded=not bool(db_global["active_match_id"])):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**CREATE NEW MATCH**")
                match_id = st.text_input("Match ID:", placeholder="Match_01", key="new_match_id")
                team1 = st.selectbox("Team 1 (Batting First):", list(TEAM_DB.keys()), key="team1")
                team2 = st.selectbox("Team 2 (Bowling First):", list(TEAM_DB.keys()), key="team2")
                overs = st.number_input("Overs:", 1, 10, DEFAULT_OVERS, key="overs")
                if st.button("🚀 Create Match", use_container_width=True):
                    if match_id and team1 != team2:
                        with lock:
                            db_global["matches"][match_id] = {
                                "id": match_id, "team_1": team1, "team_2": team2,
                                "total_overs": overs, "current_innings": 1, "match_complete": False,
                                "innings_1": init_blank_innings(), "innings_2": init_blank_innings(),
                                "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None
                            }
                            db_global["active_match_id"] = match_id
                        st.success(f"✅ Match '{match_id}' created!")
                        st.rerun()
                    else:
                        st.error("Please enter unique ID and different teams")
            with col2:
                if db_global["matches"]:
                    st.markdown("**MANAGE MATCHES**")
                    matches = list(db_global["matches"].keys())
                    sel = st.selectbox("Select Match:", matches, key="select_match")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Set Active", use_container_width=True):
                            db_global["active_match_id"] = sel
                            st.rerun()
                    with col_b:
                        if st.button("Reset", use_container_width=True):
                            reset_match(sel)
                            st.rerun()
                    with col_c:
                        if st.button("Delete", use_container_width=True):
                            delete_match(sel)
                            st.rerun()
    
    # Live Match Display
    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("🏏 No active match. Create one in Admin section above.")
    else:
        m = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
        
        # Auto-switch to innings 2 when innings 1 is complete
        inn1_complete = is_innings_complete(m["innings_1"], m["total_overs"])
        if m["current_innings"] == 1 and inn1_complete and m["innings_1"]["b1"]["name"]:
            with lock:
                m["current_innings"] = 2
                add_commentary(m["innings_2"], f"🏏 INNINGS 2 STARTED! {m['team_2']} needs {m['innings_1']['runs'] + 1} runs")
            st.rerun()
        
        inn_key = "innings_1" if m["current_innings"] == 1 else "innings_2"
        inn = m[inn_key]
        bat_team = m["team_1"] if m["current_innings"] == 1 else m["team_2"]
        bowl_team = m["team_2"] if m["current_innings"] == 1 else m["team_1"]
        target = m["innings_1"]["runs"] + 1 if m["current_innings"] == 2 else None
        
        # Team logos display
        col_logo1, col_vs, col_logo2 = st.columns([1, 1, 1])
        with col_logo1:
            st.image(TEAM_DB[bat_team]["logo"], width=80)
            st.caption(bat_team)
        with col_vs:
            st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
        with col_logo2:
            st.image(TEAM_DB[bowl_team]["logo"], width=80)
            st.caption(bowl_team)
        
        # Lineup Setup
        if inn["b1"]["name"] == "":
            if is_admin:
                st.warning(f"### ⚙️ Configure {bat_team} Batting Lineup")
                with st.form("lineup_form"):
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
                            add_commentary(inn, f"MATCH STARTED! {bat_team} batting")
                            if m["current_innings"] == 2:
                                add_commentary(inn, f"Target: {target} runs")
                        st.rerun()
            else:
                st.info("⏳ Waiting for scorer to start the match")
        else:
            # Calculate stats
            comp_ov = inn["balls"] // BALLS_PER_OVER
            rem_ball = inn["balls"] % BALLS_PER_OVER
            frac_ov = comp_ov + (rem_ball / BALLS_PER_OVER) if BALLS_PER_OVER > 0 else 0
            crr = (inn["runs"] / frac_ov) if frac_ov > 0 else 0
            innings_end = is_innings_complete(inn, m["total_overs"]) or (target and inn["runs"] >= target)
            status = "FINISHED" if innings_end else ("INNINGS 2" if m["current_innings"] == 2 else "INNINGS 1")
            
            # Target info
            if m["current_innings"] == 2 and not innings_end:
                need = target - inn['runs']
                balls_left = (m["total_overs"] * BALLS_PER_OVER) - inn['balls']
                st.warning(f"🎯 **Target: {target}** | {bat_team} needs {need} runs from {balls_left} balls")
            elif m["current_innings"] == 2 and inn['runs'] >= target:
                st.success(f"🏆 **{bat_team} WINS!**")
            elif m["current_innings"] == 1 and is_innings_complete(inn, m["total_overs"]):
                st.success(f"📊 **Innings 1 Complete!** {bat_team} scored {inn['runs']}/{inn['wickets']}")
            
            # Main Layout
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">{status}</span>
                        <h1>{inn['runs']} - {inn['wickets']}</h1>
                        <h3>Overs: {comp_ov}.{rem_ball} / {m['total_overs']} | Run Rate: {crr:.2f}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Stats
                a, b, c, d = st.columns(4)
                a.metric("Total Runs", inn['runs'])
                b.metric("Wickets", inn['wickets'])
                c.metric("Extras", inn['extras'] + inn.get('penalty', 0))
                d.metric("Run Rate", f"{crr:.2f}")
                
                # Current Over
                st.markdown("**📦 Current Over**")
                if inn["this_over"]:
                    balls_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px;">'
                    for ball in inn["this_over"][-6:]:
                        color = "#10B981" if ball in ["4", "6"] else "#EF4444" if "W" in str(ball) else "#F59E0B" if any(x in str(ball) for x in ["WD", "NB"]) else "#6B7280"
                        balls_html += f'<span class="ball-bubble" style="background:{color};color:white; display:inline-flex; align-items:center; justify-content:center; width:40px; height:40px; border-radius:50%; margin:3px; font-weight:bold;">{ball}</span>'
                    balls_html += '</div>'
                    st.markdown(balls_html, unsafe_allow_html=True)
                else:
                    st.info("No deliveries yet this over")
                
                # Over History
                st.markdown("**📊 Over History**")
                if inn["over_history"]:
                    df = pd.DataFrame(inn["over_history"])
                    st.dataframe(df[["Over", "Bowler", "Score", "Timeline"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No overs recorded yet")
            
            with col_right:
                st.markdown(f"""
                    <div class="mobile-card">
                        <h3>🏏 BATTING</h3>
                        <div style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span><b>{'👉 ' if inn['b1']['strike'] else ''}{inn['b1']['name']}</b></span>
                                <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}b)</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                <span><b>{'👉 ' if inn['b2']['strike'] else ''}{inn['b2']['name']}</b></span>
                                <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}b)</span>
                            </div>
                        </div>
                        <h3>🥎 BOWLING</h3>
                        <div style="margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span><b>{inn['bowler']['name']}</b></span>
                                <span>Wickets: {inn['bowler']['wickets']} | Runs: {inn['bowler']['runs']}</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Scoring Controls (Admin only)
                if is_admin and not innings_end:
                    if inn["awaiting_batsman"]:
                        st.error("☝️ Wicket! Select new batsman:")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen_history"]]
                        available = [p for p in TEAM_DB[bat_team]["squad"] if p not in used] or ["New Player"]
                        new_bat = st.selectbox("Incoming Batsman:", available, key="new_bat")
                        if st.button("✅ Confirm Batsman", use_container_width=True):
                            with lock:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen_history"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike", "dismissal_type": None}
                                else:
                                    inn["all_batsmen_history"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out", "dismissal_type": None}
                                inn["awaiting_batsman"] = False
                                add_commentary(inn, f"New batsman: {new_bat} comes to the crease")
                            st.rerun()
                    elif inn["awaiting_bowler"]:
                        st.success("🔄 Over complete! Select next bowler:")
                        next_bowler = st.selectbox("Next Bowler:", TEAM_DB[bowl_team]["squad"], key="new_bowler")
                        if st.button("✅ Confirm Bowler", use_container_width=True):
                            with lock:
                                if inn["bowler"]["name"]:
                                    inn["all_bowlers_history"].append(copy.deepcopy(inn["bowler"]))
                                inn["over_history"].append({
                                    "Over": len(inn["over_history"]) + 1,
                                    "Bowler": inn["bowler"]["name"],
                                    "Score": f"{inn['runs']}/{inn['wickets']}",
                                    "Timeline": ", ".join(map(str, inn["this_over"]))
                                })
                                inn["this_over"] = []
                                inn["bowler"] = {"name": next_bowler, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn["awaiting_bowler"] = False
                                add_commentary(inn, f"New bowler: {next_bowler}")
                            st.rerun()
                    else:
                        # Run buttons
                        cols = st.columns(5)
                        for idx, val in enumerate([0, 1, 2, 3, 4]):
                            with cols[idx]:
                                if st.button(str(val), use_container_width=True):
                                    with lock: process_ball_input(inn, val, 0, True); st.rerun()
                        
                        cols2 = st.columns(5)
                        with cols2[0]:
                            if st.button("6", use_container_width=True):
                                with lock: process_ball_input(inn, 6, 0, True); st.rerun()
                        with cols2[1]:
                            if st.button("WD", use_container_width=True):
                                with lock: process_ball_input(inn, 1, 1, False, symbol="WD"); st.rerun()
                        with cols2[2]:
                            if st.button("NB", use_container_width=True):
                                with lock: process_ball_input(inn, 1, 1, False, symbol="NB"); st.rerun()
                        with cols2[3]:
                            with st.popover("WICKET"):
                                st.markdown("### Dismissal Type")
                                dismissal = st.selectbox("Select:", DISMISSAL_TYPES, key="wicket_dismissal")
                                if st.button("Confirm Wicket", use_container_width=True):
                                    with lock: process_ball_input(inn, 0, 0, True, True, symbol="W", dismissal_type=dismissal); st.rerun()
                        with cols2[4]:
                            if st.button("SWAP", use_container_width=True):
                                with lock: inn["b1"]["strike"], inn["b2"]["strike"] = inn["b2"]["strike"], inn["b1"]["strike"]; add_commentary(inn, "Strike rotated"); st.rerun()
                        
                        # Undo button
                        if inn.get("undo_stack") and len(inn["undo_stack"]) > 0:
                            if st.button("↩️ Undo Last Ball", use_container_width=True):
                                with lock:
                                    prev = inn["undo_stack"].pop()
                                    for k in prev:
                                        inn[k] = prev[k]
                                st.rerun()
                        
                        # Extras
                        with st.expander("➕ Add Extras"):
                            extra_type = st.radio("Type:", ["Extra Run", "Penalty Run"], horizontal=True)
                            extra_runs = st.number_input("Runs:", 1, 10, 1)
                            if st.button("Add Runs", use_container_width=True):
                                with lock:
                                    if "undo_stack" not in inn:
                                        inn["undo_stack"] = []
                                    inn["undo_stack"].append({"runs": inn["runs"], "extras": inn["extras"], "penalty": inn.get("penalty", 0), "this_over": list(inn["this_over"])})
                                    inn["runs"] += extra_runs
                                    if extra_type == "Extra Run":
                                        inn["extras"] += extra_runs
                                        inn["this_over"].append(f"+{extra_runs}")
                                        add_commentary(inn, f"{extra_runs} extra runs added")
                                    else:
                                        inn["penalty"] = inn.get("penalty", 0) + extra_runs
                                        inn["this_over"].append(f"Pen+{extra_runs}")
                                        add_commentary(inn, f"{extra_runs} penalty runs awarded")
                                st.rerun()
                
                # Commentary
                with st.expander("📝 Ball-by-Ball Commentary", expanded=False):
                    if inn.get("commentary"):
                        for comment in inn["commentary"][-15:]:
                            st.caption(comment)
                    else:
                        st.caption("No commentary yet")
            
            # PDF Export Button
            st.markdown("---")
            pdf_data = generate_pdf_bytes(m)
            if pdf_data and len(pdf_data) > 500:
                st.download_button(
                    label="📥 DOWNLOAD PDF SCORECARD",
                    data=pdf_data,
                    file_name=f"APL_{m['id']}_Scorecard.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.info("📄 PDF will be available once match data is entered. Please add some overs first.")

# Archives Tab
with tab_review:
    st.markdown("### 📊 Match Archives")
    if not db_global["matches"]:
        st.info("No matches played yet. Create a match in Live Match tab!")
    else:
        sel = st.selectbox("Select Match to Review:", list(db_global["matches"].keys()))
        m = ensure_match_keys(db_global["matches"][sel])
        
        result = get_match_result(m)
        if "WINNER" in result or "VICTORY" in result:
            st.success(result)
        elif "Tied" in result:
            st.warning(result)
        else:
            st.info(result)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Innings 1: {m['team_1']}")
            d1 = m["innings_1"]
            if d1["b1"]["name"]:
                st.metric("Score", f"{d1['runs']}/{d1['wickets']}", f"{d1['balls']//6}.{d1['balls']%6} overs")
                if d1["over_history"]:
                    st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
            else:
                st.caption("Innings not played")
        with col2:
            st.subheader(f"Innings 2: {m['team_2']}")
            d2 = m["innings_2"]
            if d2["b1"]["name"]:
                st.metric("Score", f"{d2['runs']}/{d2['wickets']}", f"{d2['balls']//6}.{d2['balls']%6} overs")
                if d2["over_history"]:
                    st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
            else:
                st.caption("Innings not played")
        
        # PDF for archived match
        pdf_data = generate_pdf_bytes(m)
        if pdf_data and len(pdf_data) > 500:
            st.download_button(
                label="📥 Download Full Scorecard PDF",
                data=pdf_data,
                file_name=f"APL_{m['id']}_FullScorecard.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
