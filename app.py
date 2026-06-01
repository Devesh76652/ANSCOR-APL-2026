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
        "short_name": "CAP"
    },
    "Black panther": {
        "local": "Blackpanther.jpeg",
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"],
        "short_name": "BLK"
    },
    "Super Kings": {
        "local": "SuperKings.jpeg",
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"],
        "short_name": "SK"
    },
    "Power Hitter": {
        "local": "PowerHitter.jpeg",
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"],
        "short_name": "PH"
    },
    "Royal Warriors XI": {
        "local": "RoyalWarriorsXI.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"],
        "short_name": "RW"
    },
    "UnStoppable": {
        "local": "UnStoppable.jpeg",
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"],
        "short_name": "US"
    }
}

# Global storage for player statistics
if 'player_stats' not in st.session_state:
    st.session_state.player_stats = defaultdict(lambda: {
        "matches": 0, "runs": 0, "balls": 0, "fours": 0, "sixes": 0,
        "wickets": 0, "overs": 0, "runs_conceded": 0,
        "fifties": 0, "hundreds": 0
    })

if 'commentary_store' not in st.session_state:
    st.session_state.commentary_store = []

if 'scheduled_matches' not in st.session_state:
    st.session_state.scheduled_matches = []

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

# CSS
st.markdown("""
    <style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Button styles */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(59,130,246,0.5);
    }
    
    /* Score display */
    .compact-score {
        background: linear-gradient(135deg, #1E3A8A, #0F172A);
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid rgba(59,130,246,0.5);
        position: relative;
    }
    .score-big {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
    }
    
    /* Info rows */
    .info-row {
        background: #1E293B;
        padding: 12px;
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #334155;
    }
    
    /* Ball bubbles */
    .ball {
        display: inline-block;
        width: 38px;
        height: 38px;
        line-height: 38px;
        text-align: center;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .ball:hover {
        transform: scale(1.1);
    }
    .run-ball { background: #475569; color: white; }
    .four-ball { background: #10B981; color: white; }
    .six-ball { background: #10B981; color: white; }
    .wicket-ball { background: #EF4444; color: white; }
    .extra-ball { background: #F59E0B; color: white; }
    
    /* Status indicators */
    .live-indicator {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #EF4444;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        animation: pulse 1.5s infinite;
    }
    .finished-indicator {
        position: absolute;
        top: 10px;
        right: 15px;
        background: #6B7280;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Team header */
    .team-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .team-logo-container {
        text-align: center;
        flex: 1;
    }
    .team-logo {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: 2px solid #3B82F6;
        object-fit: cover;
    }
    .team-name-small {
        font-size: 10px;
        margin-top: 3px;
        color: #93C5FD;
    }
    .score-center {
        text-align: center;
        flex: 2;
    }
    
    /* Commentary box */
    .commentary-box {
        background: #0F172A;
        border-radius: 12px;
        padding: 12px;
        max-height: 250px;
        overflow-y: auto;
    }
    .commentary-item {
        padding: 6px;
        margin: 4px 0;
        border-left: 3px solid #3B82F6;
        background: #1E293B;
        border-radius: 6px;
        font-size: 12px;
    }
    
    /* Team cards */
    .team-card {
        background: #1E293B;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin: 8px;
        transition: transform 0.3s;
    }
    .team-card:hover {
        transform: translateY(-5px);
    }
    .team-logo-card {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 10px;
        border: 2px solid #3B82F6;
    }
    
    /* Schedule card */
    .schedule-card {
        background: #1E293B;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #3B82F6;
    }
    
    /* Player card */
    .player-card {
        background: #1E293B;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
    }
    .player-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 12px;
    }
    .stat-box {
        background: #0F172A;
        padding: 8px;
        border-radius: 8px;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 800;
        color: #3B82F6;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .team-logo {
            width: 40px;
            height: 40px;
        }
        .score-big {
            font-size: 1.8rem;
        }
        .ball {
            width: 32px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
        }
        .team-name-small {
            font-size: 8px;
        }
    }
    </style>
""", unsafe_allow_html=True)

