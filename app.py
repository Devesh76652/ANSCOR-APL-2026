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

# Constants
BALLS_PER_OVER = 6
MAX_WICKETS = 10
DEFAULT_OVERS = 4
ADMIN_PASSWORD = st.secrets.get("admin_password", "anscor2026")  # Use secrets in production

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False
    st.warning("Install 'streamlit-autorefresh' for auto-refresh features: pip install streamlit-autorefresh")

# Page Configuration
st.set_page_config(
    page_title="APL 2026 - Advanced Cricket Scoring System",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Raw GitHub repository directory path configuration
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"

# Official Tournament Team Database
TEAM_DB = {
    "Capital Chellengers": {
        "local": "CapitalChellengers.jpeg",
        "remote": GITHUB_RAW_BASE + "CapitalChellengers.jpeg",
        "squad": [
            "Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", 
            "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", 
            "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"
        ]
    },
    "Black panther": {
        "local": "Blackpanther.jpeg",
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": [
            "Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", 
            "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", 
            "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", 
            "Akash nagade"
        ]
    },
    "Super Kings": {
        "local": "SuperKings.jpeg",
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": [
            "Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", 
            "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", 
            "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", 
            "Sudhir pal"
        ]
    },
    "Power Hitter": {
        "local": "PowerHitter.jpeg",
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": [
            "Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", 
            "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", 
            "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"
        ]
    },
    "Royal Warriors XI": {
        "local": "RoyalWarriorsXI.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": [
            "Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", 
            "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", 
            "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"
        ]
    },
    "UnStoppable": {
        "local": "UnStoppable.jpeg",
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": [
            "Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", 
            "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", 
            "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"
        ]
    }
}

# Dismissal types
DISMISSAL_TYPES = [
    "Bowled", "Caught", "LBW", "Run Out", "Stumped", 
    "Hit Wicket", "Obstructing Field", "Retired Hurt"
]

def get_image_src(local_path: str, remote_url: str = "") -> str:
    """Get image source as base64 or remote URL"""
    if isinstance(local_path, list):
        local_path = local_path[0] if len(local_path) > 0 else ""
    if isinstance(remote_url, list):
        remote_url = remote_url[0] if len(remote_url) > 0 else ""
        
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            ext = local_path.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
        except:
            pass
    return remote_url

def smart_load_image(local_path: str, remote_url: str, width: int = None, use_container: bool = True) -> bool:
    """Smart load image from local or remote"""
    if isinstance(local_path, list):
        local_path = local_path[0] if len(local_path) > 0 else ""
    if isinstance(remote_url, list):
        remote_url = remote_url[0] if len(remote_url) > 0 else ""
        
    if local_path and os.path.exists(local_path):
        try:
            st.image(local_path, width=width, use_container_width=use_container)
            return True
        except:
            pass
    try:
        st.image(remote_url, width=width, use_container_width=use_container)
        return True
    except:
        pass
    return False

