import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading
import copy
import os

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

def smart_load_image(local_path, remote_url, width=None, use_container=True):
    if os.path.exists(local_path):
        try: st.image(local_path, width=width, use_container_width=use_container); return True
        except: pass
    try: st.image(remote_url, width=width, use_container_width=use_container); return True
    except: pass
    return False

# Custom CSS
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

# Helper function template for empty innings structures
def create_empty_innings_struct():
    return {
        "runs": 0, "wickets": 0, "balls": 0, "extras": 0,
        "this_over": [], "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"},
        "b2": {"name": "", "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0, "maidens": 0},
        "all_batsmen_history": [], "all_bowlers_history": [], "undo_stack": []
    }

# 🛠️ CACHE ENGINE UPDATE: Holds history of multiple matches
@st.cache_resource
def get_global_tournament_database():
    return {
        "lock": threading.Lock(),
        "active_match_id": None,
        "matches": {}  # Key: Match ID string -> Value: Complete Match State
    }

db_global = get_global_tournament_database()
lock = db_global["lock"]

# --- 1. POPUP WINDOW COMPONENT FOR TEAM ROSTERS ---
@st.dialog("📋 Official Squad Lineup")
def show_squad_popup(team_name):
    st.markdown(f"### {team_name}")
    st.write("---")
    squad_members = TEAM_DB[team_name]["squad"]
    cols = st.columns(2)
    mid = (len(squad_members) + 1) // 2
    with cols[0]:
        for p in squad_members[:mid]: st.markdown(f"• {p}")
    with cols[1]:
        for p in squad_members[mid:]: st.markdown(f"• {p}")

# --- SYSTEM ACCESS CONTROLS ---
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
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="broadcast_pulse")

# Main Header Banner
banner_c1, banner_c2 = st.columns([0.15, 0.85])
with banner_c1: smart_load_image(MAIN_LOGOS["local"], MAIN_LOGOS["remote"], width=80, use_container=False)
with banner_c2:
    st.markdown("<h2 style='color: white; margin-bottom: 0px;'>ANSCOR APL 2026</h2><p style='color: #94A3B8; margin-top:0px;'>Corporate Tournament Broadcast Portal</p>", unsafe_allow_html=True)

# Main Application Navigation Routing Tabs
tab_live, tab_review, tab_teams = st.tabs(["📺 Live Match Console", "🗄️ Historical Match Review", "📋 Team Profiles"])

# ================= TAB: TEAM DIRECTORY (POPUP MODE) =================
with tab_teams:
    st.markdown("### Tournament Roster Directory")
    t_cols = st.columns(3)
    for idx, t_name in enumerate(TEAM_DB.keys()):
        with t_cols[idx % 3]:
            st.markdown('<div class="team-block-container">', unsafe_allow_html=True)
            smart_load_image(TEAM_DB[t_name]["local"], TEAM_DB[t_name]["remote"], use_container=True)
            if st.button(f"View Squad", key=f"popup_btn_{idx}", use_container_width=True):
                show_squad_popup(t_name)
            st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB: LIVE SCORES ENGINE (2-INNINGS MATCH ALLOCATION) =================