def update_player_stats(player_name, runs=0, balls=0, fours=0, sixes=0, wicket=False, overs=0, runs_conceded=0):
    """Update player statistics - only increment when actually played"""
    if not player_name:
        return
    
    stats = st.session_state.player_stats[player_name]
    
    # Only increment matches if this is a new match entry for this player
    # This is handled by checking if we're adding stats for a new match
    
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

def add_commentary(description, runs=0, is_wicket=False, is_four=False, is_six=False, bowler="", batsman=""):
    comment = {
        "description": description,
        "runs": runs,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.commentary_store.insert(0, comment)
    while len(st.session_state.commentary_store) > 30:
        st.session_state.commentary_store.pop()
    
    if is_wicket:
        st.toast(f"⚡ WICKET! {batsman} is out!", icon="🎯")
    elif is_six:
        st.toast(f"💥 SIX! {batsman} hits a maximum!", icon="🏏")
    elif is_four:
        st.toast(f"🎯 FOUR! {batsman} finds the boundary!", icon="⭐")

def get_top_batsmen(limit=10):
    batsmen = []
    for name, stats in st.session_state.player_stats.items():
        if stats["runs"] > 0:
            avg = stats["runs"] / stats["matches"] if stats["matches"] > 0 else 0
            sr = (stats["runs"] * 100 / stats["balls"]) if stats["balls"] > 0 else 0
            batsmen.append({
                "Player": name[:20],
                "M": stats["matches"],
                "Runs": stats["runs"],
                "Balls": stats["balls"],
                "4s": stats["fours"],
                "6s": stats["sixes"],
                "SR": f"{sr:.1f}",
                "Avg": f"{avg:.1f}"
            })
    return sorted(batsmen, key=lambda x: x["Runs"], reverse=True)[:limit]

def get_top_bowlers(limit=10):
    bowlers = []
    for name, stats in st.session_state.player_stats.items():
        if stats["wickets"] > 0:
            econ = stats["runs_conceded"] / stats["overs"] if stats["overs"] > 0 else 0
            bowlers.append({
                "Player": name[:20],
                "M": stats["matches"],
                "Wkts": stats["wickets"],
                "Overs": f"{stats['overs']:.1f}",
                "Runs": stats["runs_conceded"],
                "Econ": f"{econ:.2f}"
            })
    return sorted(bowlers, key=lambda x: x["Wkts"], reverse=True)[:limit]

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
    
    runs_i1, wickets_i1 = d1["runs"], d1["wickets"]
    runs_i2, wickets_i2 = d2["runs"], d2["wickets"]
    total_balls = m["total_overs"] * 6
    
    if m["current_innings"] == 1:
        if d1["balls"] >= total_balls or wickets_i1 >= 10:
            return f"Innings 1: {runs_i1}/{wickets_i1}"
        return f"{m['team_1']} batting - {runs_i1}/{wickets_i1}"
    
    target = runs_i1 + 1
    if runs_i2 >= target:
        return f"🏆 {m['team_2']} won by {10 - wickets_i2} wickets"
    if d2["balls"] >= total_balls or wickets_i2 >= 10:
        if runs_i2 < runs_i1:
            return f"🏆 {m['team_1']} won by {runs_i1 - runs_i2} runs"
        elif runs_i2 == runs_i1:
            return "Match Tied"
    runs_needed = target - runs_i2
    balls_left = total_balls - d2["balls"]
    return f"{m['team_2']} needs {runs_needed} runs from {balls_left} balls"

def generate_pdf(m):
    try:
        m = ensure_match(m)
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_fill_color(59, 130, 246)
        pdf.rect(0, 0, 210, 8, 'F')
        
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "MATCH SCORECARD", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"{m['team_1']} vs {m['team_2']} ({m['total_overs']} Overs)", ln=True, align="C")
        pdf.cell(0, 6, f"Match ID: {m['id']}", ln=True, align="C")
        pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        
        result = get_match_result(m)
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(220, 240, 220)
        pdf.rect(10, 70, 190, 8, 'F')
        pdf.set_xy(15, 73)
        pdf.cell(0, 5, result, ln=True)
        
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue()
    except:
        return b""

