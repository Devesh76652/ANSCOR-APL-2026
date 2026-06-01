import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from datetime import datetime
import io
import re
import json
from typing import Dict, List, Optional
from collections import defaultdict

# Page Configuration
st.set_page_config(
    page_title="APL 2026 - Professional Cricket Scorer", 
    page_icon="🏏", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# GitHub repo path
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"
TOURNAMENT_LOGO_FILE = "image_4d6904.png"

# Team Database
TEAM_DB = {
    "Capital Chellengers": {
        "local": "CapitalChellengers.jpeg",
        "remote": GITHUB_RAW_BASE + "CapitalChellengers.jpeg",
        "squad": ["Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"],
        "short_name": "CAP",
        "city": "Mumbai",
        "founded": 2020
    },
    "Black panther": {
        "local": "Blackpanther.jpeg",
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"],
        "short_name": "BLK",
        "city": "Delhi",
        "founded": 2020
    },
    "Super Kings": {
        "local": "SuperKings.jpeg",
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"],
        "short_name": "SK",
        "city": "Chennai",
        "founded": 2020
    },
    "Power Hitter": {
        "local": "PowerHitter.jpeg",
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"],
        "short_name": "PH",
        "city": "Kolkata",
        "founded": 2020
    },
    "Royal Warriors XI": {
        "local": "RoyalWarriorsXI.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"],
        "short_name": "RW",
        "city": "Jaipur",
        "founded": 2020
    },
    "UnStoppable": {
        "local": "UnStoppable.jpeg",
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"],
        "short_name": "US",
        "city": "Pune",
        "founded": 2020
    }
}

# Ball-by-Ball Commentary Storage
commentary_store = []

# Player Statistics Database
player_stats = defaultdict(lambda: {
    "matches": 0, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
    "wickets": 0, "overs": 0, "runs_conceded": 0, "catches": 0,
    "fifties": 0, "hundreds": 0, "five_wickets": 0
})

# Scheduled Matches
scheduled_matches = []

def get_image_base64(local_path, remote_url=""):
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return ""

def get_team_logo_base64(team_name):
    team_data = TEAM_DB.get(team_name, {})
    local_path = team_data.get("local", "")
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return ""

# Enhanced CSS
st.markdown("""
    <style>
    /* Modern Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .main {
        animation: fadeIn 0.5s ease-out;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(59,130,246,0.5);
    }
    div[data-testid="column"] button {
        padding: 12px 0;
        font-size: 18px;
        font-weight: 700;
    }
    .compact-score {
        background: linear-gradient(135deg, #1E3A8A, #0F172A);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid rgba(59,130,246,0.5);
        position: relative;
        animation: slideIn 0.5s ease-out;
    }
    .score-big {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F1F5F9, #94A3B8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .info-row {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        font-size: 15px;
        border: 1px solid rgba(59,130,246,0.3);
        transition: all 0.3s ease;
    }
    .info-row:hover {
        transform: translateX(5px);
        border-color: #3B82F6;
    }
    .ball {
        display: inline-block;
        width: 45px;
        height: 45px;
        line-height: 45px;
        text-align: center;
        border-radius: 50%;
        margin: 5px;
        font-weight: bold;
        font-size: 16px;
        animation: fadeIn 0.3s ease-out;
        transition: transform 0.2s;
        cursor: pointer;
    }
    .ball:hover {
        transform: scale(1.1);
    }
    .run-ball { background: linear-gradient(135deg, #475569, #334155); color: white; }
    .four-ball { background: linear-gradient(135deg, #10B981, #059669); color: white; animation: pulse 0.5s ease; }
    .six-ball { background: linear-gradient(135deg, #10B981, #059669); color: white; animation: pulse 0.5s ease; }
    .wicket-ball { background: linear-gradient(135deg, #EF4444, #DC2626); color: white; animation: shake 0.5s ease; }
    .extra-ball { background: linear-gradient(135deg, #F59E0B, #D97706); color: white; }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981, #059669) !important;
        font-size: 18px !important;
        padding: 12px 24px !important;
    }
    .team-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        border: 1px solid rgba(59,130,246,0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .team-card:hover {
        transform: translateY(-5px) scale(1.02);
        border-color: #3B82F6;
        box-shadow: 0 20px 25px -12px rgba(59,130,246,0.3);
    }
    .team-logo-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid #3B82F6;
        object-fit: cover;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .team-card:hover .team-logo-large {
        transform: scale(1.05);
    }
    .team-name-large {
        font-size: 1.1rem;
        font-weight: 700;
        color: #F1F5F9;
    }
    .squad-player {
        padding: 5px 10px;
        margin: 3px;
        background: #0F172A;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    .squad-player:hover {
        background: #3B82F6;
        transform: scale(1.02);
    }
    
    /* LIVE Indicator */
    .live-indicator {
        position: absolute;
        top: 15px;
        right: 20px;
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        padding: 5px 15px;
        border-radius: 25px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 15px rgba(239,68,68,0.5);
    }
    .finished-indicator {
        position: absolute;
        top: 15px;
        right: 20px;
        background: linear-gradient(135deg, #6B7280, #4B5563);
        color: white;
        padding: 5px 15px;
        border-radius: 25px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    
    /* Commentary Box */
    .commentary-box {
        background: #0F172A;
        border-radius: 12px;
        padding: 15px;
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #334155;
    }
    .commentary-item {
        padding: 8px;
        margin: 5px 0;
        border-left: 3px solid #3B82F6;
        background: #1E293B;
        border-radius: 8px;
        font-size: 13px;
        animation: slideIn 0.3s ease-out;
    }
    .commentary-four {
        border-left-color: #10B981;
        background: rgba(16,185,129,0.1);
    }
    .commentary-six {
        border-left-color: #10B981;
        background: rgba(16,185,129,0.1);
    }
    .commentary-wicket {
        border-left-color: #EF4444;
        background: rgba(239,68,68,0.1);
    }
    
    /* Notification */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1E293B;
        border-left: 4px solid #3B82F6;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    
    /* Player Profile Card */
    .player-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s;
    }
    .player-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 15px;
    }
    .stat-box {
        background: #0F172A;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #3B82F6;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #94A3B8;
    }
    
    /* Rankings Table */
    .rankings-table {
        background: #1E293B;
        border-radius: 12px;
        overflow: hidden;
    }
    .rank-row {
        display: flex;
        padding: 10px 15px;
        border-bottom: 1px solid #334155;
        transition: background 0.2s;
    }
    .rank-row:hover {
        background: #2D3A4E;
    }
    .rank-number {
        width: 50px;
        font-weight: 800;
        color: #F59E0B;
    }
    .rank-name {
        flex: 1;
        font-weight: 600;
    }
    .rank-value {
        width: 80px;
        text-align: right;
        font-weight: 700;
        color: #10B981;
    }
    
    /* Match Schedule Card */
    .schedule-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #3B82F6;
    }
    </style>
""", unsafe_allow_html=True)

