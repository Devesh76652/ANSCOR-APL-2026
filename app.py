import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from datetime import datetime
import io

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    pass

# Page Configuration
st.set_page_config(page_title="APL 2026 - Premium Cricket Scorer", page_icon="🏏", layout="wide")

# Raw GitHub repository directory path configuration
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"
TOURNAMENT_LOGO_FILE = "image_4d6904.png"

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

def get_image_src(local_path, remote_url=""):
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
        except: pass
    return remote_url

def get_tournament_logo_src():
    if os.path.exists(TOURNAMENT_LOGO_FILE):
        try:
            with open(TOURNAMENT_LOGO_FILE, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            ext = TOURNAMENT_LOGO_FILE.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
        except: pass
    return ""

def smart_load_image(local_path, remote_url, width=None, use_container=True):
    if isinstance(local_path, list):
        local_path = local_path[0] if len(local_path) > 0 else ""
    if isinstance(remote_url, list):
        remote_url = remote_url[0] if len(remote_url) > 0 else ""
        
    if local_path and os.path.exists(local_path):
        try: st.image(local_path, width=width, use_container_width=use_container); return True
        except: pass
    try: st.image(remote_url, width=width, use_container_width=use_container); return True
    except: pass
    return False

# Enhanced Custom CSS Stylesheet Config
st.markdown("""
    <style>
    /* Modern Design System */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container { 
        padding: 0.5rem 1rem !important; 
        max-width: 100% !important;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    }
    
    /* Enhanced Score Box with Logo Integration */
    .score-box-enhanced {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        color: white;
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
        border: 2px solid rgba(59,130,246,0.5);
        position: relative;
        box-shadow: 0 20px 40px -15px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease;
    }
    
    .score-box-enhanced:hover {
        transform: translateY(-5px);
    }
    
    /* Team Header with Logos */
    .team-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding: 0 10px;
    }
    
    .team-logo-container {
        text-align: center;
        flex: 1;
    }
    
    .team-logo {
        width: 80px;
        height: 80px;
        object-fit: contain;
        border-radius: 50%;
        border: 3px solid #3B82F6;
        padding: 5px;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .team-logo:hover {
        transform: scale(1.05);
    }
    
    .team-name {
        margin-top: 8px;
        font-weight: 700;
        font-size: 0.9rem;
        color: #F1F5F9;
    }
    
    .vs-divider {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F59E0B, #EF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 20px;
    }
    
    .tournament-logo {
        width: 60px;
        height: 60px;
        object-fit: contain;
        margin: 0 20px;
    }
    
    /* Score Display */
    .score-display {
        text-align: center;
        margin: 15px 0;
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F1F5F9, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
    }
    
    .overs-info {
        color: #93C5FD;
        font-size: 1rem;
        margin-top: 5px;
    }
    
    .crr-info {
        color: #34D399;
        font-weight: 800;
        font-size: 1.1rem;
        margin-top: 8px;
    }
    
    /* Status Badge */
    .status-badge {
        position: absolute;
        top: 15px;
        right: 20px;
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 2px 10px rgba(239,68,68,0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
        100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    }
    
    /* Modern Cards */
    .mobile-card, .team-block-container {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(59,130,246,0.3);
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .mobile-card:hover, .team-block-container:hover {
        border-color: #3B82F6;
        transform: translateY(-3px);
        box-shadow: 0 10px 25px -5px rgba(59,130,246,0.2);
    }
    
    /* Ball Bubbles */
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        margin: 4px;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        animation: fadeIn 0.3s ease;
    }
    
    .ball-bubble:hover {
        transform: scale(1.1);
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(59,130,246,0.4);
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Score Input Buttons */
    div[data-testid="column"] button {
        background: linear-gradient(135deg, #334155, #1E293B);
        border: 1px solid #475569;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    div[data-testid="column"] button:hover {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        border-color: #3B82F6;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        padding: 15px;
        border-radius: 16px;
        border: 1px solid rgba(59,130,246,0.3);
        backdrop-filter: blur(10px);
    }
    
    div[data-testid="stMetric"] label {
        color: #94A3B8;
        font-weight: 500;
    }
    
    div[data-testid="stMetric"] div {
        color: #F1F5F9;
        font-weight: 700;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30,41,59,0.5);
        padding: 8px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 12px;
        border: 1px solid rgba(59,130,246,0.3);
        font-weight: 600;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Select Box Styling */
    .stSelectbox > div > div {
        background: #1E293B;
        border-color: #3B82F6;
        border-radius: 10px;
    }
    
    /* Info/Warning/Success Messages */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
    }
    
    /* Target Chase Box */
    .target-chase {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-left: 4px solid #F59E0B;
        padding: 12px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .team-logo {
            width: 50px;
            height: 50px;
        }
        .vs-divider {
            font-size: 1.2rem;
        }
        .score-number {
            font-size: 2.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def init_blank_innings():
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0, "penalty": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [], "all_bowlers_history": [], "undo_stack": [],
        "awaiting_batsman": False, "awaiting_bowler": False
    }

def ensure_innings_keys(inn):
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

def ensure_match_keys(m):
    if not isinstance(m, dict):
        m = {
            "id": "Match", "team_1": "Team 1", "team_2": "Team 2",
            "total_overs": 4, "current_innings": 1, "match_complete": False,
            "innings_1": init_blank_innings(), "innings_2": init_blank_innings()
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
        m["total_overs"] = 4
    if "id" not in m:
        m["id"] = "Match"
    return m

def get_match_result(m):
    m = ensure_match_keys(m)
    d1 = m["innings_1"]
    d2 = m["innings_2"]
    
    if d1["b1"]["name"] == "":
        return "Setup State: Awaiting match lineup configuration."
        
    runs_i1 = d1["runs"]
    wickets_i1 = d1["wickets"]
    balls_i1 = d1["balls"]
    
    runs_i2 = d2["runs"]
    wickets_i2 = d2["wickets"]
    balls_i2 = d2["balls"]
    
    total_overs = m["total_overs"]
    i1_complete = (balls_i1 >= total_overs * 6) or (wickets_i1 >= 10)
    
    if m["current_innings"] == 1:
        if i1_complete:
            return f"Innings 1 Finished: {m['team_1']} scored {runs_i1}/{wickets_i1}. Ready for run chase."
        else:
            return f"Match Active: {m['team_1']} is batting in the 1st Innings."
            
    target = runs_i1 + 1
    if runs_i2 >= target:
        wickets_won = 10 - wickets_i2
        return f"WINNER: {m['team_2']} won by {wickets_won} wickets!"
        
    i2_complete = (balls_i2 >= total_overs * 6) or (wickets_i2 >= 10)
    if i2_complete:
        if runs_i2 < runs_i1:
            margin = runs_i1 - runs_i2
            return f"WINNER: {m['team_1']} won by {margin} runs!"
        elif runs_i2 == runs_i1:
            return "RESULT: Match Ended in a Tie!"
            
    runs_needed = target - runs_i2
    balls_rem = (total_overs * 6) - balls_i2
    return f"CHASE: {m['team_2']} needs {runs_needed} runs from {balls_rem} balls to win."

# ENHANCED PROFESSIONAL PDF GENERATION
def generate_professional_pdf(m):
    """Generate a professional detailed PDF scorecard"""
    try:
        m = ensure_match_keys(m)
        
        # Create PDF with better layout
        pdf = FPDF()
        pdf.add_page()
        
        # Add a decorative header line
        pdf.set_fill_color(59, 130, 246)
        pdf.rect(0, 0, 210, 8, 'F')
        
        # Title with gradient effect
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 20, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "OFFICIAL MATCH SCORECARD", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        
        # Match Info Box
        pdf.set_fill_color(240, 248, 255)
        pdf.set_draw_color(59, 130, 246)
        pdf.set_line_width(0.5)
        pdf.rect(10, 40, 190, 40, 'D')
        pdf.set_font("Arial", "B", 12)
        pdf.set_xy(15, 45)
        pdf.cell(0, 8, f"{m['team_1']} vs {m['team_2']}", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(15, 53)
        pdf.cell(0, 6, f"Match ID: {m['id']}  |  Overs: {m['total_overs']}  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        
        # Result Box
        result = get_match_result(m)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(220, 240, 220)
        pdf.rect(10, 85, 190, 12, 'F')
        pdf.set_xy(15, 88)
        pdf.cell(0, 6, result, ln=True)
        
        y_pos = 105
        
        # Innings 1 Detailed Scorecard
        d1 = m["innings_1"]
        if d1["b1"]["name"]:
            # Innings Header
            pdf.set_font("Arial", "B", 14)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y_pos, 190, 10, 'F')
            pdf.set_xy(15, y_pos + 2)
            pdf.cell(0, 6, f"INNINGS 1: {m['team_1']} BATTING", ln=True)
            pdf.set_text_color(0, 0, 0)
            y_pos += 15
            
            # Score Summary
            pdf.set_font("Arial", "B", 12)
            overs1 = f"{d1['balls']//6}.{d1['balls']%6}"
            pdf.cell(0, 8, f"Total: {d1['runs']}/{d1['wickets']} in {overs1} overs (Run Rate: {(d1['runs']/(d1['balls']/6)) if d1['balls']>0 else 0:.2f})", ln=True)
            y_pos += 5
            
            # Batting Table Header
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(55, 8, "BATSMAN", 1, 0, "C", 1)
            pdf.cell(20, 8, "R", 1, 0, "C", 1)
            pdf.cell(20, 8, "B", 1, 0, "C", 1)
            pdf.cell(15, 8, "4s", 1, 0, "C", 1)
            pdf.cell(15, 8, "6s", 1, 0, "C", 1)
            pdf.cell(25, 8, "SR", 1, 0, "C", 1)
            pdf.cell(50, 8, "STATUS", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            # Current batsmen
            if d1["b1"]["name"]:
                sr = (d1["b1"]["runs"] / d1["b1"]["balls"] * 100) if d1["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, d1["b1"]["name"][:25], 1)
                pdf.cell(20, 6, str(d1["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"].get("fours", 0)), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"].get("sixes", 0)), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, d1["b1"].get("status", "Active")[:20], 1, 1, "C")
            
            if d1["b2"]["name"]:
                sr = (d1["b2"]["runs"] / d1["b2"]["balls"] * 100) if d1["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, d1["b2"]["name"][:25], 1)
                pdf.cell(20, 6, str(d1["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"].get("fours", 0)), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"].get("sixes", 0)), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, d1["b2"].get("status", "Active")[:20], 1, 1, "C")
            
            # Dismissed batsmen
            for b in d1.get("all_batsmen_history", []):
                if b.get("name"):
                    sr = (b.get("runs", 0) / b.get("balls", 1) * 100) if b.get("balls", 0) > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(20, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(20, 6, str(b.get("balls", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                    pdf.cell(50, 6, b.get("status", "Out")[:20], 1, 1, "C")
            
            y_pos = pdf.get_y() + 5
            
            # Bowling Table
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y_pos, 190, 8, 'F')
            pdf.set_xy(15, y_pos + 1.5)
            pdf.cell(0, 5, "BOWLING FIGURES", ln=True)
            pdf.set_text_color(0, 0, 0)
            y_pos += 12
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(55, 7, "BOWLER", 1, 0, "C", 1)
            pdf.cell(25, 7, "OVERS", 1, 0, "C", 1)
            pdf.cell(25, 7, "RUNS", 1, 0, "C", 1)
            pdf.cell(25, 7, "WICKETS", 1, 0, "C", 1)
            pdf.cell(25, 7, "MAIDENS", 1, 0, "C", 1)
            pdf.cell(30, 7, "ECONOMY", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            # Current bowler
            if d1["bowler"]["name"]:
                overs_bowled = d1["bowler"]["balls"] / 6
                economy = d1["bowler"]["runs"] / overs_bowled if overs_bowled > 0 else 0
                pdf.cell(55, 6, d1["bowler"]["name"][:25], 1)
                pdf.cell(25, 6, f"{overs_bowled:.1f}", 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["runs"]), 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["wickets"]), 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"].get("maidens", 0)), 1, 0, "C")
                pdf.cell(30, 6, f"{economy:.2f}", 1, 1, "C")
            
            # Past bowlers
            for b in d1.get("all_bowlers_history", []):
                if b.get("name"):
                    overs_bowled = b.get("balls", 0) / 6
                    economy = b.get("runs", 0) / overs_bowled if overs_bowled > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(25, 6, f"{overs_bowled:.1f}", 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("wickets", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("maidens", 0)), 1, 0, "C")
                    pdf.cell(30, 6, f"{economy:.2f}", 1, 1, "C")
            
            y_pos = pdf.get_y() + 5
            
            # Over by Over Summary
            if d1["over_history"]:
                pdf.set_font("Arial", "B", 11)
                pdf.set_fill_color(59, 130, 246)
                pdf.set_text_color(255, 255, 255)
                pdf.rect(10, y_pos, 190, 8, 'F')
                pdf.set_xy(15, y_pos + 1.5)
                pdf.cell(0, 5, "OVER BY OVER SUMMARY", ln=True)
                pdf.set_text_color(0, 0, 0)
                y_pos += 12
                
                pdf.set_font("Arial", "B", 8)
                pdf.cell(15, 6, "Over", 1, 0, "C", 1)
                pdf.cell(50, 6, "Bowler", 1, 0, "C", 1)
                pdf.cell(30, 6, "Score", 1, 0, "C", 1)
                pdf.cell(95, 6, "Ball-by-Ball", 1, 1, "C", 1)
                
                pdf.set_font("Arial", "", 7)
                for over in d1["over_history"]:
                    pdf.cell(15, 5, str(over.get("Over", "")), 1, 0, "C")
                    pdf.cell(50, 5, over.get("Bowler", "")[:20], 1, 0, "C")
                    pdf.cell(30, 5, over.get("Score", ""), 1, 0, "C")
                    timeline = over.get("Timeline", "")[:50]
                    pdf.cell(95, 5, timeline, 1, 1, "L")
        
        # Innings 2 (Similar detailed format)
        d2 = m["innings_2"]
        if d2["b1"]["name"]:
            pdf.add_page()
            y_pos = 20
            
            pdf.set_font("Arial", "B", 14)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y_pos, 190, 10, 'F')
            pdf.set_xy(15, y_pos + 2)
            pdf.cell(0, 6, f"INNINGS 2: {m['team_2']} BATTING", ln=True)
            pdf.set_text_color(0, 0, 0)
            y_pos += 15
            
            # Score Summary with target
            pdf.set_font("Arial", "B", 12)
            overs2 = f"{d2['balls']//6}.{d2['balls']%6}"
            target = d1["runs"] + 1
            pdf.cell(0, 8, f"Target: {target} runs  |  Current: {d2['runs']}/{d2['wickets']} in {overs2} overs", ln=True)
            y_pos += 5
            
            # Batting Table
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(55, 8, "BATSMAN", 1, 0, "C", 1)
            pdf.cell(20, 8, "R", 1, 0, "C", 1)
            pdf.cell(20, 8, "B", 1, 0, "C", 1)
            pdf.cell(15, 8, "4s", 1, 0, "C", 1)
            pdf.cell(15, 8, "6s", 1, 0, "C", 1)
            pdf.cell(25, 8, "SR", 1, 0, "C", 1)
            pdf.cell(50, 8, "STATUS", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d2["b1"]["name"]:
                sr = (d2["b1"]["runs"] / d2["b1"]["balls"] * 100) if d2["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, d2["b1"]["name"][:25], 1)
                pdf.cell(20, 6, str(d2["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"].get("fours", 0)), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"].get("sixes", 0)), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, d2["b1"].get("status", "Active")[:20], 1, 1, "C")
            
            if d2["b2"]["name"]:
                sr = (d2["b2"]["runs"] / d2["b2"]["balls"] * 100) if d2["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, d2["b2"]["name"][:25], 1)
                pdf.cell(20, 6, str(d2["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"].get("fours", 0)), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"].get("sixes", 0)), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, d2["b2"].get("status", "Active")[:20], 1, 1, "C")
            
            for b in d2.get("all_batsmen_history", []):
                if b.get("name"):
                    sr = (b.get("runs", 0) / b.get("balls", 1) * 100) if b.get("balls", 0) > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(20, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(20, 6, str(b.get("balls", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                    pdf.cell(50, 6, b.get("status", "Out")[:20], 1, 1, "C")
            
            y_pos = pdf.get_y() + 5
            
            # Bowling Table
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y_pos, 190, 8, 'F')
            pdf.set_xy(15, y_pos + 1.5)
            pdf.cell(0, 5, "BOWLING FIGURES", ln=True)
            pdf.set_text_color(0, 0, 0)
            y_pos += 12
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(55, 7, "BOWLER", 1, 0, "C", 1)
            pdf.cell(25, 7, "OVERS", 1, 0, "C", 1)
            pdf.cell(25, 7, "RUNS", 1, 0, "C", 1)
            pdf.cell(25, 7, "WICKETS", 1, 0, "C", 1)
            pdf.cell(25, 7, "MAIDENS", 1, 0, "C", 1)
            pdf.cell(30, 7, "ECONOMY", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d2["bowler"]["name"]:
                overs_bowled = d2["bowler"]["balls"] / 6
                economy = d2["bowler"]["runs"] / overs_bowled if overs_bowled > 0 else 0
                pdf.cell(55, 6, d2["bowler"]["name"][:25], 1)
                pdf.cell(25, 6, f"{overs_bowled:.1f}", 1, 0, "C")
                pdf.cell(25, 6, str(d2["bowler"]["runs"]), 1, 0, "C")
                pdf.cell(25, 6, str(d2["bowler"]["wickets"]), 1, 0, "C")
                pdf.cell(25, 6, str(d2["bowler"].get("maidens", 0)), 1, 0, "C")
                pdf.cell(30, 6, f"{economy:.2f}", 1, 1, "C")
            
            for b in d2.get("all_bowlers_history", []):
                if b.get("name"):
                    overs_bowled = b.get("balls", 0) / 6
                    economy = b.get("runs", 0) / overs_bowled if overs_bowled > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(25, 6, f"{overs_bowled:.1f}", 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("wickets", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("maidens", 0)), 1, 0, "C")
                    pdf.cell(30, 6, f"{economy:.2f}", 1, 1, "C")
            
            y_pos = pdf.get_y() + 5
            
            if d2["over_history"]:
                pdf.set_font("Arial", "B", 11)
                pdf.set_fill_color(59, 130, 246)
                pdf.set_text_color(255, 255, 255)
                pdf.rect(10, y_pos, 190, 8, 'F')
                pdf.set_xy(15, y_pos + 1.5)
                pdf.cell(0, 5, "OVER BY OVER SUMMARY", ln=True)
                pdf.set_text_color(0, 0, 0)
                y_pos += 12
                
                pdf.set_font("Arial", "B", 8)
                pdf.cell(15, 6, "Over", 1, 0, "C", 1)
                pdf.cell(50, 6, "Bowler", 1, 0, "C", 1)
                pdf.cell(30, 6, "Score", 1, 0, "C", 1)
                pdf.cell(95, 6, "Ball-by-Ball", 1, 1, "C", 1)
                
                pdf.set_font("Arial", "", 7)
                for over in d2["over_history"]:
                    pdf.cell(15, 5, str(over.get("Over", "")), 1, 0, "C")
                    pdf.cell(50, 5, over.get("Bowler", "")[:20], 1, 0, "C")
                    pdf.cell(30, 5, over.get("Score", ""), 1, 0, "C")
                    timeline = over.get("Timeline", "")[:50]
                    pdf.cell(95, 5, timeline, 1, 1, "L")
        
        # Generate PDF output
        try:
            output_buffer = io.BytesIO()
            pdf.output(output_buffer)
            return output_buffer.getvalue()
        except:
            return b""
        
    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Error Generating Scorecard", ln=True, align="C")
            output_buffer = io.BytesIO()
            pdf.output(output_buffer)
            return output_buffer.getvalue()
        except:
            return b""

@st.cache_resource
def get_tournament_database():
    return {
        "lock": threading.Lock(),
        "active_match_id": None,
        "matches": {}
    }

db_global = get_tournament_database()
lock = db_global["lock"]

with lock:
    for m_id in list(db_global["matches"].keys()):
        db_global["matches"][m_id] = ensure_match_keys(db_global["matches"][m_id])

# --- SQUAD MODAL ---
@st.dialog("📋 Squad Roster Profile")
def show_squad_popup(team_name):
    st.markdown(f"### {team_name} Squad")
    st.write("---")
    squad_members = TEAM_DB[team_name]["squad"]
    cols = st.columns(2)
    mid = (len(squad_members) + 1) // 2
    with cols[0]:
        for p in squad_members[:mid]: st.markdown(f"• {p}")
    with cols[1]:
        for p in squad_members[mid:]: st.markdown(f"• {p}")

# --- SECURITY SYSTEM CONTROL SIDEBAR ---
st.sidebar.markdown("### 🔑 Live System Portal")
user_role = st.sidebar.radio("Your Access Profile:", ["📢 Player View (Live Auto-Sync)", "⚡ Scorer Panel (Admin Mode)"])

is_admin = False
if user_role == "⚡ Scorer Panel (Admin Mode)":
    password = st.sidebar.text_input("Enter Admin Password:", type="password")
    if password == "anscor2026":
        is_admin = True
        st.sidebar.success("Admin Controls Connected!")
    elif password != "":
        st.sidebar.error("Invalid Security Credentials")
else:
    try:
        st_autorefresh(interval=3000, key="broadcast_pulse")
    except:
        pass

# Global Permanent Navigation Structure
tab_live, tab_review, tab_teams = st.tabs(["📺 Live Match Console", "🗄️ Tournament Match Review", "📋 Team Profiles"])

# ================= TAB: TEAM PROFILE REVIEWS =================
with tab_teams:
    st.markdown("### Tournament Roster Groups")
    t_cols = st.columns(3)
    for idx, t_name in enumerate(TEAM_DB.keys()):
        with t_cols[idx % 3]:
            st.markdown('<div class="team-block-container">', unsafe_allow_html=True)
            smart_load_image(TEAM_DB[t_name]["local"], TEAM_DB[t_name]["remote"], use_container=True)
            st.markdown(f"#### {t_name}")
            if st.button(f"View Squad Roster", key=f"squad_popup_key_{idx}", use_container_width=True):
                show_squad_popup(t_name)
            st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB: LIVE CONSOLE ENGINE =================
with tab_live:
    if is_admin:
        with st.expander("🛠 Match Allocation Parameters & Inning Control Hub", expanded=not bool(db_global["active_match_id"])):
            st.markdown("#### Initialize a Brand New Match Instance")
            with st.form("new_match_allocation_form"):
                new_m_id = st.text_input("Unique Match Identifier Name (e.g., Match_01):")
                team_a = st.selectbox("Innings 1 - Batting Team", list(TEAM_DB.keys()), index=0)
                team_b = st.selectbox("Innings 1 - Bowling Team", list(TEAM_DB.keys()), index=1)
                match_ovs = st.number_input("Target Match Overs Limits:", min_value=1, max_value=20, value=4)
                
                if st.form_submit_button("Launch & Register Match Ecosystem 🏁"):
                    if new_m_id and team_a != team_b:
                        with lock:
                            db_global["matches"][new_m_id] = {
                                "id": new_m_id, "team_1": team_a, "team_2": team_b,
                                "total_overs": match_ovs, "current_innings": 1, "match_complete": False,
                                "innings_1": init_blank_innings(), "innings_2": init_blank_innings()
                            }
                            db_global["active_match_id"] = new_m_id
                        st.success(f"Match '{new_m_id}' configured successfully.")
                        st.rerun()

            if db_global["matches"]:
                st.markdown("---")
                selected_focus = st.selectbox("Switch Active Admin Stream Focus Window:", list(db_global["matches"].keys()), index=list(db_global["matches"].keys()).index(db_global["active_match_id"]) if db_global["active_match_id"] else 0)
                if st.button("Apply Selected Focus Switch Stream"):
                    db_global["active_match_id"] = selected_focus
                    st.rerun()
                
                if db_global["active_match_id"] in db_global["matches"]:
                    active_match = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
                    if active_match["current_innings"] == 1:
                        if st.button("🔄 Transition Match to Innings 2 ➡️", type="primary", use_container_width=True):
                            with lock:
                                active_match["current_innings"] = 2
                            st.success("Match flipped cleanly over to Innings 2!")
                            st.rerun()

    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("⏳ Waiting for active tournament score tracking initiation across layers...")
    else:
        m_instance = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
        inn_key = "innings_1" if m_instance["current_innings"] == 1 else "innings_2"
        inn_data = m_instance[inn_key]
        
        bat_team = m_instance["team_1"] if m_instance["current_innings"] == 1 else m_instance["team_2"]
        bowl_team = m_instance["team_2"] if m_instance["current_innings"] == 1 else m_instance["team_1"]
        target_score = (m_instance["innings_1"]["runs"] + 1) if m_instance["current_innings"] == 2 else None
        
        if inn_data["b1"]["name"] == "":
            if is_admin:
                st.warning(f"Configure active opening rosters for Innings #{m_instance['current_innings']}")
                with st.form(f"opening_lineup_setup_{inn_key}"):
                    bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else ["Player 1", "Player 2"]
                    bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else ["Player 1", "Player 2"]
                    p1 = st.selectbox("Striker Batsman", bat_squad, index=0)
                    p2 = st.selectbox("Non-Striker Batsman", bat_squad, index=1 if len(bat_squad) > 1 else 0)
                    bw = st.selectbox("Opening Bowler Assignment", bowl_squad, index=0)
                    if st.form_submit_button("Activate Opening Rosters Lineups"):
                        with lock:
                            inn_data["b1"]["name"] = p1
                            inn_data["b2"]["name"] = p2
                            inn_data["bowler"]["name"] = bw
                        st.rerun()
            else:
                st.info(f"⏳ Waiting for scorer initialization parameters for Innings #{m_instance['current_innings']}")
        else:
            comp_ov = inn_data["balls"] // 6
            rem_bl = inn_data["balls"] % 6
            frac_ov = comp_ov + (rem_bl / 6)
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            innings_ended = (comp_ov >= m_instance["total_overs"]) or (inn_data["wickets"] >= 10)
            if target_score and inn_data["runs"] >= target_score:
                innings_ended = True
                
            status_tag = "FINISHED" if innings_ended else "LIVE"

            # Get team logos
            b_local = TEAM_DB[bat_team]["local"] if bat_team in TEAM_DB else ""
            b_remote = TEAM_DB[bat_team]["remote"] if bat_team in TEAM_DB else ""
            f_local = TEAM_DB[bowl_team]["local"] if bowl_team in TEAM_DB else ""
            f_remote = TEAM_DB[bowl_team]["remote"] if bowl_team in TEAM_DB else ""
            
            b_logo_src = get_image_src(b_local, b_remote)
            f_logo_src = get_image_src(f_local, f_remote)
            t_logo_src = get_tournament_logo_src()

            # Enhanced Score Display with Logos
            st.markdown(f"""
                <div class="score-box-enhanced">
                    <span class="status-badge">{status_tag}</span>
                    <div class="team-header">
                        <div class="team-logo-container">
                            <img src="{b_logo_src}" class="team-logo" alt="{bat_team}">
                            <div class="team-name">{bat_team}</div>
                        </div>
                        <div class="vs-divider">VS</div>
                        <div class="team-logo-container">
                            <img src="{f_logo_src}" class="team-logo" alt="{bowl_team}">
                            <div class="team-name">{bowl_team}</div>
                        </div>
                    </div>
                    <div class="score-display">
                        <div class="score-number">{inn_data['runs']} - {inn_data['wickets']}</div>
                        <div class="overs-info">Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</div>
                        <div class="crr-info">Current Run Rate (CRR): {crr:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if target_score:
                runs_needed = target_score - inn_data['runs']
                balls_left = (m_instance['total_overs']*6) - inn_data['balls']
                required_rate = (runs_needed / (balls_left/6)) if balls_left > 0 else 0
                st.markdown(f"""
                    <div class="target-chase">
                        <div style="font-weight: 700; color: #F59E0B;">🎯 TARGET CHASE</div>
                        <div>Need <b>{runs_needed}</b> runs from <b>{balls_left}</b> balls</div>
                        <div>Required Run Rate: <b>{required_rate:.2f}</b> runs/over</div>
                    </div>
                """, unsafe_allow_html=True)

            # Metrics Row
            m_c1, m_c2, m_c3 = st.columns(3)
            m_c1.metric("Extras", f"{inn_data['extras'] + inn_data.get('penalty', 0)}")
            m_c2.metric("Partnership", f"{inn_data['b1']['runs'] + inn_data['b2']['runs']}")
            m_c3.metric("CRR", f"{crr:.2f}")

            # Main Content Columns
            l_col, r_col = st.columns([1.1, 0.9])
            
            with l_col:
                st.markdown("##### 📦 Over Timeline Tracker")
                if inn_data["this_over"]:
                    html_b = ""
                    for idx, b in enumerate(inn_data["this_over"]):
                        bg_color = "#475569"
                        if str(b) in ["4", "6"]: 
                            bg_color = "linear-gradient(135deg, #10B981, #059669)"
                        elif "W" in str(b): 
                            bg_color = "linear-gradient(135deg, #EF4444, #DC2626)"
                        elif "WD" in str(b) or "NB" in str(b) or "Ex" in str(b) or "Pen" in str(b): 
                            bg_color = "linear-gradient(135deg, #F59E0B, #D97706)"
                        html_b += f'<span class="ball-bubble" style="background:{bg_color}; color:white; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">{b}</span>'
                    st.markdown(html_b, unsafe_allow_html=True)
                else: 
                    st.caption("Waiting for delivery logs...")
                
                match_outcome = get_match_result(m_instance)
                st.info(f"📢 Status: {match_outcome}")

            with r_col:
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.7rem; color:#94A3B8; text-transform: uppercase; letter-spacing: 1px;"><b>🏏 BATTING PARTNERSHIP</b></div>
                        <div style="display:flex; justify-content:space-between; margin:10px 0; padding: 8px; background: rgba(59,130,246,0.1); border-radius: 8px;">
                            <div style="font-weight: 600;">{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}</div>
                            <div><b style="font-size: 1.2rem;">{inn_data['b1']['runs']}</b> <span style="color:#A1A1AA;">({inn_data['b1']['balls']}b)</span></div>
                            <div style="color:#10B981;">{f"{(inn_data['b1']['runs']/inn_data['b1']['balls']*100):.1f}" if inn_data['b1']['balls']>0 else "0.0"} SR</div>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin:10px 0; padding: 8px; background: rgba(59,130,246,0.1); border-radius: 8px;">
                            <div style="font-weight: 600;">{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}</div>
                            <div><b style="font-size: 1.2rem;">{inn_data['b2']['runs']}</b> <span style="color:#A1A1AA;">({inn_data['b2']['balls']}b)</span></div>
                            <div style="color:#10B981;">{f"{(inn_data['b2']['runs']/inn_data['b2']['balls']*100):.1f}" if inn_data['b2']['balls']>0 else "0.0"} SR</div>
                        </div>
                        <div style="margin-top:15px; padding-top:10px; border-top: 1px solid #334155;">
                            <div style="font-size:0.7rem; color:#94A3B8;"><b>🥎 CURRENT BOWLER</b></div>
                            <div style="display:flex; justify-content:space-between; margin-top:8px;">
                                <div style="font-weight: 600;">👤 {inn_data['bowler']['name']}</div>
                                <div>Wkts: <b style="color:#EF4444;">{inn_data['bowler']['wickets']}</b> | Runs: <b>{inn_data['bowler']['runs']}</b></div>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8;">Economy: {f"{(inn_data['bowler']['runs']/(inn_data['bowler']['balls']/6)):.2f}" if inn_data['bowler']['balls']>0 else "0.00"}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin:
                    st.markdown("### 🎛️ Scoring Input Controls")
                    
                    def process_ball_input(runs_inc, extra_inc=0, is_legal=True, is_wicket=False, symbol=None):
                        with lock:
                            state_snap = copy.deepcopy({
                                "runs": inn_data["runs"], "wickets": inn_data["wickets"], "balls": inn_data["balls"],
                                "extras": inn_data["extras"], "penalty": inn_data.get("penalty", 0), "this_over": list(inn_data["this_over"]), "over_history": copy.deepcopy(inn_data["over_history"]),
                                "b1": copy.deepcopy(inn_data["b1"]), "b2": copy.deepcopy(inn_data["b2"]), "bowler": copy.deepcopy(inn_data["bowler"]),
                                "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]), "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
                                "awaiting_batsman": inn_data["awaiting_batsman"], "awaiting_bowler": inn_data["awaiting_bowler"]
                            })
                            if "undo_stack" not in inn_data: inn_data["undo_stack"] = []
                            inn_data["undo_stack"].append(state_snap)

                            striker = inn_data["b1"] if inn_data["b1"]["strike"] else inn_data["b2"]
                            inn_data["runs"] += runs_inc
                            inn_data["extras"] += extra_inc
                            inn_data["bowler"]["runs"] += runs_inc
                            
                            if is_wicket:
                                inn_data["wickets"] += 1
                                inn_data["bowler"]["wickets"] += 1
                                
                            if is_legal:
                                inn_data["balls"] += 1
                                inn_data["bowler"]["balls"] += 1
                                striker["balls"] += 1
                                striker["runs"] += (runs_inc - extra_inc)
                                inn_data["this_over"].append(symbol if symbol is not None else runs_inc)
                            else:
                                inn_data["this_over"].append(symbol)
                                
                            if is_legal and (runs_inc % 2 != 0) and not is_wicket:
                                inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                
                            legal_balls_in_over = [b for b in inn_data["this_over"] if b not in ['WD', 'NB']]
                            
                            if len(legal_balls_in_over) == 6:
                                inn_data["awaiting_bowler"] = True
                            if is_wicket and inn_data["wickets"] < 10:
                                inn_data["awaiting_batsman"] = True

                    if inn_data["awaiting_batsman"]:
                        st.error("☝️ Wicket Fallen! Choose Incoming Batsman Below:")
                        used_batsmen = [inn_data["b1"]["name"], inn_data["b2"]["name"]] + [b["name"] for b in inn_data["all_batsmen_history"]]
                        bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else ["Player 1", "Player 2"]
                        available_batters = [p for p in bat_squad if p not in used_batsmen]
                        if not available_batters: available_batters = bat_squad
                        
                        next_b = st.selectbox("Select New Batter:", available_batters, key="inline_select_new_batter")
                        if st.button("Confirm New Batsman & Resume Play", type="primary", use_container_width=True):
                            with lock:
                                if inn_data["b1"]["strike"]:
                                    inn_data["b1"]["status"] = f"b {inn_data['bowler']['name']}"
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b1"]))
                                    inn_data["b1"] = {"name": next_b, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"}
                                else:
                                    inn_data["b2"]["status"] = f"b {inn_data['bowler']['name']}"
                                    inn_data["all_batsmen_history"].append(copy.deepcopy(inn_data["b2"]))
                                    inn_data["b2"] = {"name": next_b, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"}
                                inn_data["awaiting_batsman"] = False
                            st.rerun()
                            
                    elif inn_data["awaiting_bowler"]:
                        st.success("🔄 Over Completed! Choose the Next Bowler Below:")
                        bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else ["Player 1", "Player 2"]
                        next_bw = st.selectbox("Select Next Bowler Rotation:", bowl_squad, key="inline_select_new_bowler")
                        if st.button("Confirm Bowler Rotation & Open Next Over", type="primary", use_container_width=True):
                            with lock:
                                if inn_data["bowler"]["name"] != "":
                                    inn_data["all_bowlers_history"].append(copy.deepcopy(inn_data["bowler"]))
                                inn_data["over_history"].append({
                                    "Over": len(inn_data["over_history"]) + 1, "Bowler": inn_data["bowler"]["name"],
                                    "Score": f"{inn_data['runs']}/{inn_data['wickets']}", "Timeline": ", ".join(map(str, inn_data["this_over"]))
                                })
                                inn_data["this_over"] = []
                                inn_data["bowler"] = {"name": next_bw, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn_data["awaiting_bowler"] = False
                            st.rerun()

                    elif not innings_ended:
                        # Fixed button layout without syntax errors
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button("0️⃣ 0", use_container_width=True):
                                process_ball_input(0, 0, True)
                                st.rerun()
                            if st.button("1️⃣ 1", use_container_width=True):
                                process_ball_input(1, 0, True)
                                st.rerun()
                        
                        with col2:
                            if st.button("2️⃣ 2", use_container_width=True):
                                process_ball_input(2, 0, True)
                                st.rerun()
                            if st.button("3️⃣ 3", use_container_width=True):
                                process_ball_input(3, 0, True)
                                st.rerun()
                        
                        with col3:
                            if st.button("4️⃣ 4", use_container_width=True):
                                process_ball_input(4, 0, True)
                                # Update fours count
                                if inn_data["b1"]["strike"]:
                                    inn_data["b1"]["fours"] += 1
                                else:
                                    inn_data["b2"]["fours"] += 1
                                st.rerun()
                            if st.button("6️⃣ 6", use_container_width=True):
                                process_ball_input(6, 0, True)
                                # Update sixes count
                                if inn_data["b1"]["strike"]:
                                    inn_data["b1"]["sixes"] += 1
                                else:
                                    inn_data["b2"]["sixes"] += 1
                                st.rerun()
                        
                        with col4:
                            if st.button("🟡 WD", use_container_width=True):
                                process_ball_input(1, 1, False, symbol="WD")
                                st.rerun()
                            if st.button("🟠 NB", use_container_width=True):
                                process_ball_input(1, 1, False, symbol="NB")
                                st.rerun()
                        
                        st.markdown("---")
                        if st.button("☝️ OUT / FALL OF WICKET", type="primary", use_container_width=True):
                            process_ball_input(runs_inc=0, extra_inc=0, is_legal=True, is_wicket=True, symbol="W")
                            st.rerun()
                    else:
                        st.success("🏁 Innings complete.")

                    st.write("")
                    with st.expander("⚖️ Administrative Extra Runs & Penalty Additions", expanded=False):
                        adj_col1, adj_col2 = st.columns([2, 1])
                        with adj_col1:
                            adjustment_type = st.selectbox("Classification Type:", ["General Inning Extras", "Field Penalty Award Runs"], key=f"adj_type_{inn_key}")
                        with adj_col2:
                            runs_to_add = st.number_input("Runs Value:", min_value=1, max_value=20, value=1, step=1, key=f"adj_val_{inn_key}")
                            
                        if st.button("Apply Direct Additive Adjustment ⚡", use_container_width=True, type="secondary", key=f"adj_btn_{inn_key}"):
                            mapped_type = "Extras" if adjustment_type == "General Inning Extras" else "Penalty"
                            with lock:
                                state_snap = copy.deepcopy({
                                    "runs": inn_data["runs"], "wickets": inn_data["wickets"], "balls": inn_data["balls"],
                                    "extras": inn_data["extras"], "penalty": inn_data.get("penalty", 0), "this_over": list(inn_data["this_over"]), "over_history": copy.deepcopy(inn_data["over_history"]),
                                    "b1": copy.deepcopy(inn_data["b1"]), "b2": copy.deepcopy(inn_data["b2"]), "bowler": copy.deepcopy(inn_data["bowler"]),
                                    "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]), "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
                                    "awaiting_batsman": inn_data["awaiting_batsman"], "awaiting_bowler": inn_data["awaiting_bowler"]
                                })
                                if "undo_stack" not in inn_data: inn_data["undo_stack"] = []
                                inn_data["undo_stack"].append(state_snap)
                                
                                inn_data["runs"] += runs_to_add
                                if mapped_type == "Extras":
                                    inn_data["extras"] += runs_to_add
                                    inn_data["this_over"].append(f"+{runs_to_add}Ex")
                                else:
                                    if "penalty" not in inn_data: inn_data["penalty"] = 0
                                    inn_data["penalty"] += runs_to_add
                                    inn_data["this_over"].append(f"+{runs_to_add}Pen")
                            st.success(f"Injected +{runs_to_add} adjustment runs into database score.")
                            st.rerun()

                    st.write("")
                    col_undo, col_swap = st.columns(2)
                    with col_undo:
                        if "undo_stack" in inn_data and inn_data["undo_stack"]:
                            if st.button("⚠️ Undo Last Ball", use_container_width=True):
                                with lock:
                                    prev_state = inn_data["undo_stack"].pop()
                                    for k in ["runs", "wickets", "balls", "extras", "penalty", "this_over", "over_history", "b1", "b2", "bowler", "all_batsmen_history", "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]:
                                        inn_data[k] = prev_state.get(k, prev_state[k] if k in prev_state else 0)
                                st.rerun()
                        else:
                            st.button("Undo Disabled", disabled=True, use_container_width=True)
                    with col_swap:
                        if not innings_ended and not inn_data["awaiting_batsman"] and not inn_data["awaiting_bowler"]:
                            if st.button("🔄 Swap Strike", use_container_width=True):
                                with lock:
                                    inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                    inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                st.rerun()
                        else:
                            st.button("Swap Disabled", disabled=True, use_container_width=True)

                st.markdown("##### 📊 Completed Overs Log")
                if inn_data["over_history"]:
                    st.dataframe(pd.DataFrame(inn_data["over_history"]), use_container_width=True, hide_index=True)
                else: 
                    st.caption("No archived records.")

            # PDF Export Section
            st.markdown("---")
            st.markdown("### 📄 Export Match Report")
            
            # Generate PDF
            if m_instance["innings_1"]["balls"] > 0 or m_instance["innings_2"]["balls"] > 0:
                pdf_data = generate_professional_pdf(m_instance)
                
                if pdf_data and len(pdf_data) > 100:
                    st.download_button(
                        label="📥 Download Complete Match Scorecard (PDF)",
                        data=pdf_data,
                        file_name=f"APL_Match_{str(m_instance['id'])}_Scorecard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="pdf_download_btn"
                    )
                else:
                    st.warning("⚠️ PDF generation in progress. Please try again in a few seconds.")
            else:
                st.info("📄 PDF will be available once some overs are bowled in the match.")

# ================= TAB: TOURNAMENT REVIEW LEDGER =================
with tab_review:
    st.markdown("### Match Outcome Review Ledgers")
    if not db_global["matches"]:
        st.caption("No historical logs recorded within active engine instances.")
    else:
        select_review_id = st.selectbox("Select Match Profile Key to Audit:", list(db_global["matches"].keys()))
        m_rev = ensure_match_keys(db_global["matches"][select_review_id])
        
        st.markdown(f"## Match Record: {m_rev['id']}")
        st.info(f"📋 Lineup Setup: **{m_rev['team_1']}** vs **{m_rev['team_2']}**")
        
        d1 = m_rev["innings_1"]
        d2 = m_rev["innings_2"]
        
        match_outcome = get_match_result(m_rev)
        st.success(f"🏆 Final Result Summary: {match_outcome}")
        
        rev_i1, rev_i2 = st.tabs(["Innings #1 Complete Report Log", "Innings #2 Complete Report Log"])
        with rev_i1:
            st.metric(f"Total Innings 1 Score ({m_rev['team_1']})", f"{d1['runs']} - {d1['wickets']}", f"Overs: {d1['balls'] // 6}.{d1['balls'] % 6}")
            if d1["over_history"]: 
                st.table(pd.DataFrame(d1["over_history"]))
            else: 
                st.caption("No historical timelines stored for this inning.")
        with rev_i2:
            st.metric(f"Total Innings 2 Score ({m_rev['team_2']})", f"{d2['runs']} - {d2['wickets']}", f"Overs: {d2['balls'] // 6}.{d2['balls'] % 6}")
            if d2["over_history"]: 
                st.table(pd.DataFrame(d2["over_history"]))
            else: 
                st.caption("No historical timelines stored for this inning.")
        
        # PDF Export for archived match
        st.markdown("---")
        if m_rev["innings_1"]["balls"] > 0 or m_rev["innings_2"]["balls"] > 0:
            pdf_data = generate_professional_pdf(m_rev)
            if pdf_data and len(pdf_data) > 100:
                st.download_button(
                    label="📥 Download Archived Match Scorecard (PDF)",
                    data=pdf_data,
                    file_name=f"APL_Match_{str(m_rev['id'])}_Archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="archive_pdf_btn"
                )
            else:
                st.info("📄 PDF generation in progress...")
        else:
            st.info("📄 No match data available for PDF export")
