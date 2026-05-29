import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os

# Background auto-refresh integration
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st.error("Please ensure 'streamlit-autorefresh' is added to your requirements.txt file!")

# 1. Page Configuration
st.set_page_config(page_title="ANSCOR APL 2026", page_icon="🏏", layout="wide")

# Fixed the exact repository name spelling to pull directly from your GitHub repo
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Anscortournament/APL/main/"

# Static Team Database
TEAM_DB = {
    "Capital Chellengers": {
        "local": "CapitalChellengers.jpeg",
        "remote": GITHUB_RAW_BASE + "CapitalChellengers.jpeg",
        "squad": ["Amit (IT) - C", "Vikram (Fin)", "Rahul (HR)", "Suresh (Ops)", "Alok (Sales)", "Deepak (Mkt)", "Nitin (IT)", "Rohan (Legal)", "Sumit (Fin)", "Kapil (HR)", "Gaurav (Ops)"]
    },
    "Black panther": {
        "local": "Blackpanther.jpeg",
        "remote": GITHUB_RAW_BASE + "Blackpanther.jpeg",
        "squad": ["Karan (Sales) - C", "Arjun (IT)", "Vijay (Fin)", "Rajesh (Ops)", "Sanjay (HR)", "Anil (Mkt)", "Sunil (Legal)", "Manoj (Fin)", "Ravi (IT)", "Abhishek (Ops)", "Prakash (Sales)"]
    },
    "Super Kings": {
        "local": "SuperKings.jpeg",
        "remote": GITHUB_RAW_BASE + "SuperKings.jpeg",
        "squad": ["Mahesh (Mkt) - C", "Dinesh (Sales)", "Harish (IT)", "Naresh (Fin)", "Ramesh (Ops)", "Suresh (HR)", "Umesh (Legal)", "Ashok (Mkt)", "Vinod (IT)", "Lalit (Fin)", "Pradeep (Ops)"]
    },
    "Power Hitter": {
        "local": "PowerHitter.jpeg",
        "remote": GITHUB_RAW_BASE + "PowerHitter.jpeg",
        "squad": ["Rohit (Ops) - C", "Hardik (HR)", "Jasprit (IT)", "KL (Fin)", "Shikhar (Sales)", "Shreyas (Mkt)", "Yuzvendra (Legal)", "Bhuvneshwar (IT)", "Mohammed (Fin)", "Ravindra (Ops)", "Rishabh (HR)"]
    },
    "Royal Warriors XI": {
        "local": "RoyalWarriorsXI.jpeg",
        "remote": GITHUB_RAW_BASE + "RoyalWarriorsXI.jpeg",
        "squad": ["Virat (Fin) - C", "AB (IT)", "Chris (Sales)", "Glenn (Ops)", "Yuzvendra (HR)", "Mohammed (Mkt)", "Navdeep (Legal)", "Devdutt (IT)", "Washington (Fin)", "Shahbaz (Ops)", "Harshal (HR)"]
    },
    "UnStoppable": {
        "local": "UnStoppable.jpeg",
        "remote": GITHUB_RAW_BASE + "UnStoppable.jpeg",
        "squad": ["Shubman (HR) - C", "Rashid (IT)", "David (Fin)", "Kane (Ops)", "Wriddhiman (Sales)", "Rahul (Mkt)", "Vijay (Legal)", "Hardik (IT)", "Mohammed (Fin)", "Sai (Ops)", "Darshan (HR)"]
    }
}

# Tournament Main Logo Links
MAIN_LOGOS = {
    "local": "le.mat.jpeg",
    "remote": GITHUB_RAW_BASE + "le.mat.jpeg"
}

# Standardized reliable image loading function
def smart_load_image(local_path, remote_url, width=None, use_container=True):
    if os.path.exists(local_path):
        try:
            st.image(local_path, width=width, use_container_width=use_container)
            return True
        except Exception:
            pass
    try:
        st.image(remote_url, width=width, use_container_width=use_container)
        return True
    except Exception:
        pass
    return False