def add_commentary(description, runs, is_wicket=False, is_four=False, is_six=False, bowler="", batsman=""):
    """Add ball-by-ball commentary"""
    commentary = {
        "ball_number": len(commentary_store) + 1,
        "runs": runs,
        "is_wicket": is_wicket,
        "is_four": is_four,
        "is_six": is_six,
        "bowler": bowler,
        "batsman": batsman,
        "timestamp": datetime.now(),
        "description": description
    }
    commentary_store.insert(0, commentary)
    
    # Keep only last 50 comments
    while len(commentary_store) > 50:
        commentary_store.pop()
    
    # Send notification for key events
    if is_wicket:
        st.toast(f"🎉 WICKET! {batsman} is out!", icon="⚡")
    elif is_six:
        st.toast(f"💥 SIX! {batsman} hits a maximum!", icon="🏏")
    elif is_four:
        st.toast(f"🎯 FOUR! {batsman} finds the boundary!", icon="🎯")

def update_player_stats(player_name, runs=0, balls=0, fours=0, sixes=0, wicket=False, overs=0, runs_conceded=0):
    """Update player statistics"""
    stats = player_stats[player_name]
    stats["matches"] += 1
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
    
    stats["overs"] += overs
    stats["runs_conceded"] += runs_conceded

def get_top_batsmen(limit=10):
    """Get top run scorers"""
    batsmen = []
    for name, stats in player_stats.items():
        if stats["runs"] > 0:
            avg = stats["runs"] / stats["matches"] if stats["matches"] > 0 else 0
            sr = (stats["runs"] * 100 / stats["balls"]) if stats["balls"] > 0 else 0
            batsmen.append({
                "name": name,
                "runs": stats["runs"],
                "matches": stats["matches"],
                "average": avg,
                "strike_rate": sr,
                "fours": stats["fours"],
                "sixes": stats["sixes"],
                "fifties": stats["fifties"],
                "hundreds": stats["hundreds"]
            })
    return sorted(batsmen, key=lambda x: x["runs"], reverse=True)[:limit]

def get_top_bowlers(limit=10):
    """Get top wicket takers"""
    bowlers = []
    for name, stats in player_stats.items():
        if stats["wickets"] > 0:
            econ = stats["runs_conceded"] / stats["overs"] if stats["overs"] > 0 else 0
            avg = stats["runs_conceded"] / stats["wickets"] if stats["wickets"] > 0 else 0
            bowlers.append({
                "name": name,
                "wickets": stats["wickets"],
                "matches": stats["matches"],
                "economy": econ,
                "average": avg,
                "runs": stats["runs_conceded"],
                "overs": stats["overs"]
            })
    return sorted(bowlers, key=lambda x: x["wickets"], reverse=True)[:limit]

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
                "innings_1": init_innings(), "innings_2": init_innings(), "created_at": datetime.now().isoformat()}
    if "innings_1" not in m:
        m["innings_1"] = init_innings()
    if "innings_2" not in m:
        m["innings_2"] = init_innings()
    if "created_at" not in m:
        m["created_at"] = datetime.now().isoformat()
    return m

