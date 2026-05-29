import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os

# 1. Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Please ensure 'streamlit-autorefresh' is added to your requirements.txt file!")

# 2. Page Configuration
st.set_page_config(page_title="ANSCOR APL 2026", page_icon="🏏", layout="wide")

# Raw GitHub repository base link
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

def smart_load_image(local_path, remote_url, width=None, use_container=True):
    if os.path.exists(local_path):
        try: st.image(local_path, width=width, use_container_width=use_container); return True
        except: pass
    try: st.image(remote_url, width=width, use_container_width=use_container); return True
    except: pass
    return False

# Custom CSS styling overrides
st.markdown("""
    <style>
    .block-container { padding: 0.5rem 0.75rem !important; max-width: 100% !important; }
    .score-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: white;
        padding: 20px 15px; border-radius: 14px; text-align: center; margin-bottom: 12px;
        border: 2px solid #1E40AF; position: relative; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .status-badge {
        position: absolute; top: 10px; right: 15px; background-color: #EF4444; color: white;
        padding: 3px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 900; letter-spacing: 1px;
    }
    .mobile-card { background-color: #1E293B; border: 1px solid #334155; padding: 14px; border-radius: 12px; margin-bottom: 12px; }
    .ball-bubble {
        display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px;
        border-radius: 50%; margin: 3px; font-weight: 800; font-size: 0.9rem;
    }
    .team-block-container { background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

def init_blank_innings():
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [], "all_bowlers_history": [], "undo_stack": []
    }

# Global Shared Cache Engine for Multiple Matches
@st.cache_resource
def get_tournament_database():
    return {
        "lock": threading.Lock(),
        "active_match_id": None,
        "matches": {}
    }

db_global = get_tournament_database()
lock = db_global["lock"]

# --- 1. POPUP WINDOW MODALS (NATIVE DIALOGS) ---
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

@st.dialog("☝️ Wicket Broken - Incoming Batsman Selector")
def show_wicket_dialog(match_id, inning_key, bat_team_name):
    st.warning("Select the incoming batsman to resume gameplay.")
    match_data = db_global["matches"][match_id][inning_key]
    
    used = [match_data["b1"]["name"], match_data["b2"]["name"]] + [b["name"] for b in match_data["all_batsmen_history"]]
    available = [p for p in TEAM_DB[bat_team_name]["squad"] if p not in used]
    if not available: available = TEAM_DB[bat_team_name]["squad"]
    
    next_batter = st.selectbox("Incoming Batter:", available)
    if st.button("Confirm Selection & Resume", use_container_width=True):
        with lock:
            if match_data["b1"]["strike"]:
                match_data["b1"]["status"] = f"b {match_data['bowler']['name']}"
                match_data["all_batsmen_history"].append(match_data["b1"].copy())
                match_data["b1"] = {"name": next_batter, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"}
            else:
                match_data["b2"]["status"] = f"b {match_data['bowler']['name']}"
                match_data["all_batsmen_history"].append(match_data["b2"].copy())
                match_data["b2"] = {"name": next_batter, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"}
        st.rerun()

@st.dialog("🔄 Over Complete - Next Bowler Rotation Selector")
def show_over_dialog(match_id, inning_key, bowl_team_name):
    st.success("The previous over has concluded successfully. Select the next bowler.")
    match_data = db_global["matches"][match_id][inning_key]
    
    next_bowler = st.selectbox("Select Next Bowler:", TEAM_DB[bowl_team_name]["squad"])
    if st.button("Rotate Bowler & Unlock Over", use_container_width=True):
        with lock:
            past_bowler = next((b for b in match_data["all_bowlers_history"] if b["name"] == match_data["bowler"]["name"]), None)
            if past_bowler:
                past_bowler["runs"] += match_data["bowler"]["runs"]
                past_bowler["wickets"] += match_data["bowler"]["wickets"]
                past_bowler["balls"] += match_data["bowler"]["balls"]
            else:
                if match_data["bowler"]["name"] != "":
                    match_data["all_bowlers_history"].append(match_data["bowler"].copy())
            match_data["bowler"] = {"name": next_bowler, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
        st.rerun()

# --- ACCESS INTERFACE SECURITY PORTAL ---
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

# Main Page Branding Layout Headers
banner_c1, banner_c2 = st.columns([0.15, 0.85])
with banner_c1: smart_load_image(MAIN_LOGOS["local"], MAIN_LOGOS["remote"], width=80, use_container=False)
with banner_c2:
    st.markdown("<h2 style='color: white; margin-bottom: 0px;'>ANSCOR APL 2026</h2><p style='color: #94A3B8; margin-top:0px;'>Corporate Tournament Broadcast Portal</p>", unsafe_allow_html=True)

# Main Navigation Hub Tabs Setup
tab_live, tab_review, tab_teams = st.tabs(["📺 Live Match Console", "🗄️ Tournament Match Review", "📋 Team Profiles"])

# ================= TAB 3: TEAM DIRECTORY PROFILE MODALS =================
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

# ================= TAB 1: LIVE MATRICES & 2-INNING ENGINE =================
with tab_live:
    if is_admin:
        with st.expander("🛠️ Match Allocation Parameters & Inning Control Hub", expanded=not bool(db_global["active_match_id"])):
            st.markdown("#### Initialize a Brand New Match Instance")
            with st.form("new_match_allocation_form"):
                new_m_id = st.text_input("Unique Match Identifier Name (e.g., Match_01, Semifinal_1):")
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
                    else:
                        st.error("Invalid configuration credentials. Ensure names are distinct.")

            if db_global["matches"]:
                st.markdown("---")
                st.markdown("#### Live Console Stream Focus Routing")
                selected_focus = st.selectbox("Switch Active Admin Console Focus Window:", list(db_global["matches"].keys()), index=list(db_global["matches"].keys()).index(db_global["active_match_id"]) if db_global["active_match_id"] else 0)
                if st.button("Apply Selected Focus Switch Stream"):
                    db_global["active_match_id"] = selected_focus
                    st.rerun()
                
                active_match = db_global["matches"][db_global["active_match_id"]]
                if active_match["current_innings"] == 1:
                    if st.button("🔄 Transition Match to Innings 2 (Begin Target Run Chase) ➡️", type="primary"):
                        with lock:
                            active_match["current_innings"] = 2
                        st.success("Match flipped over cleanly to Innings 2!")
                        st.rerun()

    # Scoreboard Execution Operations
    if not db_global["active_match_id"]:
        st.info("⏳ Waiting for the administration panel team to launch an active match ecosystem...")
    else:
        m_instance = db_global["matches"][db_global["active_match_id"]]
        inn_key = "innings_1" if m_instance["current_innings"] == 1 else "innings_2"
        inn_data = m_instance[inn_key]
        
        bat_team = m_instance["team_1"] if m_instance["current_innings"] == 1 else m_instance["team_2"]
        bowl_team = m_instance["team_2"] if m_instance["current_innings"] == 1 else m_instance["team_1"]
        
        # Calculate Chase Targets context variables dynamically
        target_score = (m_instance["innings_1"]["runs"] + 1) if m_instance["current_innings"] == 2 else None
        
        # Opening configuration form setup layer checks
        if inn_data["b1"]["name"] == "":
            if is_admin:
                st.warning(f"Configure active opening batting pair lineups for Innings #{m_instance['current_innings']}")
                with st.form(f"opening_lineup_setup_{inn_key}"):
                    p1 = st.selectbox("Striker Batsman", TEAM_DB[bat_team]["squad"], index=0)
                    p2 = st.selectbox("Non-Striker Batsman", TEAM_DB[bat_team]["squad"], index=1)
                    bw = st.selectbox("Opening Bowler Assignment", TEAM_DB[bowl_team]["squad"], index=0)
                    if st.form_submit_button("Activate Opening Rosters Lineups"):
                        with lock:
                            inn_data["b1"]["name"] = p1
                            inn_data["b2"]["name"] = p2
                            inn_data["bowler"]["name"] = bw
                        st.rerun()
            else:
                st.info(f"⏳ Waiting for the scorers to configure opening rosters line for Innings #{m_instance['current_innings']}")
        else:
            # Mathematical calculations runrate variables
            comp_ov = inn_data["balls"] // 6
            rem_bl = inn_data["balls"] % 6
            frac_ov = comp_ov + (rem_bl / 6)
            crr = (inn_data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            # Main Layout Panels Rendering Matrix
            l_col, r_col = st.columns([1.1, 0.9])
            with l_col:
                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">INN {m_instance['current_innings']}</span>
                        <h3>🏏 {bat_team} vs 🥎 {bowl_team}</h3>
                        <h1 style="font-size:4rem; margin:0;">{inn_data['runs']} - {inn_data['wickets']}</h1>
                        <h5>Overs: {comp_ov}.{rem_bl} / {m_instance['total_overs']}</h5>
                        {f'<h4 style="color:#F59E0B; background-color:rgba(0,0,0,0.2); padding:6px; border-radius:6px;">🎯 Run Chase Target: {target_score} (Needs {target_score - inn_data["runs"]} runs off {(m_instance["total_overs"]*6) - inn_data["balls"]} balls)</h4>' if target_score else ''}
                        <hr style="opacity:0.2; margin:10px 0;">
                        <div style="display:flex; justify-content:space-around; font-size:0.9rem;">
                            <div>Extras Context Base: <b>{inn_data['extras']}</b></div>
                            <div>Current Run Rate (CRR): <b>{crr:.2f}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if is_admin:
                    def submit_ball(runs_inc, extra_inc=0, is_legal=True, symbol=None):
                        with lock:
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
                                
                            # Check Over End logic hook bounds
                            legal_balls_in_over = [b for b in inn_data["this_over"] if b not in ['WD', 'NB']]
                            if len(legal_balls_in_over) == 6:
                                inn_data["over_history"].append({
                                    "Over": len(inn_data["over_history"]) + 1, "Bowler": inn_data["bowler"]["name"],
                                    "Score": f"{inn_data['runs']}/{inn_data['wickets']}", "Timeline": ", ".join(map(str, inn_data["this_over"]))
                                })
                                inn_data["this_over"] = []
                                show_over_dialog(db_global["active_match_id"], inn_key, bowl_team)

                    st.markdown("#### 🎛️ Delivery Controls Console Input Panel")
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
                    
                    if st.button("☝️ OUT / FALL OF WICKET DETECTED", type="primary", use_container_width=True):
                        with lock:
                            inn_data["wickets"] += 1
                            inn_data["balls"] += 1
                            inn_data["bowler"]["wickets"] += 1
                            inn_data["this_over"].append("W")
                        
                        if inn_data["wickets"] >= 10 or (inn_data["balls"] >= m_instance["total_overs"] * 6):
                            st.info("Innings limits completed fully.")
                        else:
                            show_wicket_dialog(db_global["active_match_id"], inn_key, bat_team)
                        st.rerun()

            with r_col:
                st.markdown("#### Live Active Metrics Performances")
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.8rem; color:#94A3B8;">🏏 BATTING SQUAD PARTNERSHIP</div>
                        <div>{"👉 " if inn_data['b1']['strike'] else ""}{inn_data['b1']['name']}: <b>{inn_data['b1']['runs']}</b> ({inn_data['b1']['balls']})</div>
                        <div>{"👉 " if inn_data['b2']['strike'] else ""}{inn_data['b2']['name']}: <b>{inn_data['b2']['runs']}</b> ({inn_data['b2']['balls']})</div>
                        <div style="margin-top:10px; font-size:0.8rem; color:#94A3B8;">🥎 CURRENT OPERATING BOWLER</div>
                        <div>👤 {inn_data['bowler']['name']} | Wickets: <b style="color:#EF4444;">{inn_data['bowler']['wickets']}</b> | Runs Conceded: <b>{inn_data['bowler']['runs']}</b></div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Live Active Over Delivery Timeline Trackers")
                if inn_data["this_over"]:
                    html_b = "".join([f'<span class="ball-bubble" style="background-color:{"#10B981" if str(b) in ["4","6"] else ("#EF4444" if "W" in str(b) else "#475569")}; color:white;">{b}</span>' for b in inn_data["this_over"]])
                    st.markdown(html_b, unsafe_allow_html=True)
                else: st.caption("Waiting for delivery run logs sequence details...")

# ================= TAB 2: HISTORICAL ARCHIVE MUTLI-MATCH AUDIT =================
with tab_review:
    st.markdown("### Match Archive Ledgers & Historical Review Audit Database")
    if not db_global["matches"]:
        st.caption("No older historical match profiles saved in current runtime sequence caches.")
    else:
        select_review_id = st.selectbox("Select Historical Match Profile Key to Audit:", list(db_global["matches"].keys()))
        m_rev = db_global["matches"][select_review_id]
        
        st.markdown(f"## Record Verification Summary: {m_rev['id']}")
        st.info(f"Match Blueprint Structure Configuration: **{m_rev['team_1']}** vs **{m_rev['team_2']}** | Length: {m_rev['total_overs']} Overs")
        
        rev_i1, rev_i2 = st.tabs(["Innings #1 Complete Report Log", "Innings #2 Complete Report Log"])
        with rev_i1:
            d1 = m_rev["innings_1"]
            st.metric(f"Total Innings 1 Score for {m_rev['team_1']}", f"{d1['runs']} - {d1['wickets']}", f"Overs: {d1['balls'] // 6}.{d1['balls'] % 6}")
            if d1["over_history"]: st.table(pd.DataFrame(d1["over_history"]))
            else: st.caption("No completed over timeline histories saved for Innings 1.")
        with rev_i2:
            d2 = m_rev["innings_2"]
            st.metric(f"Total Innings 2 Score for {m_rev['team_2']}", f"{d2['runs']} - {d2['wickets']}", f"Overs: {d2['balls'] // 6}.{d2['balls'] % 6}")
            if d2["over_history"]: st.table(pd.DataFrame(d2["over_history"]))
            else: st.caption("No completed over timeline histories saved for Innings 2.")