with tab_live:
    # 1. Admin Allocation Panel
    if is_admin:
        with st.expander("🛠️ Match Allocation & Inning Management", expanded=not bool(db_global["active_match_id"])):
            st.markdown("### Setup / Select Active Match Instance")
            
            # Allow creation of a brand new match profile
            with st.form("new_match_form"):
                st.markdown("**Create a New Match Sequence**")
                m_id = st.text_input("Unique Match Identifier ID (e.g., Match_01, Final_Game)")
                bat_team = st.selectbox("Innings 1 Batting Team", list(TEAM_DB.keys()))
                bowl_team = st.selectbox("Innings 1 Bowling Team", list(TEAM_DB.keys()))
                t_overs = st.number_input("Target Match Overs", min_value=1, max_value=20, value=4)
                
                if st.form_submit_button("Initialize Match Ecosystem 🏁"):
                    if m_id and bat_team != bowl_team:
                        with lock:
                            db_global["matches"][m_id] = {
                                "id": m_id, "batting_team_i1": bat_team, "bowling_team_i1": bowl_team,
                                "total_overs": t_overs, "current_innings": 1, "match_complete": False,
                                "innings_1": create_empty_innings_struct(),
                                "innings_2": create_empty_innings_struct()
                            }
                            db_global["active_match_id"] = m_id
                        st.success(f"Ecosystem {m_id} Ready!")
                        st.rerun()
                    else:
                        st.error("Invalid Configuration Parameters.")

            # Selection / Inning flip overrides
            if db_global["matches"]:
                st.markdown("---")
                st.markdown("**Ecosystem Status Toggles**")
                selected_active = st.selectbox("Change Active Control Console Focus:", list(db_global["matches"].keys()), index=list(db_global["matches"].keys()).index(db_global["active_match_id"]) if db_global["active_match_id"] else 0)
                
                if st.button("Set Selected Match as Active Focal Stream"):
                    db_global["active_match_id"] = selected_active
                    st.rerun()
                    
                cur_m = db_global["matches"].get(db_global["active_match_id"])
                if cur_m and cur_m["current_innings"] == 1:
                    if st.button("🔄 Flip Innings manually (Innings 1 ➡️ Innings 2 Chase)", type="primary"):
                        with lock:
                            cur_m["current_innings"] = 2
                        st.success("Flipped to 2nd Innings Target Chase Sequence!")
                        st.rerun()

    # Execution Loop For Active Live Stream
    if not db_global["active_match_id"]:
        st.info("⏳ Waiting for active match initialization across deployment layers...")
    else:
        match = db_global["matches"][db_global["active_match_id"]]
        inn_idx = "innings_1" if match["current_innings"] == 1 else "innings_2"
        data = match[inn_idx]
        
        # Calculate context variables dynamically
        bat_team_name = match["batting_team_i1"] if match["current_innings"] == 1 else match["bowling_team_i1"]
        bowl_team_name = match["bowling_team_i1"] if match["current_innings"] == 1 else match["batting_team_i1"]
        
        # Target evaluation for run chase tracking
        target_score = None
        if match["current_innings"] == 2:
            target_score = match["innings_1"]["runs"] + 1

        # Setup inside innings validation if parameters are blank
        if data["b1"]["name"] == "" and is_admin:
            st.warning(f"Configure active opening rosters for Innings {match['current_innings']}")
            with st.form(f"roster_form_{inn_idx}"):
                b1_sel = st.selectbox("Striker Batsman", TEAM_DB[bat_team_name]["squad"], index=0)
                b2_sel = st.selectbox("Non-Striker Batsman", TEAM_DB[bat_team_name]["squad"], index=1)
                bw_sel = st.selectbox("Opening Bowler Profile", TEAM_DB[bowl_team_name]["squad"], index=0)
                if st.form_submit_button("Activate Roster Lineup"):
                    with lock:
                        data["b1"]["name"] = b1_sel
                        data["b2"]["name"] = b2_sel
                        data["bowler"]["name"] = bw_sel
                    st.rerun()
        
        elif data["b1"]["name"] != "":
            # Run calculations
            comp_ov = data["balls"] // 6
            rem_bl = data["balls"] % 6
            frac_ov = comp_ov + (rem_bl / 6)
            crr = (data["runs"] / frac_ov) if frac_ov > 0 else 0.0
            
            # Wicket / Over change logic hooks
            if getattr(st.session_state, 'show_w_pop', False) and is_admin:
                used = [data["b1"]["name"], data["b2"]["name"]] + [b["name"] for b in data["all_batsmen_history"]]
                avail = [p for p in TEAM_DB[bat_team_name]["squad"] if p not in used]
                nb = st.selectbox("Incoming Batsman:", avail if avail else TEAM_DB[bat_team_name]["squad"])
                if st.button("Resume Play"):
                    with lock:
                        if data["b1"]["strike"]:
                            data["b1"]["status"] = f"b {data['bowler']['name']}"
                            data["all_batsmen_history"].append(data["b1"].copy())
                            data["b1"] = {"name": nb, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": True, "status": "On Strike"}
                        else:
                            data["b2"]["status"] = f"b {data['bowler']['name']}"
                            data["all_batsmen_history"].append(data["b2"].copy())
                            data["b2"] = {"name": nb, "runs": 0, "balls": 0, "fours": 0, "sixes": 0, "strike": False, "status": "Not Out"}
                    st.session_state.show_w_pop = False
                    st.rerun()
                    
            # Scoring UI Elements Rendering
            l_col, r_col = st.columns([1.1, 0.9])
            with l_col:
                st.markdown(f"""
                    <div class="score-box">
                        <span class="status-badge">INN {match['current_innings']}</span>
                        <h3>🏏 {bat_team_name} vs 🥎 {bowl_team_name}</h3>
                        <h1 style="font-size:4rem; margin:0;">{data['runs']} - {data['wickets']}</h1>
                        <h5>Overs: {comp_ov}.{rem_bl} / {match['total_overs']}</h5>
                        {f'<h4 style="color:#F59E0B; border:none;">🎯 Target Run Chase: {target_score} (Needs {target_score - data["runs"]} runs off {(match["total_overs"]*6) - data["balls"]} balls)</h4>' if target_score else ''}
                        <hr style="opacity:0.2; margin:10px 0;">
                        <div style="display:flex; justify-content:space-around; font-size:0.9rem;">
                            <div>Extras: <b>{data['extras']}</b></div>
                            <div>Run Rate: <b>{crr:.2f}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Input controls for admin dashboard interface
                if is_admin and not match["match_complete"]:
                    def register_ball(runs_inc, extra_inc=0, is_legal=True, outcome_tag=None):
                        with lock:
                            # Basic backup snapshot tracking logic
                            state_snap = copy.deepcopy({k: data[k] for k in ["runs", "wickets", "balls", "extras", "this_over"]})
                            data["undo_stack"].append(state_snap)
                            
                            striker = data["b1"] if data["b1"]["strike"] else data["b2"]
                            data["runs"] += runs_inc
                            data["extras"] += extra_inc
                            data["bowler"]["runs"] += runs_inc
                            
                            if is_legal:
                                data["balls"] += 1
                                data["bowler"]["balls"] += 1
                                striker["balls"] += 1
                                striker["runs"] += (runs_inc - extra_inc)
                                if outcome_tag is not None: data["this_over"].append(outcome_tag)
                                else: data["this_over"].append(runs_inc)
                            else:
                                data["this_over"].append(outcome_tag)
                                
                            # Odd runs change striker mechanics
                            if is_legal and (runs_inc % 2 != 0):
                                data["b1"]["strike"] = not data["b1"]["strike"]
                                data["b2"]["strike"] = not data["b2"]["strike"]

                            # Evaluate Over limits
                            legal_balls_over = [b for b in data["this_over"] if b not in ['WD', 'NB']]
                            if len(legal_balls_over) == 6:
                                data["over_history"].append({
                                    "Over": len(data["over_history"]) + 1, "Bowler": data["bowler"]["name"],
                                    "Score": f"{data['runs']}/{data['wickets']}", "Timeline": ", ".join(map(str, data["this_over"]))
                                })
                                data["this_over"] = []
                                # Automatically prompt bowler rotation changes
                                st.session_state.show_o_pop = True

                    # Input Button Layout Configuration matrix
                    st.markdown("#### 🎛️ Scorer Controls Input Panel")
                    b_c1, b_c2, b_c3, b_c4 = st.columns(4)
                    if b_c1.button("0 Runs"): register_ball(0, 0, True)
                    if b_c2.button("1 Run"): register_ball(1, 0, True)
                    if b_c3.button("2 Runs"): register_ball(2, 0, True)
                    if b_c4.button("3 Runs"): register_ball(3, 0, True)
                    
                    b_br1, b_br2, b_br3, b_br4 = st.columns(4)
                    if b_br1.button("🟢 4"): register_ball(4, 0, True); data["b1" if data["b1"]["strike"] else "b2"]["fours"] += 1
                    if b_br2.button("🟢 6"): register_ball(6, 0, True); data["b1" if data["b1"]["strike"] else "b2"]["sixes"] += 1
                    if b_br3.button("🟡 WD"): register_ball(1, 1, False, "WD")
                    if b_br4.button("🟠 NB"): register_ball(1, 1, False, "NB")
                    
                    if st.button("☝️ OUT / WICKET FALLEN", type="primary", use_container_width=True):
                        with lock:
                            data["wickets"] += 1
                            data["balls"] += 1
                            data["bowler"]["wickets"] += 1
                            data["this_over"].append("W")
                        if data["wickets"] >= 10 or (data["balls"] >= match["total_overs"] * 6):
                            st.info("Innings complete limit bounds reached.")
                        else:
                            st.session_state.show_w_pop = True
                        st.rerun()

            with r_col:
                st.markdown("#### Active Metrics Performance Matrix")
                st.markdown(f"""
                    <div class="mobile-card">
                        <div style="font-size:0.8rem; color:#94A3B8;">🏏 BATTING PAIR</div>
                        <div>{"👉 " if data['b1']['strike'] else ""}{data['b1']['name']}: <b>{data['b1']['runs']}</b> ({data['b1']['balls']})</div>
                        <div>{"👉 " if data['b2']['strike'] else ""}{data['b2']['name']}: <b>{data['b2']['runs']}</b> ({data['b2']['balls']})</div>
                        <div style="margin-top:10px; font-size:0.8rem; color:#94A3B8;">🥎 ACTIVE BOWLER</div>
                        <div>👤 {data['bowler']['name']} | Wkts: <b style="color:#EF4444;">{data['bowler']['wickets']}</b> | Runs: <b>{data['bowler']['runs']}</b></div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Active Over Timeline Logs")
                if data["this_over"]:
                    b_html = "".join([f'<span class="ball-bubble" style="background-color:{"#10B981" if str(b) in ["4","6"] else ("#EF4444" if "W" in str(b) else "#475569")}; color:white;">{b}</span>' for b in data["this_over"]])
                    st.markdown(b_html, unsafe_allow_html=True)
                else: st.caption("Waiting for deployment delivery details...")

# ================= TAB: HISTORICAL AUDIT LOG REVIEW =================
with tab_review:
    st.markdown("### Match Archive & Historical Review Ledger Database")
    if not db_global["matches"]:
        st.caption("No historical records currently archived.")
    else:
        select_review_id = st.selectbox("Select Historical Match Profile Record to Review:", list(db_global["matches"].keys()))
        m_rev = db_global["matches"][select_review_id]
        
        st.markdown(f"## Record Profile Verification: {m_rev['id']}")
        st.info(f"Configuration Layout: {m_rev['batting_team_i1']} vs {m_rev['bowling_team_i1']} | Target Setting Context Profile Length: {m_rev['total_overs']} Overs")
        
        rev_i1, rev_i2 = st.tabs(["Innings 1 Complete Profile", "Innings 2 Complete Profile"])
        with rev_i1:
            d1 = m_rev["innings_1"]
            st.metric(f"Total Innings 1 Score for {m_rev['batting_team_i1']}", f"{d1['runs']} - {d1['wickets']}", f"Overs: {d1['balls'] // 6}.{d1['balls'] % 6}")
            if d1["over_history"]: st.table(pd.DataFrame(d1["over_history"]))
        with rev_i2:
            d2 = m_rev["innings_2"]
            st.metric(f"Total Innings 2 Score for {m_rev['bowling_team_i1']}", f"{d2['runs']} - {d2['wickets']}", f"Overs: {d2['balls'] // 6}.{d2['balls'] % 6}")
            if d2["over_history"]: st.table(pd.DataFrame(d2["over_history"]))