# Custom CSS Layout Overrides
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        max-width: 100% !important;
    }
    .score-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        color: white;
        padding: 20px 15px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 12px;
        border: 2px solid #1E40AF;
        position: relative;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .status-badge {
        position: absolute;
        top: 10px;
        right: 15px;
        background-color: #EF4444;
        color: white;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 900;
        letter-spacing: 1px;
    }
    .mobile-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        margin: 3px;
        font-weight: 800;
        font-size: 0.9rem;
    }
    h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #3B82F6 !important;
        font-size: 1.15rem !important;
        border-left: 3px solid #3B82F6;
        padding-left: 8px;
    }
    div.stButton > button {
        padding: 6px 12px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
    }
    .team-block-container {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .squad-container {
        background-color: #0F172A;
        border: 1px dashed #334155;
        border-radius: 8px;
        padding: 14px;
        margin-top: 10px;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# Shared Memory Application Cache Engine Setup
@st.cache_resource
def get_global_match_data():
    return {
        "lock": threading.Lock(),
        "match_started": False,
        "batting_team": "Capital Chellengers",
        "bowling_team": "Black panther",
        "total_overs": 4,
        "runs": 0,
        "wickets": 0,
        "balls": 0,
        "extras": 0,
        "this_over": [],
        "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [],
        "all_bowlers_history": [],
        "undo_stack": []
    }

global_data = get_global_match_data()
lock = global_data["lock"]

if 'show_wicket_popup' not in st.session_state: st.session_state.show_wicket_popup = False
if 'show_over_popup' not in st.session_state: st.session_state.show_over_popup = False
if 'active_team' not in st.session_state: st.session_state.active_team = None

# --- LIVE REFRESH HANDLER ---
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
    st_autorefresh(interval=3000, key="broadcast_sync_pulse")
    st.sidebar.caption("🟢 Live broadcast sync link active. Automatic UI refreshes every 3 seconds.")

# Visual Main Brand Banner Header Layout - Logo BEFORE the Name
banner_col1, banner_col2 = st.columns([0.15, 0.85])
with banner_col1:
    smart_load_image(MAIN_LOGOS["local"], MAIN_LOGOS["remote"], width=80, use_container=False)
with banner_col2:
    st.markdown(
        "<h2 style='color: #FFFFFF; font-size: 2.3rem; font-weight: 900; letter-spacing: 1px; margin-bottom: 0px; padding-top:4px;'>ANSCOR APL 2026</h2>"
        "<p style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 1px; margin-bottom: 15px;'>Corporate Tournament Broadcast Portal</p>",
        unsafe_allow_html=True
    )

def save_state_for_undo():
    state_snapshot = {
        "runs": global_data["runs"],
        "wickets": global_data["wickets"],
        "balls": global_data["balls"],
        "extras": global_data["extras"],
        "this_over": list(global_data["this_over"]),
        "over_history": copy.deepcopy(global_data["over_history"]),
        "b1": copy.deepcopy(global_data["b1"]),
        "b2": copy.deepcopy(global_data["b2"]),
        "bowler": copy.deepcopy(global_data["bowler"]),
        "all_batsmen_history": copy.deepcopy(global_data["all_batsmen_history"]),
        "all_bowlers_history": copy.deepcopy(global_data["all_bowlers_history"])
    }
    global_data["undo_stack"].append(state_snapshot)

# --- VIEW ASSIGNMENT: TABS FOR VIEWER MODE ---
if not is_admin:
    tab_live, tab_teams = st.tabs(["📺 Live Match Broadcast", "📋 Tournament Team Directory"])
else:
    tab_live = st.container()
    tab_teams = st.container()

# ================= TAB: TOURNAMENT SQUADS DIRECTORY =================
if not is_admin:
    with tab_teams:
        st.markdown("### 📋 Official Team Lists")
        st.caption("Select a team below to view their active player lineup roster.")
        
        teams_list = list(TEAM_DB.keys())
        
        # Grid placement logic to separate team card selections cleanly without locking the UI
        cols = st.columns(3)
        for idx, t_name in enumerate(teams_list):
            with cols[idx % 3]:
                st.markdown('<div class="team-block-container">', unsafe_allow_html=True)
                smart_load_image(TEAM_DB[t_name]["local"], TEAM_DB[t_name]["remote"], use_container=True)
                
                if st.button(f"View {t_name}", key=f"team_btn_{idx}", use_container_width=True):
                    st.session_state.active_team = None if st.session_state.active_team == t_name else t_name
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Dynamic output target panel to prevent list elements getting stuck
        if st.session_state.active_team and st.session_state.active_team in TEAM_DB:
            selected_team = st.session_state.active_team
            st.markdown(f'<div class="squad-container">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#3B82F6; margin:0 0 10px 0;'>📋 {selected_team} Squad Lineup</h3>", unsafe_allow_html=True)
            
            # Display squad players split into two columns for scannability
            sq_c1, sq_c2 = st.columns(2)
            squad_members = TEAM_DB[selected_team]["squad"]
            midpoint = (len(squad_members) + 1) // 2
            
            with sq_c1:
                for player in squad_members[:midpoint]:
                    st.markdown(f"<p style='color:#E2E8F0; margin:4px 0; font-size:1rem;'>• {player}</p>", unsafe_allow_html=True)
            with sq_c2:
                for player in squad_members[midpoint:]:
                    st.markdown(f"<p style='color:#E2E8F0; margin:4px 0; font-size:1rem;'>• {player}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")

# ================= TAB: LIVE SCORES ENGINE =================
with tab_live:
    # --- SETUP SCREEN VIEW ---
    if not global_data["match_started"]:
        if is_admin:
            st.markdown("### 🚀 Match Allocation Parameters")
            with st.form("setup_form"):
                col1, col2 = st.columns(2)
                with col1:
                    batting_team = st.selectbox("Batting Team Lineup", list(TEAM_DB.keys()), index=0)
                    batter1 = st.text_input("Striker Batsman", value="Amit (IT)")
                    bowler = st.text_input("Opening Bowler Profile", value="Vikram (Fin)")
                with col2:
                    bowling_team = st.selectbox("Bowling Team Lineup", list(TEAM_DB.keys()), index=1)
                    batter2 = st.text_input("Non-Striker Batsman", value="Rahul (HR)")
                    total_overs = st.number_input("Target Innings Overs", min_value=1, max_value=20, value=4)
                
                if st.form_submit_button("Launch Live Broadcast 🏁", use_container_width=True):
                    with lock:
                        global_data["match_started"] = True
                        global_data["batting_team"] = batting_team
                        global_data["bowling_team"] = bowling_team
                        global_data["total_overs"] = total_overs
                        global_data["runs"], global_data["wickets"], global_data["balls"], global_data["extras"] = 0, 0, 0, 0
                        global_data["this_over"], global_data["over_history"] = [], []
                        global_data["b1"] = {"name": batter1, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"}
                        global_data["b2"] = {"name": batter2, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"}
                        global_data["bowler"] = {"name": bowler, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                        global_data["all_batsmen_history"] = []
                        global_data["all_bowlers_history"] = []
                        global_data["undo_stack"] = []
                    st.rerun()
        else:
            st.warning("⏳ Waiting for the administration team to initialize the data systems. Standby...")

    # --- SCOREBOARD ACTIVE LIVE LOOP ---
    else:
        # Administration Fallback Modal Interfaces
        if st.session_state.show_wicket_popup and is_admin:
            st.markdown('<div class="popup-box">', unsafe_allow_html=True)
            st.error("☝️ WICKET FALLEN DETECTED")
            new_batter_name = st.text_input("Incoming Batsman Name:", value="")
            if st.button("Resume Match Activity 🏏", use_container_width=True):
                if not new_batter_name: new_batter_name = f"Batter {global_data['wickets'] + 1}"
                with lock:
                    save_state_for_undo()
                    if global_data["b1"]["strike"]:
                        global_data["b1"]["status"] = f"b {global_data['bowler']['name']}"
                        global_data["all_batsmen_history"].append(global_data["b1"].copy())
                        global_data["b1"] = {"name": new_batter_name, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"}
                    else:
                        global_data["b2"]["status"] = f"b {global_data['bowler']['name']}"
                        global_data["all_batsmen_history"].append(global_data["b2"].copy())
                        global_data["b2"] = {"name": new_batter_name, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"}
                st.session_state.show_wicket_popup = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.show_over_popup and is_admin:
            st.markdown('<div class="popup-box">', unsafe_allow_html=True)
            st.info("🔄 OVER SYSTEM MARGIN COMPLETE")
            new_bowler_name = st.text_input("Next Bowler Target Assignment:", value="")
            if st.button("Unlock Over Sequences 🥎", use_container_width=True):
                if not new_bowler_name: new_bowler_name = f"Bowler {len(global_data['all_bowlers_history']) + 1}"
                with lock:
                    save_state_for_undo()
                    existing_bowler = next((b for b in global_data["all_bowlers_history"] if b["name"] == global_data["bowler"]["name"]), None)
                    if existing_bowler:
                        existing_bowler["runs"] += global_data["bowler"]["runs"]
                        existing_bowler["wickets"] += global_data["bowler"]["wickets"]
                        existing_bowler["balls"] += global_data["bowler"]["balls"]
                        existing_bowler["maidens"] += global_data["bowler"]["maidens"]
                    else:
                        global_data["all_bowlers_history"].append(global_data["bowler"].copy())
                    global_data["bowler"] = {"name": new_bowler_name, "runs": 0, "wickets": 0, "balls": 0, "maidens": 0}
                st.session_state.show_over_popup = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Innings Calculators
        completed_overs = global_data["balls"] // 6
        rem_balls = global_data["balls"] % 6
        total_overs_frac = completed_overs + (rem_balls / 6)
        crr = (global_data["runs"] / total_overs_frac) if total_overs_frac > 0 else 0.0
        match_finished = (completed_overs >= global_data["total_overs"]) or (global_data["wickets"] >= 10)
        status_tag = "FINISHED" if match_finished else "LIVE"

        def switch_strike():
            global_data["b1"]["strike"] = not global_data["b1"]["strike"]
            global_data["b2"]["strike"] = not global_data["b2"]["strike"]
            global_data["b1"]["status"] = "On Strike" if global_data["b1"]["strike"] else "Not Out"
            global_data["b2"]["status"] = "On Strike" if global_data["b2"]["strike"] else "Not Out"

        def check_over_end():
            legal_balls = [b for b in global_data["this_over"] if b not in ['WD', 'NB']]
            if len(legal_balls) == 6:
                runs_in_over = sum([b for b in global_data["this_over"] if isinstance(b, int)])
                if runs_in_over == 0: global_data["bowler"]["maidens"] += 1
                global_data["over_history"].append({
                    "Over": len(global_data["over_history"]) + 1,
                    "Bowler": global_data["bowler"]["name"],
                    "Score": f"{global_data['runs']}/{global_data['wickets']}",
                    "Timeline": ", ".join(map(str, global_data["this_over"]))
                })
                st.session_state.show_over_popup = True

        # Layout Allocation Strategy
        left_col, right_col = st.columns([1.1, 0.9], gap="small")

        with left_col:
            # Match Banner Logo Injections
            logo_c1, logo_vs, logo_c2 = st.columns([1, 0.5, 1])
            with logo_c1:
                b_team = global_data["batting_team"]
                if b_team in TEAM_DB:
                    smart_load_image(TEAM_DB[b_team]["local"], TEAM_DB[b_team]["remote"], width=70, use_container=False)
            with logo_vs:
                st.markdown("<h4 style='text-align: center; margin-top: 15px; border: none; padding: 0; color:#64748B;'>VS</h4>", unsafe_allow_html=True)
            with logo_c2:
                f_team = global_data["bowling_team"]
                if f_team in TEAM_DB:
                    smart_load_image(TEAM_DB[f_team]["local"], TEAM_DB[f_team]["remote"], width=70, use_container=False)

            st.markdown(f"""
                <div class="score-box">
                    <span class="status-badge">{status_tag}</span>
                    <div style="font-weight: 800; font-size: 1.05rem; letter-spacing:0.5px; opacity: 0.9; margin-bottom: 4px;">
                        🏏 {global_data["batting_team"]} <span style="color:#60A5FA; font-weight:400; padding:0 4px;">vs</span> 🥎 {global_data["bowling_team"]}
                    </div>
                    <div style="font-size: 3.6rem; font-weight: 900; line-height: 1.1; margin: 4px 0; color: #FFFFFF;">{global_data["runs"]} - {global_data["wickets"]}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #93C5FD;">Overs: {completed_overs}.{rem_balls} / {global_data["total_overs"]}</div>
                    <div style="display: flex; justify-content: space-around; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.15); font-size: 0.85rem; font-weight: 600;">
                        <div>Extras: <b style="color:#F59E0B; font-size:0.95rem;">{global_data["extras"]}</b></div>
                        <div>Run Rate: <b style="color:#10B981; font-size:0.95rem;">{crr:.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Scorer Administration Actions Panel
            if is_admin:
                col_undo, col_swap = st.columns([1.2, 0.8])
                with col_undo:
                    if global_data["undo_stack"]:
                        if st.button("⚠️ Undo Last Ball", use_container_width=True):
                            with lock:
                                previous_state = global_data["undo_stack"].pop()
                                global_data["runs"] = previous_state["runs"]
                                global_data["wickets"] = previous_state["wickets"]
                                global_data["balls"] = previous_state["balls"]
                                global_data["extras"] = previous_state["extras"]
                                global_data["this_over"] = previous_state["this_over"]
                                global_data["over_history"] = previous_state["over_history"]
                                global_data["b1"] = previous_state["b1"]
                                global_data["b2"] = previous_state["b2"]
                                global_data["bowler"] = previous_state["bowler"]
                                global_data["all_batsmen_history"] = previous_state["all_batsmen_history"]
                                global_data["all_bowlers_history"] = previous_state["all_bowlers_history"]
                            st.rerun()
                    else:
                        st.button("Undo Disabled", disabled=True, use_container_width=True)
                with col_swap:
                    if st.button("🔄 Swap Strike", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            switch_strike()
                        st.rerun()

                if not match_finished and not st.session_state.show_wicket_popup and not st.session_state.show_over_popup:
                    st.markdown("#### 🎛️ Delivery Inputs")
                    striker = global_data["b1"] if global_data["b1"]["strike"] else global_data["b2"]
                    
                    r1, r2, r3, r4 = st.columns(4)
                    if r1.button("0 Runs", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["balls"] += 1; striker["balls"] += 1; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(0); check_over_end()
                        st.rerun()
                    if r2.button("1 Run", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 1; global_data["balls"] += 1; striker["runs"] += 1; striker["balls"] += 1
                            global_data["bowler"]["runs"] += 1; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(1); switch_strike(); check_over_end()
                        st.rerun()
                    if r3.button("2 Runs", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 2; global_data["balls"] += 1; striker["runs"] += 2; striker["balls"] += 1
                            global_data["bowler"]["runs"] += 2; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(2); check_over_end()
                        st.rerun()
                    if r4.button("3 Runs", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 3; global_data["balls"] += 1; striker["runs"] += 3; striker["balls"] += 1
                            global_data["bowler"]["runs"] += 3; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(3); switch_strike(); check_over_end()
                        st.rerun()

                    br1, br2, br3, br4 = st.columns(4)
                    if br1.button("🟢 4", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 4; global_data["balls"] += 1; striker["runs"] += 4; striker["balls"] += 1; striker["fours"] += 1
                            global_data["bowler"]["runs"] += 4; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(4); check_over_end()
                        st.rerun()
                    if br2.button("🟢 6", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 6; global_data["balls"] += 1; striker["runs"] += 6; striker["balls"] += 1; striker["sixes"] += 1
                            global_data["bowler"]["runs"] += 6; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append(6); check_over_end()
                        st.rerun()
                    if br3.button("🟡 WD", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 1; global_data["extras"] += 1; global_data["bowler"]["runs"] += 1
                            global_data["this_over"].append("WD")
                        st.rerun()
                    if br4.button("🟠 NB", use_container_width=True):
                        with lock:
                            save_state_for_undo()
                            global_data["runs"] += 1; global_data["extras"] += 1; global_data["bowler"]["runs"] += 1
                            global_data["this_over"].append("NB")
                        st.rerun()

                    st.markdown("#### ⚙️ Manual Custom Extras Adjustments")
                    with st.expander("Inject Manual Overthrow/Penalty Runs", expanded=False):
                        extra_type = st.selectbox("Select Extra Category:", ["Penalty Runs", "Leg Byes / Byes", "Overthrow Extras"])
                        manual_count = st.number_input("Enter exact total runs to add:", min_value=1, max_value=10, value=1, step=1)
                        ball_impact = st.radio("Consume a legal delivery count?", ["No", "Yes"])
                        
                        if st.button("Inject Manual Runs Into Scorecard ⚡", use_container_width=True):
                            with lock:
                                save_state_for_undo()
                                global_data["runs"] += manual_count
                                global_data["extras"] += manual_count
                                if extra_type == "Overthrow Extras":
                                    global_data["bowler"]["runs"] += manual_count
                                    
                                if ball_impact == "Yes":
                                    global_data["balls"] += 1
                                    global_data["bowler"]["balls"] += 1
                                    striker["balls"] += 1
                                    global_data["this_over"].append(f"+{manual_count}Ex")
                                    check_over_end()
                                else:
                                    global_data["this_over"].append(f"+{manual_count}M")
                            st.success("Successfully customized values updated.")
                            st.rerun()

                    st.write("")
                    if st.button("🔴 OUT / WICKET FALLEN", use_container_width=True, type="primary"):
                        with lock:
                            save_state_for_undo()
                            global_data["wickets"] += 1; global_data["balls"] += 1; striker["balls"] += 1
                            global_data["bowler"]["wickets"] += 1; global_data["bowler"]["balls"] += 1
                            global_data["this_over"].append("W")
                        if global_data["wickets"] >= 10:
                            with lock:
                                global_data["b1"]["status"] = "Innings Ended"
                                global_data["b2"]["status"] = "Innings Ended"
                            st.rerun()
                        else:
                            st.session_state.show_wicket_popup = True
                            st.rerun()

        with right_col:
            st.markdown("#### 📊 Active Player Metrics")
            st.markdown(f"""
                <div class="mobile-card">
                    <div style="font-size:0.8rem; color:#94A3B8; font-weight:bold; margin-bottom:4px;"> 🏏 BATTING PAIR</div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.95rem;">
                        <span><b>{"👉 " if global_data["b1"]["strike"] else ""}{global_data["b1"]["name"] if global_data["b1"]["name"] else "Batter 1"}</b></span>
                        <span><b>{global_data["b1"]["runs"]}</b> <span style="font-size:0.8rem; color:#A1A1AA;">({global_data["b1"]["balls"]})</span></span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.95rem;">
                        <span><b>{"👉 " if global_data["b2"]["strike"] else ""}{global_data["b2"]["name"] if global_data["b2"]["name"] else "Batter 2"}</b></span>
                        <span><b>{global_data["b2"]["runs"]}</b> <span style="font-size:0.8rem; color:#A1A1AA;">({global_data["b2"]["balls"]})</span></span>
                    </div>
                    <div style="margin-top:10px; font-size:0.8rem; color:#94A3B8; font-weight:bold; margin-bottom:2px;">🥎 ACTIVE BOWLER</div>
                    <div style="display:flex; justify-content:space-between; font-size:0.95rem;">
                        <span>👤 <b>{global_data["bowler"]["name"] if global_data["bowler"]["name"] else "Active Bowler"}</b></span>
                        <span>Wkts: <b style="color:#EF4444;">{global_data["bowler"]["wickets"]}</b> | Runs: <b>{global_data["bowler"]["runs"]}</b> <span style="font-size:0.8rem; color:#A1A1AA;">({global_data["bowler"]["balls"] // 6}.{global_data["bowler"]["balls"] % 6} Ov)</span></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 📍 Active Over Sequences")
            if not global_data["this_over"]: st.caption("Waiting for delivery...")
            else:
                b_html = "".join([f'<span class="ball-bubble" style="background-color:{"#10B981" if str(b) in ["4","6"] or "4" in str(b) or "6" in str(b) else ("#EF4444" if "W" in str(b) else "#475569")}; color:white;">{b}</span>' for b in global_data["this_over"]])
                st.markdown(b_html, unsafe_allow_html=True)

            st.markdown("#### 📋 Completed Overs Log")
            if global_data["over_history"]:
                st.dataframe(pd.DataFrame(global_data["over_history"]), use_container_width=True, hide_index=True, height=115)
            else: st.caption("No archived records.")

            # ================= REPORT GENERATION ENGINE =================
            def generate_full_pdf_report():
                all_batsmen = list(global_data["all_batsmen_history"])
                if global_data["b1"] not in all_batsmen: all_batsmen.append(global_data["b1"])
                if global_data["b2"] not in all_batsmen: all_batsmen.append(global_data["b2"])
                
                all_bowlers = list(global_data["all_bowlers_history"])
                active_b_match = next((b for b in all_bowlers if b["name"] == global_data["bowler"]["name"]), None)
                if active_b_match:
                    active_b_match["runs"] += global_data["bowler"]["runs"]
                    active_b_match["wickets"] += global_data["bowler"]["wickets"]
                    active_b_match["balls"] += global_data["bowler"]["balls"]
                    active_b_match["maidens"] += global_data["bowler"]["maidens"]
                else:
                    if global_data["bowler"]["balls"] > 0 or global_data["bowler"]["name"] != "":
                        all_bowlers.append(global_data["bowler"])

                pdf = FPDF()
                pdf.add_page()
                
                pdf.set_font("Helvetica", "B", 20)
                pdf.set_text_color(30, 58, 138)
                pdf.cell(0, 12, "ANSCOR APL 2026 OFFICIAL MATCH REPORT", ln=True, align="C")
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_text_color(100, 116, 139)
                pdf.cell(0, 6, "Official Corporate Live Tournament Scorecard Profile Summary", ln=True, align="C")
                pdf.ln(6)
                
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(15, 23, 42)
                pdf.set_fill_color(241, 245, 249)
                pdf.cell(0, 10, f" MATCH OVERVIEW: {global_data['batting_team'].upper()} vs {global_data['bowling_team'].upper()}", ln=True, fill=True)
                pdf.ln(1)
                
                pdf.set_font("Helvetica", "", 10)
                b_disp = f"{global_data['balls'] // 6}.{global_data['balls'] % 6}"
                pdf.cell(95, 7, f"Total Innings Runs: {global_data['runs']} / {global_data['wickets']}", ln=False)
                pdf.cell(95, 7, f"Overs Completed: {b_disp} / {global_data['total_overs']} Ov", ln=True)
                pdf.cell(95, 7, f"Innings Extras: {global_data['extras']}", ln=False)
                pdf.cell(95, 7, f"Net Run Rate (CRR): {crr:.2f}", ln=True)
                pdf.ln(4)
                
                # Batsmen Tables
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, f" BATSMAN METRICS PROFILE ({global_data['batting_team']})", ln=True, fill=True)
                pdf.ln(1)
                
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(226, 232, 240)
                pdf.cell(55, 7, " Batsman Name", border=1, ln=False, fill=True)
                pdf.cell(45, 7, " Mode of Dismissal", border=1, ln=False, fill=True)
                pdf.cell(18, 7, " Runs", border=1, ln=False, fill=True)
                pdf.cell(18, 7, " Balls", border=1, ln=False, fill=True)
                pdf.cell(14, 7, " 4s", border=1, ln=False, fill=True)
                pdf.cell(14, 7, " 6s", border=1, ln=False, fill=True)
                pdf.cell(16, 7, " SR", border=1, ln=True, fill=True)
                
                pdf.set_font("Helvetica", "", 9)
                for b in all_batsmen:
                    if b["name"] == "": continue
                    sr = (b["runs"] / b["balls"] * 100) if b["balls"] > 0 else 0.0
                    pdf.cell(55, 7, f" {b['name']}", border=1, ln=False)
                    pdf.cell(45, 7, f" {b['status']}", border=1, ln=False)
                    pdf.cell(18, 7, f" {b['runs']}", border=1, ln=False, align="C")
                    pdf.cell(18, 7, f" {b['balls']}", border=1, ln=False, align="C")
                    pdf.cell(14, 7, f" {b['fours']}", border=1, ln=False, align="C")
                    pdf.cell(14, 7, f" {b['sixes']}", border=1, ln=False, align="C")
                    pdf.cell(16, 7, f" {sr:.1f}", border=1, ln=True, align="C")
                pdf.ln(4)
                
                # Bowlers Table
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, f" BOWLER ANALYSIS LOGS ({global_data['bowling_team']})", ln=True, fill=True)
                pdf.ln(1)
                
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(226, 232, 240)
                pdf.cell(60, 7, " Bowler Target Name", border=1, ln=False, fill=True)
                pdf.cell(24, 7, " Overs", border=1, ln=False, fill=True)
                pdf.cell(24, 7, " Maidens", border=1, ln=False, fill=True)
                pdf.cell(28, 7, " Runs Conceded", border=1, ln=False, fill=True)
                pdf.cell(24, 7, " Wickets", border=1, ln=False, fill=True)
                pdf.cell(20, 7, " Economy", border=1, ln=True, fill=True)
                
                pdf.set_font("Helvetica", "", 9)
                for blr in all_bowlers:
                    if blr["name"] == "" or blr["name"] == "New Bowler": continue
                    b_ov_num = f"{blr['balls'] // 6}.{blr['balls'] % 6}"
                    ov_frac = (blr["balls"] / 6)
                    econ = (blr["runs"] / ov_frac) if ov_frac > 0 else 0.0
                    pdf.cell(60, 7, f" {blr['name']}", border=1, ln=False)
                    pdf.cell(24, 7, f" {b_ov_num}", border=1, ln=False, align="C")
                    pdf.cell(24, 7, f" {blr['maidens']}", border=1, ln=False, align="C")
                    pdf.cell(28, 7, f" {blr['runs']}", border=1, ln=False, align="C")
                    pdf.cell(24, 7, f" {blr['wickets']}", border=1, ln=False, align="C")
                    pdf.cell(20, 7, f" {econ:.2f}", border=1, ln=True, align="C")
                pdf.ln(4)
                
                # History Table
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, " INNINGS BALL-BY-BALL PROGRESSION MATRIX", ln=True, fill=True)
                pdf.ln(1)
                
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(226, 232, 240)
                pdf.cell(20, 7, " Over #", border=1, ln=False, fill=True)
                pdf.cell(45, 7, " Bowler Operating", border=1, ln=False, fill=True)
                pdf.cell(30, 7, " End Score", border=1, ln=False, fill=True)
                pdf.cell(85, 7, " Delivery Timeline Sequence Logs", border=1, ln=True, fill=True)
                
                pdf.set_font("Helvetica", "", 9)
                for ho in global_data["over_history"]:
                    pdf.cell(20, 7, f" Over {ho['Over']}", border=1, ln=False, align="C")
                    pdf.cell(45, 7, f" {ho['Bowler']}", border=1, ln=False)
                    pdf.cell(30, 7, f" {ho['Score']}", border=1, ln=False, align="C")
                    pdf.cell(85, 7, f" [ {ho['Timeline']} ]", border=1, ln=True)
                    
                return bytes(pdf.output())

            st.write("")
            st.download_button(
                label="📥 Export Report as Comprehensive PDF", 
                data=generate_full_pdf_report(), 
                file_name=f"APL_Official_Scorecard_{global_data['batting_team']}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )

        # Reset Engine
        if is_admin:
            st.markdown("---")
            if st.button("Reset Tournament Dashboard Application", type="secondary", use_container_width=True):
                with lock:
                    global_data["match_started"] = False
                    global_data["runs"], global_data["wickets"], global_data["balls"] = 0, 0, 0
                    global_data["this_over"], global_data["over_history"] = [], []
                    global_data["all_batsmen_history"], global_data["all_bowlers_history"] = [], []
                    global_data["undo_stack"] = []
                st.rerun()