@st.cache_resource
def get_db():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db = get_db()

# Sidebar
with st.sidebar:
    st.markdown("### 🏏 APL 2026")
    st.markdown("---")
    
    commentary_enabled = st.toggle("📝 Commentary", value=True)
    
    st.markdown("---")
    
    role = st.radio("Access:", ["👤 Player View", "⚡ Scorer Panel"])
    
    is_admin = False
    if role == "⚡ Scorer Panel":
        pwd = st.text_input("Password:", type="password")
        if pwd == "anscor2026":
            is_admin = True
            st.success("✅ Admin Access")
        elif pwd:
            st.error("Wrong Password")
    
    # Show scheduled matches count in sidebar
    if st.session_state.scheduled_matches:
        st.markdown("---")
        st.markdown(f"📅 {len(st.session_state.scheduled_matches)} Matches Scheduled")

# Tabs
tab_live, tab_analytics, tab_players, tab_rankings, tab_schedule, tab_teams = st.tabs([
    "🏏 Live", "📊 Analytics", "👤 Players", "🏆 Rankings", "📅 Schedule", "👥 Teams"
])

# Teams Tab
with tab_teams:
    st.markdown("### 🏏 Tournament Teams")
    cols = st.columns(3)
    for idx, (team_name, team_data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            logo = team_data["remote"]
            st.image(logo, width=100)
            st.markdown(f"**{team_name}**")
            if st.button(f"View Squad", key=f"squad_{idx}"):
                with st.expander(f"{team_name} Squad", expanded=True):
                    for player in team_data["squad"]:
                        st.markdown(f"• {player}")

# Schedule Tab - Fixed visibility for all users
with tab_schedule:
    st.markdown("### 📅 Match Schedule")
    
    # Admin can schedule matches
    if is_admin:
        with st.expander("➕ Schedule New Match", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                match_id = st.text_input("Match ID:", "Match_001")
                team1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="sch_t1")
                date = st.date_input("Date:", datetime.now())
            with col2:
                venue = st.text_input("Venue:", "Main Stadium")
                team2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="sch_t2")
                time = st.time_input("Time:", datetime.now().time())
            
            if st.button("📅 Schedule Match", use_container_width=True):
                st.session_state.scheduled_matches.append({
                    "id": match_id,
                    "team1": team1,
                    "team2": team2,
                    "date": date.strftime("%Y-%m-%d"),
                    "time": time.strftime("%H:%M"),
                    "venue": venue,
                    "status": "upcoming"
                })
                st.success(f"Match {match_id} scheduled!")
                st.rerun()
    
    # Display scheduled matches - visible to all users
    if st.session_state.scheduled_matches:
        st.markdown("#### Upcoming Matches")
        for match in st.session_state.scheduled_matches:
            st.markdown(f"""
                <div class="schedule-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>🏆 {match['id']}</strong><br>
                            {match['team1']} vs {match['team2']}<br>
                            📍 {match['venue']}
                        </div>
                        <div style="text-align: right;">
                            📅 {match['date']}<br>
                            🕐 {match['time']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No matches scheduled yet.")

# Rankings Tab - Fixed with correct calculations
with tab_rankings:
    st.markdown("### 🏆 Player Rankings")
    
    tab_bats, tab_bowl = st.tabs(["🏏 Top Batsmen", "🎯 Top Bowlers"])
    
    with tab_bats:
        top_batsmen = get_top_batsmen()
        if top_batsmen:
            df = pd.DataFrame(top_batsmen)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No batting statistics available. Play matches to see rankings!")
    
    with tab_bowl:
        top_bowlers = get_top_bowlers()
        if top_bowlers:
            df = pd.DataFrame(top_bowlers)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No bowling statistics available. Play matches to see rankings!")

# Players Tab
with tab_players:
    st.markdown("### 👤 Player Profiles")
    
    all_players = []
    for team in TEAM_DB.values():
        all_players.extend(team["squad"])
    
    search = st.selectbox("Search Player:", sorted(all_players))
    
    if search:
        stats = st.session_state.player_stats.get(search, {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="player-card">
                    <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #3B82F6, #2563EB); border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 1.5rem; color: white;">{search[0]}</span>
                    </div>
                    <h4>{search}</h4>
                    <div class="player-stats">
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('matches', 0)}</div>
                            <div>Matches</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('runs', 0)}</div>
                            <div>Runs</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('balls', 0)}</div>
                            <div>Balls</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('wickets', 0)}</div>
                            <div>Wickets</div>
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
                            <div>4s</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('sixes', 0)}</div>
                            <div>6s</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('fifties', 0)}</div>
                            <div>50s</div>
                        </div>
                    </div>
                    <h4>Bowling Stats</h4>
                    <div class="player-stats">
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('overs', 0):.1f}</div>
                            <div>Overs</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">{stats.get('runs_conceded', 0)}</div>
                            <div>Runs</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Analytics Tab
with tab_analytics:
    st.markdown("### 📊 Match Analytics")
    
    if db["matches"]:
        match_id = st.selectbox("Select Match:", list(db["matches"].keys()))
        m = ensure_match(db["matches"][match_id])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Runs", m["innings_1"]["runs"] + m["innings_2"]["runs"])
        with col2:
            st.metric("Total Wickets", m["innings_1"]["wickets"] + m["innings_2"]["wickets"])
        with col3:
            total_fours = m["innings_1"]["b1"]["fours"] + m["innings_1"]["b2"]["fours"]
            st.metric("Total Fours", total_fours)
        with col4:
            total_sixes = m["innings_1"]["b1"]["sixes"] + m["innings_1"]["b2"]["sixes"]
            st.metric("Total Sixes", total_sixes)
        
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
        st.info("No matches played yet")

# Live Match Tab
with tab_live:
    if is_admin:
        with st.expander("⚙️ New Match", expanded=not db["active_match_id"]):
            col1, col2, col3 = st.columns(3)
            with col1:
                match_id = st.text_input("Match ID:", "Match_001")
            with col2:
                team1 = st.selectbox("Team 1:", list(TEAM_DB.keys()), key="t1")
            with col3:
                team2 = st.selectbox("Team 2:", list(TEAM_DB.keys()), key="t2")
            
            col4, col5 = st.columns(2)
            with col4:
                overs = st.number_input("Overs:", 1, 10, 4)
            with col5:
                if st.button("🚀 Create Match", use_container_width=True):
                    if match_id and team1 != team2:
                        with db["lock"]:
                            db["matches"][match_id] = {
                                "id": match_id, "team_1": team1, "team_2": team2,
                                "total_overs": overs, "current_innings": 1,
                                "innings_1": init_innings(), "innings_2": init_innings()
                            }
                            db["active_match_id"] = match_id
                        st.rerun()
        
        if db["matches"]:
            current = db["active_match_id"] if db["active_match_id"] else list(db["matches"].keys())[0]
            selected = st.selectbox("Active Match:", list(db["matches"].keys()), 
                                   index=list(db["matches"].keys()).index(current))
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
                            st.rerun()
    
    if not db["active_match_id"] or db["active_match_id"] not in db["matches"]:
        st.info("No active match. Create one above.")
    else:
        match = ensure_match(db["matches"][db["active_match_id"]])
        inn = match["innings_1"] if match["current_innings"] == 1 else match["innings_2"]
        batting = match["team_1"] if match["current_innings"] == 1 else match["team_2"]
        bowling = match["team_2"] if match["current_innings"] == 1 else match["team_1"]
        target = match["innings_1"]["runs"] + 1 if match["current_innings"] == 2 else None
        
        if inn["b1"]["name"] == "" and is_admin:
            with st.form("setup"):
                st.warning(f"📝 Setup {batting} Batting")
                col1, col2, col3 = st.columns(3)
                with col1:
                    striker = st.selectbox("Striker:", TEAM_DB[batting]["squad"])
                with col2:
                    non_striker = st.selectbox("Non-Striker:", TEAM_DB[batting]["squad"])
                with col3:
                    bowler = st.selectbox("Bowler:", TEAM_DB[bowling]["squad"])
                if st.form_submit_button("🚀 Start Match"):
                    with db["lock"]:
                        inn["b1"]["name"] = striker
                        inn["b2"]["name"] = non_striker
                        inn["bowler"]["name"] = bowler
                    st.rerun()
        
        elif inn["b1"]["name"]:
            overs_done = inn["balls"] // 6
            balls_in_over = inn["balls"] % 6
            crr = inn["runs"] / (inn["balls"]/6) if inn["balls"] > 0 else 0
            
            total_balls_allowed = match["total_overs"] * 6
            if match["current_innings"] == 1:
                innings_complete = (inn["balls"] >= total_balls_allowed or inn["wickets"] >= 10)
            else:
                innings_complete = (inn["balls"] >= total_balls_allowed or inn["wickets"] >= 10 or (target and inn["runs"] >= target))
            
            status = '<span class="finished-indicator">FINISHED</span>' if innings_complete else '<span class="live-indicator">LIVE</span>'
            
            # Score Display
            st.markdown(f"""
                <div class="compact-score">
                    {status}
                    <div class="team-header">
                        <div class="team-logo-container">
                            <img src="{TEAM_DB[batting]['remote']}" class="team-logo">
                            <div class="team-name-small">{batting[:12]}</div>
                        </div>
                        <div class="score-center">
                            <div class="score-big">{inn['runs']}-{inn['wickets']}</div>
                            <div style="font-size: 12px;">{overs_done}.{balls_in_over}/{match['total_overs']} | CRR: {crr:.2f}</div>
                        </div>
                        <div class="team-logo-container">
                            <img src="{TEAM_DB[bowling]['remote']}" class="team-logo">
                            <div class="team-name-small">{bowling[:12]}</div>
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
                    st.info(f"🎯 Target: {target} | Need {runs_needed} runs from {balls_left} balls | RR: {req_rate:.2f}")
            
            if is_admin:
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.markdown(f"""
                        <div class="info-row">
                            <b>🏏 BATTING</b><br>
                            <div style="display: flex; justify-content: space-between;">
                                <span>{'👉 ' if inn['b1']['strike'] else ''}{inn['b1']['name'][:15]}</span>
                                <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                                <span>{'👉 ' if inn['b2']['strike'] else ''}{inn['b2']['name'][:15]}</span>
                                <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}</span>
                            </div>
                        </div>
                        <div class="info-row">
                            <b>🥎 BOWLER</b><br>
                            <div style="display: flex; justify-content: space-between;">
                                <span>{inn['bowler']['name'][:15]}</span>
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
                        st.caption("No deliveries")
                    
                    if inn["over_history"]:
                        st.markdown("**📊 RECENT OVERS**")
                        for over in inn["over_history"][-3:]:
                            st.caption(f"Over {over['Over']}: {over['Bowler'][:10]} - {over['Timeline']}")
                    
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
                                                  fours=1 if runs == 4 else 0, sixes=1 if runs == 6 else 0)
                            
                            if wicket:
                                inn["wickets"] += 1
                                inn["bowler"]["wickets"] += 1
                                if inn["bowler"]["name"]:
                                    update_player_stats(inn["bowler"]["name"], wicket=True, overs=0.166 if legal else 0, runs_conceded=runs)
                            
                            if legal:
                                inn["balls"] += 1
                                inn["bowler"]["balls"] += 1
                                if not wicket and striker["name"]:
                                    striker["balls"] += 1
                                    striker["runs"] += (runs - extra)
                                inn["this_over"].append(symbol if symbol else runs)
                                
                                if commentary_enabled:
                                    if wicket:
                                        add_commentary(f"OUT! {striker['name']} ({striker['runs']}) b {inn['bowler']['name']}", 
                                                      runs, is_wicket=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    elif runs == 6:
                                        add_commentary(f"SIX! {striker['name']} launches it over the boundary!", 
                                                      runs, is_six=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    elif runs == 4:
                                        add_commentary(f"FOUR! {striker['name']} finds the gap beautifully!", 
                                                      runs, is_four=True, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    elif runs > 0:
                                        add_commentary(f"{runs} run{'s' if runs>1 else ''} - {striker['name']} rotates the strike", 
                                                      runs, bowler=inn['bowler']['name'], batsman=striker['name'])
                                    else:
                                        add_commentary(f"Dot ball! {striker['name']} defends it well", 
                                                      runs, bowler=inn['bowler']['name'], batsman=striker['name'])
                            else:
                                inn["this_over"].append(symbol)
                                if commentary_enabled:
                                    add_commentary(f"{symbol} - Extra run conceded by {inn['bowler']['name']}", 
                                                  runs, bowler=inn['bowler']['name'], batsman=striker['name'])
                            
                            if legal and (runs % 2 == 1) and not wicket:
                                inn["b1"]["strike"] = not inn["b1"]["strike"]
                                inn["b2"]["strike"] = not inn["b2"]["strike"]
                            
                            legal_balls = [b for b in inn["this_over"] if b not in ['WD', 'NB']]
                            if len(legal_balls) == 6:
                                inn["awaiting_bowler"] = True
                            if wicket and inn["wickets"] < 10:
                                inn["awaiting_batsman"] = True
                    
                    if inn["awaiting_batsman"]:
                        st.warning("⚠️ New Batsman")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen"]]
                        available = [p for p in TEAM_DB[batting]["squad"] if p not in used]
                        if not available:
                            available = TEAM_DB[batting]["squad"]
                        new_bat = st.selectbox("Select:", available)
                        if st.button("✅ Confirm", use_container_width=True):
                            with db["lock"]:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True}
                                else:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False}
                                inn["awaiting_batsman"] = False
                                if commentary_enabled:
                                    add_commentary(f"👤 New batsman: {new_bat} comes to the crease", 0)
                            st.rerun()
                    
                    elif inn["awaiting_bowler"]:
                        st.success("🔄 Over Complete!")
                        new_bowl = st.selectbox("Select Bowler:", TEAM_DB[bowling]["squad"])
                        if st.button("✅ Next Over", use_container_width=True):
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
                                if commentary_enabled:
                                    add_commentary(f"🔄 New over! {new_bowl} will bowl now", 0)
                            st.rerun()
                    
                    elif not innings_complete:
                        if target and inn["runs"] >= target:
                            st.success("🏆 Target Achieved!")
                        else:
                            st.markdown("**RUNS**")
                            r1, r2, r3, r4 = st.columns(4)
                            with r1:
                                if st.button("0", use_container_width=True):
                                    add_ball(0)
                                    st.rerun()
                                if st.button("1", use_container_width=True):
                                    add_ball(1)
                                    st.rerun()
                            with r2:
                                if st.button("2", use_container_width=True):
                                    add_ball(2)
                                    st.rerun()
                                if st.button("3", use_container_width=True):
                                    add_ball(3)
                                    st.rerun()
                            with r3:
                                if st.button("4", use_container_width=True):
                                    add_ball(4)
                                    if inn["b1"]["strike"]:
                                        inn["b1"]["fours"] += 1
                                    else:
                                        inn["b2"]["fours"] += 1
                                    st.rerun()
                                if st.button("6", use_container_width=True):
                                    add_ball(6)
                                    if inn["b1"]["strike"]:
                                        inn["b1"]["sixes"] += 1
                                    else:
                                        inn["b2"]["sixes"] += 1
                                    st.rerun()
                            with r4:
                                if st.button("WD", use_container_width=True):
                                    add_ball(1, 1, False, symbol="WD")
                                    st.rerun()
                                if st.button("NB", use_container_width=True):
                                    add_ball(1, 1, False, symbol="NB")
                                    st.rerun()
                            
                            st.markdown("---")
                            a1, a2, a3 = st.columns(3)
                            with a1:
                                if st.button("OUT", type="primary", use_container_width=True):
                                    add_ball(0, 0, True, True, "W")
                                    st.rerun()
                            with a2:
                                if inn["undo_stack"]:
                                    if st.button("UNDO", use_container_width=True):
                                        with db["lock"]:
                                            prev = inn["undo_stack"].pop()
                                            for k in ["runs", "wickets", "balls", "extras", "this_over", "b1", "b2", "bowler"]:
                                                inn[k] = prev[k]
                                        st.rerun()
                            with a3:
                                if st.button("SWAP", use_container_width=True):
                                    with db["lock"]:
                                        inn["b1"]["strike"] = not inn["b1"]["strike"]
                                        inn["b2"]["strike"] = not inn["b2"]["strike"]
                                    st.rerun()
                    else:
                        st.success("🏁 Innings Complete!")
                        if match["current_innings"] == 1:
                            if st.button("➡️ Start Innings 2", use_container_width=True, type="primary"):
                                with db["lock"]:
                                    match["current_innings"] = 2
                                    if commentary_enabled:
                                        add_commentary(f"🏏 Second innings begins! {match['team_2']} needs {match['innings_1']['runs'] + 1} to win", 0)
                                st.rerun()
                    
                    with st.expander("⚙️ Admin", expanded=False):
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
                                else:
                                    inn["penalty"] = inn.get("penalty", 0) + extra_runs
                                    inn["this_over"].append(f"+{extra_runs}Pen")
                            st.rerun()
                    
                    st.markdown("---")
                    if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                        pdf_data = generate_pdf(match)
                        if pdf_data:
                            st.download_button("📥 Download PDF", pdf_data, f"match_{match['id']}.pdf", use_container_width=True)
            
            else:
                # Player View
                st.markdown(f"""
                    <div class="info-row">
                        <b>🏏 BATTING</b><br>
                        {inn['b1']['name'][:18]}: {inn['b1']['runs']}({inn['b1']['balls']}) {'*' if inn['b1']['strike'] else ''}<br>
                        {inn['b2']['name'][:18]}: {inn['b2']['runs']}({inn['b2']['balls']}) {'*' if inn['b2']['strike'] else ''}
                    </div>
                    <div class="info-row">
                        <b>🥎 BOWLER</b><br>
                        {inn['bowler']['name'][:18]}: {inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6})
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
                    st.caption("No deliveries")
                
                if inn["over_history"]:
                    st.markdown("**📊 RECENT OVERS**")
                    for over in inn["over_history"][-5:]:
                        st.caption(f"Over {over['Over']}: {over['Bowler']} - {over['Timeline']}")
                
                if inn["all_batsmen"]:
                    st.markdown("**📋 FALLEN WICKETS**")
                    for w in inn["all_batsmen"][-5:]:
                        st.caption(f"• {w['name']} - {w['runs']}({w['balls']})")
                
                st.info(get_match_result(match))
                
                if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                    pdf_data = generate_pdf(match)
                    if pdf_data:
                        st.download_button("📥 Download PDF", pdf_data, f"match_{match['id']}.pdf", use_container_width=True)
            
            # Commentary Section
            if commentary_enabled and st.session_state.commentary_store:
                st.markdown("---")
                st.markdown("### 📝 Live Commentary")
                st.markdown('<div class="commentary-box">', unsafe_allow_html=True)
                for comment in st.session_state.commentary_store[:10]:
                    st.markdown(f"""
                        <div class="commentary-item">
                            <small>{comment['time']}</small><br>
                            {comment['description']}
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