def get_match_status(m):
    d1, d2 = m["innings_1"], m["innings_2"]
    if d1["b1"]["name"] == "":
        return "Awaiting lineup"
    total_balls = m["total_overs"] * 6
    if m["current_innings"] == 1:
        if d1["balls"] >= total_balls or d1["wickets"] >= 10:
            return f"Innings 1: {d1['runs']}/{d1['wickets']}"
        return f"{m['team_1']} batting"
    target = d1["runs"] + 1
    if d2["runs"] >= target:
        return f"{m['team_2']} wins by {10 - d2['wickets']} wickets"
    if d2["balls"] >= total_balls or d2["wickets"] >= 10:
        if d2["runs"] < d1["runs"]:
            return f"{m['team_1']} wins by {d1['runs'] - d2['runs']} runs"
        elif d2["runs"] == d1["runs"]:
            return "MATCH TIED"
    return f"Need {target - d2['runs']} runs from {total_balls - d2['balls']} balls"

def clean_text(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    text = ''.join(char if ord(char) < 128 else ' ' for char in text)
    return text.strip()

def generate_complete_pdf(m):
    """Generate complete PDF with both innings details"""
    try:
        m = ensure_match(m)
        pdf = FPDF()
        
        # Page 1: Innings 1
        pdf.add_page()
        pdf.set_fill_color(59, 130, 246)
        pdf.rect(0, 0, 210, 10, 'F')
        pdf.set_font("Arial", "B", 22)
        pdf.cell(0, 15, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "OFFICIAL MATCH SCORECARD", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, f"{clean_text(m['team_1'])} vs {clean_text(m['team_2'])} ({m['total_overs']} Overs)", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 6, f"Match ID: {clean_text(m['id'])}", ln=True, align="C")
        pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        
        result = get_match_status(m)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(200, 230, 200)
        pdf.rect(10, 70, 190, 10, 'F')
        pdf.set_xy(15, 73)
        pdf.cell(0, 6, clean_text(result), ln=True)
        
        output_buffer = io.BytesIO()
        pdf.output(output_buffer)
        return output_buffer.getvalue()
    except:
        return b""

@st.cache_resource
def get_db():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db = get_db()

# Initialize session state
if 'notifications_enabled' not in st.session_state:
    st.session_state.notifications_enabled = True
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'commentary_enabled' not in st.session_state:
    st.session_state.commentary_enabled = True

# Sidebar with enhanced UI
with st.sidebar:
    st.markdown("### 🏏 APL 2026")
    st.markdown("---")
    
    # Theme Toggle
    theme = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = theme
    
    # Notifications Toggle
    st.session_state.notifications_enabled = st.toggle("🔔 Live Notifications", value=st.session_state.notifications_enabled)
    
    # Commentary Toggle
    st.session_state.commentary_enabled = st.toggle("📝 Ball-by-Ball Commentary", value=st.session_state.commentary_enabled)
    
    st.markdown("---")
    
    role = st.radio("Access:", ["👤 Player View", "⚡ Scorer Panel"])
    
    is_admin = False
    if role == "⚡ Scorer Panel":
        pwd = st.text_input("Password:", type="password")
        if pwd == "anscor2026":
            is_admin = True
            st.success("✅ Admin Access Granted")
        elif pwd:
            st.error("Wrong Password")
    
    if not is_admin:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=3000, key="refresh")
        except:
            pass

# Tabs
tab_live, tab_history, tab_players, tab_rankings, tab_schedule, tab_teams = st.tabs([
    "🏏 Live", "📊 Analytics", "👤 Players", "🏆 Rankings", "📅 Schedule", "👥 Teams"
])

