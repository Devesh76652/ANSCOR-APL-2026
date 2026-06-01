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

# Page Configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="APL 2026 - Cricket Scoring System",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

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
        "local": "RoyalWarriorsXl.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXl.jpeg",
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

# Dark Theme CSS - Fixed background
st.markdown("""
    <style>
    /* Main container - Dark background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .main {
        background: transparent;
    }
    
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: rgba(26, 26, 46, 0.95);
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Score card styling */
    .score-box {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid #e94560;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        position: relative;
    }
    
    .score-box h1 {
        font-size: 3rem !important;
        margin: 10px 0;
        font-weight: 800;
        color: #e94560;
    }
    
    .score-box h2 {
        font-size: 1.2rem !important;
        margin: 5px 0;
        color: #fff;
    }
    
    .score-box h3, .score-box h4 {
        font-size: 0.9rem !important;
        margin: 5px 0;
        color: #a0a0a0;
    }
    
    .status-badge {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #e94560;
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    /* Mobile card styling */
    .mobile-card {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        color: white;
        border: 1px solid #e94560;
    }
    
    .mobile-card h3 {
        font-size: 1rem;
        margin-bottom: 10px;
        color: #e94560;
    }
    
    /* Team card styling */
    .team-card {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #e94560;
        transition: transform 0.2s;
        cursor: pointer;
    }
    
    .team-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(233,69,96,0.3);
    }
    
    .team-card h3 {
        color: #e94560;
        margin: 0;
        font-size: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #e94560 0%, #c62a4a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233,69,96,0.4);
    }
    
    /* Metric styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e94560;
    }
    
    div[data-testid="stMetric"] label {
        color: #a0a0a0 !important;
        font-size: 0.8rem !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #e94560 !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f3460;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.85rem;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: #e94560 !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: #0f3460;
        border-radius: 10px;
        border: 1px solid #e94560;
    }
    
    .stDataFrame table {
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #0f3460;
        border-radius: 8px;
        color: white;
        font-size: 0.9rem;
    }
    
    /* Selectbox styling */
    .stSelectbox div {
        background: #0f3460;
        color: white;
    }
    
    .stSelectbox label {
        color: #a0a0a0 !important;
    }
    
    /* Text input styling */
    .stTextInput input {
        background: #0f3460;
        color: white;
        border: 1px solid #e94560;
    }
    
    .stTextInput label {
        color: #a0a0a0 !important;
    }
    
    /* Number input styling */
    .stNumberInput input {
        background: #0f3460;
        color: white;
        border: 1px solid #e94560;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 8px;
        font-size: 0.85rem;
        padding: 8px;
        background: #0f3460;
        border-left: 4px solid #e94560;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
        border-right: 1px solid #e94560;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Ball bubble styling */
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem !important;
        }
        
        .score-box h1 {
            font-size: 2rem !important;
        }
        
        .ball-bubble {
            width: 32px;
            height: 32px;
            font-size: 0.75rem;
        }
        
        .stButton > button {
            padding: 4px 8px;
            font-size: 0.7rem;
        }
    }
    
    hr {
        margin: 15px 0;
        border-color: #e94560;
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
        return "⚙️ Setup State: Awaiting match lineup configuration."
        
    runs_i1 = d1["runs"]
    wickets_i1 = d1["wickets"]
    
    # Innings 1 not started/completed
    if m["current_innings"] == 1:
        if is_innings_complete(d1, m["total_overs"]):
            return f"📊 Innings 1 Complete: {m['team_1']} scored {runs_i1}/{wickets_i1}"
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
        return f"🏆 VICTORY! {m['team_2']} won {margin}!"
        
    if is_innings_complete(d2, m["total_overs"]):
        if runs_i2 < runs_i1:
            margin = runs_i1 - runs_i2
            result = f"by {margin} runs"
            m["winner"] = m["team_1"]
            m["win_margin"] = result
            return f"🏆 VICTORY! {m['team_1']} won {result}!"
        elif runs_i2 == runs_i1:
            m["winner"] = "Match Tied"
            m["win_margin"] = ""
            return "🤝 RESULT: Match Tied!"
            
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
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    return text.encode('ascii', 'ignore').decode('ascii')

def safe_display_image(image_path: str, fallback_text: str = "🏏"):
    """Safely display an image or fallback to emoji"""
    try:
        if image_path and os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{fallback_text}</div>", unsafe_allow_html=True)
    except Exception:
        st.markdown(f"<div style='font-size: 3rem; text-align: center;'>{fallback_text}</div>", unsafe_allow_html=True)

def generate_pdf_bytes(m: MatchData) -> bytes:
    """Generate comprehensive match PDF report - FIXED VERSION"""
    try:
        m = ensure_match_keys(m)
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 15, "APL 2026 - MATCH SCORECARD", ln=True, align="C")
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"{m['team_1']} vs {m['team_2']}", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Match: {m['id']} | Overs: {m['total_overs']}", ln=True, align="C")
        pdf.ln(5)
        
        # Result
        match_outcome = get_match_result(m)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, match_outcome, ln=True, align="C")
        pdf.ln(5)
        
        # Innings 1
        d1 = m["innings_1"]
        if d1["b1"]["name"]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f"INNINGS 1: {m['team_1']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            
            comp_ov = d1["balls"] // BALLS_PER_OVER
            rem_bl = d1["balls"] % BALLS_PER_OVER
            
            pdf.cell(0, 6, f"Score: {d1['runs']}/{d1['wickets']} ({comp_ov}.{rem_bl} overs)", ln=True)
            pdf.ln(4)
            
            # Batting list
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(70, 6, "Batsman", 1)
            pdf.cell(25, 6, "Runs", 1, 0, "C")
            pdf.cell(25, 6, "Balls", 1, 0, "C")
            pdf.cell(30, 6, "Status", 1, 1, "C")
            
            pdf.set_font("Helvetica", "", 8)
            for b in [d1["b1"], d1["b2"]] + d1.get("all_batsmen_history", []):
                if b["name"]:
                    pdf.cell(70, 5, b["name"][:30], 1)
                    pdf.cell(25, 5, str(b["runs"]), 1, 0, "C")
                    pdf.cell(25, 5, str(b["balls"]), 1, 0, "C")
                    pdf.cell(30, 5, b.get("status", "Out")[:20], 1, 1, "C")
            
            pdf.ln(4)
        
        # Innings 2  
        d2 = m["innings_2"]
        if d2["b1"]["name"]:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f"INNINGS 2: {m['team_2']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            
            comp_ov = d2["balls"] // BALLS_PER_OVER
            rem_bl = d2["balls"] % BALLS_PER_OVER
            
            pdf.cell(0, 6, f"Score: {d2['runs']}/{d2['wickets']} ({comp_ov}.{rem_bl} overs)", ln=True)
            pdf.ln(4)
            
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(70, 6, "Batsman", 1)
            pdf.cell(25, 6, "Runs", 1, 0, "C")
            pdf.cell(25, 6, "Balls", 1, 0, "C")
            pdf.cell(30, 6, "Status", 1, 1, "C")
            
            pdf.set_font("Helvetica", "", 8)
            for b in [d2["b1"], d2["b2"]] + d2.get("all_batsmen_history", []):
                if b["name"]:
                    pdf.cell(70, 5, b["name"][:30], 1)
                    pdf.cell(25, 5, str(b["runs"]), 1, 0, "C")
                    pdf.cell(25, 5, str(b["balls"]), 1, 0, "C")
                    pdf.cell(30, 5, b.get("status", "Out")[:20], 1, 1, "C")
        
        # Get PDF output
        pdf_output = pdf.output(dest='S')
        return pdf_output.encode('latin-1', errors='replace')
    except Exception as e:
        # Return empty bytes on error
        return b""

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
    dismissal_type: Optional[str] = None
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
            add_commentary(inn_data, f"FOUR! {striker['name']}")
        elif runs_inc == 6:
            striker["sixes"] += 1
            add_commentary(inn_data, f"SIX! {striker['name']}")
        elif runs_inc > 0 and not is_wicket:
            add_commentary(inn_data, f"{runs_inc} run(s) to {striker['name']}")
        elif runs_inc == 0 and not is_wicket:
            add_commentary(inn_data, f"Dot ball! {striker['name']}")
        
        # Add to over
        display_symbol = symbol if symbol is not None else str(runs_inc)
        inn_data["this_over"].append(display_symbol)
    else:
        # Extra delivery
        add_commentary(inn_data, f"Extra: {symbol} - {runs_inc} run(s)")
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
@st.dialog("📋 Team Squad", width="large")
def show_squad_popup(team_name: str):
    """Display squad popup dialog that stays open until user closes"""
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #e94560;">{team_name}</h2>
            <hr>
        </div>
    """, unsafe_allow_html=True)
    
    squad_members = TEAM_DB[team_name]["squad"]
    
    # Display players in a grid
    cols = st.columns(3)
    for idx, player in enumerate(squad_members):
        with cols[idx % 3]:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%); 
                            color: white; padding: 10px; margin: 5px; border-radius: 10px; 
                            text-align: center; border: 1px solid #e94560;">
                    🏏 {player}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info(f"Total Players: {len(squad_members)}")
    
    # Close button
    if st.button("Close", use_container_width=True):
        st.rerun()

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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="color: #e94560;">🏏 APL 2026</h2>
            <p style="color: #a0a0a0;">Advanced Cricket Scoring System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔑 Access Control")
    user_role = st.radio(
        "Select Role:",
        ["👁️ Viewer Mode", "⚡ Scorer Mode"],
        help="Viewer mode auto-refreshes, Scorer mode allows match updates"
    )
    
    is_admin = False
    if user_role == "⚡ Scorer Mode":
        password = st.text_input("Admin Password:", type="password")
        if password == ADMIN_PASSWORD:
            is_admin = True
            st.success("✅ Admin Access Granted")
        elif password:
            st.error("❌ Invalid Password")
    
    st.markdown("---")
    st.caption("© 2026 APL Tournament")

