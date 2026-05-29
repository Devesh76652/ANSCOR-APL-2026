import streamlit as st
import pandas as pd
from fpdf import FPDF
import threading

# 1. Page Configuration
st.set_page_config(page_title="ANSCOR APL 2026", page_icon="🏏", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 95% !important;
    }
    .score-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        color: white;
        padding: 18px 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #1E40AF;
        position: relative;
    }
    .status-badge {
        position: absolute;
        top: 12px;
        right: 20px;
        background-color: #EF4444;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .ball-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin: 2px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    div.stButton > button {
        padding: 8px 4px !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
    }
    .popup-box {
        background-color: #1E293B;
        border: 2px solid #3B82F6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Main Dashboard Header Title Banner
st.markdown(
    "<h1 style='text-align: center; color: #FFFFFF; font-size: 2.5rem; font-weight: 800; letter-spacing: 2px; margin-bottom: 0px;'>🏏🏏 ANSCOR APL 2026 🏏🏏</h1>"
    "<p style='text-align: center; color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin-top: 2px;'>Official Corporate Live Scoring Dashboard</p>",
    unsafe_allow_html=True
)

# ================= CRITICAL FIX: GLOBAL DATA SYNC REGISTRY =================
# We use a memory cache with a thread lock to share data across all corporate connections safely
@st.cache_resource
def get_global_match_data():
    return {
        "lock": threading.Lock(),
        "match_started": False,
        "batting_team": "",
        "bowling_team": "",
        "total_overs": 4,
        "runs": 0,
        "wickets": 0,
        "balls": 0,
        "extras": 0,
        "this_over": [],
        "over_history": [],
        "b1": {"name": "", "runs": 0, "balls": 0, "strike": True},
        "b2": {"name": "", "runs": 0, "balls": 0, "strike": False},
        "bowler": {"name": "", "runs": 0, "wickets": 0, "balls": 0}
    }

global_data = get_global_match_data()
lock = global_data["lock"]

# Initialize local interface states (Modals remain local so they don't pop up on viewer screens)
if 'show_wicket_popup' not in st.session_state: st.session_state.show_wicket_popup = False
if 'show_over_popup' not in st.session_state: st.session_state.show_over_popup = False

# --- ROLE SELECTION SIDEBAR ---
st.sidebar.markdown("## 🔑 Access Portal")

# Auto-Refresh Toggle for Viewers so they get live scores automatically
st.sidebar.markdown("### 🔄 Live Feed")
if st.sidebar.button("Refresh Scoreboard ⚡", use_container_width=True):
    st.rerun()

user_role = st.sidebar.radio("Select Your Role:", ["📢 Player / Viewer (Read-Only)", "⚡ Match Scorer (Admin)"])

is_admin = False
if user_role == "⚡ Match Scorer (Admin)":
    password = st.sidebar.text_input("Enter Admin Password:", type="password")
    if password == "anscor2026":
        is_admin = True
        st.sidebar.success("Admin Access Granted!")
    elif password != "":
        st.sidebar.error("Incorrect Password")

# --- INITIAL MATCH CONFIGURATION (ADMIN ONLY) ---
if not global_data["match_started"]:
    if is_admin:
        st.markdown("### 🚀 Initialize Tournament Match")
        with st.form("setup_form"):
            col1, col2 = st.columns(2)
            with col1:
                batting_team = st.text_input("Batting Team", value="Tech Titans")
                batter1 = st.text_input("Batter 1 (On Strike)", value="Amit (IT)")
                bowler = st.text_input("Opening Bowler", value="Vikram (Fin)")
            with col2:
                bowling_team = st.text_input("Bowling Team", value="Finance Furies")
                batter2 = st.text_input("Batter 2 (Off Strike)", value="Rahul (HR)")
                total_overs = st.number_input("Total Match Overs", min_value=1, max_value=20, value=4)
            
            if st.form_submit_button("Start Live Match 🏁", use_container_width=True):
                with lock:
                    global_data["match_started"] = True
                    global_data["batting_team"] = batting_team
                    global_data["bowling_team"] = bowling_team
                    global_data["total_overs"] = total_overs
                    global_data["runs"], global_data["wickets"], global_data["balls"], global_data["extras"] = 0, 0, 0, 0
                    global_data["this_over"], global_data["over_history"] = [], []
                    global_data["b1"] = {"name": batter1, "runs": 0, "balls": 0, "strike": True}
                    global_data["b2"] = {"name": batter2, "runs": 0, "balls": 0, "strike": False}
                    global_data["bowler"] = {"name": bowler, "runs": 0, "wickets": 0, "balls": 0}
                st.rerun()
    else:
        st.warning("👋 Welcome! The match has not been started yet by the scoring team. Please wait for the admin to configure the teams.")

# --- CORE SYNCED DASHBOARD SCREEN ---
else:
    # Handle Modals/Pop-ups (Admin Side Only)
    if st.session_state.show_wicket_popup and is_admin:
        st.markdown('<div class="popup-box">', unsafe_allow_html=True)
        st.error("☝️ WICKET FALLEN!")
        new_batter_name = st.text_input("Enter Incoming Batsman Name:", value="")
        if st.button("Confirm New Batsman & Resume 🏏", use_container_width=True):
            if not new_batter_name:
                new_batter_name = f"Batter {global_data['wickets'] + 1}"
            with lock:
                if global_data["b1"]["strike"]:
                    global_data["b1"] = {"name": new_batter_name, "runs": 0, "balls": 0, "strike": True}
                else:
                    global_data["b2"] = {"name": new_batter_name, "runs": 0, "balls": 0, "strike": True}
            st.session_state.show_wicket_popup = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_over_popup and is_admin:
        st.markdown('<div class="popup-box">', unsafe_allow_html=True)
        st.info("🔄 OVER COMPLETE!")
        new_bowler_name = st.text_input("Enter Next Bowler Name:", value="")
        if st.button("Confirm Next Bowler & Resume 🥎", use_container_width=True):
            if not new_bowler_name:
                new_bowler_name = "New Bowler"
            with lock:
                global_data["bowler"] = {"name": new_bowler_name, "runs": 0, "wickets": 0, "balls": 0}
            st.session_state.show_over_popup = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Core Calculations Engine mapped directly to shared global cache registry
    completed_overs = global_data["balls"] // 6
    rem_balls = global_data["balls"] % 6
    total_overs_frac = completed_overs + (rem_balls / 6)
    crr = (global_data["runs"] / total_overs_frac) if total_overs_frac > 0 else 0.0
    match_finished = (completed_overs >= global_data["total_overs"]) or (global_data["wickets"] >= 10)
    status_tag = "FINISHED" if match_finished else "LIVE"

    def switch_strike():
        global_data["b1"]["strike"] = not global_data["b1"]["strike"]
        global_data["b2"]["strike"] = not global_data["b2"]["strike"]

    def check_over_end():
        legal_balls = len([b for b in global_data["this_over"] if b not in ['WD', 'NB']])
        if legal_balls == 6:
            global_data["over_history"].append({
                "Over": len(global_data["over_history"]) + 1,
                "Bowler": global_data["bowler"]["name"],
                "Score": f"{global_data['runs']}/{global_data['wickets']}",
                "Timeline": ", ".join(map(str, global_data["this_over"]))
            })
            global_data["this_over"] = []
            switch_strike()
            st.session_state.show_over_popup = True

    # Main Grid Layout Allocation
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    # ================= LEFT PANEL =================
    with left_col:
        # Score Board Banner
        st.markdown(f"""
            <div class="score-box">
                <span class="status-badge">{status_tag}</span>
                <div style="display:flex; justify-content:flex-start; opacity:0.8; font-size:0.9rem; font-weight:bold; margin-bottom:5px;">
                    <b>🏏 {global_data["batting_team"]}</b> <span style='margin: 0 8px;'>vs</span> 🥎 {global_data["bowling_team"]}
                </div>
                <div style="font-size: 3.8rem; font-weight: 900; margin: 2px 0;">{global_data["runs"]} - {global_data["wickets"]}</div>
                <div style="font-size: 1.1rem; opacity:0.95;">Overs: <b>{completed_overs}.{rem_balls}</b> / {global_data["total_overs"]}</div>
                <div style="display:flex; justify-content:space-around; margin-top:12px; font-size:0.9rem; border-top:1px solid rgba(255,255,255,0.15); padding-top:8px;">
                    <span>Extras: <b>{global_data["extras"]}</b></span>
                    <span>Run Rate: <b>{crr:.2f}</b></span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Control Panel - ONLY ACCESSIBLE IF VERIFIED ADMIN
        if is_admin:
            if not match_finished and not st.session_state.show_wicket_popup and not st.session_state.show_over_popup:
                st.markdown("#### 🎛️ Input Runs & Events")
                striker = global_data["b1"] if global_data["b1"]["strike"] else global_data["b2"]
                
                r1, r2, r3, r4 = st.columns(4)
                if r1.button("0 Runs", use_container_width=True):
                    with lock:
                        global_data["balls"] += 1; striker["balls"] += 1; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(0); check_over_end()
                    st.rerun()
                if r2.button("1 Run", use_container_width=True):
                    with lock:
                        global_data["runs"] += 1; global_data["balls"] += 1; striker["runs"] += 1; striker["balls"] += 1
                        global_data["bowler"]["runs"] += 1; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(1); switch_strike(); check_over_end()
                    st.rerun()
                if r3.button("2 Runs", use_container_width=True):
                    with lock:
                        global_data["runs"] += 2; global_data["balls"] += 1; striker["runs"] += 2; striker["balls"] += 1
                        global_data["bowler"]["runs"] += 2; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(2); check_over_end()
                    st.rerun()
                if r4.button("3 Runs", use_container_width=True):
                    with lock:
                        global_data["runs"] += 3; global_data["balls"] += 1; striker["runs"] += 3; striker["balls"] += 1
                        global_data["bowler"]["runs"] += 3; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(3); switch_strike(); check_over_end()
                    st.rerun()

                br1, br2, br3, br4 = st.columns(4)
                if br1.button("🟢 4", use_container_width=True):
                    with lock:
                        global_data["runs"] += 4; global_data["balls"] += 1; striker["runs"] += 4; striker["balls"] += 1
                        global_data["bowler"]["runs"] += 4; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(4); check_over_end()
                    st.rerun()
                if br2.button("🟢 6", use_container_width=True):
                    with lock:
                        global_data["runs"] += 6; global_data["balls"] += 1; striker["runs"] += 6; striker["balls"] += 1
                        global_data["bowler"]["runs"] += 6; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append(6); check_over_end()
                    st.rerun()
                if br3.button("🟡 WD", use_container_width=True):
                    with lock:
                        global_data["runs"] += 1; global_data["extras"] += 1; global_data["bowler"]["runs"] += 1
                        global_data["this_over"].append("WD")
                    st.rerun()
                if br4.button("🟠 NB", use_container_width=True):
                    with lock:
                        global_data["runs"] += 1; global_data["extras"] += 1; global_data["bowler"]["runs"] += 1
                        global_data["this_over"].append("NB")
                    st.rerun()

                st.write("")
                act1, act2 = st.columns(2)
                if act1.button("🔴 OUT / WICKET", use_container_width=True, type="primary"):
                    with lock:
                        global_data["wickets"] += 1; global_data["balls"] += 1; striker["balls"] += 1
                        global_data["bowler"]["wickets"] += 1; global_data["bowler"]["balls"] += 1
                        global_data["this_over"].append("W")
                    if global_data["wickets"] >= 10:
                        st.rerun()
                    else:
                        st.session_state.show_wicket_popup = True
                        st.rerun()
                if act2.button("🔄 Manual Swap Strike", use_container_width=True):
                    with lock: switch_strike()
                    st.rerun()
        else:
            st.info("ℹ️ Broadcast Mode: This portal automatically syncs live with the official match scorer's tablet.")

# ================= RIGHT PANEL =================
    with right_col:
        st.markdown("#### 📊 Live Player Metrics")
        m1, m2 = st.columns(2)
        with m1:
            mark1 = "🏏 (Striker)" if global_data["b1"]["strike"] else ""
            mark2 = "🏏 (Striker)" if global_data["b2"]["strike"] else ""
            st.caption(f"👤 {global_data['b1']['name']} {mark1}")
            st.markdown(f"**{global_data['b1']['runs']}** runs / **{global_data['b1']['balls']}** balls")
            st.caption(f"👤 {global_data['b2']['name']} {mark2}")
            st.markdown(f"**{global_data['b2']['runs']}** runs / **{global_data['b2']['balls']}** balls")
        with m2:
            st.caption(f"🥎 Active Bowler: **{global_data['bowler']['name']}**")
            b_ov = f"{global_data['bowler']['balls'] // 6}.{global_data['bowler']['balls'] % 6}"
            st.markdown(f"Wickets: **{global_data['bowler']['wickets']}**")
            st.markdown(f"Runs: **{global_data['bowler']['runs']}** ({b_ov} Ov)")

        st.markdown("#### 📍 Active Over Sequence")
        if not global_data["this_over"]: st.caption("Waiting for delivery...")
        else:
            b_html = "".join([f'<span class="ball-bubble" style="background-color:{"#10B981" if str(b) in ["4","6"] else ("#EF4444" if b=="W" else "#475569")}; color:white;">{b}</span>' for b in global_data["this_over"]])
            st.markdown(b_html, unsafe_allow_html=True)

        st.markdown("#### 📋 Completed Over Metrics")
        if global_data["over_history"]:
            st.dataframe(pd.DataFrame(global_data["over_history"]), use_container_width=True, hide_index=True, height=110)
        else: st.caption("No archived completed overs.")

        # --- PDF Generation Report Engine ---
        def generate_pdf_report():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(30, 58, 138)
            pdf.cell(0, 15, "ANSCOR APL 2026 OFFICIAL MATCH REPORT", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, f"Teams: {global_data['batting_team']} vs {global_data['bowling_team']}", ln=True)
            pdf.cell(0, 10, f"Final Inning Score: {global_data['runs']}/{global_data['wickets']} ({global_data['balls'] // 6}.{global_data['balls'] % 6} Overs)", ln=True)
            pdf.cell(0, 10, f"Total Extras: {global_data['extras']} | Final Innings Run Rate: {crr:.2f}", ln=True)
            pdf.ln(5)
            
            pdf.cell(0, 10, "Individual Batsman Contributions:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, f"- {global_data['b1']['name']}: {global_data['b1']['runs']} Runs scored off {global_data['b1']['balls']} balls", ln=True)
            pdf.cell(0, 8, f"- {global_data['b2']['name']}: {global_data['b2']['runs']} Runs scored off {global_data['b2']['balls']} balls", ln=True)
            
            return bytes(pdf.output())

        st.write("")
        st.download_button(
            label="📥 Export Report as Official PDF", 
            data=generate_pdf_report(), 
            file_name=f"APL_Match_{global_data['batting_team']}.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )

    # --- RESET APPLICATION CONTROL (ADMIN ONLY) ---
    if is_admin:
        st.markdown("---")
        if st.button("Reset Tournament Dashboard Application", type="secondary", use_container_width=True):
            with lock:
                global_data["match_started"] = False
                global_data["runs"], global_data["wickets"], global_data["balls"] = 0, 0, 0
                global_data["this_over"], global_data["over_history"] = [], []
            st.rerun()