# Teams Tab
with tab_teams:
    st.markdown("### 🏏 Tournament Teams")
    st.markdown("---")
    
    cols = st.columns(3)
    for idx, (team_name, team_data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            logo_base64 = get_team_logo_base64(team_name)
            
            if logo_base64:
                st.markdown(f"""
                    <div class="team-card">
                        <img src="data:image/jpeg;base64,{logo_base64}" class="team-logo-large">
                        <div class="team-name-large">{team_name}</div>
                        <div style="font-size: 11px; color: #94A3B8;">{team_data.get('city', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="team-card">
                        <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #3B82F6, #2563EB); border-radius: 50%; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 2rem; color: white;">{team_name[0]}</span>
                        </div>
                        <div class="team-name-large">{team_name}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            if st.button(f"View Squad", key=f"squad_btn_{idx}", use_container_width=True):
                with st.expander(f"{team_name} Squad ({len(team_data['squad'])} Players)", expanded=True):
                    player_cols = st.columns(2)
                    for i, player in enumerate(team_data['squad']):
                        with player_cols[i % 2]:
                            st.markdown(f'<div class="squad-player">🏏 {player}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Tournament Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Teams", len(TEAM_DB))
    with col2:
        total_players = sum(len(data["squad"]) for data in TEAM_DB.values())
        st.metric("Total Players", total_players)
    with col3:
        matches_played = len([m for m in db["matches"].values() if m["innings_1"]["balls"] > 0])
        st.metric("Matches Played", matches_played)
    with col4:
        st.metric("Format", "T10/T20")

# Schedule Tab
with tab_schedule:
    st.markdown("### 📅 Match Schedule")
    st.markdown("---")
    
    if is_admin:
        with st.expander("📝 Schedule New Match", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_match_id = st.text_input("Match ID:", "Match_Schedule_01")
                team1_sch = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="sch_t1")
                date_sch = st.date_input("Match Date:", datetime.now())
            with col2:
                venue_sch = st.text_input("Venue:", "Main Stadium")
                team2_sch = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="sch_t2")
                time_sch = st.time_input("Match Time:", datetime.now().time())
            
            if st.button("Schedule Match", use_container_width=True):
                scheduled_matches.append({
                    "match_id": new_match_id,
                    "team1": team1_sch,
                    "team2": team2_sch,
                    "scheduled_date": datetime.combine(date_sch, time_sch),
                    "venue": venue_sch,
                    "status": "upcoming"
                })
                st.success(f"Match scheduled for {date_sch} at {venue_sch}")
                st.rerun()
    
    # Display scheduled matches
    for match in scheduled_matches:
        st.markdown(f"""
            <div class="schedule-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{match['match_id']}</strong><br>
                        {match['team1']} vs {match['team2']}<br>
                        📍 {match['venue']}
                    </div>
                    <div style="text-align: right;">
                        🕐 {match['scheduled_date'].strftime('%Y-%m-%d %H:%M')}<br>
                        <span style="background: #3B82F6; padding: 2px 10px; border-radius: 20px; font-size: 11px;">{match['status'].upper()}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Rankings Tab
with tab_rankings:
    st.markdown("### 🏆 Player Rankings")
    st.markdown("---")
    
    tab_batsmen, tab_bowlers = st.tabs(["🏏 Top Batsmen", "🎯 Top Bowlers"])
    
    with tab_batsmen:
        top_batsmen = get_top_batsmen(10)
        if top_batsmen:
            df_batsmen = pd.DataFrame(top_batsmen)
            df_batsmen.index = range(1, len(df_batsmen) + 1)
            st.dataframe(df_batsmen, use_container_width=True)
        else:
            st.info("No batting statistics available yet")
    
    with tab_bowlers:
        top_bowlers = get_top_bowlers(10)
        if top_bowlers:
            df_bowlers = pd.DataFrame(top_bowlers)
            df_bowlers.index = range(1, len(df_bowlers) + 1)
            st.dataframe(df_bowlers, use_container_width=True)
        else:
            st.info("No bowling statistics available yet")

# Players Tab
with tab_players:
    st.markdown("### 👤 Player Profiles")
    st.markdown("---")
    
    # Search player
    all_players = []
    for team in TEAM_DB.values():
        all_players.extend(team["squad"])
    
    search_player = st.selectbox("Search Player:", sorted(all_players))
    
    if search_player:
        stats = player_stats.get(search_player, {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="player-card">
                    <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #3B82F6, #2563EB); border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 2rem; color: white;">{search_player[0]}</span>
                    </div>
                    <h3>{search_player}</h3>
                    <div class="player-stats">
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('matches', 0)}</div>
                            <div class="stat-label">Matches</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('runs', 0)}</div>
                            <div class="stat-label">Runs</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('wickets', 0)}</div>
                            <div class="stat-label">Wickets</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="player-card">
                    <h4>Batting Stats</h4>
                    <div class="player-stats">
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('fours', 0)}</div>
                            <div class="stat-label">Fours</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('sixes', 0)}</div>
                            <div class="stat-label">Sixes</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('fifties', 0)}</div>
                            <div class="stat-label">50s</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="player-card">
                    <h4>Bowling Stats</h4>
                    <div class="player-stats">
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('overs', 0):.1f}</div>
                            <div class="stat-label">Overs</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('runs_conceded', 0)}</div>
                            <div class="stat-label">Runs</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('five_wickets', 0)}</div>
                            <div class="stat-label">5-Wkts</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# History & Analytics Tab
