import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os
import base64

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Please ensure 'streamlit-autorefresh' is added to your requirements.txt file!")

# Page Configuration
st.set_page_config(page_title="APL 2026", page_icon="🏏", layout="wide")

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

def clean_for_pdf(text):
    if text is None:
        return ""
    text = str(text)
    
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    
    replacements = {
        "🏆": "WINNER:", "👔": "TIE:", "👉": ">", "🟢": "", "🟠": "", "🟡": "", 
        "🏏": "", "👤": "", "🥎": "", "🎛️": "", "📥": "", "🛠": "", "⚡": "", "📢": ""
    }
    for emoji, rep in replacements.items():
        text = text.replace(emoji, rep)
        
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf_bytes(m, inn_data, bat_team, bowl_team, crr):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, clean_for_pdf("APL 2026 - OFFICIAL SCORECARD REPORT"), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, clean_for_pdf(f"Match Series: {bat_team} vs {bowl_team}"), ln=True, align="C")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    comp_ov = inn_data["balls"] // 6
    rem_bl = inn_data["balls"] % 6
    pdf.cell(0, 8, clean_for_pdf(f"Batting Side Team: {bat_team}"), ln=True)
    pdf.cell(0, 8, clean_for_pdf(f"Current Team Score: {inn_data['runs']} / {inn_data['wickets']} ({comp_ov}.{rem_bl} Overs Played)"), ln=True)
    pdf.cell(0, 8, clean_for_pdf(f"Current Run Rate (CRR): {crr:.2f}"), ln=True)
    pdf.cell(0, 8, clean_for_pdf(f"Total Extras Awarded: {inn_data['extras']}"), ln=True)
    if inn_data.get("penalty", 0) > 0:
        pdf.cell(0, 8, clean_for_pdf(f"Administrative Penalty Runs: {inn_data['penalty']}"), ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, clean_for_pdf("Active Partnerships & Batters Status"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    b1_name = inn_data.get('b1', {}).get('name', 'Opening Batter 1') or 'Opening Batter 1'
    b2_name = inn_data.get('b2', {}).get('name', 'Opening Batter 2') or 'Opening Batter 2'
    bowler_name = inn_data.get('bowler', {}).get('name', 'Active Bowler') or 'Active Bowler'
    
    s1 = " *On-Strike" if inn_data.get('b1', {}).get('strike', False) else ""
    s2 = " *On-Strike" if inn_data.get('b2', {}).get('strike', False) else ""
    
    pdf.cell(0, 6, clean_for_pdf(f"- {b1_name}{s1}: {inn_data.get('b1', {}).get('runs', 0)} Runs scored from {inn_data.get('b1', {}).get('balls', 0)} balls"), ln=True)
    pdf.cell(0, 6, clean_for_pdf(f"- {b2_name}{s2}: {inn_data.get('b2', {}).get('runs', 0)} Runs scored from {inn_data.get('b2', {}).get('balls', 0)} balls"), ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, clean_for_pdf("Active Bowler Analysis Profile"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, clean_for_pdf(f"- Bowler: {bowler_name} -> Wickets Taken: {inn_data.get('bowler', {}).get('wickets', 0)} | Conceded Runs: {inn_data.get('bowler', {}).get('runs', 0)}"), ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, clean_for_pdf("Historical Over Ledger Progress Tracker"), ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 6, "Over No.", 1)
    pdf.cell(55, 6, "Bowler Assigned", 1)
    pdf.cell(40, 6, "Score Progression", 1)
    pdf.cell(70, 6, "Timeline Delivery History", 1, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    for ov in inn_data.get("over_history", []):
        pdf.cell(25, 6, clean_for_pdf(str(ov.get("Over", ""))), 1)
        pdf.cell(55, 6, clean_for_pdf(str(ov.get("Bowler", ""))), 1)
        pdf.cell(40, 6, clean_for_pdf(str(ov.get("Score", ""))), 1)
        pdf.cell(70, 6, clean_for_pdf(str(ov.get("Timeline", ""))), 1, ln=True)
        
    return bytes(pdf.output())

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
    st_autorefresh(interval=3000, key="broadcast_pulse")

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
        with st.expander("🛠  Match Allocation Parameters & Inning Control Hub", expanded=not bool(db_global["active_match_id"])):
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
            # Run Rate Calculations
            comp_ov = inn_data["balls"] // 6
            rem_bl = inn_data["balls"] % 6
            frac_ov = comp_ov + (rem_bl / 6)
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            innings_ended = (comp_ov >= m_instance["total_overs"]) or (inn_data["wickets"] >= 10)
            if target_score and inn_data["runs"] >= target_score:
                innings_ended = True
                
            status_tag = "FINISHED" if innings_ended else "LIVE"

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
                        <h5 style="margin:6px 0 0 0; font-weight:800; color:#34D399;">Current Run Rate (CRR): {crr:.2f}</h5>
                    </div>
                """, unsafe_allow_html=True)
                
                if target_score:
                    st.warning(f"🎯 Target Chase: {target_score} (Needs {target_score - inn_data['runs']} runs off {(m_instance['total_overs']*6) - inn_data['balls']} balls)")

                m_c1, m_c2 = st.columns(2)
                m_c1.metric("Extras Granted", f"{inn_data['extras'] + inn_data.get('penalty', 0)}")
                m_c2.metric("Current Run Rate (CRR Summary)", f"{crr:.2f}")

                st.markdown("##### 📦 Over Timeline Tracker")
                if inn_data["this_over"]:
                    html_b = ""
                    for b in inn_data["this_over"]:
                        bg_color = "#475569"
                        if str(b) in ["4", "6"]: bg_color = "#10B981"
                        elif "W" in str(b): bg_color = "#EF4444"
                        elif "WD" in str(b) or "NB" in str(b) or "Ex" in str(b) or "Pen" in str(b): bg_color = "#D97706"
                        html_b += f'<span class="ball-bubble" style="background-color:{bg_color}; color:white;">{b}</span>'
                    st.markdown(html_b, unsafe_allow_html=True)
                else: 
                    st.caption("Waiting for delivery logs...")
                
                match_outcome = get_match_result(m_instance)
                st.info(f"📢 Status: {match_outcome}")

            with r_col:
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.75rem; color:#94A3B8;"><b>🏏 BATTING PARTNERSHIP</b></div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.9rem;">
                            <span>{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}</span>
                            <span><b>{inn_data['b1']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b1']['balls']}b)</span></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.9rem;">
                            <span>{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}</span>
                            <span><b>{inn_data['b2']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b2']['balls']}b)</span></span>
                        </div>
                        <div style="margin-top:8px; font-size:0.75rem; color:#94A3B8;"><b>🥎 CURRENT OPERATING BOWLER</b></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                            <span>👤 {inn_data['bowler']['name']}</span>
                            <span>Wkts: <b style="color:#EF4444;">{inn_data['bowler']['wickets']}</b> | Runs: <b>{inn_data['bowler']['runs']}</b></span>
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
                        b_c1, b_c2, b_c3, b_c4 = st.columns(4)
                        if b_c1.button("0 Runs", use_container_width=True): process_ball_input(0, 0, True); st.rerun()
                        if b_c2.button("1 Run", use_container_width=True): process_ball_input(1, 0, True); st.rerun()
                        if b_c3.button("2 Runs", use_container_width=True): process_ball_input(2, 0, True); st.rerun()
                        if b_c4.button("3 Runs", use_container_width=True): process_ball_input(3, 0, True); st.rerun()
                        
                        b_br1, b_br2, b_br3, b_br4 = st.columns(4)
                        if b_br1.button("🟢 4", use_container_width=True): 
                            process_ball_input(4, 0, True)
                            (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["fours"] += 1
                            st.rerun()
                        if b_br2.button("🟢 6", use_container_width=True): 
                            process_ball_input(6, 0, True)
                            (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["sixes"] += 1
                            st.rerun()
                        if b_br3.button("🟡 WD", use_container_width=True): process_ball_input(1, 1, False, symbol="WD"); st.rerun()
                        if b_br4.button("🟠 NB", use_container_width=True): process_ball_input(1, 1, False, symbol="NB"); st.rerun()
                        
                        st.write("")
                        if st.button("☝️ OUT / FALL OF WICKET DETECTED", type="primary", use_container_width=True):
                            process_ball_input(runs_inc=0, extra_inc=0, is_legal=True, is_wicket=True, symbol="W")
                            st.rerun()
                    else:
                        st.success("🏁 Innings complete.")

                    # --- ADDED: EXTRA RUNS & PENALTY DIRECT PANELS ---
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
                            if st.button("⚠️ Undo Ball", use_container_width=True):
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

            # --- EXPORT REGION ---
