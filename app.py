import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64
from datetime import datetime
import io
from PIL import Image

# Page Configuration
st.set_page_config(page_title="APL 2026", page_icon="🏏", layout="wide", initial_sidebar_state="collapsed")

# GitHub repo path
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"
TOURNAMENT_LOGO_FILE = "image_4d6904.png"

# Team Database with enhanced logo handling
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
    """Get image as base64 string for HTML display"""
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return ""

def get_team_logo_base64(team_name):
    """Get team logo as base64 string"""
    team_data = TEAM_DB.get(team_name, {})
    local_path = team_data.get("local", "")
    remote_url = team_data.get("remote", "")
    
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return ""

# Enhanced CSS for Teams section
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
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
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
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        width: 100% !important;
        border: none !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(16,185,129,0.5) !important;
    }
    
    /* Teams Section Enhanced Styles */
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
        transform: translateY(-5px);
        border-color: #3B82F6;
        box-shadow: 0 10px 25px -5px rgba(59,130,246,0.3);
    }
    .team-logo-large {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 4px solid #3B82F6;
        object-fit: cover;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .team-name-large {
        font-size: 1.2rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 10px;
    }
    .team-short-name {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-bottom: 15px;
    }
    .squad-container {
        background: #1E293B;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        border: 1px solid #334155;
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
    """Remove emojis and special characters from text"""
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
    text = ''.join(char if ord(char) < 128 else ' ' for char in text)
    return text.strip()

def generate_match_pdf(m):
    """Generate a simple PDF scorecard without emojis"""
    try:
        m = ensure_match(m)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Tournament Title
        pdf.set_font("Arial", "B", 20)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 15, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "MATCH SCORECARD", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        
        # Match Details
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, f"{clean_text(m['team_1'])} vs {clean_text(m['team_2'])} ({m['total_overs']} Overs)", ln=True, align="C")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 6, f"Match ID: {clean_text(m['id'])}", ln=True, align="C")
        pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        
        # Result
        result = get_match_status(m)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(200, 230, 200)
        pdf.rect(10, 70, 190, 10, 'F')
        pdf.set_xy(15, 73)
        pdf.cell(0, 6, clean_text(result), ln=True)
        
        # Innings 1
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
            # Current batsmen
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
            
            # Dismissed batsmen
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
            
            y = pdf.get_y() + 5
            
            # Bowling Table
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 7, 'F')
            pdf.set_xy(15, y + 1.5)
            pdf.cell(0, 4, "BOWLING", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 10
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(55, 7, "BOWLER", 1, 0, "C", 1)
            pdf.cell(25, 7, "OVERS", 1, 0, "C", 1)
            pdf.cell(25, 7, "RUNS", 1, 0, "C", 1)
            pdf.cell(25, 7, "WKTS", 1, 0, "C", 1)
            pdf.cell(30, 7, "ECON", 1, 0, "C", 1)
            pdf.cell(30, 7, "MAIDENS", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d1["bowler"]["name"]:
                overs = d1["bowler"]["balls"] / 6
                econ = d1["bowler"]["runs"] / overs if overs > 0 else 0
                pdf.cell(55, 6, clean_text(d1["bowler"]["name"][:22]), 1)
                pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["runs"]), 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["wickets"]), 1, 0, "C")
                pdf.cell(30, 6, f"{econ:.2f}", 1, 0, "C")
                pdf.cell(30, 6, "0", 1, 1, "C")
            
            for b in d1.get("all_bowlers", []):
                if b.get("name"):
                    overs = b.get("balls", 0) / 6
                    econ = b.get("runs", 0) / overs if overs > 0 else 0
                    pdf.cell(55, 6, clean_text(b["name"][:22]), 1)
                    pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("wickets", 0)), 1, 0, "C")
                    pdf.cell(30, 6, f"{econ:.2f}", 1, 0, "C")
                    pdf.cell(30, 6, "0", 1, 1, "C")
        
        # Innings 2
        d2 = m["innings_2"]
        if d2["b1"]["name"]:
            pdf.add_page()
            y = 20
            
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 8, 'F')
            pdf.set_xy(15, y + 2)
            pdf.cell(0, 5, f"INNINGS 2: {clean_text(m['team_2'])}", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 12
            
            target = d1["runs"] + 1
            overs2 = f"{d2['balls']//6}.{d2['balls']%6}"
            rr = d2['runs']/(d2['balls']/6) if d2['balls'] > 0 else 0
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 7, f"Target: {target} | Score: {d2['runs']}/{d2['wickets']} in {overs2} overs (RR: {rr:.2f})", ln=True)
            y += 8
            
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
                sr = (d2["b1"]["runs"] * 100 / d2["b1"]["balls"]) if d2["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, clean_text(d2["b1"]["name"][:22]), 1)
                pdf.cell(20, 6, str(d2["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            if d2["b2"]["name"]:
                sr = (d2["b2"]["runs"] * 100 / d2["b2"]["balls"]) if d2["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, clean_text(d2["b2"]["name"][:22]), 1)
                pdf.cell(20, 6, str(d2["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            for b in d2.get("all_batsmen", []):
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
        
        # Output PDF as bytes
        output_buffer = io.BytesIO()
        pdf.output(output_buffer)
        return output_buffer.getvalue()
            
    except Exception as e:
        # Return a simple error PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Scorecard Summary", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Match: {clean_text(m['team_1'])} vs {clean_text(m['team_2'])}", ln=True, align="C")
            pdf.cell(0, 10, f"Score: {m['innings_1']['runs']}/{m['innings_1']['wickets']}", ln=True, align="C")
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

# Teams Tab - Enhanced Version
with tab_teams:
    st.markdown("### Tournament Teams")
    st.markdown("---")
    
    # Display teams in a grid with enhanced styling
    cols = st.columns(3)
    
    for idx, (team_name, team_data) in enumerate(TEAM_DB.items()):
        with cols[idx % 3]:
            # Get logo base64
            logo_base64 = get_team_logo_base64(team_name)
            
            # Create team card
            if logo_base64:
                st.markdown(f"""
                    <div class="team-card">
                        <img src="data:image/jpeg;base64,{logo_base64}" class="team-logo-large">
                        <div class="team-name-large">{team_name}</div>
                        <div class="team-short-name">{team_data.get('short_name', team_name[:3].upper())}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Fallback if logo not available
                st.markdown(f"""
                    <div class="team-card">
                        <div style="width: 120px; height: 120px; background: linear-gradient(135deg, #3B82F6, #2563EB); border-radius: 50%; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 2rem; color: white;">{team_name[0]}</span>
                        </div>
                        <div class="team-name-large">{team_name}</div>
                        <div class="team-short-name">{team_data.get('short_name', team_name[:3].upper())}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Squad button
            if st.button(f"View Squad", key=f"squad_btn_{idx}", use_container_width=True):
                with st.expander(f"{team_name} Squad ({len(team_data['squad'])} Players)", expanded=True):
                    st.markdown('<div class="squad-container">', unsafe_allow_html=True)
                    
                    # Display players in a grid
                    player_cols = st.columns(2)
                    for i, player in enumerate(team_data['squad']):
                        with player_cols[i % 2]:
                            st.markdown(f'<div class="squad-player">🏏 {player}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")

    # Add tournament statistics section
    st.markdown("### Tournament Statistics")
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
        st.metric("Overs per Match", "4-20")

# Rest of the code remains the same (Live Match and Review tabs)
# ... (keeping all the existing Live Match and Review code from previous version)

# Note: The Live Match and Review tabs code remains exactly the same as in the previous working version
# I'm showing only the Teams tab changes above for brevity