# Custom CSS Stylesheet Config
st.markdown("""
    <style>
    .block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }
    .score-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: white;
        padding: 18px; border-radius: 12px; text-align: center; margin-bottom: 10px;
        border: 2px solid #1E40AF; position: relative; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    .status-badge {
        position: absolute; top: 10px; right: 15px; background-color: #EF4444; color: white;
        padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; letter-spacing: 1px;
    }
    .mobile-card { background-color: #1E293B; border: 1px solid #334155; padding: 12px; border-radius: 10px; margin-bottom: 10px; }
    .ball-bubble {
        display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px;
        border-radius: 50%; margin: 3px; font-weight: 800; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.1);
    }
    .team-block-container { background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 10px; }
    div[data-testid="stMetric"] { background-color: #1E293B; padding: 10px; border-radius: 8px; border: 1px solid #334155; }
    
    @media (max-width: 768px) {
        .score-box h1 { font-size: 2rem !important; }
        .ball-bubble { width: 28px; height: 28px; font-size: 0.7rem; }
        .block-container { padding: 0.25rem 0.5rem !important; }
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
    """Initialize blank innings data structure"""
    return {
        "runs": 0,
        "wickets": 0,
        "balls": 0,
        "extras": 0,
        "penalty": 0,
        "this_over": [],
        "over_history": [],
        "b1": {
            "name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
            "strike": True, "status": "Not Out", "dismissal_type": None
        },
        "b2": {
            "name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
            "strike": False, "status": "Not Out", "dismissal_type": None
        },
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [],
        "all_bowlers_history": [],
        "undo_stack": [],
        "awaiting_batsman": False,
        "awaiting_bowler": False,
        "commentary": []
    }

def ensure_innings_keys(inn: Dict) -> InningsData:
    """Ensure innings has all required keys"""
    if not isinstance(inn, dict):
        inn = init_blank_innings()
    defaults = init_blank_innings()
    for k, v in defaults.items():
        if k not in inn:
            inn[k] = v
    for player_key in ["b1", "b2", "bowler"]:
        if player_key in inn:
            if not isinstance(inn[player_key], dict):
                inn[player_key] = copy.deepcopy(defaults[player_key])
            for pk, pv in defaults[player_key].items():
                if pk not in inn[player_key]:
                    inn[player_key][pk] = pv
    return inn

def ensure_match_keys(m: Dict) -> MatchData:
    """Ensure match has all required keys"""
    if not isinstance(m, dict):
        m = {
            "id": "Match", "team_1": "Team 1", "team_2": "Team 2",
            "total_overs": DEFAULT_OVERS, "current_innings": 1, "match_complete": False,
            "innings_1": init_blank_innings(), "innings_2": init_blank_innings(),
            "created_at": datetime.now().isoformat(), "winner": None, "win_margin": None
        }
    if "team_1" not in m:
        m["team_1"] = m.get("batting_team_i1", m.get("team_a", "Team 1"))
    if "team_2" not in m:
        m["team_2"] = m.get("bowling_team_i1", m.get("team_b", "Team 2"))
    if "innings_1" not in m or isinstance(m["innings_1"], list):
        m["innings_1"] = init_blank_innings()
    if "innings_2" not in m or isinstance(m["innings_2"], list):
        m["innings_2"] = init_blank_innings()
    m["innings_1"] = ensure_innings_keys(m["innings_1"])
    m["innings_2"] = ensure_innings_keys(m["innings_2"])
    if "current_innings" not in m:
        m["current_innings"] = 1
    if "total_overs" not in m:
        m["total_overs"] = DEFAULT_OVERS
    if "id" not in m:
        m["id"] = "Match"
    if "created_at" not in m:
        m["created_at"] = datetime.now().isoformat()
    if "winner" not in m:
        m["winner"] = None
    if "win_margin" not in m:
        m["win_margin"] = None
    return m

def is_innings_complete(inn: InningsData, total_overs: int) -> bool:
    """Check if innings is complete"""
    return (inn["balls"] >= total_overs * BALLS_PER_OVER) or (inn["wickets"] >= MAX_WICKETS)

def get_match_result(m: MatchData) -> str:
    """Get current match result/status"""
    m = ensure_match_keys(m)
    
    # Check if match already has a winner
    if m.get("winner"):
        return f"🏆 WINNER: {m['winner']} ({m.get('win_margin', '')})"
    
    d1 = m["innings_1"]
    d2 = m["innings_2"]
    
    if d1["b1"]["name"] == "":
        return "Setup State: Awaiting match lineup configuration."
        
    runs_i1 = d1["runs"]
    wickets_i1 = d1["wickets"]
    
    # Innings 1 not started/completed
    if m["current_innings"] == 1:
        if is_innings_complete(d1, m["total_overs"]):
            return f"Innings 1 Complete: {m['team_1']} scored {runs_i1}/{wickets_i1}. Ready for chase."
        else:
            return f"🏏 Innings 1 in Progress: {m['team_1']} batting"
    
    # Innings 2 logic
    runs_i2 = d2["runs"]
    wickets_i2 = d2["wickets"]
    balls_i2 = d2["balls"]
    
    target = runs_i1 + 1
    
    # Check for win conditions
    if runs_i2 >= target:
        wickets_won = MAX_WICKETS - wickets_i2
        margin = f"by {wickets_won} wickets"
        m["winner"] = m["team_2"]
        m["win_margin"] = margin
        return f"🏆 WINNER: {m['team_2']} won {margin}!"
        
    if is_innings_complete(d2, m["total_overs"]):
        if runs_i2 < runs_i1:
            margin = runs_i1 - runs_i2
            result = f"by {margin} runs"
            m["winner"] = m["team_1"]
            m["win_margin"] = result
            return f"🏆 WINNER: {m['team_1']} won {result}!"
        elif runs_i2 == runs_i1:
            m["winner"] = "Match Tied"
            m["win_margin"] = ""
            return "🎯 RESULT: Match Tied!"
            
    runs_needed = target - runs_i2
    balls_rem = (m["total_overs"] * BALLS_PER_OVER) - balls_i2
    return f"🎯 Chase in Progress: {m['team_2']} needs {runs_needed} runs from {balls_rem} balls"

def clean_for_pdf(text: str) -> str:
    """Clean text for PDF encoding"""
    if text is None:
        return ""
    text = str(text)
    
    # Replace Unicode characters
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    
    # Remove emojis
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_innings_table(pdf: FPDF, inn_data: InningsData, team_name: str, innings_num: int):
    """Generate batting and bowling tables for an innings"""
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_for_pdf(f"INNINGS #{innings_num}: {team_name} BATTING"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    comp_ov = inn_data["balls"] // BALLS_PER_OVER
    rem_bl = inn_data["balls"] % BALLS_PER_OVER
    frac_ov = comp_ov + (rem_bl / BALLS_PER_OVER) if BALLS_PER_OVER > 0 else 0
    crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
    
    # Summary
    pdf.cell(95, 6, clean_for_pdf(f"Score: {inn_data['runs']}/{inn_data['wickets']} ({comp_ov}.{rem_bl} overs)"), 0, 0)
    pdf.cell(95, 6, clean_for_pdf(f"Run Rate: {crr:.2f}"), 0, 1)
    pdf.cell(95, 6, clean_for_pdf(f"Extras: {inn_data['extras']}"), 0, 0)
    pdf.cell(95, 6, clean_for_pdf(f"Penalties: {inn_data.get('penalty', 0)}"), 0, 1)
    pdf.ln(4)
    
    # Batting table
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(70, 6, "Batsman", 1)
    pdf.cell(25, 6, "Runs", 1, 0, "C")
    pdf.cell(25, 6, "Balls", 1, 0, "C")
    pdf.cell(20, 6, "4s", 1, 0, "C")
    pdf.cell(20, 6, "6s", 1, 0, "C")
    pdf.cell(30, 6, "Status", 1, 1, "C")
    
    pdf.set_font("Helvetica", "", 8)
    # Active batsmen
    for b_key in ["b1", "b2"]:
        b_data = inn_data[b_key]
        if b_data["name"]:
            strike_marker = " *" if b_data.get("strike", False) else ""
            pdf.cell(70, 5, clean_for_pdf(f"{b_data['name']}{strike_marker}"), 1)
            pdf.cell(25, 5, str(b_data["runs"]), 1, 0, "C")
            pdf.cell(25, 5, str(b_data["balls"]), 1, 0, "C")
            pdf.cell(20, 5, str(b_data.get("fours", 0)), 1, 0, "C")
            pdf.cell(20, 5, str(b_data.get("sixes", 0)), 1, 0, "C")
            pdf.cell(30, 5, clean_for_pdf(b_data.get("status", "Active")), 1, 1, "C")
    
    # Dismissed batsmen
    for b_hist in inn_data.get("all_batsmen_history", []):
        pdf.cell(70, 5, clean_for_pdf(b_hist["name"]), 1)
        pdf.cell(25, 5, str(b_hist["runs"]), 1, 0, "C")
        pdf.cell(25, 5, str(b_hist["balls"]), 1, 0, "C")
        pdf.cell(20, 5, str(b_hist.get("fours", 0)), 1, 0, "C")
        pdf.cell(20, 5, str(b_hist.get("sixes", 0)), 1, 0, "C")
        pdf.cell(30, 5, clean_for_pdf(b_hist.get("status", "Out")), 1, 1, "C")
        
    pdf.ln(4)
    
    # Bowling table
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(80, 6, "Bowler", 1)
    pdf.cell(30, 6, "Overs", 1, 0, "C")
    pdf.cell(30, 6, "Runs", 1, 0, "C")
    pdf.cell(30, 6, "Wickets", 1, 0, "C")
    pdf.cell(30, 6, "Economy", 1, 1, "C")
    
    pdf.set_font("Helvetica", "", 8)
    # Current bowler
    cw_bowler = inn_data["bowler"]
    if cw_bowler["name"]:
        overs = cw_bowler["balls"] / BALLS_PER_OVER
        eco = cw_bowler["runs"] / overs if overs > 0 else 0
        pdf.cell(80, 5, clean_for_pdf(cw_bowler["name"] + " (Current)"), 1)
        pdf.cell(30, 5, f"{cw_bowler['balls'] // BALLS_PER_OVER}.{cw_bowler['balls'] % BALLS_PER_OVER}", 1, 0, "C")
        pdf.cell(30, 5, str(cw_bowler["runs"]), 1, 0, "C")
        pdf.cell(30, 5, str(cw_bowler["wickets"]), 1, 0, "C")
        pdf.cell(30, 5, f"{eco:.2f}", 1, 1, "C")
    
    # Historical bowlers
    for bowl_h in inn_data.get("all_bowlers_history", []):
        overs = bowl_h["balls"] / BALLS_PER_OVER
        eco = bowl_h["runs"] / overs if overs > 0 else 0
        pdf.cell(80, 5, clean_for_pdf(bowl_h["name"]), 1)
        pdf.cell(30, 5, f"{bowl_h['balls'] // BALLS_PER_OVER}.{bowl_h['balls'] % BALLS_PER_OVER}", 1, 0, "C")
        pdf.cell(30, 5, str(bowl_h["runs"]), 1, 0, "C")
        pdf.cell(30, 5, str(bowl_h["wickets"]), 1, 0, "C")
        pdf.cell(30, 5, f"{eco:.2f}", 1, 1, "C")
        
    pdf.ln(4)

def generate_over_history_table(pdf: FPDF, inn_data: InningsData):
    """Generate over history table"""
    if not inn_data.get("over_history"):
        return
        
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(25, 6, "Over", 1)
    pdf.cell(50, 6, "Bowler", 1)
    pdf.cell(40, 6, "Score", 1)
    pdf.cell(75, 6, "Deliveries", 1, ln=True)
    
    pdf.set_font("Helvetica", "", 8)
    for ov in inn_data.get("over_history", []):
        pdf.cell(25, 5, str(ov.get("Over", "")), 1)
        pdf.cell(50, 5, clean_for_pdf(str(ov.get("Bowler", ""))), 1)
        pdf.cell(40, 5, str(ov.get("Score", "")), 1)
        timeline = ov.get("Timeline", "")
        if len(timeline) > 60:
            timeline = timeline[:57] + "..."
        pdf.cell(75, 5, clean_for_pdf(timeline), 1, ln=True)
        
    pdf.ln(6)

def generate_pdf_bytes(m: MatchData) -> bytes:
    """Generate comprehensive match PDF report"""
    m = ensure_match_keys(m)
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean_for_pdf("APL 2026 - COMPLETE MATCH SCORECARD"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, clean_for_pdf(f"{m['team_1']} vs {m['team_2']} ({m['total_overs']} Overs Match)"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, clean_for_pdf(f"Match ID: {m['id']} | Date: {m.get('created_at', 'N/A')[:10]}"), ln=True, align="C")
    pdf.ln(4)
    
    # Result
    match_outcome = get_match_result(m)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 8, clean_for_pdf(f"RESULT: {match_outcome}"), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)
    
    # Generate innings reports
    innings_data = [
        (m["innings_1"], m["team_1"], 1),
        (m["innings_2"], m["team_2"], 2)
    ]
    
    for inn_data, team_name, inn_num in innings_data:
        if inn_data["b1"]["name"]:  # Only show if innings has started
            generate_innings_table(pdf, inn_data, team_name, inn_num)
            generate_over_history_table(pdf, inn_data)
            
            # Add page break between innings if needed
            if inn_num == 1 and m["innings_2"]["b1"]["name"]:
                pdf.add_page()
    
    # Commentary section
    all_commentary = []
    for inn_num in [1, 2]:
        inn_key = f"innings_{inn_num}"
        commentary = m[inn_key].get("commentary", [])
        if commentary:
            all_commentary.extend([f"Innings {inn_num}: {c}" for c in commentary[-20:]])  # Last 20 balls
    
    if all_commentary:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "BALL-BY-BALL COMMENTARY (Last 20 balls)", ln=True)
        pdf.set_font("Helvetica", "", 8)
        for comment in all_commentary[-20:]:
            pdf.cell(0, 4, clean_for_pdf(comment), ln=True)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def add_commentary(inn_data: InningsData, message: str):
    """Add commentary entry"""
    if "commentary" not in inn_data:
        inn_data["commentary"] = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    inn_data["commentary"].append(f"[{timestamp}] {message}")
    # Keep only last 100 entries
    if len(inn_data["commentary"]) > 100:
        inn_data["commentary"] = inn_data["commentary"][-100:]

def process_ball_input(
    inn_data: InningsData,
    runs_inc: int,
    extra_inc: int = 0,
    is_legal: bool = True,
    is_wicket: bool = False,
    symbol: Optional[str] = None,
    dismissal_type: Optional[str] = None,
    bowler_name: Optional[str] = None
):
    """Process a ball input with proper state management"""
    # Save state for undo
    state_snap = copy.deepcopy({
        "runs": inn_data["runs"],
        "wickets": inn_data["wickets"],
        "balls": inn_data["balls"],
        "extras": inn_data["extras"],
        "penalty": inn_data.get("penalty", 0),
        "this_over": list(inn_data["this_over"]),
        "over_history": copy.deepcopy(inn_data["over_history"]),
        "b1": copy.deepcopy(inn_data["b1"]),
        "b2": copy.deepcopy(inn_data["b2"]),
        "bowler": copy.deepcopy(inn_data["bowler"]),
        "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]),
        "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
        "awaiting_batsman": inn_data["awaiting_batsman"],
        "awaiting_bowler": inn_data["awaiting_bowler"]
    })
    if "undo_stack" not in inn_data:
        inn_data["undo_stack"] = []
    inn_data["undo_stack"].append(state_snap)
    
    # Get current striker
    striker = inn_data["b1"] if inn_data["b1"]["strike"] else inn_data["b2"]
    
    # Update runs
    inn_data["runs"] += runs_inc
    inn_data["extras"] += extra_inc
    inn_data["bowler"]["runs"] += runs_inc
    
    # Handle wicket
    if is_wicket:
        inn_data["wickets"] += 1
        inn_data["bowler"]["wickets"] += 1
        dismissal_text = f"b {inn_data['bowler']['name']}"
        if dismissal_type:
            dismissal_text = f"{dismissal_type} b {inn_data['bowler']['name']}"
        striker["status"] = dismissal_text
        striker["dismissal_type"] = dismissal_type
        add_commentary(inn_data, f"WICKET! {striker['name']} {dismissal_text} ({striker['runs']} runs)")
    
    # Handle legal delivery
    if is_legal:
        inn_data["balls"] += 1
        inn_data["bowler"]["balls"] += 1
        striker["balls"] += 1
        striker["runs"] += (runs_inc - extra_inc)
        
        # Update boundaries
        if runs_inc == 4:
            striker["fours"] += 1
            add_commentary(inn_data, f"FOUR! {striker['name']} hits a boundary")
        elif runs_inc == 6:
            striker["sixes"] += 1
            add_commentary(inn_data, f"SIX! {striker['name']} clears the rope")
        elif runs_inc > 0 and not is_wicket:
            add_commentary(inn_data, f"{runs_inc} run(s) to {striker['name']}")
        elif runs_inc == 0 and not is_wicket:
            add_commentary(inn_data, f"Dot ball! {striker['name']} defends")
        
        # Add to over
        display_symbol = symbol if symbol is not None else str(runs_inc)
        inn_data["this_over"].append(display_symbol)
    else:
        # Extra delivery
        add_commentary(inn_data, f"Extra: {symbol} - {runs_inc} run(s) added")
        inn_data["this_over"].append(symbol)
    
    # Swap strike on odd runs (if not wicket)
    if is_legal and (runs_inc % 2 != 0) and not is_wicket:
        inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
        inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
    
    # Check for over completion
    legal_balls_in_over = [b for b in inn_data["this_over"] if str(b) not in ['WD', 'NB', 'Pen']]
    if len(legal_balls_in_over) == BALLS_PER_OVER:
        inn_data["awaiting_bowler"] = True
        add_commentary(inn_data, f"End of over {len(inn_data['over_history']) + 1}")
    
    # Check for wicket and need for new batsman
    if is_wicket and inn_data["wickets"] < MAX_WICKETS:
        inn_data["awaiting_batsman"] = True

def export_match_to_csv(m: MatchData) -> str:
    """Export match data to CSV format"""
    import io
    
    output = io.StringIO()
    
    # Match info
    output.write(f"Match ID,{m['id']}\n")
    output.write(f"Teams,{m['team_1']} vs {m['team_2']}\n")
    output.write(f"Overs,{m['total_overs']}\n")
    output.write(f"Result,{get_match_result(m)}\n\n")
    
    # Innings 1 batting
    output.write("INNINGS 1 BATTING\n")
    output.write("Player,Runs,Balls,4s,6s,Status\n")
    inn1 = m["innings_1"]
    for b in [inn1["b1"], inn1["b2"]] + inn1.get("all_batsmen_history", []):
        if b["name"]:
            output.write(f"{b['name']},{b['runs']},{b['balls']},{b.get('fours',0)},{b.get('sixes',0)},{b.get('status','')}\n")
    
    output.write(f"\nTotal,{inn1['runs']}/{inn1['wickets']}\n\n")
    
    # Innings 2 batting
    output.write("INNINGS 2 BATTING\n")
    output.write("Player,Runs,Balls,4s,6s,Status\n")
    inn2 = m["innings_2"]
    for b in [inn2["b1"], inn2["b2"]] + inn2.get("all_batsmen_history", []):
        if b["name"]:
            output.write(f"{b['name']},{b['runs']},{b['balls']},{b.get('fours',0)},{b.get('sixes',0)},{b.get('status','')}\n")
    
    output.write(f"\nTotal,{inn2['runs']}/{inn2['wickets']}\n")
    
    return output.getvalue()

@st.cache_resource
def get_tournament_database():
    """Get or create tournament database"""
    return {
        "lock": threading.Lock(),
        "active_match_id": None,
        "matches": {}
    }

# Initialize database
db_global = get_tournament_database()
lock = db_global["lock"]

with lock:
    for m_id in list(db_global["matches"].keys()):
        db_global["matches"][m_id] = ensure_match_keys(db_global["matches"][m_id])

# --- SQUAD MODAL ---
@st.dialog("📋 Squad Roster Profile")
def show_squad_popup(team_name: str):
    """Display squad popup dialog"""
    st.markdown(f"### {team_name} Squad")
    st.write("---")
    squad_members = TEAM_DB[team_name]["squad"]
    cols = st.columns(2)
    mid = (len(squad_members) + 1) // 2
    with cols[0]:
        for p in squad_members[:mid]:
            st.markdown(f"• {p}")
    with cols[1]:
        for p in squad_members[mid:]:
            st.markdown(f"• {p}")

def reset_match(match_id: str):
    """Reset a match to initial state"""
    with lock:
        if match_id in db_global["matches"]:
            db_global["matches"][match_id] = {
                "id": match_id,
                "team_1": db_global["matches"][match_id]["team_1"],
                "team_2": db_global["matches"][match_id]["team_2"],
                "total_overs": db_global["matches"][match_id]["total_overs"],
                "current_innings": 1,
                "match_complete": False,
                "innings_1": init_blank_innings(),
                "innings_2": init_blank_innings(),
                "created_at": datetime.now().isoformat(),
                "winner": None,
                "win_margin": None
            }
            return True
    return False

def delete_match(match_id: str):
    """Delete a match from database"""
    with lock:
        if match_id in db_global["matches"]:
            if db_global["active_match_id"] == match_id:
                db_global["active_match_id"] = None
            del db_global["matches"][match_id]
            return True
    return False

# --- SECURITY SYSTEM CONTROL SIDEBAR ---
st.sidebar.markdown("### 🔑 Live System Portal")
user_role = st.sidebar.radio("Your Access Profile:", ["📢 Player View (Live Auto-Sync)", "⚡ Scorer Panel (Admin Mode)"])

is_admin = False
if user_role == "⚡ Scorer Panel (Admin Mode)":
    password = st.sidebar.text_input("Enter Admin Password:", type="password")
    if password == ADMIN_PASSWORD:
        is_admin = True
        st.sidebar.success("✅ Admin Controls Connected!")
    elif password != "":
        st.sidebar.error("❌ Invalid Security Credentials")
else:
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=3000, key="broadcast_pulse")
    else:
        st.sidebar.info("Auto-refresh not available. Install streamlit-autorefresh for live updates.")

# Global Permanent Navigation Structure
tab_live, tab_review, tab_teams = st.tabs(["📺 Live Match Console", "🗄️ Tournament Match Review", "📋 Team Profiles"])

# ================= TAB: TEAM PROFILE REVIEWS =================
with tab_teams:
    st.markdown("### 🏆 Tournament Teams")
    t_cols = st.columns(3)
    for idx, t_name in enumerate(TEAM_DB.keys()):
        with t_cols[idx % 3]:
            st.markdown('<div class="team-block-container">', unsafe_allow_html=True)
            smart_load_image(TEAM_DB[t_name]["local"], TEAM_DB[t_name]["remote"], use_container=True)
            st.markdown(f"#### {t_name}")
            if st.button(f"📋 View Squad", key=f"squad_popup_key_{idx}", use_container_width=True):
                show_squad_popup(t_name)
            st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB: LIVE CONSOLE ENGINE =================
with tab_live:
    if is_admin:
        with st.expander("🛠 Match Administration Hub", expanded=not bool(db_global["active_match_id"])):
            st.markdown("#### Create New Match")
            with st.form("new_match_allocation_form"):
                new_m_id = st.text_input("Match Identifier (e.g., Match_01):")
                team_a = st.selectbox("Batting First (Team 1)", list(TEAM_DB.keys()), index=0)
                team_b = st.selectbox("Bowling First (Team 2)", list(TEAM_DB.keys()), index=1)
                match_ovs = st.number_input("Overs per innings:", min_value=1, max_value=20, value=DEFAULT_OVERS)
                
                if st.form_submit_button("🚀 Create Match", type="primary"):
                    if new_m_id and team_a != team_b:
                        with lock:
                            db_global["matches"][new_m_id] = {
                                "id": new_m_id,
                                "team_1": team_a,
                                "team_2": team_b,
                                "total_overs": match_ovs,
                                "current_innings": 1,
                                "match_complete": False,
                                "innings_1": init_blank_innings(),
                                "innings_2": init_blank_innings(),
                                "created_at": datetime.now().isoformat(),
                                "winner": None,
                                "win_margin": None
                            }
                            db_global["active_match_id"] = new_m_id
                        st.success(f"✅ Match '{new_m_id}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter unique match ID and different teams")

            if db_global["matches"]:
                st.markdown("---")
                st.markdown("#### Match Management")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    selected_focus = st.selectbox(
                        "Active Match:",
                        list(db_global["matches"].keys()),
                        index=list(db_global["matches"].keys()).index(db_global["active_match_id"]) if db_global["active_match_id"] in db_global["matches"] else 0
                    )
                    if st.button("🎯 Set Active", use_container_width=True):
                        db_global["active_match_id"] = selected_focus
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Reset Match", use_container_width=True, type="secondary"):
                        if reset_match(selected_focus):
                            st.success("Match reset successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to reset match")
                
                with col3:
                    if st.button("🗑️ Delete Match", use_container_width=True, type="secondary"):
                        if delete_match(selected_focus):
                            st.success("Match deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete match")
                
                # Innings transition
                if db_global["active_match_id"] and db_global["active_match_id"] in db_global["matches"]:
                    active_match = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
                    if active_match["current_innings"] == 1:
                        innings1_complete = is_innings_complete(active_match["innings_1"], active_match["total_overs"])
                        if innings1_complete:
                            if st.button("➡️ Start Innings 2", type="primary", use_container_width=True):
                                with lock:
                                    active_match["current_innings"] = 2
                                st.success("Moving to second innings!")
                                st.rerun()
                        else:
                            st.info("Innings 1 in progress...")

    # Live match display
    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("⏳ No active match. Please create or select a match from admin panel.")
    else:
        m_instance = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
        inn_key = "innings_1" if m_instance["current_innings"] == 1 else "innings_2"
        inn_data = m_instance[inn_key]
        
        bat_team = m_instance["team_1"] if m_instance["current_innings"] == 1 else m_instance["team_2"]
        bowl_team = m_instance["team_2"] if m_instance["current_innings"] == 1 else m_instance["team_1"]
        target_score = m_instance["innings_1"]["runs"] + 1 if m_instance["current_innings"] == 2 else None
        
        # Lineup setup
        if inn_data["b1"]["name"] == "":
            if is_admin:
                st.warning(f"⚙️ Configure Lineup for Innings #{m_instance['current_innings']}")
                with st.form(f"opening_lineup_setup_{inn_key}"):
                    bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else ["Player 1", "Player 2"]
                    bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else ["Player 1", "Player 2"]
                    p1 = st.selectbox("Opening Batsman (Striker)", bat_squad, index=0)
                    p2 = st.selectbox("Opening Batsman (Non-Striker)", bat_squad, index=1 if len(bat_squad) > 1 else 0)
                    bw = st.selectbox("Opening Bowler", bowl_squad, index=0)
                    if st.form_submit_button("Start Innings"):
                        with lock:
                            inn_data["b1"]["name"] = p1
                            inn_data["b2"]["name"] = p2
                            inn_data["bowler"]["name"] = bw
                            add_commentary(inn_data, f"Match started! {bat_team} batting first")
                            add_commentary(inn_data, f"Opening partnership: {p1} and {p2}")
                            add_commentary(inn_data, f"Opening bowler: {bw}")
                        st.rerun()
            else:
                st.info("⏳ Waiting for scorer to start the innings")
        else:
            # Display live match
            comp_ov = inn_data["balls"] // BALLS_PER_OVER
            rem_bl = inn_data["balls"] % BALLS_PER_OVER
            frac_ov = comp_ov + (rem_bl / BALLS_PER_OVER)
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            innings_ended = is_innings_complete(inn_data, m_instance["total_overs"])
            if target_score and inn_data["runs"] >= target_score:
                innings_ended = True
                
            status_tag = "🏁 FINISHED" if innings_ended else "🟢 LIVE"

            l_col, r_col = st.columns([1.1, 0.9])
            
            with l_col:
                b_local = TEAM_DB[bat_team]["local"] if bat_team in TEAM_DB else ""
                b_remote = TEAM_DB[bat_team]["remote"] if bat_team in TEAM_DB else ""
                f_local = TEAM_DB[bowl_team]["local"] if bowl_team in TEAM_DB else ""
                f_remote = TEAM_DB[bowl_team]["remote"] if bowl_team in TEAM_DB else ""
                
                b_logo_src = get_image_src(b_local, b_remote)
                f_logo_src = get_image_src(f_local, f_remote)
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 40px; margin-bottom: 10px; width: 100%;">
                        <div style="text-align: center; width: 60px;"><img src="{b_logo_src}" style="width: 55px; height: 55px; object-fit: contain; border-radius: 8px;"></div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #3B82F6; letter-spacing: 1px;">VS</div>
                        <div style="text-align: center; width: 60px;"><img src="{f_logo_src}" style="width: 55px; height: 55px; object-fit: contain; border-radius: 8px;"></div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">{status_tag}</span>
                        <h4 style="margin:0; font-weight:700;">{bat_team} vs {bowl_team}</h4>
                        <h1 style="font-size:3.5rem; margin:5px 0;">{inn_data['runs']} - {inn_data['wickets']}</h1>
                        <h5 style="margin:0; color:#93C5FD;">Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</h5>
                        <h5 style="margin:6px 0 0 0; font-weight:800; color:#34D399;">Run Rate: {crr:.2f}</h5>
                    </div>
                """, unsafe_allow_html=True)
                
                if target_score:
                    runs_needed = target_score - inn_data['runs']
                    balls_rem = (m_instance['total_overs'] * BALLS_PER_OVER) - inn_data['balls']
                    if runs_needed > 0:
                        st.warning(f"🎯 Target: {target_score} | Need {runs_needed} runs from {balls_rem} balls")
                    else:
                        st.success(f"🏆 Target achieved! {bat_team} wins!")

                col1, col2, col3 = st.columns(3)
                col1.metric("Extras", f"{inn_data['extras'] + inn_data.get('penalty', 0)}")
                col2.metric("Run Rate", f"{crr:.2f}")
                col3.metric("Partnership", f"{inn_data['b1']['runs'] + inn_data['b2']['runs']}")

                st.markdown("##### 📦 Current Over")
                if inn_data["this_over"]:
                    html_b = ""
                    for b in inn_data["this_over"]:
                        bg_color = "#475569"
                        if str(b) in ["4", "6"]:
                            bg_color = "#10B981"
                        elif "W" in str(b):
                            bg_color = "#EF4444"
                        elif any(x in str(b) for x in ["WD", "NB", "Ex", "Pen"]):
                            bg_color = "#D97706"
                        html_b += f'<span class="ball-bubble" style="background-color:{bg_color}; color:white;">{b}</span>'
                    st.markdown(html_b, unsafe_allow_html=True)
                else:
                    st.caption("No deliveries yet this over")
                
                match_outcome = get_match_result(m_instance)
                st.info(f"📢 {match_outcome}")

            with r_col:
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.75rem; color:#94A3B8;"><b>🏏 BATTING</b></div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.9rem;">
                            <span>{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}</span>
                            <span><b>{inn_data['b1']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b1']['balls']}b)</span></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.9rem;">
                            <span>{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}</span>
                            <span><b>{inn_data['b2']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b2']['balls']}b)</span></span>
                        </div>
                        <div style="margin-top:8px; font-size:0.75rem; color:#94A3B8;"><b>🥎 BOWLING</b></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                            <span>{inn_data['bowler']['name']}</span>
                            <span>W: {inn_data['bowler']['wickets']} | R: {inn_data['bowler']['runs']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin and not innings_ended:
                    st.markdown("### 🎛️ Scoring Controls")
                    
                    # Handle awaiting states
                    if inn_data["awaiting_batsman"]:
                        st.error("☝️ Wicket! Select new batsman:")
                        used_batsmen = [inn_data["b1"]["name"], inn_data["b2"]["name"]] + [b["name"] for b in inn_data["all_batsmen_history"]]
                        bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else []
                        available_batters = [p for p in bat_squad if p not in used_batsmen]
                        if not available_batters:
                            available_batters = ["New Player"]
                        
                        next_b = st.selectbox("Incoming Batsman:", available_batters, key="new_batsman_select")
                        if st.button("✅ Confirm Batsman", type="primary", use_container_width=True):
                            with lock:
                                if inn_data["b1"]["strike"]:
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b1"]))
                                    inn_data["b1"] = {
                                        "name": next_b, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                                        "strike": True, "status": "On Strike", "dismissal_type": None
                                    }
                                else:
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b2"]))
                                    inn_data["b2"] = {
                                        "name": next_b, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                                        "strike": False, "status": "Not Out", "dismissal_type": None
                                    }
                                inn_data["awaiting_batsman"] = False
                                add_commentary(inn_data, f"New batsman: {next_b} comes to the crease")
                            st.rerun()
                            
                    elif inn_data["awaiting_bowler"]:
                        st.success("🔄 Over complete! Select next bowler:")
                        bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else []
                        next_bw = st.selectbox("Next Bowler:", bowl_squad, key="new_bowler_select")
                        if st.button("✅ Confirm Bowler", type="primary", use_container_width=True):
                            with lock:
                                if inn_data["bowler"]["name"]:
                                    inn_data["all_bowlers_history"].append(copy.deepcopy(inn_data["bowler"]))
                                inn_data["over_history"].append({
                                    "Over": len(inn_data["over_history"]) + 1,
                                    "Bowler": inn_data["bowler"]["name"],
                                    "Score": f"{inn_data['runs']}/{inn_data['wickets']}",
                                    "Timeline": ", ".join(map(str, inn_data["this_over"]))
                                })
                                inn_data["this_over"] = []
                                inn_data["bowler"] = {"name": next_bw, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn_data["awaiting_bowler"] = False
                                add_commentary(inn_data, f"New bowler: {next_bw} comes into the attack")
                            st.rerun()

                    else:
                        # Run scoring buttons
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        with col_b1:
                            if st.button("0️⃣ 0", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 0, 0, True)
                                st.rerun()
                        with col_b2:
                            if st.button("1️⃣ 1", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 1, 0, True)
                                st.rerun()
                        with col_b3:
                            if st.button("2️⃣ 2", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 2, 0, True)
                                st.rerun()
                        with col_b4:
                            if st.button("3️⃣ 3", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 3, 0, True)
                                st.rerun()
                        
                        col_b5, col_b6, col_b7, col_b8 = st.columns(4)
                        with col_b5:
                            if st.button("4️⃣ FOUR", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 4, 0, True)
                                st.rerun()
                        with col_b6:
                            if st.button("6️⃣ SIX", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 6, 0, True)
                                st.rerun()
                        with col_b7:
                            if st.button("🟡 WIDE", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 1, 1, False, symbol="WD")
                                st.rerun()
                        with col_b8:
                            if st.button("🟠 NO BALL", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 1, 1, False, symbol="NB")
                                st.rerun()
                        
                        col_wicket, col_undo, col_swap = st.columns(3)
                        with col_wicket:
                            with st.popover("☝️ WICKET", use_container_width=True):
                                st.markdown("### Dismissal Type")
                                dismissal = st.selectbox("Select:", DISMISSAL_TYPES)
                                if st.button("Confirm Wicket", type="primary", use_container_width=True):
                                    with lock:
                                        process_ball_input(inn_data, 0, 0, True, True, symbol="W", dismissal_type=dismissal)
                                    st.rerun()
                        
                        with col_undo:
                            if inn_data.get("undo_stack") and len(inn_data["undo_stack"]) > 0:
                                if st.button("↩️ UNDO", use_container_width=True):
                                    with lock:
                                        prev_state = inn_data["undo_stack"].pop()
                                        for k in ["runs", "wickets", "balls", "extras", "penalty", "this_over", 
                                                  "over_history", "b1", "b2", "bowler", "all_batsmen_history", 
                                                  "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]:
                                            if k in prev_state:
                                                inn_data[k] = prev_state[k]
                                    st.rerun()
                        
                        with col_swap:
                            if not inn_data["awaiting_batsman"] and not inn_data["awaiting_bowler"]:
                                if st.button("🔄 SWAP", use_container_width=True):
                                    with lock:
                                        inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                        inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                        add_commentary(inn_data, "Strike rotated")
                                    st.rerun()

                    # Admin extras section
                    with st.expander("⚖️ Add Extras/Penalty"):
                        col_adj1, col_adj2 = st.columns([2, 1])
                        with col_adj1:
                            adj_type = st.selectbox("Type:", ["General Extras", "Penalty Runs"])
                        with col_adj2:
                            adj_runs = st.number_input("Runs:", min_value=1, max_value=20, value=1)
                        if st.button("➕ Add Runs", use_container_width=True):
                            with lock:
                                state_snap = copy.deepcopy({
                                    "runs": inn_data["runs"], "extras": inn_data["extras"], 
                                    "penalty": inn_data.get("penalty", 0), "this_over": list(inn_data["this_over"])
                                })
                                if "undo_stack" not in inn_data:
                                    inn_data["undo_stack"] = []
                                inn_data["undo_stack"].append(state_snap)
                                
                                inn_data["runs"] += adj_runs
                                if adj_type == "General Extras":
                                    inn_data["extras"] += adj_runs
                                    inn_data["this_over"].append(f"+{adj_runs}Ex")
                                    add_commentary(inn_data, f"{adj_runs} extra runs added")
                                else:
                                    inn_data["penalty"] = inn_data.get("penalty", 0) + adj_runs
                                    inn_data["this_over"].append(f"+{adj_runs}Pen")
                                    add_commentary(inn_data, f"{adj_runs} penalty runs awarded")
                            st.rerun()

                # Over history
                st.markdown("##### 📊 Over History")
                if inn_data["over_history"]:
                    df = pd.DataFrame(inn_data["over_history"])
                    st.dataframe(df[["Over", "Bowler", "Score", "Timeline"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No overs recorded yet")

                # Commentary
                with st.expander("📝 Ball-by-Ball Commentary"):
                    if inn_data.get("commentary"):
                        for comment in inn_data["commentary"][-20:]:
                            st.text(comment)
                    else:
                        st.caption("No commentary available")

            # Export section
            st.markdown("---")
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                try:
                    pdf_data = generate_pdf_bytes(m_instance)
                    st.download_button(
                        label="📥 Download PDF Scorecard",
                        data=pdf_data,
                        file_name=f"APL_{m_instance['id']}_Scorecard.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="pdf_export"
                    )
                except Exception as e:
                    st.error(f"PDF generation error: {str(e)}")
            
            with export_col2:
                csv_data = export_match_to_csv(m_instance)
                st.download_button(
                    label="📊 Download CSV Data",
                    data=csv_data,
                    file_name=f"APL_{m_instance['id']}_Data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="csv_export"
                )

# ================= TAB: TOURNAMENT REVIEW LEDGER =================
with tab_review:
    st.markdown("### 📊 Match Archives")
    if not db_global["matches"]:
        st.caption("No matches recorded yet")
    else:
        select_review_id = st.selectbox("Select Match:", list(db_global["matches"].keys()))
        m_rev = ensure_match_keys(db_global["matches"][select_review_id])
        
        st.markdown(f"## 🏏 {m_rev['id']}")
        st.info(f"**{m_rev['team_1']}** vs **{m_rev['team_2']}** | {m_rev['total_overs']} overs")
        
        result = get_match_result(m_rev)
        if "WINNER" in result:
            st.success(result)
        elif "Tied" in result:
            st.warning(result)
        else:
            st.info(result)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"Innings 1: {m_rev['team_1']}")
            d1 = m_rev["innings_1"]
            st.metric("Score", f"{d1['runs']}/{d1['wickets']}", 
                     f"{d1['balls'] // BALLS_PER_OVER}.{d1['balls'] % BALLS_PER_OVER} overs")
            if d1["over_history"]:
                st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader(f"Innings 2: {m_rev['team_2']}")
            d2 = m_rev["innings_2"]
            st.metric("Score", f"{d2['runs']}/{d2['wickets']}", 
                     f"{d2['balls'] // BALLS_PER_OVER}.{d2['balls'] % BALLS_PER_OVER} overs")
            if d2["over_history"]:
                st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
        
        # Full scorecard download for archived match
        try:
            pdf_data = generate_pdf_bytes(m_rev)
            st.download_button(
                label="📥 Download Full Scorecard",
                data=pdf_data,
                file_name=f"APL_{m_rev['id']}_FullScorecard.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="archive_pdf"
            )
        except Exception as e:
            st.error(f"Cannot generate PDF: {str(e)}")