with tab_history:
    st.markdown("### 📊 Match Analytics Dashboard")
    st.markdown("---")
    
    if db["matches"]:
        # Match Selector
        selected_match = st.selectbox("Select Match to Analyze:", list(db["matches"].keys()))
        m = ensure_match(db["matches"][selected_match])
        
        # Match Overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Runs", m["innings_1"]["runs"] + m["innings_2"]["runs"])
        with col2:
            st.metric("Total Wickets", m["innings_1"]["wickets"] + m["innings_2"]["wickets"])
        with col3:
            total_fours = (m["innings_1"]["b1"]["fours"] + m["innings_1"]["b2"]["fours"] + 
                          sum(b.get("fours", 0) for b in m["innings_1"].get("all_batsmen", [])))
            st.metric("Total Fours", total_fours)
        with col4:
            total_sixes = (m["innings_1"]["b1"]["sixes"] + m["innings_1"]["b2"]["sixes"] + 
                          sum(b.get("sixes", 0) for b in m["innings_1"].get("all_batsmen", [])))
            st.metric("Total Sixes", total_sixes)
        
        # Innings Comparison
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Innings 1: {m['team_1']}")
            st.metric("Score", f"{m['innings_1']['runs']}/{m['innings_1']['wickets']}")
            
            # Display batting table for innings 1
            if m["innings_1"]["over_history"]:
                st.dataframe(pd.DataFrame(m["innings_1"]["over_history"]), use_container_width=True)
        
        with col2:
            st.subheader(f"Innings 2: {m['team_2']}")
            st.metric("Score", f"{m['innings_2']['runs']}/{m['innings_2']['wickets']}")
            
            # Display batting table for innings 2
            if m["innings_2"]["over_history"]:
                st.dataframe(pd.DataFrame(m["innings_2"]["over_history"]), use_container_width=True)
        
        # Match Result
        st.success(get_match_status(m))
    else:
        st.info("No matches played yet. Start scoring to see analytics!")

