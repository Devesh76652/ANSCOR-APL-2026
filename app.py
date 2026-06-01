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

# Page Configuration
st.set_page_config(page_title="APL 2026", page_icon="🏏", layout="wide", initial_sidebar_state="collapsed")

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
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(59,130,246,0.5);
    }
    div[data-testid="column"] button {
        padding: 10px 0;
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
    }
    .score-big {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
    }
    .info-row {
        background: #1E293B;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        font-size: 15px;
        border: 1px solid #334155;
    }
    .ball {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        margin: 4px;
        font-weight: bold;
        font-size: 14px;
    }
    .run-ball { background: #475569; color: white; }
    .four-ball { background: #10B981; color: white; }
    .six-ball { background: #10B981; color: white; }
    .wicket-ball { background: #EF4444; color: white; }
    .extra-ball { background: #F59E0B; color: white; }
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
    }
    .team-card:hover {
        transform: translateY(-5px);
        border-color: #3B82F6;
    }
    .team-logo-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid #3B82F6;
        object-fit: cover;
        margin-bottom: 15px;
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
    }
    </style>
""", unsafe_allow_html=True)

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

def generate_match_pdf(m):
    try:
        m = ensure_match(m)
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 20)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 15, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "MATCH SCORECARD", ln=True, align="C")
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
        
        d1 = m["innings_1"]
        if d1["b1"]["name"]:
            y = 95
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 8, 'F')
            pdf.set_xy(15, y + 2)
            pdf.cell(0, 5, f"INNINGS 1: {clean_text(m['team_1'])}", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 12
            
            overs1 = f"{d1['balls']//6}.{d1['balls']%6}"
            rr = d1['runs']/(d1['balls']/6) if d1['balls'] > 0 else 0
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 7, f"Score: {d1['runs']}/{d1['wickets']} in {overs1} overs (Run Rate: {rr:.2f})", ln=True)
            y += 8
            
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
            if d1["b1"]["name"]:
                sr = (d1["b1"]["runs"] * 100 / d1["b1"]["balls"]) if d1["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, clean_text(d1["b1"]["name"][:22]), 1)
                pdf.cell(20, 6, str(d1["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            if d1["b2"]["name"]:
                sr = (d1["b2"]["runs"] * 100 / d1["b2"]["balls"]) if d1["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, clean_text(d1["b2"]["name"][:22]), 1)
                pdf.cell(20, 6, str(d1["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            for b in d1.get("all_batsmen", []):
                if b.get("name"):
                    sr = (b.get("runs", 0) * 100 / b.get("balls", 1)) if b.get("balls", 0) > 0 else 0
                    pdf.cell(55, 6, clean_text(b["name"][:22]), 1)
                    pdf.cell(20, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(20, 6, str(b.get("balls", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                    status = b.get("status", "Out")
                    pdf.cell(50, 6, clean_text(status[:18]), 1, 1, "C")
        
        output_buffer = io.BytesIO()
        pdf.output(output_buffer)
        return output_buffer.getvalue()
    except Exception as e:
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Scorecard Summary", ln=True, align="C")
            output_buffer = io.BytesIO()
            pdf.output(output_buffer)
            return output_buffer.getvalue()
        except:
            return b""

@st.cache_resource
def get_db():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db = get_db()

# Sidebar
with st.sidebar:
    st.markdown("### Portal")
    role = st.radio("Access:", ["Player View", "Scorer Panel"])
    
    is_admin = False
    if role == "Scorer Panel":
        pwd = st.text_input("Password:", type="password")
        if pwd == "anscor2026":
            is_admin = True
            st.success("Admin Access")
        elif pwd:
            st.error("Wrong password")
    
    if not is_admin:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=3000, key="refresh")
        except:
            pass

# Tabs
tab_live, tab_review, tab_teams = st.tabs(["Live", "Review", "Teams"])

# Teams Tab
with tab_teams:
    st.markdown("### Tournament Teams")
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

# Live Match Tab
with tab_live:
    if is_admin:
        with st.expander("New Match", expanded=not db["active_match_id"]):
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
                if st.button("Create Match", use_container_width=True):
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
            selected = st.selectbox("Active:", list(db["matches"].keys()), index=list(db["matches"].keys()).index(current))
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Set Active", use_container_width=True):
                    db["active_match_id"] = selected
                    st.rerun()
            with col_b:
                if db["active_match_id"] and db["active_match_id"] in db["matches"]:
                    m = ensure_match(db["matches"][db["active_match_id"]])
                    if m["current_innings"] == 1 and m["innings_1"]["b1"]["name"]:
                        if st.button("Innings 2", use_container_width=True):
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
                st.warning(f"Setup {batting} Batting")
                col1, col2, col3 = st.columns(3)
                with col1:
                    striker = st.selectbox("Striker:", TEAM_DB[batting]["squad"])
                with col2:
                    non_striker = st.selectbox("Non-Striker:", TEAM_DB[batting]["squad"])
                with col3:
                    bowler = st.selectbox("Bowler:", TEAM_DB[bowling]["squad"])
                if st.form_submit_button("Start Match", use_container_width=True):
                    with db["lock"]:
                        inn["b1"]["name"] = striker
                        inn["b2"]["name"] = non_striker
                        inn["bowler"]["name"] = bowler
                    st.rerun()
        
        elif inn["b1"]["name"]:
            overs_done = inn["balls"] // 6
            balls_in_over = inn["balls"] % 6
            crr = inn["runs"] / (inn["balls"]/6) if inn["balls"] > 0 else 0
            
            b_logo = get_image_base64(TEAM_DB[batting]["local"], TEAM_DB[batting]["remote"])
            bowl_logo = get_image_base64(TEAM_DB[bowling]["local"], TEAM_DB[bowling]["remote"])
            
            st.markdown(f"""
                <div class="compact-score">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="text-align: center; min-width: 100px;">
                            <img src="data:image/jpeg;base64,{b_logo}" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="font-size: 11px; font-weight: bold;">{batting[:12]}</div>
                        </div>
                        <div>
                            <div class="score-big">{inn['runs']}-{inn['wickets']}</div>
                            <div style="font-size: 13px;">{overs_done}.{balls_in_over}/{match['total_overs']} | CRR: {crr:.2f}</div>
                        </div>
                        <div style="text-align: center; min-width: 100px;">
                            <img src="data:image/jpeg;base64,{bowl_logo}" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="font-size: 11px; font-weight: bold;">{bowling[:12]}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if target:
                runs_needed = target - inn['runs']
                balls_left = (match['total_overs'] * 6) - inn['balls']
                req_rate = runs_needed / (balls_left/6) if balls_left > 0 else 0
                if inn['runs'] >= target:
                    st.success(f"Target Achieved! {batting} wins!")
                else:
                    st.info(f"Target: {target} | Need {runs_needed} off {balls_left} | RR: {req_rate:.2f}")
            
            if is_admin:
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.markdown(f"""
                        <div class="info-row">
                            <b>BATTING</b><br>
                            {inn['b1']['name'][:18]}: {inn['b1']['runs']}({inn['b1']['balls']}) {"*" if inn['b1']['strike'] else ""} | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}<br>
                            {inn['b2']['name'][:18]}: {inn['b2']['runs']}({inn['b2']['balls']}) {"*" if inn['b2']['strike'] else ""} | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}
                        </div>
                        <div class="info-row">
                            <b>BOWLER</b><br>
                            {inn['bowler']['name'][:18]}: {inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6}) | Econ: {inn['bowler']['runs']/(inn['bowler']['balls']/6) if inn['bowler']['balls']>0 else 0:.2f}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**CURRENT OVER**")
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
                        st.markdown("**RECENT OVERS**")
                        for over in inn["over_history"][-3:]:
                            st.caption(f"Over {over['Over']}: {over['Bowler'][:12]} - {over['Timeline']}")
                    
                    st.info(get_match_status(match))
                
                with col_right:
                    st.markdown("### SCORING")
                    
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
                            
                            if wicket:
                                inn["wickets"] += 1
                                inn["bowler"]["wickets"] += 1
                            
                            if legal:
                                inn["balls"] += 1
                                inn["bowler"]["balls"] += 1
                                striker["balls"] += 1
                                striker["runs"] += (runs - extra)
                                inn["this_over"].append(symbol if symbol else runs)
                            else:
                                inn["this_over"].append(symbol)
                            
                            if legal and (runs % 2 == 1) and not wicket:
                                inn["b1"]["strike"] = not inn["b1"]["strike"]
                                inn["b2"]["strike"] = not inn["b2"]["strike"]
                            
                            legal_balls = [b for b in inn["this_over"] if b not in ['WD', 'NB']]
                            if len(legal_balls) == 6:
                                inn["awaiting_bowler"] = True
                            if wicket and inn["wickets"] < 10:
                                inn["awaiting_batsman"] = True
                    
                    if inn["awaiting_batsman"]:
                        st.warning("New Batsman")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen"]]
                        available = [p for p in TEAM_DB[batting]["squad"] if p not in used]
                        if not available:
                            available = TEAM_DB[batting]["squad"]
                        new_bat = st.selectbox("Select:", available)
                        if st.button("Confirm", use_container_width=True):
                            with db["lock"]:
                                if inn["b1"]["strike"]:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b1"]))
                                    inn["b1"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True}
                                else:
                                    inn["all_batsmen"].append(copy.deepcopy(inn["b2"]))
                                    inn["b2"] = {"name": new_bat, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False}
                                inn["awaiting_batsman"] = False
                            st.rerun()
                    
                    elif inn["awaiting_bowler"]:
                        st.success("Over Complete!")
                        new_bowl = st.selectbox("Select Bowler:", TEAM_DB[bowling]["squad"])
                        if st.button("Next Over", use_container_width=True):
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
                            st.rerun()
                    
                    elif overs_done < match["total_overs"] and inn["wickets"] < 10:
                        if target and inn["runs"] >= target:
                            st.success("Target Achieved!")
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
                        st.success("Innings Complete!")
                        if match["current_innings"] == 1:
                            if st.button("Start Innings 2", use_container_width=True, type="primary"):
                                with db["lock"]:
                                    match["current_innings"] = 2
                                st.rerun()
                    
                    with st.expander("Admin"):
                        col1, col2 = st.columns(2)
                        with col1:
                            extra_type = st.selectbox("Type", ["Extras", "Penalty"])
                        with col2:
                            extra_runs = st.number_input("Runs", 1, 20, 1)
                        if st.button("Add Runs", use_container_width=True):
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
                    st.markdown("### EXPORT")
                    if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                        pdf_data = generate_match_pdf(match)
                        if pdf_data and len(pdf_data) > 500:
                            st.download_button(
                                label="DOWNLOAD PDF",
                                data=pdf_data,
                                file_name=f"APL_{match['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("Generating PDF...")
            
            else:
                st.markdown(f"""
                    <div class="info-row">
                        <b>BATTING</b><br>
                        {inn['b1']['name']}: {inn['b1']['runs']}({inn['b1']['balls']}) {"*" if inn['b1']['strike'] else ""} | SR: {inn['b1']['runs']*100/inn['b1']['balls'] if inn['b1']['balls']>0 else 0:.1f}<br>
                        {inn['b2']['name']}: {inn['b2']['runs']}({inn['b2']['balls']}) {"*" if inn['b2']['strike'] else ""} | SR: {inn['b2']['runs']*100/inn['b2']['balls'] if inn['b2']['balls']>0 else 0:.1f}
                    </div>
                    <div class="info-row">
                        <b>BOWLER</b><br>
                        {inn['bowler']['name']}: {inn['bowler']['wickets']}/{inn['bowler']['runs']} ({inn['bowler']['balls']//6}.{inn['bowler']['balls']%6}) | Econ: {inn['bowler']['runs']/(inn['bowler']['balls']/6) if inn['bowler']['balls']>0 else 0:.2f}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**CURRENT OVER**")
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
                    st.markdown("**RECENT OVERS**")
                    for over in inn["over_history"][-5:]:
                        st.caption(f"Over {over['Over']}: {over['Bowler']} - {over['Timeline']}")
                
                if inn["all_batsmen"]:
                    st.markdown("**FALLEN WICKETS**")
                    for w in inn["all_batsmen"][-5:]:
                        st.caption(f"- {w['name']} - {w['runs']}({w['balls']})")
                
                st.info(get_match_status(match))
                
                if match["innings_1"]["balls"] > 0 or match["innings_2"]["balls"] > 0:
                    pdf_data = generate_match_pdf(match)
                    if pdf_data and len(pdf_data) > 500:
                        st.download_button(
                            label="DOWNLOAD PDF",
                            data=pdf_data,
                            file_name=f"APL_{match['id']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

# Review Tab
with tab_review:
    if db["matches"]:
        match_id = st.selectbox("Select Match:", list(db["matches"].keys()))
        m = ensure_match(db["matches"][match_id])
        
        st.markdown(f"## {m['team_1']} vs {m['team_2']}")
        
        col1, col2 = st.columns(2)
        with col1:
            d1 = m["innings_1"]
            st.metric(f"Innings 1: {m['team_1']}", f"{d1['runs']}/{d1['wickets']}")
            if d1["over_history"]:
                st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True)
        with col2:
            d2 = m["innings_2"]
            st.metric(f"Innings 2: {m['team_2']}", f"{d2['runs']}/{d2['wickets']}")
            if d2["over_history"]:
                st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True)
        
        st.success(get_match_status(m))
        
        if m["innings_1"]["balls"] > 0 or m["innings_2"]["balls"] > 0:
            pdf_data = generate_match_pdf(m)
            if pdf_data and len(pdf_data) > 500:
                st.markdown("---")
                st.download_button(
                    label="DOWNLOAD PDF",
                    data=pdf_data,
                    file_name=f"APL_{m['id']}_Complete.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.info("No matches played yet")
