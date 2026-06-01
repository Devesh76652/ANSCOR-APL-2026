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
st.set_page_config(page_title="APL 2026 - Cricket Scorer", page_icon="🏏", layout="wide", initial_sidebar_state="collapsed")

# GitHub repo path
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"
TOURNAMENT_LOGO_FILE = "image_4d6904.png"

# Team Database
TEAM_DB = {
    "Capital Chellengers": {
        "local": "CapitalChellengers.jpeg",
        "remote": GITHUB_RAW_BASE + "CapitalChellengers.jpeg",
        "squad": ["Umesh sutar", "Kisan Pawar", "Imran Khan", "Pooja Gaikwad", "Rohan Mhatre", "Saurabh Padad", "Vijayaraj Yadav", "Vaibhav Sonawane", "Azad kanojiya", "Shrushti Thali", "Gaurav Singh", "Siddhesh A"]
    },
    "Black panther": {
        "local": "Blackpanther.jpeg",
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": ["Vishal Rajput", "Hitesh Purohit", "Omprakash Ashok Kamble", "Daraksha Khan", "Rohan vaity", "Devesh Tatale", "Suvarna Gupta", "Sanjay Sakpal", "SUMIIT M MORASKAR", "PRADEEP SHRIVASTAV", "Ishwar", "Rakesh Mishra", "Akash nagade"]
    },
    "Super Kings": {
        "local": "SuperKings.jpeg",
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": ["Bhushan Jagtap", "Lav gupta", "Shama Idrisi", "Md Munna", "Nilesh Chavhan", "Manvendra", "Pooja Jaikumar Vishwakarma", "Karan ramlakhan gupta", "Virendra mohite", "JAY", "SONALI VERMA", "Sudhir pal"]
    },
    "Power Hitter": {
        "local": "PowerHitter.jpeg",
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": ["Surendran Shankar", "SAURABH KURHADE", "Akhilesh Yadav", "Vikas Yadav", "sumit thorat", "Nitesh Manoj Gupta", "Omkar chandrakant upalkar", "Sanvi Jadhav", "Prithviraj Singh", "Divyanshu Mishra", "Krishna", "pinki", "Snehal S", "Amit Dubey"]
    },
    "Royal Warriors XI": {
        "local": "RoyalWarriorsXI.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": ["Siddharth Yadav", "Aditi Shankar Giri", "Gulam Shaikh", "Altaf Khan", "Ranjeet Kumar", "Rakesh yadav", "Milind Devrukhkar", "Sahil yadav", "Aarti Gaud", "Sumit Kumar Yadav", "Rahul jadhav", "Priyanka Jaiswal"]
    },
    "UnStoppable": {
        "local": "UnStoppable.jpeg",
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": ["Rajjesh", "Suvidha", "Lukman khan", "Prashun singh", "Omkar Rajesh Pandya", "Ganesh Kekan", "Abhishek Rokade", "Vipin Dilip Benvanshi", "Laxmi", "Priti Singh", "Zaid khan", "Yash patole"]
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

def get_tournament_logo_base64():
    if os.path.exists(TOURNAMENT_LOGO_FILE):
        try:
            with open(TOURNAMENT_LOGO_FILE, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            pass
    return ""

# CSS for better UI
st.markdown("""
    <style>
    .main > div { padding: 0 1rem; }
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59,130,246,0.4);
    }
    .score-card {
        background: linear-gradient(135deg, #1E3A8A, #0F172A);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(59,130,246,0.5);
    }
    .score-number {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .info-card {
        background: #1E293B;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border: 1px solid #334155;
    }
    .ball {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        margin: 3px;
        font-weight: bold;
    }
    .run-ball { background: #475569; color: white; }
    .four-ball { background: #10B981; color: white; }
    .six-ball { background: #10B981; color: white; }
    .wicket-ball { background: #EF4444; color: white; }
    .extra-ball { background: #F59E0B; color: white; }
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
        return f"🏆 {m['team_2']} wins by {10 - d2['wickets']} wickets"
    if d2["balls"] >= total_balls or d2["wickets"] >= 10:
        if d2["runs"] < d1["runs"]:
            return f"🏆 {m['team_1']} wins by {d1['runs'] - d2['runs']} runs"
    return f"Need {target - d2['runs']} runs from {total_balls - d2['balls']} balls"

# Comprehensive PDF Generation
def generate_complete_pdf(m):
    try:
        m = ensure_match(m)
        pdf = FPDF()
        
        # Helper function to add logo
        def add_logo(pdf, x, y, logo_path, size=20):
            if logo_path and os.path.exists(logo_path):
                try:
                    pdf.image(logo_path, x, y, size, size)
                except:
                    pass
        
        # Page 1 - Match Summary & Innings 1
        pdf.add_page()
        
        # Header with tournament logo
        pdf.set_fill_color(59, 130, 246)
        pdf.rect(0, 0, 210, 10, 'F')
        
        # Tournament Title
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 20, "APL 2026", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(59, 130, 246)
        pdf.cell(0, 8, "OFFICIAL MATCH SCORECARD", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        
        # Match Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{m['team_1']} vs {m['team_2']}", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Match ID: {m['id']}  |  Overs: {m['total_overs']}  |  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        
        # Result
        result = get_match_status(m)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(220, 240, 220)
        pdf.rect(10, 75, 190, 10, 'F')
        pdf.set_xy(15, 78)
        pdf.cell(0, 6, result, ln=True)
        
        y = 95
        
        # Innings 1
        d1 = m["innings_1"]
        if d1["b1"]["name"]:
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 8, 'F')
            pdf.set_xy(15, y + 1.5)
            pdf.cell(0, 5, f"INNINGS 1: {m['team_1']} BATTING", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 12
            
            overs1 = f"{d1['balls']//6}.{d1['balls']%6}"
            run_rate = d1['runs']/(d1['balls']/6) if d1['balls'] > 0 else 0
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 7, f"Total: {d1['runs']}/{d1['wickets']} in {overs1} overs (Run Rate: {run_rate:.2f})", ln=True)
            y += 5
            
            # Batting Table
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(55, 8, "BATSMAN", 1, 0, "C", 1)
            pdf.cell(20, 8, "R", 1, 0, "C", 1)
            pdf.cell(20, 8, "B", 1, 0, "C", 1)
            pdf.cell(15, 8, "4s", 1, 0, "C", 1)
            pdf.cell(15, 8, "6s", 1, 0, "C", 1)
            pdf.cell(25, 8, "SR", 1, 0, "C", 1)
            pdf.cell(50, 8, "DISMISSAL", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            # Current batsmen
            if d1["b1"]["name"]:
                sr = d1["b1"]["runs"] * 100 / d1["b1"]["balls"] if d1["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, d1["b1"]["name"][:25], 1)
                pdf.cell(20, 6, str(d1["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b1"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            if d1["b2"]["name"]:
                sr = d1["b2"]["runs"] * 100 / d1["b2"]["balls"] if d1["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, d1["b2"]["name"][:25], 1)
                pdf.cell(20, 6, str(d1["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d1["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d1["b2"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            # Dismissed batsmen
            for b in d1.get("all_batsmen", []):
                if b.get("name"):
                    sr = b.get("runs", 0) * 100 / b.get("balls", 1) if b.get("balls", 0) > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(20, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(20, 6, str(b.get("balls", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                    pdf.cell(50, 6, b.get("status", "Out")[:20], 1, 1, "C")
            
            y = pdf.get_y() + 3
            
            # Bowling Table
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 7, 'F')
            pdf.set_xy(15, y + 1.5)
            pdf.cell(0, 4, "BOWLING FIGURES", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 10
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(60, 7, "BOWLER", 1, 0, "C", 1)
            pdf.cell(25, 7, "OVERS", 1, 0, "C", 1)
            pdf.cell(25, 7, "RUNS", 1, 0, "C", 1)
            pdf.cell(25, 7, "WICKETS", 1, 0, "C", 1)
            pdf.cell(25, 7, "ECON", 1, 0, "C", 1)
            pdf.cell(30, 7, "MAIDENS", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d1["bowler"]["name"]:
                overs = d1["bowler"]["balls"] / 6
                econ = d1["bowler"]["runs"] / overs if overs > 0 else 0
                pdf.cell(60, 6, d1["bowler"]["name"][:25], 1)
                pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["runs"]), 1, 0, "C")
                pdf.cell(25, 6, str(d1["bowler"]["wickets"]), 1, 0, "C")
                pdf.cell(25, 6, f"{econ:.2f}", 1, 0, "C")
                pdf.cell(30, 6, "0", 1, 1, "C")
            
            for b in d1.get("all_bowlers", []):
                if b.get("name"):
                    overs = b.get("balls", 0) / 6
                    econ = b.get("runs", 0) / overs if overs > 0 else 0
                    pdf.cell(60, 6, b["name"][:25], 1)
                    pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("wickets", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{econ:.2f}", 1, 0, "C")
                    pdf.cell(30, 6, "0", 1, 1, "C")
            
            y = pdf.get_y() + 3
            
            # Over by Over
            if d1["over_history"]:
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(59, 130, 246)
                pdf.set_text_color(255, 255, 255)
                pdf.rect(10, y, 190, 7, 'F')
                pdf.set_xy(15, y + 1.5)
                pdf.cell(0, 4, "OVER BY OVER SUMMARY", ln=True)
                pdf.set_text_color(0, 0, 0)
                y += 10
                
                pdf.set_font("Arial", "B", 8)
                pdf.cell(15, 6, "Over", 1, 0, "C", 1)
                pdf.cell(50, 6, "Bowler", 1, 0, "C", 1)
                pdf.cell(25, 6, "Score", 1, 0, "C", 1)
                pdf.cell(100, 6, "Ball-by-Ball", 1, 1, "C", 1)
                
                pdf.set_font("Arial", "", 7)
                for over in d1["over_history"]:
                    pdf.cell(15, 5, str(over.get("Over", "")), 1, 0, "C")
                    pdf.cell(50, 5, over.get("Bowler", "")[:20], 1, 0, "C")
                    pdf.cell(25, 5, over.get("Score", ""), 1, 0, "C")
                    timeline = over.get("Timeline", "")[:60]
                    pdf.cell(100, 5, timeline, 1, 1, "L")
        
        # Page 2 - Innings 2
        d2 = m["innings_2"]
        if d2["b1"]["name"]:
            pdf.add_page()
            y = 20
            
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 8, 'F')
            pdf.set_xy(15, y + 1.5)
            pdf.cell(0, 5, f"INNINGS 2: {m['team_2']} BATTING", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 12
            
            target = d1["runs"] + 1
            overs2 = f"{d2['balls']//6}.{d2['balls']%6}"
            run_rate = d2['runs']/(d2['balls']/6) if d2['balls'] > 0 else 0
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 7, f"Target: {target} runs  |  Current: {d2['runs']}/{d2['wickets']} in {overs2} overs (RR: {run_rate:.2f})", ln=True)
            y += 5
            
            # Batting Table
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(55, 8, "BATSMAN", 1, 0, "C", 1)
            pdf.cell(20, 8, "R", 1, 0, "C", 1)
            pdf.cell(20, 8, "B", 1, 0, "C", 1)
            pdf.cell(15, 8, "4s", 1, 0, "C", 1)
            pdf.cell(15, 8, "6s", 1, 0, "C", 1)
            pdf.cell(25, 8, "SR", 1, 0, "C", 1)
            pdf.cell(50, 8, "DISMISSAL", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d2["b1"]["name"]:
                sr = d2["b1"]["runs"] * 100 / d2["b1"]["balls"] if d2["b1"]["balls"] > 0 else 0
                pdf.cell(55, 6, d2["b1"]["name"][:25], 1)
                pdf.cell(20, 6, str(d2["b1"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b1"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b1"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            if d2["b2"]["name"]:
                sr = d2["b2"]["runs"] * 100 / d2["b2"]["balls"] if d2["b2"]["balls"] > 0 else 0
                pdf.cell(55, 6, d2["b2"]["name"][:25], 1)
                pdf.cell(20, 6, str(d2["b2"]["runs"]), 1, 0, "C")
                pdf.cell(20, 6, str(d2["b2"]["balls"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"]["fours"]), 1, 0, "C")
                pdf.cell(15, 6, str(d2["b2"]["sixes"]), 1, 0, "C")
                pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                pdf.cell(50, 6, "Not Out", 1, 1, "C")
            
            for b in d2.get("all_batsmen", []):
                if b.get("name"):
                    sr = b.get("runs", 0) * 100 / b.get("balls", 1) if b.get("balls", 0) > 0 else 0
                    pdf.cell(55, 6, b["name"][:25], 1)
                    pdf.cell(20, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(20, 6, str(b.get("balls", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("fours", 0)), 1, 0, "C")
                    pdf.cell(15, 6, str(b.get("sixes", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{sr:.1f}", 1, 0, "C")
                    pdf.cell(50, 6, b.get("status", "Out")[:20], 1, 1, "C")
            
            y = pdf.get_y() + 3
            
            # Bowling Table
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(59, 130, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.rect(10, y, 190, 7, 'F')
            pdf.set_xy(15, y + 1.5)
            pdf.cell(0, 4, "BOWLING FIGURES", ln=True)
            pdf.set_text_color(0, 0, 0)
            y += 10
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(60, 7, "BOWLER", 1, 0, "C", 1)
            pdf.cell(25, 7, "OVERS", 1, 0, "C", 1)
            pdf.cell(25, 7, "RUNS", 1, 0, "C", 1)
            pdf.cell(25, 7, "WICKETS", 1, 0, "C", 1)
            pdf.cell(25, 7, "ECON", 1, 0, "C", 1)
            pdf.cell(30, 7, "MAIDENS", 1, 1, "C", 1)
            
            pdf.set_font("Arial", "", 8)
            if d2["bowler"]["name"]:
                overs = d2["bowler"]["balls"] / 6
                econ = d2["bowler"]["runs"] / overs if overs > 0 else 0
                pdf.cell(60, 6, d2["bowler"]["name"][:25], 1)
                pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                pdf.cell(25, 6, str(d2["bowler"]["runs"]), 1, 0, "C")
                pdf.cell(25, 6, str(d2["bowler"]["wickets"]), 1, 0, "C")
                pdf.cell(25, 6, f"{econ:.2f}", 1, 0, "C")
                pdf.cell(30, 6, "0", 1, 1, "C")
            
            for b in d2.get("all_bowlers", []):
                if b.get("name"):
                    overs = b.get("balls", 0) / 6
                    econ = b.get("runs", 0) / overs if overs > 0 else 0
                    pdf.cell(60, 6, b["name"][:25], 1)
                    pdf.cell(25, 6, f"{overs:.1f}", 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("runs", 0)), 1, 0, "C")
                    pdf.cell(25, 6, str(b.get("wickets", 0)), 1, 0, "C")
                    pdf.cell(25, 6, f"{econ:.2f}", 1, 0, "C")
                    pdf.cell(30, 6, "0", 1, 1, "C")
            
            y = pdf.get_y() + 3
            
            if d2["over_history"]:
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(59, 130, 246)
                pdf.set_text_color(255, 255, 255)
                pdf.rect(10, y, 190, 7, 'F')
                pdf.set_xy(15, y + 1.5)
                pdf.cell(0, 4, "OVER BY OVER SUMMARY", ln=True)
                pdf.set_text_color(0, 0, 0)
                y += 10
                
                pdf.set_font("Arial", "B", 8)
                pdf.cell(15, 6, "Over", 1, 0, "C", 1)
                pdf.cell(50, 6, "Bowler", 1, 0, "C", 1)
                pdf.cell(25, 6, "Score", 1, 0, "C", 1)
                pdf.cell(100, 6, "Ball-by-Ball", 1, 1, "C", 1)
                
                pdf.set_font("Arial", "", 7)
                for over in d2["over_history"]:
                    pdf.cell(15, 5, str(over.get("Over", "")), 1, 0, "C")
                    pdf.cell(50, 5, over.get("Bowler", "")[:20], 1, 0, "C")
                    pdf.cell(25, 5, over.get("Score", ""), 1, 0, "C")
                    timeline = over.get("Timeline", "")[:60]
                    pdf.cell(100, 5, timeline, 1, 1, "L")
        
        # Output PDF
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue()
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return b""

@st.cache_resource
def get_db():
    return {"lock": threading.Lock(), "active_match_id": None, "matches": {}}

db = get_db()

# Sidebar - Auto hide when not admin
with st.sidebar:
    st.markdown("### 🔑 Live System Portal")
    role = st.radio("Access Profile:", ["📢 Player View", "⚡ Scorer Panel"])
    
    is_admin = False
    if role == "⚡ Scorer Panel":
        pwd = st.text_input("Admin Password:", type="password")
        if pwd == "anscor2026":
            is_admin = True
            st.success("✅ Admin Access Granted")
        elif pwd:
            st.error("Invalid Password")
    
    if not is_admin:
        st.markdown("---")
        st.caption("📺 Auto-refreshing every 3 seconds")
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=3000, key="auto_refresh")
        except:
            pass

# Main Tabs
tab_live, tab_review, tab_teams = st.tabs(["🏏 Live Match", "📊 Match Review", "👥 Teams"])

# Teams Tab
with tab_teams:
    st.markdown("### Tournament Teams")
    cols = st.columns(3)
    for i, (name, data) in enumerate(TEAM_DB.items()):
        with cols[i % 3]:
            st.image(data["remote"], width=120)
            st.markdown(f"**{name}**")
            if st.button(f"View Squad", key=f"squad_{i}"):
                with st.expander(f"{name} Squad", expanded=True):
                    for player in data["squad"]:
                        st.markdown(f"• {player}")

# Live Match Tab
with tab_live:
    # Match Management (Admin only)
    if is_admin:
        with st.expander("⚙️ Match Management", expanded=not db["active_match_id"]):
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.form("create_match"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        match_id = st.text_input("Match ID:", "Match_01")
                    with col_b:
                        team1 = st.selectbox("Team 1:", list(TEAM_DB.keys()))
                    with col_c:
                        team2 = st.selectbox("Team 2:", list(TEAM_DB.keys()))
                    
                    col_d, col_e = st.columns(2)
                    with col_d:
                        overs = st.number_input("Overs:", 1, 20, 4)
                    with col_e:
                        if st.form_submit_button("🚀 Create Match", use_container_width=True):
                            if match_id and team1 != team2:
                                with db["lock"]:
                                    db["matches"][match_id] = {
                                        "id": match_id, "team_1": team1, "team_2": team2,
                                        "total_overs": overs, "current_innings": 1,
                                        "innings_1": init_innings(), "innings_2": init_innings()
                                    }
                                    db["active_match_id"] = match_id
                                st.rerun()
            
            with col2:
                if db["matches"]:
                    current = db["active_match_id"] if db["active_match_id"] else list(db["matches"].keys())[0]
                    selected = st.selectbox("Active Match:", list(db["matches"].keys()), index=list(db["matches"].keys()).index(current))
                    if st.button("Set Active", use_container_width=True):
                        db["active_match_id"] = selected
                        st.rerun()
    
    # Display Active Match
    if not db["active_match_id"] or db["active_match_id"] not in db["matches"]:
        st.info("⏳ No active match. Create one using Match Management.")
    else:
        match = ensure_match(db["matches"][db["active_match_id"]])
        inn = match["innings_1"] if match["current_innings"] == 1 else match["innings_2"]
        batting = match["team_1"] if match["current_innings"] == 1 else match["team_2"]
        bowling = match["team_2"] if match["current_innings"] == 1 else match["team_1"]
        target = match["innings_1"]["runs"] + 1 if match["current_innings"] == 2 else None
        
        # Setup inning if needed
        if inn["b1"]["name"] == "" and is_admin:
            with st.form("setup_innings"):
                st.warning(f"📝 Setup {batting} Batting Lineup")
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
            # Calculate stats
            overs_done = inn["balls"] // 6
            balls_in_over = inn["balls"] % 6
            crr = inn["runs"] / (inn["balls"]/6) if inn["balls"] > 0 else 0
            
            # Get logos
            b_logo = get_image_base64(TEAM_DB[batting]["local"], TEAM_DB[batting]["remote"])
            bowl_logo = get_image_base64(TEAM_DB[bowling]["local"], TEAM_DB[bowling]["remote"])
            tour_logo = get_tournament_logo_base64()
            
            # Score Display
            st.markdown(f"""
                <div class="score-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <div style="text-align: center;">
                            <img src="data:image/jpeg;base64,{b_logo}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="margin-top: 5px; font-weight: bold;">{batting}</div>
                        </div>
                        <div style="font-size: 2rem; font-weight: bold; background: linear-gradient(135deg, #F59E0B, #EF4444); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">VS</div>
                        <div style="text-align: center;">
                            <img src="data:image/jpeg;base64,{bowl_logo}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #3B82F6;">
                            <div style="margin-top: 5px; font-weight: bold;">{bowling}</div>
                        </div>
                    </div>
                    <div class="score-number">{inn['runs']} - {inn['wickets']}</div>
                    <div>Overs: {overs_done}.{balls_in_over} / {match['total_overs']}</div>
                    <div>CRR: {crr:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if target:
                runs_needed = target - inn['runs']
                balls_left = (match['total_overs'] * 6) - inn['balls']
                req_rate = runs_needed / (balls_left/6) if balls_left > 0 else 0
                st.info(f"🎯 Target: {target} | Need {runs_needed} runs from {balls_left} balls | Required Rate: {req_rate:.2f}")
            
            # Main content area - Different for Admin vs Player
            if is_admin:
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    # Partnership and Bowler Info
                    st.markdown(f"""
                        <div class="info-card">
                            <b>🏏 CURRENT PARTNERSHIP</b><br>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <span>{"👉 " if inn['b1']['strike'] else ""}{inn['b1']['name']}</span>
                                <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {f"{inn['b1']['runs']*100/inn['b1']['balls']:.1f}" if inn['b1']['balls']>0 else "0.0"}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                                <span>{"👉 " if inn['b2']['strike'] else ""}{inn['b2']['name']}</span>
                                <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {f"{inn['b2']['runs']*100/inn['b2']['balls']:.1f}" if inn['b2']['balls']>0 else "0.0"}</span>
                            </div>
                            <hr>
                            <b>🥎 CURRENT BOWLER</b><br>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                                <span>{inn['bowler']['name']}</span>
                                <span>{inn['bowler']['wickets']}/{inn['bowler']['runs']} (Econ: {f"{inn['bowler']['runs']/(inn['bowler']['balls']/6):.2f}" if inn['bowler']['balls']>0 else "0.00"})</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Current Over Display
                    st.markdown("**📦 CURRENT OVER**")
                    if inn["this_over"]:
                        balls_html = ""
                        for ball in inn["this_over"]:
                            if ball in [4, 6]:
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
                    
                    # Recent Overs
                    st.markdown("**📊 RECENT OVERS**")
                    if inn["over_history"]:
                        for over in inn["over_history"][-5:]:
                            st.text(f"Over {over['Over']}: {over['Bowler']} - {over['Timeline']}")
                    else:
                        st.caption("No overs completed")
                    
                    # Match Status
                    st.info(get_match_status(match))
                
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
                    
                    # Handle special states
                    if inn["awaiting_batsman"]:
                        st.warning("⚠️ New Batsman Required")
                        used = [inn["b1"]["name"], inn["b2"]["name"]] + [b["name"] for b in inn["all_batsmen"]]
                        available = [p for p in TEAM_DB[batting]["squad"] if p not in used]
                        if not available:
                            available = TEAM_DB[batting]["squad"]
                        new_bat = st.selectbox("Select Batsman:", available)
                        if st.button("✅ Enter Batsman", use_container_width=True):
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
                        st.success("🔄 Over Complete! New Bowler Needed")
                        new_bowl = st.selectbox("Select Bowler:", TEAM_DB[bowling]["squad"])
                        if st.button("✅ Start Next Over", use_container_width=True):
                            with db["lock"]:
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
                            st.success("🏆 Target Achieved!")
                        else:
                            # Run buttons
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
                                if st.button("☝️ OUT", type="primary", use_container_width=True):
                                    add_ball(0, 0, True, True, "W")
                                    st.rerun()
                            with a2:
                                if inn["undo_stack"]:
                                    if st.button("↩️ UNDO", use_container_width=True):
                                        with db["lock"]:
                                            prev = inn["undo_stack"].pop()
                                            for k in ["runs", "wickets", "balls", "extras", "this_over", "b1", "b2", "bowler"]:
                                                inn[k] = prev[k]
                                        st.rerun()
                            with a3:
                                if st.button("🔄 SWAP", use_container_width=True):
                                    with db["lock"]:
                                        inn["b1"]["strike"] = not inn["b1"]["strike"]
                                        inn["b2"]["strike"] = not inn["b2"]["strike"]
                                    st.rerun()
                    else:
                        st.success("🏁 Innings Complete!")
                        if match["current_innings"] == 1 and is_admin:
                            if st.button("➡️ Start Innings 2", use_container_width=True, type="primary"):
                                with db["lock"]:
                                    match["current_innings"] = 2
                                st.rerun()
                    
                    # Admin extras
                    with st.expander("⚙️ Admin Tools"):
                        col1, col2 = st.columns(2)
                        with col1:
                            extra_type = st.selectbox("Type", ["Extras", "Penalty"])
                        with col2:
                            extra_runs = st.number_input("Runs", 1, 20, 1)
                        if st.button("Add Runs"):
                            with db["lock"]:
                                inn["runs"] += extra_runs
                                if extra_type == "Extras":
                                    inn["extras"] += extra_runs
                                    inn["this_over"].append(f"+{extra_runs}Ex")
                                else:
                                    inn["penalty"] = inn.get("penalty", 0) + extra_runs
                                    inn["this_over"].append(f"+{extra_runs}Pen")
                            st.rerun()
                    
                    # PDF Export
                    st.markdown("---")
                    if match["innings_1"]["balls"] > 0:
                        pdf_data = generate_complete_pdf(match)
                        if pdf_data and len(pdf_data) > 1000:
                            st.download_button("📥 Download Full Scorecard", pdf_data, f"APL_{match['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", use_container_width=True)
            
            else:
                # PLAYER VIEW - Full match details visible
                # Partnership and Bowler Info
                st.markdown(f"""
                    <div class="info-card">
                        <b>🏏 BATTING PARTNERSHIP</b><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <span>{"👉 " if inn['b1']['strike'] else ""}{inn['b1']['name']}</span>
                            <span><b>{inn['b1']['runs']}</b> ({inn['b1']['balls']}) | SR: {f"{inn['b1']['runs']*100/inn['b1']['balls']:.1f}" if inn['b1']['balls']>0 else "0.0"}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span>{"👉 " if inn['b2']['strike'] else ""}{inn['b2']['name']}</span>
                            <span><b>{inn['b2']['runs']}</b> ({inn['b2']['balls']}) | SR: {f"{inn['b2']['runs']*100/inn['b2']['balls']:.1f}" if inn['b2']['balls']>0 else "0.0"}</span>
                        </div>
                        <hr>
                        <b>🥎 CURRENT BOWLER</b><br>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <span>{inn['bowler']['name']}</span>
                            <span>{inn['bowler']['wickets']}/{inn['bowler']['runs']} (Econ: {f"{inn['bowler']['runs']/(inn['bowler']['balls']/6):.2f}" if inn['bowler']['balls']>0 else "0.00"})</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Current Over Display
                st.markdown("**📦 CURRENT OVER**")
                if inn["this_over"]:
                    balls_html = ""
                    for ball in inn["this_over"]:
                        if ball in [4, 6]:
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
                
                # Recent Overs
                st.markdown("**📊 RECENT OVERS**")
                if inn["over_history"]:
                    for over in inn["over_history"][-5:]:
                        st.text(f"Over {over['Over']}: {over['Bowler']} - {over['Timeline']}")
                else:
                    st.caption("No overs completed")
                
                # Fallen Wickets
                if inn["all_batsmen"]:
                    st.markdown("**📋 FALLEN WICKETS**")
                    for wkt in inn["all_batsmen"][-5:]:
                        st.caption(f"• {wkt['name']} - {wkt['runs']}({wkt['balls']})")
                
                # Match Status
                st.info(get_match_status(match))
                
                # PDF Export for Player View too
                st.markdown("---")
                if match["innings_1"]["balls"] > 0:
                    pdf_data = generate_complete_pdf(match)
                    if pdf_data and len(pdf_data) > 1000:
                        st.download_button("📥 Download Scorecard", pdf_data, f"APL_{match['id']}.pdf", use_container_width=True)

# Review Tab
with tab_review:
    if db["matches"]:
        match_id = st.selectbox("Select Match to Review:", list(db["matches"].keys()))
        m = ensure_match(db["matches"][match_id])
        
        st.markdown(f"## {m['team_1']} vs {m['team_2']}")
        st.caption(f"📋 {m['id']} | {m['total_overs']} overs")
        
        col1, col2 = st.columns(2)
        with col1:
            d1 = m["innings_1"]
            st.metric(f"Innings 1: {m['team_1']}", f"{d1['runs']}/{d1['wickets']}", f"{d1['balls']//6}.{d1['balls']%6} overs")
            if d1["over_history"]:
                st.dataframe(pd.DataFrame(d1["over_history"]), use_container_width=True, hide_index=True)
        with col2:
            d2 = m["innings_2"]
            st.metric(f"Innings 2: {m['team_2']}", f"{d2['runs']}/{d2['wickets']}", f"{d2['balls']//6}.{d2['balls']%6} overs")
            if d2["over_history"]:
                st.dataframe(pd.DataFrame(d2["over_history"]), use_container_width=True, hide_index=True)
        
        st.success(get_match_status(m))
        
        if m["innings_1"]["balls"] > 0:
            pdf_data = generate_complete_pdf(m)
            if pdf_data and len(pdf_data) > 1000:
                st.download_button("📥 Download Full Scorecard", pdf_data, f"APL_{m['id']}_Complete.pdf", use_container_width=True)
    else:
        st.info("No matches played yet")