# Live Match Tab
with tab_live:
    if is_admin:
        with st.expander("⚙️ New Match", expanded=not db["active_match_id"]):
            col1, col2, col3 = st.columns(3)
            with col1:
                match_id = st.text_input("Match ID:", "Match_01")
            with col2:
                team1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="t1")
            with col3:
                team2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="t2")
            
            col4, col5 = st.columns(2)
            with col4:
                overs = st.number_input("Overs:", 1, 20, 4)
            with col5:
                if st.button("🚀 Create Match", use_container_width=True):
                    if match_id and team1 != team2:
                        with db["lock"]:
                            db["matches"][match_id] = {
                                "id": match_id, "team_1": team1, "team_2": team2,
                                "total_overs": overs, "current_innings": 1,
                                "innings_1": init_innings(), "innings_2": init_innings(),
                                "created_at": datetime.now().isoformat()
                            }
                            db["active_match_id"] = match_id
                        st.success(f"Match '{match_id}' created!")
                        st.rerun()
        
        if db["matches"]:
            current = db["active_match_id"] if db["active_match_id"] else list(db["matches"].keys())[0]
            selected = st.selectbox("Active Match:", list(db["matches"].keys()), index=list(db["matches"].keys()).index(current))
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎯 Set Active", use_container_width=True):
                    db["active_match_id"] = selected
                    st.rerun()
            with col_b:
                if db["active_match_id"] and db["active_match_id"] in db["matches"]:
                    m = ensure_match(db["matches"][db["active_match_id"]])
                    if m["current_innings"] == 1 and m["innings_1"]["b1"]["name"]:
                        if st.button("➡️ Start Innings 2", use_container_width=True):
                            with db["lock"]:
                                m["current_innings"] = 2
                            st.success("Switched to Innings 2!")
                            st.rerun()
    
    if not db["active_match_id"] or db["active_match_id"] not in db["matches"]:
        st.info("No active match. Create one above.")
    else:
        match = ensure_match(db["matches"][db["active_match_id"]])
        inn = match["innings_1"] if match["current_innings"] == 1 else match["innings_2"]
        batting = match["team_1"] if match["current_innings"] == 1 else match["team_2"]
        bowling = match["team_2"] if match["current_innings"] == 1 else match["team_1"]
        target = match["innings_1"]["runs"] + 1 if match["current_innings"] == 2 else None
        
        total_balls_allowed = match["total_overs"] * 6
        if match["current_innings"] == 1:
            innings_complete = (inn["balls"] >= total_balls_allowed or inn["wickets"] >= 10)
        else:
            innings_complete = (inn["balls"] >= total_balls_allowed or inn["wickets"] >= 10 or (target and inn["runs"] >= target))
        
        if inn["b1"]["name"] == "" and is_admin:
            with st.form("setup"):
                st.warning(f"📝 Setup {batting} Batting Lineup")
                col1, col2, col3 = st.columns(3)
                with col1:
                    striker = st.selectbox("Striker:", TEAM_DB[batting]["squad"])
                with col2:
                    non_striker = st.selectbox("Non-Striker:", TEAM_DB[batting]["squad"])
                with col3:
                    bowler = st.selectbox("Bowler:", TEAM_DB[bowling]["squad"])
                if st.form_submit_button("🚀 Start Match", use_container_width=True):
                    with db["lock"]:
                        inn["b1"]["name"] = striker
                        inn["b2"]["name"] = non_striker
                        inn["bowler"]["name"] = bowler
                    st.success("Match Started!")
                    st.rerun()
        
        elif inn["b1"]["name"]:
            overs_done = inn["balls"] // 6
            balls_in_over = inn["balls"] % 6
            crr = inn["runs"] / (inn["balls"]/6) if inn["balls"] > 0 else 0
            
            b_logo = get_image_base64(TEAM_DB[batting]["local"], TEAM_DB[batting]["remote"])
            bowl_logo = get_image_base64(TEAM_DB[bowling]["local"], TEAM_DB[bowling]["remote"])
            
            if innings_complete:
                status_badge = '<span class="finished-indicator">🏁 FINISHED</span>'
            else:
                status_badge = '<span class="live-indicator">🔴 LIVE</span>'
            
            # Score Display
            st.markdown(f"""
                <div class="compact-score">
                    {status_badge}
                    <div style="display: flex; justify-content: center; align-items: center; gap: 15px;">
                        <div style="text-align: center;">
                            <img src="data:image/jpeg;base64,{b_logo}" style="width: 55px; height: 55px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="font-size: 10px; font-weight: bold; margin-top: 3px; color: #93C5FD;">{batting[:10]}</div>
                        </div>
                        <div style="text-align: center;">
                            <div class="score-big">{inn['runs']}-{inn['wickets']}</div>
                            <div style="font-size: 12px; color: #93C5FD;">{overs_done}.{balls_in_over}/{match['total_overs']} | CRR: {crr:.2f}</div>
                        </div>
                        <div style="text-align: center;">
                            <img src="data:image/jpeg;base64,{bowl_logo}" style="width: 55px; height: 55px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="font-size: 10px; font-weight: bold; margin-top: 3px; color: #93C5FD;">{bowling[:10]}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if target:
                runs_needed = target - inn['runs']
                balls_left = (match['total_overs'] * 6) - inn['balls']
                req_rate = runs_needed / (balls_left/6) if balls_left > 0 else 0
                if inn['runs'] >= target:
                    st.success(f"🏆 Target Achieved! {batting} wins!")
                else:
                    st.info(f"🎯 Target: {target} | Need {runs_needed} runs from {balls_left} balls | Required RR: {req_rate:.2f}")
            
            if is_admin:
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.markdown(f"""
                        <div class="info-row">
                            <b>🏏 BATTING PARTNERSHIP</b><br>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                <span>🎯 {inn['b1']['name'][:18]}{'*' if inn['b1']['strike'] else ''}</span>
                                <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                                <span>🎯 {inn['b2']['name'][:18]}{'*' if inn['b2']['strike'] else ''}</span>
                                <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}</span>
                            </div>
                        </div>
                        <div class="info-row">
                            <b>🥎 CURRENT BOWLER</b><br>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                <span>🎯 {inn['bowler']['name'][:18]}</span>
                                <span>{inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6}) | Econ: {inn['bowler']['runs']/(inn['bowler']['balls']/6) if inn['bowler']['balls']>0 else 0:.2f}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**📦 CURRENT OVER**")
                    if inn["this_over"]:
                        balls_html = ""
                        for ball in inn["this_over"]:
                            if ball in [4,6]:
                                balls_html += f'<span class="ball four-ball">{ball}</span>'
                            elif ball == "W":
                                balls_html += f'<span class="ball wicket-ball">{ball}</span>'
                            elif ball in ["WD", "NB"]:
                                balls_html += f'<span class="ball extra-ball">{ball}</span>'
                            else:
                                balls_html += f'<span class="ball run-ball">{ball}</span>'
                        st.markdown(balls_html, unsafe_allow_html=True)
                    else:
                        st.caption("No deliveries yet")
                    
                    if inn["over_history"]:
                        st.markdown("**📊 RECENT OVERS**")
                        for over in inn["over_history"][-3:]:
                            st.caption(f"Over {over['Over']}: {over['Bowler'][:12]} - {over['Timeline']}")
                    
                    st.info(f"📢 {get_match_status(match)}")
                
                with col_right:
                    st.markdown("### 🎛️ SCORING CONTROLS")
                    
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
                            
                            # Update player stats
                            if runs > 0:
                                update_player_stats(striker["name"], runs=runs, balls=1, 
                                                  fours=1 if runs == 4 else 0, sixes=1 if runs == 6 else 0)
                            
                            if wicket:
                                inn["wickets"] += 1
                                inn["bowler"]["wickets"] += 1
                                update_player_stats(inn["bowler"]["name"], wicket=True)
                            
                            if legal:
                                inn["balls"] += 1
                                inn["bowler"]["balls"] += 1
                                striker["balls"] += 1
                                striker["runs"] += (runs - extra)
                                inn["this_over"].append(symbol if symbol else runs)
                                
                                # Add commentary
                                if st.session_state.commentary_enabled:
                                    if wicket:
                                        add_commentary(f"OUT! {striker['name']} departs! Bowled by {inn['bowler']['name']}", runs, is_wicket=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    elif runs == 6:
                                        add_commentary(f"SIX! {striker['name']} sends it over the boundary!", runs, is_six=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    elif runs == 4:
                                        add_commentary(f"FOUR! {striker['name']} finds the gap!", runs, is_four=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    else:
                                        add_commentary(f"{runs} runs taken by {striker['name']}", runs, bowler=inn['bowler']['name'], batsman=striker['name'])
                            else:
                                inn["this_over"].append(symbol)
                                add_commentary(f"{symbol} called by the umpire", runs, bowler=inn['bowler']['name'], batsman=striker['name'])
                            
                            if legal and (runs % 2 == 1) and not wicket:
                                inn["b1"]["strike"] = not inn["b1"]["strike"]
                                inn["b2"]["strike"] = not inn["b2"]["strike"]
                            
                            legal_balls = [b for b in inn["this_over"] if b not in ['WD', 'NB']]
                            if len(legal_balls) == 6:
                                inn["awaiting_bowler"] = True
                            if wicket and inn["wickets"] < 10:
                                inn["awaiting_batsman"] = True
                    
                    # Keyboard shortcuts hint
                    st.caption("💡 Tip: Press 0,1,2,3,4,6 for runs, W for wicket, U for undo")
                    
                    if inn["awaiting_batsman"]:
                        st.warning("⚠️ New Batsman Required")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen"]]
                        available = [p for p in TEAM_DB[batting]["squad"] if p not in used]
                        if not available:
                            available = TEAM_DB[batting]["squad"]
                        new_bat = st.selectbox("Select Batsman:", available)
                        if st.button("✅ Confirm Batsman", use_container_width=True):
                            with db["lock"]:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True}
                                else:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False}
                                inn["awaiting_batsman"] = False
                                add_commentary(f"👤 New batsman: {new_bat} comes to the crease", 0)
                            st.rerun()
                    
                    elif inn["awaiting_bowler"]:
                        st.success("🔄 Over Complete! New Bowler Needed")
                        new_bowl = st.selectbox("Select Bowler:", TEAM_DB[bowling]["squad"])
                        if st.button("✅ Start Next Over", use_container_width=True):
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
                                add_commentary(f"🔄 New bowler: {new_bowl} comes into the attack", 0)
                            st.rerun()
                    
                    elif not innings_complete:
                        if target and inn["runs"] >= target:
                            st.success("🏆 Target Achieved! Match Complete")
                        else:
                            st.markdown("**RUNS**")
                            r1, r2, r3, r4 = st.columns(4)
                            with r1:
                                if st.button("0️⃣ 0", use_container_width=True):
                                    add_ball(0)
                                    st.rerun()
                                if st.button("1️⃣ 1", use_container_width=True):
                                    add_ball(1)
                                    st.rerun()
                            with r2:
                                if st.button("2️⃣ 2", use_container_width=True):
                                    add_ball(2)
                                    st.rerun()
                                if st.button("3️⃣ 3", use_container_width=True):
                                    add_ball(3)
                                    st.rerun()
                            with r3:
                                if st.button("4️⃣ 4", use_container_width=True):
                                    add_ball(4)
                                    if inn["b1"]["strike"]:
                                        inn["b1"]["fours"] += 1
                                    else:
                                        inn["b2"]["fours"] += 1
                                    st.rerun()
                                if st.button("6️⃣ 6", use_container_width=True):
                                    add_ball(6)
                                    if inn["b1"]["strike"]:
                                        inn["b1"]["sixes"] += 1
                                    else:
                                        inn["b2"]["sixes"] += 1
                                    st.rerun()
                            with r4:
                                if st.button("🟡 WD", use_container_width=True):
                                    add_ball(1, 1, False, symbol="WD")
                                    st.rerun()
                                if st.button("🟠 NB", use_container_width=True):
                                    add_ball(1, 1, False, symbol="NB")
                                    st.rerun()
                            
                            st.markdown("---")
                            a1, a2, a3 = st.columns(3)
                            with a1:
                                if st.button("☝️ OUT", type="primary", use_container_width=True):
                                    with db["lock"]:
                                        striker = inn["b1"] if inn["b1"]["strike"] else inn["b2"]
                                        add_commentary(f"WICKET! {striker['name']} is out!", 0, is_wicket=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    add_ball(0, 0, True, True, "W")
                                    st.rerun()
                            with a2:
                                if inn["undo_stack"]:
                                    if st.button("↩️ UNDO", use_container_width=True):
                                        with db["lock"]:
                                            prev = inn["undo_stack"].pop()
                                            for k in ["runs", "wickets", "balls", "extras", "this_over", "b1", "b2", "bowler"]:
                                                inn[k] = prev[k]
                                            add_commentary("⏪ Last ball undone", 0)
                                        st.rerun()
                            with a3:
                                if st.button("🔄 SWAP", use_container_width=True):
                                    with db["lock"]:
                                        inn["b1"]["strike"] = not inn["b1"]["strike"]
                                        inn["b2"]["strike"] = not inn["b2"]["strike"]
                                        add_commentary("🔄 Strike swapped", 0)
                                    st.rerun()
                    else:
                        st.success("🏁 Innings Complete!")
                        if match["current_innings"] == 1:
                            if st.button("➡️ Start Innings 2", use_container_width=True, type="primary"):
                                with db["lock"]:
                                    match["current_innings"] = 2
                                    add_commentary(f"🏏 Second innings begins. {match['team_2']} needs {match['innings_1']['runs'] + 1} runs to win", 0)
                                st.rerun()
                    
                    with st.expander("⚙️ Admin Tools", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            extra_type = st.selectbox("Type", ["Extras", "Penalty"])
                        with col2:
                            extra_runs = st.number_input("Runs", 1, 20, 1)
                        if st.button("➕ Add Runs", use_container_width=True):
                            with db["lock"]:
                                inn["runs"] += extra_runs
                                if extra_type == "Extras":
                                    inn["extras"] += extra_runs
                                    inn["this_over"].append(f"+{extra_runs}Ex")
                                    add_commentary(f"{extra_runs} extra runs added to total", extra_runs)
                                else:
                                    inn["penalty"] = inn.get("penalty", 0) + extra_runs
                                    inn["this_over"].append(f"+{extra_runs}Pen")
                                    add_commentary(f"{extra_runs} penalty runs awarded", extra_runs)
                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown("### 📄 EXPORT REPORT")
                    if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                        pdf_data = generate_complete_pdf(match)
                        if pdf_data and len(pdf_data) > 500:
                            st.download_button(
                                label="📥 DOWNLOAD COMPLETE SCORECARD (PDF)",
                                data=pdf_data,
                                file_name=f"APL_{match['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("⏳ Preparing PDF...")
            
            else:
                # Player View
                st.markdown(f"""
                    <div class="info-row">
                        <b>🏏 BATTING PARTNERSHIP</b><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                            <span>🎯 {inn['b1']['name'][:18]}{'*' if inn['b1']['strike'] else ''}</span>
                            <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span>🎯 {inn['b2']['name'][:18]}{'*' if inn['b2']['strike'] else ''}</span>
                            <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}</span>
                        </div>
                    </div>
                    <div class="info-row">
                        <b>🥎 CURRENT BOWLER</b><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                            <span>🎯 {inn['bowler']['name'][:18]}</span>
                            <span>{inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6}) | Econ: {inn['bowler']['runs']/(inn['bowler']['balls']/6) if inn['bowler']['balls']>0 else 0:.2f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**📦 CURRENT OVER**")
                if inn["this_over"]:
                    balls_html = ""
                    for ball in inn["this_over"]:
                        if ball in [4,6]:
                            balls_html += f'<span class="ball four-ball">{ball}</span>'
                        elif ball == "W":
                            balls_html += f'<span class="ball wicket-ball">{ball}</span>'
                        elif ball in ["WD", "NB"]:
                            balls_html += f'<span class="ball extra-ball">{ball}</span>'
                        else:
                            balls_html += f'<span class="ball run-ball">{ball}</span>'
                    st.markdown(balls_html, unsafe_allow_html=True)
                else:
                    st.caption("No deliveries yet")
                
                if inn["over_history"]:
                    st.markdown("**📊 RECENT OVERS**")
                    for over in inn["over_history"][-5:]:
                        st.caption(f"Over {over['Over']}: {over['Bowler']} - {over['Timeline']}")
                
                if inn["all_batsmen"]:
                    st.markdown("**📋 FALLEN WICKETS**")
                    for w in inn["all_batsmen"][-5:]:
                        st.caption(f"• {w['name']} - {w['runs']}({w['balls']})")
                
                st.info(f"📢 {get_match_status(match)}")
                
                st.markdown("---")
                if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                    pdf_data = generate_complete_pdf(match)
                    if pdf_data and len(pdf_data) > 500:
                        st.download_button(
                            label="📥 DOWNLOAD SCORECARD (PDF)",
                            data=pdf_data,
                            file_name=f"APL_{match['id']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            
            # Ball-by-Ball Commentary Section
            if st.session_state.commentary_enabled and commentary_store:
                st.markdown("---")
                st.markdown("### 📝 Live Commentary")
                st.markdown('<div class="commentary-box">', unsafe_allow_html=True)
                for comment in commentary_store[:10]:
                    css_class = "commentary-item"
                    if comment.get("is_six") or comment.get("is_four"):
                        css_class += " commentary-four"
                    elif comment.get("is_wicket"):
                        css_class += " commentary-wicket"
                    
                    st.markdown(f"""
                        <div class="{css_class}">
                            <small style="color:#94A3B8;">Ball {comment.get('ball_number', 0)}</small><br>
                            {comment.get('description', '')}
                            <small style="color:#6B7280; float:right;">{comment.get('timestamp', datetime.now()).strftime('%H:%M:%S')}</small>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