# Global Navigation
tab_live, tab_review, tab_teams = st.tabs([
    "🎮 Live Match", 
    "📊 Match Archives", 
    "🏆 Team Profiles"
])

# ================= TAB: TEAM PROFILES =================
with tab_teams:
    st.markdown("### 🏏 Tournament Teams")
    st.markdown("Click on any team card to view their squad")
    
    # Create responsive grid
    cols = st.columns(3)
    for idx, (team_name, team_data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                    <div class="team-card">
                        <h3>{team_name}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display team logo safely
                safe_display_image(team_data["local"], "🏏")
                
                # View Squad button
                if st.button(f"📋 View Squad", key=f"squad_btn_{idx}", use_container_width=True):
                    show_squad_popup(team_name)

# ================= TAB: LIVE MATCH =================
with tab_live:
    # Admin controls in expander
    if is_admin:
        with st.expander("⚙️ Match Administration", expanded=not bool(db_global["active_match_id"])):
            st.markdown("#### Create New Match")
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("create_match_form"):
                    match_id = st.text_input("Match ID:", placeholder="e.g., Match_01")
                    team1 = st.selectbox("Team 1 (Batting First):", list(TEAM_DB.keys()), key="team1_select")
                    team2 = st.selectbox("Team 2 (Bowling First):", list(TEAM_DB.keys()), key="team2_select")
                    overs = st.slider("Overs per innings:", 1, 10, DEFAULT_OVERS)
                    
                    if st.form_submit_button("🚀 Create Match", use_container_width=True):
                        if match_id and team1 != team2:
                            with lock:
                                db_global["matches"][match_id] = {
                                    "id": match_id,
                                    "team_1": team1,
                                    "team_2": team2,
                                    "total_overs": overs,
                                    "current_innings": 1,
                                    "match_complete": False,
                                    "innings_1": init_blank_innings(),
                                    "innings_2": init_blank_innings(),
                                    "created_at": datetime.now().isoformat(),
                                    "winner": None,
                                    "win_margin": None
                                }
                                db_global["active_match_id"] = match_id
                            st.success(f"✅ Match '{match_id}' created!")
                            st.rerun()
                        else:
                            st.error("Please enter unique ID and different teams")
            
            with col2:
                if db_global["matches"]:
                    st.markdown("#### Manage Existing Matches")
                    matches_list = list(db_global["matches"].keys())
                    selected_match = st.selectbox("Select Match:", matches_list)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("🎯 Set Active", use_container_width=True):
                            db_global["active_match_id"] = selected_match
                            st.rerun()
                    with col_b:
                        if st.button("🔄 Reset", use_container_width=True):
                            if reset_match(selected_match):
                                st.success("Match reset!")
                                st.rerun()
                    with col_c:
                        if st.button("🗑️ Delete", use_container_width=True):
                            if delete_match(selected_match):
                                st.success("Match deleted!")
                                st.rerun()
    
    # Live match display
    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("""
            ### 🏏 No Active Match
        
            Please create a new match using the administration panel above.
            Click on the expander and fill in the match details to get started.
        """)
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
                st.warning(f"### ⚙️ Configure {bat_team} Batting Lineup")
                with st.form("lineup_form"):
                    bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else []
                    bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else []
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        striker = st.selectbox("Striker:", bat_squad, index=0)
                    with col2:
                        non_striker = st.selectbox("Non-Striker:", bat_squad, index=1 if len(bat_squad) > 1 else 0)
                    with col3:
                        bowler = st.selectbox("Opening Bowler:", bowl_squad, index=0)
                    
                    if st.form_submit_button("🏏 Start Match", use_container_width=True):
                        with lock:
                            inn_data["b1"]["name"] = striker
                            inn_data["b2"]["name"] = non_striker
                            inn_data["bowler"]["name"] = bowler
                            add_commentary(inn_data, f"🏏 MATCH STARTED! {bat_team} batting first")
                            add_commentary(inn_data, f"Opening partnership: {striker} and {non_striker}")
                            add_commentary(inn_data, f"Opening bowler: {bowler}")
                        st.rerun()
            else:
                st.info("⏳ Waiting for scorer to start the match")
        else:
            # Calculate stats
            comp_ov = inn_data["balls"] // BALLS_PER_OVER
            rem_bl = inn_data["balls"] % BALLS_PER_OVER
            frac_ov = comp_ov + (rem_bl / BALLS_PER_OVER) if BALLS_PER_OVER > 0 else 0
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            innings_ended = is_innings_complete(inn_data, m_instance["total_overs"])
            if target_score and inn_data["runs"] >= target_score:
                innings_ended = True
                
            status_color = "🟢 LIVE" if not innings_ended else "🏁 FINISHED"
            
            # Main display
            col_left, col_right = st.columns([2, 1])
            
            with col_left:
                # Scorecard
                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">{status_color}</span>
                        <h2>{bat_team} vs {bowl_team}</h2>
                        <h1>{inn_data['runs']} - {inn_data['wickets']}</h1>
                        <h3>Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</h3>
                        <h4>Run Rate: {crr:.2f}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                # Target info
                if target_score:
                    runs_needed = target_score - inn_data['runs']
                    balls_rem = (m_instance['total_overs'] * BALLS_PER_OVER) - inn_data['balls']
                    if runs_needed > 0:
                        st.warning(f"🎯 Target: {target_score} | Need {runs_needed} runs from {balls_rem} balls")
                    else:
                        st.success(f"🏆 VICTORY! {bat_team} wins!")
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Runs", inn_data['runs'])
                with col2:
                    st.metric("Wickets", inn_data['wickets'])
                with col3:
                    st.metric("Extras", inn_data['extras'] + inn_data.get('penalty', 0))
                with col4:
                    st.metric("CRR", f"{crr:.2f}")
                
                # Current over display
                st.markdown("#### 📦 Current Over")
                if inn_data["this_over"]:
                    cols = st.columns(min(len(inn_data["this_over"]), 6))
                    for idx, ball in enumerate(inn_data["this_over"][:6]):
                        bg_color = "#10B981" if ball in ["4", "6"] else "#EF4444" if "W" in str(ball) else "#F59E0B" if any(x in str(ball) for x in ["WD", "NB"]) else "#4A5568"
                        with cols[idx]:
                            st.markdown(f"""
                                <div style="background-color: {bg_color}; color: white; 
                                            text-align: center; padding: 8px; border-radius: 10px;
                                            font-weight: bold; font-size: 1rem;">
                                    {ball}
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No deliveries yet this over")
                
                # Over history
                st.markdown("#### 📊 Over History")
                if inn_data["over_history"]:
                    df = pd.DataFrame(inn_data["over_history"])
                    st.dataframe(df[["Over", "Bowler", "Score", "Timeline"]], use_container_width=True, hide_index=True)
                else:
                    st.caption("No overs recorded yet")
            
            with col_right:
                # Current partnership
                st.markdown(f"""
                    <div class="mobile-card">
                        <h3>🏏 BATTING</h3>
                        <div style="margin: 15px 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 1rem;">
                                <span>{'👉 ' if inn_data['b1']['strike'] else ''}{inn_data['b1']['name']}</span>
                                <span><b>{inn_data['b1']['runs']}</b> ({inn_data['b1']['balls']})</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 1rem; margin-top: 10px;">
                                <span>{'👉 ' if inn_data['b2']['strike'] else ''}{inn_data['b2']['name']}</span>
                                <span><b>{inn_data['b2']['runs']}</b> ({inn_data['b2']['balls']})</span>
                            </div>
                        </div>
                        <h3>🥎 BOWLING</h3>
                        <div style="margin: 15px 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 1rem;">
                                <span>{inn_data['bowler']['name']}</span>
                                <span>W: {inn_data['bowler']['wickets']} | R: {inn_data['bowler']['runs']}</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Scoring controls (admin only)
                if is_admin and not innings_ended:
                    st.markdown("### 🎮 Scoring Controls")
                    
                    # Handle awaiting states
                    if inn_data["awaiting_batsman"]:
                        st.error("☝️ Wicket! Select new batsman:")
                        used_batsmen = [inn_data["b1"]["name"], inn_data["b2"]["name"]] + [b["name"] for b in inn_data["all_batsmen_history"]]
                        bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else []
                        available_batters = [p for p in bat_squad if p not in used_batsmen]
                        
                        if not available_batters:
                            available_batters = ["New Player"]
                        
                        new_batsman = st.selectbox("Incoming Batsman:", available_batters, key="new_bat")
                        if st.button("✅ Confirm", use_container_width=True, type="primary"):
                            with lock:
                                if inn_data["b1"]["strike"]:
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b1"]))
                                    inn_data["b1"] = {
                                        "name": new_batsman, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                                        "strike": True, "status": "On Strike", "dismissal_type": None
                                    }
                                else:
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b2"]))
                                    inn_data["b2"] = {
                                        "name": new_batsman, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                                        "strike": False, "status": "Not Out", "dismissal_type": None
                                    }
                                inn_data["awaiting_batsman"] = False
                                add_commentary(inn_data, f"New batsman: {new_batsman} comes to the crease")
                            st.rerun()
                    
                    elif inn_data["awaiting_bowler"]:
                        st.success("🔄 Over complete! Select next bowler:")
                        bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else []
                        next_bowler = st.selectbox("Next Bowler:", bowl_squad, key="new_bowl")
                        if st.button("✅ Confirm", use_container_width=True, type="primary"):
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
                                inn_data["bowler"] = {"name": next_bowler, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn_data["awaiting_bowler"] = False
                                add_commentary(inn_data, f"New bowler: {next_bowler} comes into the attack")
                            st.rerun()
                    
                    else:
                        # Run buttons in grid
                        run_cols = st.columns(5)
                        run_values = [0, 1, 2, 3, 4]
                        for idx, runs in enumerate(run_values):
                            with run_cols[idx]:
                                if st.button(f"{runs}", use_container_width=True):
                                    with lock:
                                        process_ball_input(inn_data, runs, 0, True)
                                    st.rerun()
                        
                        # Special buttons
                        col_a, col_b, col_c, col_d, col_e = st.columns(5)
                        with col_a:
                            if st.button("6️⃣", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 6, 0, True)
                                st.rerun()
                        with col_b:
                            if st.button("🟡 WD", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 1, 1, False, symbol="WD")
                                st.rerun()
                        with col_c:
                            if st.button("🟠 NB", use_container_width=True):
                                with lock:
                                    process_ball_input(inn_data, 1, 1, False, symbol="NB")
                                st.rerun()
                        with col_d:
                            with st.popover("☝️ WICKET", use_container_width=True):
                                st.markdown("### Dismissal Type")
                                dismissal = st.selectbox("Select:", DISMISSAL_TYPES, key="wicket_type")
                                if st.button("Confirm", type="primary", use_container_width=True):
                                    with lock:
                                        process_ball_input(inn_data, 0, 0, True, True, symbol="W", dismissal_type=dismissal)
                                    st.rerun()
                        with col_e:
                            if st.button("🔄 SWAP", use_container_width=True):
                                with lock:
                                    inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                    inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                    add_commentary(inn_data, "Strike rotated")
                                st.rerun()
                        
                        # Undo button
                        if inn_data.get("undo_stack") and len(inn_data["undo_stack"]) > 0:
                            if st.button("↩️ Undo Last Ball", use_container_width=True):
                                with lock:
                                    prev = inn_data["undo_stack"].pop()
                                    for k in ["runs", "wickets", "balls", "extras", "penalty", "this_over", 
                                              "over_history", "b1", "b2", "bowler", "all_batsmen_history", 
                                              "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]:
                                        if k in prev:
                                            inn_data[k] = prev[k]
                                st.rerun()
                        
                        # Extras section
                        with st.expander("➕ Add Extras"):
                            extra_type = st.radio("Type:", ["Extra Run", "Penalty Run"], horizontal=True)
                            extra_runs = st.number_input("Runs:", 1, 10, 1)
                            if st.button("Add", use_container_width=True):
                                with lock:
                                    state_snap = copy.deepcopy({
                                        "runs": inn_data["runs"], "extras": inn_data["extras"],
                                        "penalty": inn_data.get("penalty", 0), "this_over": list(inn_data["this_over"])
                                    })
                                    if "undo_stack" not in inn_data:
                                        inn_data["undo_stack"] = []
                                    inn_data["undo_stack"].append(state_snap)
                                    
                                    inn_data["runs"] += extra_runs
                                    if extra_type == "Extra Run":
                                        inn_data["extras"] += extra_runs
                                        inn_data["this_over"].append(f"+{extra_runs}")
                                        add_commentary(inn_data, f"{extra_runs} extra runs added")
                                    else:
                                        inn_data["penalty"] = inn_data.get("penalty", 0) + extra_runs
                                        inn_data["this_over"].append(f"Pen+{extra_runs}")
                                        add_commentary(inn_data, f"{extra_runs} penalty runs awarded")
                                st.rerun()
                
                # Commentary
                with st.expander("📝 Ball-by-Ball Commentary", expanded=True):
                    if inn_data.get("commentary"):
                        for comment in inn_data["commentary"][-15:]:
                            st.text(comment)
                    else:
                        st.caption("No commentary available")
            
            # Export section - Only PDF Button (CSV Removed)
            st.markdown("---")
            
            # Generate PDF and provide download button
            try:
                pdf_data = generate_pdf_bytes(m_instance)
                if pdf_data and len(pdf_data) > 500:  # Valid PDF has reasonable size
                    st.download_button(
                        label="📥 Download PDF Scorecard",
                        data=pdf_data,
                        file_name=f"APL_{m_instance['id']}_Scorecard.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("📄 PDF will be available once match has sufficient data")
            except Exception as e:
                st.info("📄 PDF ready when match has data")

# ================= TAB: MATCH ARCHIVES =================
with tab_review:
    st.markdown("### 📊 Match Archives")
    
    if not db_global["matches"]:
        st.info("No matches played yet. Create a match in the Live Match tab to get started!")
    else:
        archive_match = st.selectbox("Select Match to Review:", list(db_global["matches"].keys()))
        
        if archive_match:
            m_rev = ensure_match_keys(db_global["matches"][archive_match])
            
            # Match header
            result = get_match_result(m_rev)
            if "VICTORY" in result:
                st.success(result)
            elif "Tied" in result:
                st.warning(result)
            else:
                st.info(result)
            
            # Two column display for innings
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### Innings 1: {m_rev['team_1']}")
                d1 = m_rev["innings_1"]
                if d1["b1"]["name"]:
                    st.metric("Score", f"{d1['runs']}/{d1['wickets']}", 
                             f"{d1['balls']//BALLS_PER_OVER}.{d1['balls']%BALLS_PER_OVER} overs")
                    
                    if d1["over_history"]:
                        st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
                else:
                    st.caption("Innings not played")
            
            with col2:
                st.markdown(f"### Innings 2: {m_rev['team_2']}")
                d2 = m_rev["innings_2"]
                if d2["b1"]["name"]:
                    st.metric("Score", f"{d2['runs']}/{d2['wickets']}", 
                             f"{d2['balls']//BALLS_PER_OVER}.{d2['balls']%BALLS_PER_OVER} overs")
                    
                    if d2["over_history"]:
                        st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
                else:
                    st.caption("Innings not played")
            
            # PDF Download for archived match
            try:
                pdf_data = generate_pdf_bytes(m_rev)
                if pdf_data and len(pdf_data) > 500:
                    st.download_button(
                        label="📥 Download Full Scorecard PDF",
                        data=pdf_data,
                        file_name=f"APL_{m_rev['id']}_FullScorecard.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception:
                st.info("📄 PDF available")
