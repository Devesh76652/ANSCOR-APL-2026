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
st.set_page_config(page_title="ANSCOR APL 2026", page_icon="🏏", layout="wide")

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

MAIN_LOGOS = {"local": "le.mat.jpeg", "remote": GITHUB_RAW_BASE + "le.mat.jpeg"}

# FIXED: Added support for list-wrapped paths & default remote_url=""
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

# FIXED: Added support for list-wrapped paths inside Streamlit image rendering pipeline
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

# Custom App CSS Theme Styling Override Engine
st.markdown("""
    <style>
    .block-container { padding: 0.25rem 0.5rem !important; max-width: 100% !important; }
    .score-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: white;
        padding: 12px 15px; border-radius: 12px; text-align: center; margin-bottom: 6px;
        border: 2px solid #1E40AF; position: relative; box-shadow: 0 8px 12px -3px rgba(0, 0, 0, 0.3);
    }
    .status-badge {
        position: absolute; top: 6px; right: 12px; background-color: #EF4444; color: white;
        padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; letter-spacing: 0.5px;
    }
    .mobile-card { background-color: #1E293B; border: 1px solid #334155; padding: 10px; border-radius: 10px; margin-bottom: 6px; }
    .ball-bubble {
        display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px;
        border-radius: 50%; margin: 2px; font-weight: 800; font-size: 0.85rem;
    }
    .team-block-container { background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 10px; }
    
    /* Strict layout consolidation styles to eliminate vertical scrolling */
    h3, h4, h5 {
        margin-top: 3px !important;
        margin-bottom: 3px !important;
        font-size: 0.95rem !important;
    }
    div.stButton > button {
        padding: 3px 6px !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        border-radius: 6px !important;
        margin-top: 2px !important;
        margin-bottom: 2px !important;
    }
    .stExpander {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)

def init_blank_innings():
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [], "all_bowlers_history": [], "undo_stack": [],
        "awaiting_batsman": False, "awaiting_bowler": False
    }

# Migration Helper: Self-heals globally cached matches by filling missing keys on the fly
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

# Defensive Scheme Helper: Ensures absolute immunity to KeyError on outdated match objects
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

# Clean Encoder Helper: Strips non-latin1 glyphs (like emojis) to guarantee FPDF report generation stability
def sanitize_for_pdf(text):
    if not text:
        return ""
    replacements = {
        "🏆": "", "🏏": "", "🥎": "", "📢": "", "👔": "", "👉": "",
        "🟢": "", "🟡": "", "🟠": "", "☝️": "", "🏁": "", "📋": "",
        "📺": "", "🗄️": "", "📥": ""
    }
    for emoji, rep in replacements.items():
        text = text.replace(emoji, rep)
    try:
        text_encoded = text.encode("latin-1", errors="ignore")
        return text_encoded.decode("latin-1")
    except Exception:
        return "".join(c for c in text if ord(c) < 128)

# Safe PDF byte converter compatible with both fpdf (classic) and fpdf2
def get_pdf_bytes(pdf):
    try:
        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, (bytes, bytearray)):
            return bytes(pdf_bytes)
    except Exception:
        pass
    try:
        pdf_str = pdf.output(dest='S')
        if isinstance(pdf_str, str):
            return pdf_str.encode('latin-1', errors='ignore')
        return bytes(pdf_str)
    except Exception:
        pass
    try:
        return bytes(pdf.output())
    except Exception:
        return b""

# Dynamic Winner Evaluation Engine
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
    
    # Assess first innings completion status
    i1_complete = (balls_i1 >= total_overs * 6) or (wickets_i1 >= 10)
    
    if m["current_innings"] == 1:
        if i1_complete:
            return f"Innings 1 Finished: {m['team_1']} scored {runs_i1}/{wickets_i1}. Ready for target run chase."
        else:
            return f"Match Active: {m['team_1']} is batting in the first Innings."
            
    # Innings 2 Analysis
    target = runs_i1 + 1
    
    # 2nd Innings successfully chased target
    if runs_i2 >= target:
        wickets_won = 10 - wickets_i2
        return f"🏆 {m['team_2']} won by {wickets_won} wickets!"
        
    # Is 2nd Innings complete?
    i2_complete = (balls_i2 >= total_overs * 6) or (wickets_i2 >= 10)
    
    if i2_complete:
        if runs_i2 < runs_i1:
            margin = runs_i1 - runs_i2
            return f"🏆 {m['team_1']} won by {margin} runs!"
        elif runs_i2 == runs_i1:
            return "👔 Match Ended in a Tie!"
            
    # Innings 2 active
    runs_needed = target - runs_i2
    balls_rem = (total_overs * 6) - balls_i2
    return f"🏏 Target Chase: {m['team_2']} needs {runs_needed} runs from {balls_rem} balls to win."

@st.cache_resource
def get_tournament_database():
    return {
        "lock": threading.Lock(),
        "active_match_id": None,
        "matches": {}
    }

db_global = get_tournament_database()
lock = db_global["lock"]

# Run a global self-healing sweep over the cache at start to upgrade any stale cached match structures
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

# --- SECURITY PROFILE SETTINGS ---
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

# Branding Header Banner - Self-healing, aligned, elegant design
main_logo_src = get_image_src(MAIN_LOGOS["local"], MAIN_LOGOS["remote"])
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 12px; padding-top:2px;">
        <div style="width: 55px; height: 55px; background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); flex-shrink: 0; overflow: hidden; border: 1px solid #1E40AF;">
            <img src="{main_logo_src}" style="width: 100%; height: 100%; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
            <div style="display: none; font-size: 1.6rem; align-items: center; justify-content: center; width: 100%; height: 100%;">🏏</div>
        </div>
        <div>
            <h2 style='color: #FFFFFF; font-size: 1.8rem; font-weight: 900; letter-spacing: 0.5px; margin: 0; line-height: 1.1;'>ANSCOR APL 2026</h2>
            <p style='color: #94A3B8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; margin: 2px 0 0 0;'>Corporate Tournament Broadcast Portal</p>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_live, tab_review, tab_teams = st.tabs(["📺 Live Match Console", "🗄️ Tournament Match Review", "📋 Team Profiles"])

# ================= TAB: TEAM DIRECTORIES =================
with tab_teams:
    st.markdown("### Tournament Roster Groups")
    t_cols = st.columns(3)
    for idx, t_name in enumerate(TEAM_DB.keys()):
        with t_cols[idx % 3]:
            st.markdown('<div class="team-block-container">', unsafe_allow_html=True)
            smart_load_image(TEAM_DB[t_name]["local"], TEAM_DB[t_name]["remote"], use_container=True)
            if st.button(f"View Squad Roster", key=f"squad_popup_key_{idx}", use_container_width=True):
                show_squad_popup(t_name)
            st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB: LIVE SCORES ENGINE =================
with tab_live:
    if is_admin:
        with st.expander("🛠  Match Allocation Parameters & Inning Control Hub", expanded=not bool(db_global["active_match_id"])):
            st.markdown("#### Initialize a Brand New Match Instance")
            with st.form("new_match_allocation_form"):
                new_m_id = st.text_input("Unique Match Identifier Name (e.g., Match_01, Final_Game):")
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
                        st.success(f"Ecosystem match profile '{new_m_id}' configured successfully.")
                        st.rerun()

            if db_global["matches"]:
                st.markdown("---")
                st.markdown("#### Live Control Focusing System")
                selected_focus = st.selectbox("Switch Active Admin Stream Focus Window:", list(db_global["matches"].keys()), index=list(db_global["matches"].keys()).index(db_global["active_match_id"]) if db_global["active_match_id"] else 0)
                if st.button("Apply Selected Focus Switch Stream"):
                    db_global["active_match_id"] = selected_focus
                    st.rerun()
                
                # Safety guard to ensure ensure_match_keys is called only if the selected active match exists in the dictionary
                if db_global["active_match_id"] in db_global["matches"]:
                    active_match = ensure_match_keys(db_global["matches"][db_global["active_match_id"]])
                    if active_match["current_innings"] == 1:
                        if st.button("🔄 Transition Match to Innings 2 (Begin Target Run Chase) ➡️", type="primary"):
                            with lock:
                                active_match["current_innings"] = 2
                            st.success("Match flipped cleanly over to Innings 2!")
                            st.rerun()

    # Scoreboard Live Session Focus Check
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
            
            # Hard Over Innings Limit Check
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
                
                # HIGHLY COMPACT INTEGRATED HORIZONTAL SCORECARD (Hides legacy Extras/CRR block to prevent any scrolling)
                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">{status_tag}</span>
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 5px;">
                            <!-- Batting Side logo and name -->
                            <div style="flex: 1; text-align: center;">
                                <div style="width: 50px; height: 50px; margin: 0 auto; background: rgba(255,255,255,0.08); border-radius: 8px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid rgba(255,255,255,0.15);">
                                    <img src="{b_logo_src}" style="width: 100%; height: 100%; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                    <div style="display: none; font-size: 1.4rem; align-items: center; justify-content: center; width:100%; height:100%;">🏏</div>
                                </div>
                                <div style="font-size: 0.8rem; font-weight: 800; margin-top: 4px; color: #F8FAFC; line-height: 1.1; max-width: 110px; margin-left: auto; margin-right: auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{bat_team}</div>
                            </div>
                            
                            <!-- Condensed Live Score & Overs -->
                            <div style="flex: 1.4; text-align: center; display: flex; flex-direction: column; justify-content: center;">
                                <div style="font-size: 2.7rem; font-weight: 900; line-height: 0.95; margin: 0; color: #FFFFFF; letter-spacing: -0.5px;">{inn_data['runs']} - {inn_data['wickets']}</div>
                                <div style="font-size: 0.85rem; font-weight: 700; color: #93C5FD; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</div>
                            </div>
                            
                            <!-- Bowling Side logo and name -->
                            <div style="flex: 1; text-align: center;">
                                <div style="width: 50px; height: 50px; margin: 0 auto; background: rgba(255,255,255,0.08); border-radius: 8px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid rgba(255,255,255,0.15);">
                                    <img src="{f_logo_src}" style="width: 100%; height: 100%; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                    <div style="display: none; font-size: 1.4rem; align-items: center; justify-content: center; width:100%; height:100%;">🥎</div>
                                </div>
                                <div style="font-size: 0.8rem; font-weight: 800; margin-top: 4px; color: #F8FAFC; line-height: 1.1; max-width: 110px; margin-left: auto; margin-right: auto; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{bowl_team}</div>
                            </div>
                        </div>
                        {f'<div style="color:#F59E0B; background-color:rgba(0,0,0,0.3); padding:4px 8px; border-radius:6px; font-size:0.8rem; font-weight:700; margin-top:6px; display:inline-block; border: 1px solid rgba(245,158,11,0.2);">🎯 Target Chase: {target_score} (Needs {target_score - inn_data["runs"]} off {(m_instance["total_overs"]*6) - inn_data["balls"]} balls)</div>' if target_score else ''}
                    </div>
                """, unsafe_allow_html=True)

                # Condensed Match Status Outcome Bar
                match_outcome = get_match_result(m_instance)
                st.markdown(f"""
                    <div style="background-color: #1E293B; border-left: 3px solid #3B82F6; padding: 5px 10px; border-radius: 6px; margin: 4px 0; font-size: 0.85rem; font-weight: 700; color: #F8FAFC; text-align: center;">
                        📢 Status: <span style="color: #60A5FA;">{match_outcome}</span>
                    </div>
                """, unsafe_allow_html=True)

                if is_admin:
                    col_undo, col_swap = st.columns([1, 1])
                    with col_undo:
                        if inn_data["undo_stack"]:
                            if st.button("⚠️ Undo Last Ball", use_container_width=True):
                                with lock:
                                    prev_state = inn_data["undo_stack"].pop()
                                    for k in ["runs", "wickets", "balls", "extras", "this_over", "over_history", "b1", "b2", "bowler", "all_batsmen_history", "all_bowlers_history", "awaiting_batsman", "awaiting_bowler"]:
                                        inn_data[k] = prev_state[k]
                                st.success("Rolled back last ball sequence.")
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
                            st.button("Swap Strike Disabled", disabled=True, use_container_width=True)

                    # --- INLINE SELECTION ROSTERS REPLACING POPUPS ---
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
                                past_b = next((b for b in inn_data["all_bowlers_history"] if b["name"] == inn_data["bowler"]["name"]), None)
                                if past_b:
                                    past_b["runs"] += inn_data["bowler"]["runs"]
                                    past_b["wickets"] += inn_data["bowler"]["wickets"]
                                    past_b["balls"] += inn_data["bowler"]["balls"]
                                    past_b["maidens"] += inn_data["bowler"]["maidens"]
                                else:
                                    if inn_data["bowler"]["name"] != "":
                                        inn_data["all_bowlers_history"].append(copy.deepcopy(inn_data["bowler"]))
                                inn_data["bowler"] = {"name": next_bw, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                                inn_data["awaiting_bowler"] = False
                            st.rerun()

                    elif not innings_ended:
                        def submit_ball(runs_inc, extra_inc=0, is_legal=True, symbol=None):
                            with lock:
                                state_snap = copy.deepcopy({
                                    "runs": inn_data["runs"], "wickets": inn_data["wickets"], "balls": inn_data["balls"],
                                    "extras": inn_data["extras"], "this_over": list(inn_data["this_over"]), "over_history": copy.deepcopy(inn_data["over_history"]),
                                    "b1": copy.deepcopy(inn_data["b1"]), "b2": copy.deepcopy(inn_data["b2"]), "bowler": copy.deepcopy(inn_data["bowler"]),
                                    "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]), "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
                                    "awaiting_batsman": inn_data["awaiting_batsman"], "awaiting_bowler": inn_data["awaiting_bowler"]
                                })
                                inn_data["undo_stack"].append(state_snap)

                                striker = inn_data["b1"] if inn_data["b1"]["strike"] else inn_data["b2"]
                                inn_data["runs"] += runs_inc
                                inn_data["extras"] += extra_inc
                                inn_data["bowler"]["runs"] += runs_inc
                                
                                if is_legal:
                                    inn_data["balls"] += 1
                                    inn_data["bowler"]["balls"] += 1
                                    striker["balls"] += 1
                                    striker["runs"] += (runs_inc - extra_inc)
                                    inn_data["this_over"].append(symbol if symbol is not None else runs_inc)
                                else:
                                    inn_data["this_over"].append(symbol)
                                    
                                if is_legal and (runs_inc % 2 != 0):
                                    inn_data["b1"]["strike"] = not inn_data["b1"]["strike"]
                                    inn_data["b2"]["strike"] = not inn_data["b2"]["strike"]
                                    
                                # Core Over Evaluation Ends Logic Bound Checks
                                legal_balls_in_over = [b for b in inn_data["this_over"] if b not in ['WD', 'NB']]
                                if len(legal_balls_in_over) == 6:
                                    runs_in_ov = sum([b for b in inn_data["this_over"] if isinstance(b, int)])
                                    if runs_in_ov == 0: inn_data["bowler"]["maidens"] += 1
                                    inn_data["over_history"].append({
                                        "Over": len(inn_data["over_history"]) + 1, "Bowler": inn_data["bowler"]["name"],
                                        "Score": f"{inn_data['runs']}/{inn_data['wickets']}", "Timeline": ", ".join(map(str, inn_data["this_over"]))
                                    })
                                    inn_data["this_over"] = []
                                    inn_data["awaiting_bowler"] = True

                        st.markdown("#### 🎛  Scoring Dashboard Control Input Panel")
                        b_c1, b_c2, b_c3, b_c4 = st.columns(4)
                        if b_c1.button("0 Runs"): submit_ball(0, 0, True)
                        if b_c2.button("1 Run"): submit_ball(1, 0, True)
                        if b_c3.button("2 Runs"): submit_ball(2, 0, True)
                        if b_c4.button("3 Runs"): submit_ball(3, 0, True)
                        
                        b_br1, b_br2, b_br3, b_br4 = st.columns(4)
                        if b_br1.button("🟢 4"): submit_ball(4, 0, True); (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["fours"] += 1
                        if b_br2.button("🟢 6"): submit_ball(6, 0, True); (inn_data["b1" if inn_data["b1"]["strike"] else "b2"])["sixes"] += 1
                        if b_br3.button("🟡 WD"): submit_ball(1, 1, False, "WD")
                        if b_br4.button("🟠 NB"): submit_ball(1, 1, False, "NB")
                        
                        st.markdown("#### ⚙️ Manual Custom Extras Adjustments")
                        with st.expander("Inject Manual Overthrow / Penalty Extras", expanded=False):
                            ex_type = st.selectbox("Select Extra Category Variant:", ["Leg Byes / Byes", "Penalty Extras", "Overthrow Bound Runs"])
                            ex_count = st.number_input("Total custom run counts to apply:", min_value=1, max_value=10, value=1)
                            ball_impact_legal = st.radio("Consume delivery count on scorecard?", ["No", "Yes"])
                            
                            if st.button("Inject Extras Into Active Dashboard", use_container_width=True):
                                submit_ball(
                                    runs_inc=ex_count, 
                                    extra_inc=ex_count, 
                                    is_legal=(ball_impact_legal == "Yes"), 
                                    symbol=f"+{ex_count}Ex"
                                )
                                st.success("Custom extras snapshot injected.")
                                st.rerun()

                        if st.button("☝️ OUT / FALL OF WICKET DETECTED", type="primary", use_container_width=True):
                            with lock:
                                state_snap = copy.deepcopy({
                                    "runs": inn_data["runs"], "wickets": inn_data["wickets"], "balls": inn_data["balls"],
                                    "extras": inn_data["extras"], "this_over": list(inn_data["this_over"]), "over_history": copy.deepcopy(inn_data["over_history"]),
                                    "b1": copy.deepcopy(inn_data["b1"]), "b2": copy.deepcopy(inn_data["b2"]), "bowler": copy.deepcopy(inn_data["bowler"]),
                                    "all_batsmen_history": copy.deepcopy(inn_data["all_batsmen_history"]), "all_bowlers_history": copy.deepcopy(inn_data["all_bowlers_history"]),
                                    "awaiting_batsman": inn_data["awaiting_batsman"], "awaiting_bowler": inn_data["awaiting_bowler"]
                                })
                                inn_data["undo_stack"].append(state_snap)

                                inn_data["wickets"] += 1
                                inn_data["balls"] += 1
                                inn_data["bowler"]["wickets"] += 1
                                inn_data["this_over"].append("W")
                                
                                if inn_data["wickets"] < 10 and (inn_data["balls"] < m_instance["total_overs"] * 6):
                                    inn_data["awaiting_batsman"] = True
                            st.rerun()
                    else:
                        st.success("🏁 Innings completion limits fulfilled. Target parameters frozen.")

            with r_col:
                st.markdown("#### Live Active Metrics Performances")
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.75rem; color:#94A3B8; margin-bottom: 2px;"><b>🏏 BATTING PAIR PARTNERSHIP</b></div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.85rem;">
                            <span>{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}</span>
                            <span><b>{inn_data['b1']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b1']['balls']}b)</span></span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin:2px 0; font-size:0.85rem;">
                            <span>{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}</span>
                            <span><b>{inn_data['b2']['runs']}</b> <span style="color:#A1A1AA; font-size:0.75rem;">({inn_data['b2']['balls']}b)</span></span>
                        </div>
                        <div style="margin-top:8px; font-size:0.75rem; color:#94A3B8; margin-bottom: 2px;"><b>🥎 CURRENT OPERATING BOWLER</b></div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                            <span>👤 {inn_data['bowler']['name']}</span>
                            <span>Wkts: <b style="color:#EF4444;">{inn_data['bowler']['wickets']}</b> | Runs: <b>{inn_data['bowler']['runs']}</b></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Live Active Over Delivery Timeline Trackers")
                if inn_data["this_over"]:
                    html_b = "".join([f'<span class="ball-bubble" style="background-color:{"#10B981" if str(b) in ["4","6"] else ("#EF4444" if "W" in str(b) else "#475569")}; color:white;">{b}</span>' for b in inn_data["this_over"]])
                    st.markdown(html_b, unsafe_allow_html=True)
                else: st.caption("Waiting for delivery run logs sequence details...")

                st.markdown("#### Completed Overs Breakdown Log")
                if inn_data["over_history"]:
                    st.dataframe(pd.DataFrame(inn_data["over_history"]), use_container_width=True, hide_index=True, height=105)
                else: st.caption("No archived records.")

                # ================= REPORT GENERATION ENGINE =================
                def generate_full_pdf_report():
                    pdf = FPDF()
                    
                    # Page for Innings 1
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 20)
                    pdf.set_text_color(30, 58, 138)
                    pdf.cell(0, 12, "ANSCOR APL 2026 OFFICIAL MATCH REPORT", ln=1, align="C")
                    pdf.set_font("Helvetica", "I", 10)
                    pdf.set_text_color(100, 116, 139)
                    pdf.cell(0, 6, "Official Corporate Live Tournament Scorecard Profile Summary", ln=1, align="C")
                    pdf.ln(4)
                    
                    # Highlight Match Winner / Result clearly at top of PDF Report with safe sanitization (Strips Emojis)
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(220, 38, 38)
                    pdf.cell(0, 8, sanitize_for_pdf(f" MATCH RESULT: {get_match_result(m_instance).upper()}"), ln=1, align="C")
                    pdf.ln(4)
                    
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(15, 23, 42)
                    pdf.set_fill_color(241, 245, 249)
                    
                    d1 = ensure_innings_keys(m_instance["innings_1"])
                    b_team_i1 = m_instance["team_1"]
                    f_team_i1 = m_instance["team_2"]
                    
                    pdf.cell(0, 10, sanitize_for_pdf(f" INNINGS 1: {b_team_i1.upper()} vs {f_team_i1.upper()}"), ln=1, fill=True)
                    pdf.ln(1)
                    
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(15, 23, 42)
                    pdf.cell(95, 7, f"Total Innings Runs: {d1['runs']} / {d1['wickets']}", ln=0)
                    pdf.cell(95, 7, f"Overs Completed: {d1['balls'] // 6}.{d1['balls'] % 6} / {m_instance['total_overs']} Ov", ln=1)
                    pdf.cell(95, 7, f"Innings Extras: {d1['extras']}", ln=0)
                    pdf.cell(95, 7, f"Current Innings End State Status: Complete", ln=1)
                    pdf.ln(4)
                    
                    # Batsmen table
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 8, " Batsman Performance Profile", ln=1)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.set_fill_color(226, 232, 240)
                    pdf.cell(75, 7, " Batsman Name", border=1, ln=0, fill=True)
                    pdf.cell(40, 7, " Dismissal", border=1, ln=0, fill=True)
                    pdf.cell(20, 7, " Runs", border=1, ln=0, fill=True)
                    pdf.cell(20, 7, " Balls", border=1, ln=0, fill=True)
                    pdf.cell(15, 7, " 4s", border=1, ln=0, fill=True)
                    pdf.cell(15, 7, " 6s", border=1, ln=1, fill=True)
                    
                    pdf.set_font("Helvetica", "", 9)
                    all_bat1 = list(d1["all_batsmen_history"])
                    if d1["b1"]["name"] != "": all_bat1.append(d1["b1"])
                    if d1["b2"]["name"] != "": all_bat1.append(d1["b2"])
                    
                    for b in all_bat1:
                        if b["name"] == "": continue
                        pdf.cell(75, 7, sanitize_for_pdf(f" {b['name']}"), border=1, ln=0)
                        pdf.cell(40, 7, sanitize_for_pdf(f" {b['status']}"), border=1, ln=0)
                        pdf.cell(20, 7, f" {b['runs']}", border=1, ln=0, align="C")
                        pdf.cell(20, 7, f" {b['balls']}", border=1, ln=0, align="C")
                        pdf.cell(15, 7, f" {b['fours']}", border=1, ln=0, align="C")
                        pdf.cell(15, 7, f" {b['sixes']}", border=1, ln=1, align="C")
                        
                    pdf.ln(4)
                    
                    # Bowlers table
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 8, " Bowlers Performance Profile", ln=1)
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.set_fill_color(226, 232, 240)
                    pdf.cell(75, 7, " Bowler Name", border=1, ln=0, fill=True)
                    pdf.cell(30, 7, " Overs", border=1, ln=0, fill=True)
                    pdf.cell(30, 7, " Runs Conceded", border=1, ln=0, fill=True)
                    pdf.cell(30, 7, " Wickets", border=1, ln=0, fill=True)
                    pdf.cell(20, 7, " Maidens", border=1, ln=1, fill=True)
                    
                    pdf.set_font("Helvetica", "", 9)
                    all_bowl1 = list(d1["all_bowlers_history"])
                    if d1["bowler"]["name"] != "": all_bowl1.append(d1["bowler"])
                    
                    for blr in all_bowl1:
                        if blr["name"] == "": continue
                        b_ov_num = f"{blr['balls'] // 6}.{blr['balls'] % 6}"
                        pdf.cell(75, 7, sanitize_for_pdf(f" {blr['name']}"), border=1, ln=0)
                        pdf.cell(30, 7, f" {b_ov_num}", border=1, ln=0, align="C")
                        pdf.cell(30, 7, f" {blr['runs']}", border=1, ln=0, align="C")
                        pdf.cell(30, 7, f" {blr['wickets']}", border=1, ln=0, align="C")
                        pdf.cell(20, 7, f" {blr['maidens']}", border=1, ln=1, align="C")
                        
                    # Page for Innings 2 (if active or finished)
                    if m_instance["current_innings"] == 2 or m_instance["innings_2"]["balls"] > 0:
                        pdf.add_page()
                        pdf.set_font("Helvetica", "B", 12)
                        pdf.set_text_color(15, 23, 42)
                        pdf.set_fill_color(241, 245, 249)
                        
                        d2 = ensure_innings_keys(m_instance["innings_2"])
                        b_team_i2 = m_instance["team_2"]
                        f_team_i2 = m_instance["team_1"]
                        
                        pdf.cell(0, 10, sanitize_for_pdf(f" INNINGS 2: {b_team_i2.upper()} vs {f_team_i2.upper()}"), ln=1, fill=True)
                        pdf.ln(1)
                        
                        pdf.set_font("Helvetica", "", 10)
                        pdf.cell(95, 7, f"Total Innings Runs: {d2['runs']} / {d2['wickets']}", ln=0)
                        pdf.cell(95, 7, f"Overs Completed: {d2['balls'] // 6}.{d2['balls'] % 6} / {m_instance['total_overs']} Ov", ln=1)
                        pdf.cell(95, 7, f"Innings Extras: {d2['extras']}", ln=0)
                        pdf.cell(95, 7, f"Target Target Run Chase: {m_instance['innings_1']['runs'] + 1}", ln=1)
                        pdf.ln(4)
                        
                        # Batsmen Table 2
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(0, 8, " Batsman Performance Profile", ln=1)
                        pdf.set_font("Helvetica", "B", 9)
                        pdf.set_fill_color(226, 232, 240)
                        pdf.cell(75, 7, " Batsman Name", border=1, ln=0, fill=True)
                        pdf.cell(40, 7, " Dismissal", border=1, ln=0, fill=True)
                        pdf.cell(20, 7, " Runs", border=1, ln=0, fill=True)
                        pdf.cell(20, 7, " Balls", border=1, ln=0, fill=True)
                        pdf.cell(15, 7, " 4s", border=1, ln=0, fill=True)
                        pdf.cell(15, 7, " 6s", border=1, ln=1, fill=True)
                        
                        pdf.set_font("Helvetica", "", 9)
                        all_bat2 = list(d2["all_batsmen_history"])
                        if d2["b1"]["name"] != "": all_bat2.append(d2["b1"])
                        if d2["b2"]["name"] != "": all_bat2.append(d2["b2"])
                        
                        for b in all_bat2:
                            if b["name"] == "": continue
                            pdf.cell(75, 7, sanitize_for_pdf(f" {b['name']}"), border=1, ln=0)
                            pdf.cell(40, 7, sanitize_for_pdf(f" {b['status']}"), border=1, ln=0)
                            pdf.cell(20, 7, f" {b['runs']}", border=1, ln=0, align="C")
                            pdf.cell(20, 7, f" {b['balls']}", border=1, ln=0, align="C")
                            pdf.cell(15, 7, f" {b['fours']}", border=1, ln=0, align="C")
                            pdf.cell(15, 7, f" {b['sixes']}", border=1, ln=1, align="C")
                            
                        pdf.ln(4)
                        
                        # Bowlers Table 2
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(0, 8, " Bowlers Performance Profile", ln=1)
                        pdf.set_font("Helvetica", "B", 9)
                        pdf.set_fill_color(226, 232, 240)
                        pdf.cell(75, 7, " Bowler Name", border=1, ln=0, fill=True)
                        pdf.cell(30, 7, " Overs", border=1, ln=0, fill=True)
                        pdf.cell(30, 7, " Runs Conceded", border=1, ln=0, fill=True)
                        pdf.cell(30, 7, " Wickets", border=1, ln=0, fill=True)
                        pdf.cell(20, 7, " Maidens", border=1, ln=1, fill=True)
                        
                        pdf.set_font("Helvetica", "", 9)
                        all_bowl2 = list(d2["all_bowlers_history"])
                        if d2["bowler"]["name"] != "": all_bowl2.append(d2["bowler"])
                        
                        for blr in all_bowl2:
                            if blr["name"] == "": continue
                            b_ov_num = f"{blr['balls'] // 6}.{blr['balls'] % 6}"
                            pdf.cell(75, 7, sanitize_for_pdf(f" {blr['name']}"), border=1, ln=0)
                            pdf.cell(30, 7, f" {b_ov_num}", border=1, ln=0, align="C")
                            pdf.cell(30, 7, f" {blr['runs']}", border=1, ln=0, align="C")
                            pdf.cell(30, 7, f" {blr['wickets']}", border=1, ln=0, align="C")
                            pdf.cell(20, 7, f" {blr['maidens']}", border=1, ln=1, align="C")
                            
                    return get_pdf_bytes(pdf)

                st.write("")
                # Sandboxed pre-execution wrapper to ensure zero layout-crashing failures upon page-load rendering
                try:
                    pdf_data = generate_full_pdf_report()
                except Exception as e:
                    pdf_data = b""
                    st.error(f"Failed to pre-compile the PDF scorecard background buffer: {e}")

                if pdf_data:
                    st.download_button(
                        label="📥 Export Report as Comprehensive PDF", 
                        data=pdf_data, 
                        file_name=f"APL_Official_Scorecard_{db_global['active_match_id']}.pdf", 
                        mime="application/pdf", 
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ Scorecard PDF compilation holds active, or match state initialization is incomplete.")

# ================= TAB: HISTORICAL ARCHIVE MUTLI-MATCH AUDIT =================
with tab_review:
    st.markdown("### Match Archive Ledgers & Historical Review Audit Database")
    if not db_global["matches"]:
        st.caption("No historical logs recorded within active engine instances.")
    else:
        select_review_id = st.selectbox("Select Historical Match Profile Key to Audit:", list(db_global["matches"].keys()))
        m_rev = ensure_match_keys(db_global["matches"][select_review_id])
        
        st.markdown(f"## Record Verification Summary: {m_rev['id']}")
        st.info(f"Configuration Blueprint Frame Structure: **{m_rev['team_1']}** vs **{m_rev['team_2']}** | Target Parameter Limits: {m_rev['total_overs']} Overs")
        
        # Self-heal reviewed historical logs on loading
        d1 = m_rev["innings_1"]
        d2 = m_rev["innings_2"]
        
        # Display Match Winner / Outcome clearly
        match_outcome = get_match_result(m_rev)
        st.success(f"Outcome Summary: {match_outcome}")
        
        rev_i1, rev_i2 = st.tabs(["Innings #1 Complete Report Log", "Innings #2 Complete Report Log"])
        with rev_i1:
            st.metric(f"Total Innings 1 Score for {m_rev['team_1']}", f"{d1['runs']} - {d1['wickets']}", f"Overs: {d1['balls'] // 6}.{d1['balls'] % 6}")
            if d1["over_history"]: st.table(pd.DataFrame(d1["over_history"]))
            else: st.caption("No historical timelines stored.")
        with rev_i2:
            st.metric(f"Total Innings 2 Score for {m_rev['team_2']}", f"{d2['runs']} - {d2['wickets']}", f"Overs: {d2['balls'] // 6}.{d2['balls'] % 6}")
            if d2["over_history"]: st.table(pd.DataFrame(d2["over_history"]))
            else: st.caption("No historical timelines stored.")
