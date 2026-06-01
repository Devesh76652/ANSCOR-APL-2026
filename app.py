import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from datetime import datetime

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

# Page Configuration
st.set_page_config(
    page_title="APL 2026 - Cricket Scoring System", 
    page_icon="🏏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Enhanced Custom CSS Stylesheet
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .block-container {
        padding: 1rem 1.5rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .score-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    
    .score-box:hover {
        transform: translateY(-2px);
    }
    
    .status-badge {
        position: absolute;
        top: 15px;
        right: 20px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    .mobile-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        margin: 4px;
        font-weight: 800;
        font-size: 0.9rem;
        transition: transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .ball-bubble:hover {
        transform: scale(1.1);
    }
    
    .team-block-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .team-block-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .team-block-container h4 {
        color: #ffd700;
        margin-top: 10px;
        font-weight: bold;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    div[data-testid="stMetric"] label {
        color: #1e3c72 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #e94560 !important;
        font-weight: bold !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(30,60,114,0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f0f2f5;
        padding: 8px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 25px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #1e3c72;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        color: white !important;
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        color: #1e3c72;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding: 0.5rem !important;
        }
        
        .score-box h1 {
            font-size: 2rem !important;
        }
        
        .ball-bubble {
            width: 30px;
            height: 30px;
            font-size: 0.75rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 5px 12px;
            font-size: 0.75rem;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .score-box, .mobile-card, .team-block-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    hr {
        margin: 20px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #1e3c72, #2a5298, #1e3c72);
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
        return "⚙️ Setup State: Awaiting match lineup configuration."
        
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
            return f"📊 Innings 1 Finished: {m['team_1']} scored {runs_i1}/{wickets_i1}. Ready for run chase."
        else:
            return f"🏏 Match Active: {m['team_1']} is batting in the 1st Innings."
            
    target = runs_i1 + 1
    if runs_i2 >= target:
        wickets_won = 10 - wickets_i2
        return f"🏆 WINNER: {m['team_2']} won by {wickets_won} wickets!"
        
    i2_complete = (balls_i2 >= total_overs * 6) or (wickets_i2 >= 10)
    if i2_complete:
        if runs_i2 < runs_i1:
            margin = runs_i1 - runs_i2
            return f"🏆 WINNER: {m['team_1']} won by {margin} runs!"
        elif runs_i2 == runs_i1:
            return "🤝 RESULT: Match Ended in a Tie!"
            
    runs_needed = target - runs_i2
    balls_rem = (total_overs * 6) - balls_i2
    return f"🎯 CHASE: {m['team_2']} needs {runs_needed} runs from {balls_rem} balls to win."

def clean_for_pdf(text):
    if text is None:
        return ""
    text = str(text)
    
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    
    replacements = {
        "🏆": "WINNER:", "👔": "TIE:", "👉": ">", "🟢": "", "🟠": "", "🟡": "", 
        "🏏": "", "👤": "", "🥎": "", "🎛️": "", "📥": "", "🛠": "", "⚡": "", "📢": "", "🎯": ""
    }
    for emoji, rep in replacements.items():
        text = text.replace(emoji, rep)
        
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf_bytes(m):
    """Generate PDF scorecard with full match details"""
    m = ensure_match_keys(m)
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "APL 2026 - MATCH SCORECARD", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_for_pdf(f"{m['team_1']} vs {m['team_2']} ({m['total_overs']} Overs Match)"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Match ID: {m['id']} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Result
    match_outcome = get_match_result(m)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 8, clean_for_pdf(match_outcome), ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)
    
    # Process both innings
    for inn_idx in [1, 2]:
        inn_key = f"innings_{inn_idx}"
        inn_data = m[inn_key]
        
        bat_team = m["team_1"] if inn_idx == 1 else m["team_2"]
        bowl_team = m["team_2"] if inn_idx == 1 else m["team_1"]
        
        if inn_data["b1"]["name"] == "":
            continue
            
        comp_ov = inn_data["balls"] // 6
        rem_bl = inn_data["balls"] % 6
        frac_ov = comp_ov + (rem_bl / 6)
        crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, clean_for_pdf(f"INNINGS #{inn_idx}: {bat_team.upper()} BATTING"), ln=True)
        pdf.set_font("Helvetica", "", 9)
        
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
                
        for b_hist in inn_data.get("all_batsmen_history", []):
            pdf.cell(70, 5, clean_for_pdf(b_hist['name']), 1)
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
        pdf.cell(30, 6, "Wkts", 1, 0, "C")
        pdf.cell(30, 6, "Econ", 1, 1, "C")
        
        pdf.set_font("Helvetica", "", 8)
        cw_bowler = inn_data["bowler"]
        if cw_bowler["name"]:
            b_ov = cw_bowler["balls"] // 6
            b_bl = cw_bowler["balls"] % 6
            overs = cw_bowler["balls"] / 6
            eco = cw_bowler["runs"] / overs if overs > 0 else 0
            pdf.cell(80, 5, clean_for_pdf(cw_bowler["name"] + " (Current)"), 1)
            pdf.cell(30, 5, f"{b_ov}.{b_bl}", 1, 0, "C")
            pdf.cell(30, 5, str(cw_bowler["runs"]), 1, 0, "C")
            pdf.cell(30, 5, str(cw_bowler["wickets"]), 1, 0, "C")
            pdf.cell(30, 5, f"{eco:.2f}", 1, 1, "C")
            
        for bowl_h in inn_data.get("all_bowlers_history", []):
            bh_ov = bowl_h["balls"] // 6
            bh_bl = bowl_h["balls"] % 6
            overs = bowl_h["balls"] / 6
            eco = bowl_h["runs"] / overs if overs > 0 else 0
            pdf.cell(80, 5, clean_for_pdf(bowl_h["name"]), 1)
            pdf.cell(30, 5, f"{bh_ov}.{bh_bl}", 1, 0, "C")
            pdf.cell(30, 5, str(bowl_h["runs"]), 1, 0, "C")
            pdf.cell(30, 5, str(bowl_h["wickets"]), 1, 0, "C")
            pdf.cell(30, 5, f"{eco:.2f}", 1, 1, "C")
            
        pdf.ln(6)
        
        # Over history
        if inn_data.get("over_history"):
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(25, 6, "Over", 1)
            pdf.cell(55, 6, "Bowler", 1)
            pdf.cell(40, 6, "Score", 1)
            pdf.cell(70, 6, "Deliveries", 1, ln=True)
            
            pdf.set_font("Helvetica", "", 8)
            for ov in inn_data.get("over_history", []):
                pdf.cell(25, 5, str(ov.get("Over", "")), 1)
                pdf.cell(55, 5, clean_for_pdf(str(ov.get("Bowler", ""))), 1)
                pdf.cell(40, 5, str(ov.get("Score", "")), 1)
                pdf.cell(70, 5, clean_for_pdf(str(ov.get("Timeline", ""))[:60]), 1, ln=True)
                
        pdf.ln(8)
        
    return pdf.output(dest='S').encode('latin-1', errors='replace')

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
@st.dialog("📋 Squad Roster Profile", width="large")
def show_squad_popup(team_name):
    st.markdown(f"### 🏏 {team_name} Squad")
    st.write("---")
    squad_members = TEAM_DB[team_name]["squad"]
    cols = st.columns(3)
    mid = (len(squad_members) + 2) // 3
    for i, col in enumerate(cols):
        with col:
            start = i * mid
            end = min((i + 1) * mid, len(squad_members))
            for p in squad_members[start:end]:
                st.markdown(f"• {p}")

# --- SECURITY SYSTEM CONTROL SIDEBAR ---
with st.sidebar:
    st.markdown("## 🏏 APL 2026")
    st.markdown("### 🔑 Live System Portal")
    st.markdown("---")
    
    user_role = st.radio("Your Access Profile:", ["📢 Player View", "⚡ Scorer Mode"], key="user_role_radio")
    
    is_admin = False
    if user_role == "⚡ Scorer Mode":
        password = st.text_input("Enter Admin Password:", type="password", key="admin_password_input")
        if password == "anscor2026":
            is_admin = True
            st.success("✅ Admin Controls Connected!")
        elif password != "":
            st.error("❌ Invalid Security Credentials")
    else:
        if AUTOREFRESH_AVAILABLE:
            st_autorefresh(interval=3000, key="broadcast_pulse")
    
    st.markdown("---")
    st.caption("© 2026 APL Tournament")

# Global Permanent Navigation Structure
tab_live, tab_review, tab_teams = st.tabs(["📺 LIVE MATCH", "🗄️ MATCH ARCHIVES", "📋 TEAM PROFILES"])

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
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("new_match_allocation_form"):
                    new_m_id = st.text_input("Match ID:", placeholder="Match_01", key="new_match_id_input")
                    team_a = st.selectbox("Batting First:", list(TEAM_DB.keys()), index=0, key="team_a_select")
                    team_b = st.selectbox("Bowling First:", list(TEAM_DB.keys()), index=1, key="team_b_select")
                    match_ovs = st.number_input("Overs:", min_value=1, max_value=20, value=4, key="match_overs_input")
                    
                    submitted = st.form_submit_button("🚀 Create Match", use_container_width=True)
                    if submitted:
                        if new_m_id and team_a != team_b:
                            with lock:
                                db_global["matches"][new_m_id] = {
                                    "id": new_m_id, "team_1": team_a, "team_2": team_b,
                                    "total_overs": match_ovs, "current_innings": 1, "match_complete": False,
                                    "innings_1": init_blank_innings(), "innings_2": init_blank_innings()
                                }
                                db_global["active_match_id"] = new_m_id
                            st.success(f"✅ Match '{new_m_id}' created successfully!")
                            st.rerun()
                        else:
                            st.error("Please enter unique ID and different teams")
            
            with col2:
                if db_global["matches"]:
                    st.markdown("#### Manage Matches")
                    matches_list = list(db_global["matches"].keys())
                    default_index = matches_list.index(db_global["active_match_id"]) if db_global["active_match_id"] in matches_list else 0
                    selected_focus = st.selectbox("Select Match:", matches_list, index=default_index, key="select_match_admin")
                    
                    if st.button("Set Active", use_container_width=True, key="set_active_btn"):
                        db_global["active_match_id"] = selected_focus
                        st.rerun()
                    
                    if db_global["active_match_id"] in db_global["matches"]:
                        active_match = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
                        if active_match["current_innings"] == 1:
                            if st.button("➡️ Start Innings 2", type="primary", use_container_width=True, key="start_innings_2_btn"):
                                with lock:
                                    active_match["current_innings"] = 2
                                st.success("Moving to Innings 2!")
                                st.rerun()

    if not db_global["active_match_id"] or db_global["active_match_id"] not in db_global["matches"]:
        st.info("⏳ No active match. Please create one using admin panel.")
    else:
        m_instance = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
        inn_key = "innings_1" if m_instance["current_innings"] == 1 else "innings_2"
        inn_data = m_instance[inn_key]
        
        bat_team = m_instance["team_1"] if m_instance["current_innings"] == 1 else m_instance["team_2"]
        bowl_team = m_instance["team_2"] if m_instance["current_innings"] == 1 else m_instance["team_1"]
        target_score = (m_instance["innings_1"]["runs"] + 1) if m_instance["current_innings"] == 2 else None
        
        # Add PDF Export Button at Top of Live Match
        st.markdown("---")
        col_pdf_top1, col_pdf_top2, col_pdf_top3 = st.columns([1, 2, 1])
        with col_pdf_top2:
            try:
                pdf_data = generate_pdf_bytes(m_instance)
                st.download_button(
                    label="📥 EXPORT MATCH SCORECARD (PDF)",
                    data=pdf_data,
                    file_name=f"APL_{m_instance['id']}_Match_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="pdf_top_export_btn"
                )
            except Exception as e:
                st.error(f"PDF Generation Error: {str(e)}")
        st.markdown("---")
        
        if inn_data["b1"]["name"] == "":
            if is_admin:
                st.warning(f"⚙️ Configure batting lineup for Innings #{m_instance['current_innings']}")
                with st.form(f"opening_lineup_setup_{inn_key}"):
                    bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else ["Player 1", "Player 2"]
                    bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else ["Player 1", "Player 2"]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        p1 = st.selectbox("Striker", bat_squad, index=0, key="striker_select")
                    with col2:
                        p2 = st.selectbox("Non-Striker", bat_squad, index=1 if len(bat_squad) > 1 else 0, key="non_striker_select")
                    with col3:
                        bw = st.selectbox("Opening Bowler", bowl_squad, index=0, key="opening_bowler_select")
                    
                    if st.form_submit_button("🏏 Start Match", use_container_width=True):
                        with lock:
                            inn_data["b1"]["name"] = p1
                            inn_data["b2"]["name"] = p2
                            inn_data["bowler"]["name"] = bw
                        st.rerun()
            else:
                st.info(f"⏳ Waiting for scorer to start Innings #{m_instance['current_innings']}")
        else:
            comp_ov = inn_data["balls"] // 6
            rem_bl = inn_data["balls"] % 6
            frac_ov = comp_ov + (rem_bl / 6)
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            innings_ended = (comp_ov >= m_instance["total_overs"]) or (inn_data["wickets"] >= 10)
            if target_score and inn_data["runs"] >= target_score:
                innings_ended = True
                
            status_tag = "🏁 FINISHED" if innings_ended else "🟢 LIVE"

            l_col, r_col = st.columns([1.2, 0.8])
            
            with l_col:
                b_local = TEAM_DB[bat_team]["local"] if bat_team in TEAM_DB else ""
                b_remote = TEAM_DB[bat_team]["remote"] if bat_team in TEAM_DB else ""
                f_local = TEAM_DB[bowl_team]["local"] if bowl_team in TEAM_DB else ""
                f_remote = TEAM_DB[bowl_team]["remote"] if bowl_team in TEAM_DB else ""
                
                b_logo_src = get_image_src(b_local, b_remote)
                f_logo_src = get_image_src(f_local, f_remote)
                t_logo_src = get_tournament_logo_src()
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 30px; margin-bottom: 15px;">
                        <div style="text-align: center;">
                            <img src="{b_logo_src}" style="width: 70px; height: 70px; object-fit: contain; border-radius: 12px;">
                            <div style="font-weight: bold; margin-top: 5px;">{bat_team}</div>
                        </div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #e94560;">VS</div>
                        <div style="text-align: center;">
                            <img src="{f_logo_src}" style="width: 70px; height: 70px; object-fit: contain; border-radius: 12px;">
                            <div style="font-weight: bold; margin-top: 5px;">{bowl_team}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">{status_tag}</span>
                        <h1 style="font-size: 3.5rem; margin: 5px 0;">{inn_data['runs']} - {inn_data['wickets']}</h1>
                        <h4>Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</h4>
                        <h4>Run Rate: {crr:.2f}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                if target_score:
                    st.warning(f"🎯 Target: {target_score} | Need {target_score - inn_data['runs']} runs from {(m_instance['total_overs']*6) - inn_data['balls']} balls")

                col1, col2 = st.columns(2)
                col1.metric("Extras", f"{inn_data['extras'] + inn_data.get('penalty', 0)}")
                col2.metric("CRR", f"{crr:.2f}")

                st.markdown("##### 📦 Current Over")
                if inn_data["this_over"]:
                    html_b = ""
                    for b in inn_data["this_over"]:
                        bg_color = "#475569"
                        if str(b) in ["4", "6"]: bg_color = "#10B981"
                        elif "W" in str(b): bg_color = "#EF4444"
                        elif "WD" in str(b) or "NB" in str(b): bg_color = "#F59E0B"
                        html_b += f'<span class="ball-bubble" style="background-color:{bg_color};">{b}</span>'
                    st.markdown(html_b, unsafe_allow_html=True)
                else: 
                    st.caption("No deliveries yet")
                
                match_outcome = get_match_result(m_instance)
                st.info(f"📢 {match_outcome}")

            with r_col:
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.7rem;"><b>🏏 BATTING</b></div>
                        <div style="display:flex; justify-content:space-between; margin:5px 0;">
                            <span>{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}</span>
                            <span><b>{inn_data['b1']['runs']}</b> ({inn_data['b1']['balls']}b)</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin:5px 0;">
                            <span>{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}</span>
                            <span><b>{inn_data['b2']['runs']}</b> ({inn_data['b2']['balls']}b)</span>
                        </div>
                        <div style="margin-top:10px; font-size:0.7rem;"><b>🥎 BOWLING</b></div>
                        <div style="display:flex; justify-content:space-between; margin:5px 0;">
                            <span>{inn_data['bowler']['name']}</span>
                            <span>W: {inn_data['bowler']['wickets']} | R: {inn_data['bowler']['runs']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin:
                    st.markdown("### 🎮 Scoring Controls")
                    
                    def process_ball_input(runs_inc, extra_inc=0, is_legal=True, is_wicket=False, symbol=None):
                        with lock:
                            state_snap = copy.deepcopy({
                                "runs": inn_data["runs"], "wickets": inn_data["wickets"], "balls": inn_data["balls"],
                                "extras": inn_data["extras"], "penalty": inn_data.get("penalty", 0), 
                                "this_over": list(inn_data["this_over"]), "over_history": copy.deepcopy(inn_data["over_history"]),
                                "b1": copy.deepcopy(inn_data["b1"]), "b2": copy.deepcopy(inn_data["b2"]), 
                                "bowler": copy.deepcopy(inn_data["bowler"]),
                                "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]), 
                                "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
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
                        st.error("☝️ Wicket! Select new batsman:")
                        used_batsmen = [inn_data["b1"]["name"], inn_data["b2"]["name"]] + [b["name"] for b in inn_data["all_batsmen_history"]]
                        bat_squad = TEAM_DB[bat_team]["squad"] if bat_team in TEAM_DB else []
                        available_batters = [p for p in bat_squad if p not in used_batsmen]
                        if not available_batters: available_batters = bat_squad
                        
                        next_b = st.selectbox("New Batsman:", available_batters, key="new_batsman_select")
                        if st.button("Confirm Batsman", type="primary", use_container_width=True, key="confirm_batsman_btn"):
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
                        st.success("🔄 Over complete! Select next bowler:")
                        bowl_squad = TEAM_DB[bowl_team]["squad"] if bowl_team in TEAM_DB else []
                        next_bw = st.selectbox("Next Bowler:", bowl_squad, key="next_bowler_select")
                        if st.button("Confirm Bowler", type="primary", use_container_width=True, key="confirm_bowler_btn"):
                            with lock:
                                if inn_data["bowler"]["name"] != "":
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
                            st.rerun()

                    elif not innings_ended:
                        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                        with col_btn1:
                            if st.button("0", use_container_width=True, key="runs_0"):
                                process_ball_input(0, 0, True)
                                st.rerun()
                        with col_btn2:
                            if st.button("1", use_container_width=True, key="runs_1"):
                                process_ball_input(1, 0, True)
                                st.rerun()
                        with col_btn3:
                            if st.button("2", use_container_width=True, key="runs_2"):
                                process_ball_input(2, 0, True)
                                st.rerun()
                        with col_btn4:
                            if st.button("3", use_container_width=True, key="runs_3"):
                                process_ball_input(3, 0, True)
                                st.rerun()
                        
                        col_btn5, col_btn6, col_btn7, col_btn8 = st.columns(4)
                        with col_btn5:
                            if st.button("4", use_container_width=True, key="runs_4"):
                                process_ball_input(4, 0, True)
                                (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["fours"] += 1
                                st.rerun()
                        with col_btn6:
                            if st.button("6", use_container_width=True, key="runs_6"):
                                process_ball_input(6, 0, True)
                                (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["sixes"] += 1
                                st.rerun()
                        with col_btn7:
                            if st.button("WD", use_container_width=True, key="wide_btn"):
                                process_ball_input(1, 1, False, symbol="WD")
                                st.rerun()
                        with col_btn8:
                            if st.button("NB", use_container_width=True, key="no_ball_btn"):
                                process_ball_input(1, 1, False, symbol="NB")
                                st.rerun()
                        
                        if st.button("☝️ WICKET", type="primary", use_container_width=True, key="wicket_btn"):
                            process_ball_input(runs_inc=0, extra_inc=0, is_legal=True, is_wicket=True, symbol="W")
                            st.rerun()
                    else:
                        st.success("🏁 Innings complete!")

                    with st.expander("⚖️ Add Extras/Penalty"):
                        adj_col1, adj_col2 = st.columns([2, 1])
                        with adj_col1:
                            adjustment_type = st.selectbox("Type:", ["General Extras", "Penalty Runs"], key="adj_type")
                        with adj_col2:
                            runs_to_add = st.number_input("Runs:", min_value=1, max_value=20, value=1, key="runs_to_add")
                            
                        if st.button("Add Runs", use_container_width=True, key="add_runs_btn"):
                            mapped_type = "Extras" if adjustment_type == "General Extras" else "Penalty"
                            with lock:
                                state_snap = copy.deepcopy({
                                    "runs": inn_data["runs"], "extras": inn_data["extras"],
                                    "penalty": inn_data.get("penalty", 0), "this_over": list(inn_data["this_over"])
                                })
                                if "undo_stack" not in inn_data: inn_data["undo_stack"] = []
                                inn_data["undo_stack"].append(state_snap)
                                
                                inn_data["runs"] += runs_to_add
                                if mapped_type == "Extras":
                                    inn_data["extras"] += runs_to_add
                                    inn_data["this_over"].append(f"+{runs_to_add}")
                                else:
                                    if "penalty" not in inn_data: inn_data["penalty"] = 0
                                    inn_data["penalty"] += runs_to_add
                                    inn_data["this_over"].append(f"P+{runs_to_add}")
                            st.rerun()

                    col_undo, col_swap = st.columns(2)
                    with col_undo:
                        if "undo_stack" in inn_data and inn_data["undo_stack"]:
                            if st.button("↩️ Undo", use_container_width=True, key="undo_btn"):
                                with lock:
                                    prev_state = inn_data["undo_stack"].pop()
                                    for k in ["runs", "wickets", "balls", "extras", "penalty", "this_over", 
                                              "over_history", "b1", "b2", "bowler", "all_batsmen_history", 
                                              "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]:
                                        if k in prev_state:
                                            inn_data[k] = prev_state[k]
                                st.rerun()
                    with col_swap:
                        if not innings_ended and not inn_data["awaiting_batsman"] and not inn_data["awaiting_bowler"]:
                            if st.button("🔄 Swap", use_container_width=True, key="swap_btn"):
                                with lock:
                                    inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                    inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                st.rerun()

                st.markdown("##### 📊 Over History")
                if inn_data["over_history"]:
                    df = pd.DataFrame(inn_data["over_history"])
                    st.dataframe(df[["Over", "Bowler", "Score", "Timeline"]], use_container_width=True, hide_index=True)
                else: 
                    st.caption("No overs recorded")

            # PDF Export Button at Bottom
            st.markdown("---")
            col_pdf_bottom1, col_pdf_bottom2, col_pdf_bottom3 = st.columns([1, 2, 1])
            with col_pdf_bottom2:
                try:
                    pdf_data = generate_pdf_bytes(m_instance)
                    st.download_button(
                        label="📥 EXPORT MATCH SCORECARD (PDF)",
                        data=pdf_data,
                        file_name=f"APL_{m_instance['id']}_Match_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                        key="pdf_bottom_export_btn"
                    )
                except Exception as e:
                    st.error(f"PDF Generation Error: {str(e)}")
            st.markdown("---")

# ================= TAB: TOURNAMENT REVIEW LEDGER =================
with tab_review:
    st.markdown("### 📊 Match Archives")
    if not db_global["matches"]:
        st.info("No matches recorded yet.")
    else:
        matches_list = list(db_global["matches"].keys())
        select_review_id = st.selectbox("Select Match:", matches_list, key="review_match_select")
        m_rev = ensure_match_keys(db_global["matches"][select_review_id])
        
        st.markdown(f"## 🏏 {m_rev['id']}")
        st.info(f"**{m_rev['team_1']}** vs **{m_rev['team_2']}**")
        
        d1 = m_rev["innings_1"]
        d2 = m_rev["innings_2"]
        
        match_outcome = get_match_result(m_rev)
        if "WINNER" in match_outcome:
            st.success(match_outcome)
        elif "Tie" in match_outcome:
            st.warning(match_outcome)
        else:
            st.info(match_outcome)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Innings 1: {m_rev['team_1']}")
            st.metric("Score", f"{d1['runs']} - {d1['wickets']}", f"{d1['balls'] // 6}.{d1['balls'] % 6} overs")
            if d1["over_history"]: 
                st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
            else: 
                st.caption("No overs recorded")
        with col2:
            st.subheader(f"Innings 2: {m_rev['team_2']}")
            st.metric("Score", f"{d2['runs']} - {d2['wickets']}", f"{d2['balls'] // 6}.{d2['balls'] % 6} overs")
            if d2["over_history"]: 
                st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
            else: 
                st.caption("No overs recorded")
        
        # PDF Export Button for Archives
        st.markdown("---")
        try:
            pdf_data = generate_pdf_bytes(m_rev)
            st.download_button(
                label="📥 DOWNLOAD FULL SCORECARD (PDF)",
                data=pdf_data,
                file_name=f"APL_{m_rev['id']}_Full_Scorecard.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key="archive_pdf_download"
            )
        except Exception:
            st.info("📄 PDF available for this match")
