import time
import streamlit as st
import random  # Used here to simulate live device telemetry (RSSI, Uptime)

# Page Configuration
st.set_page_config(
    page_title="Smart Classroom Automation", 
    page_icon="🏫", 
    layout="wide"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1rem;
    }
    .hero-container {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session States ---
if "light_status" not in st.session_state:
    st.session_state.light_status = "OFF"

if "human_detected" not in st.session_state:
    st.session_state.human_detected = False

if "auto_mode" not in st.session_state:
    st.session_state.auto_mode = True

if "leave_time" not in st.session_state:
    st.session_state.leave_time = None  # Tracks when the person left

COOLDOWN_SECONDS = 30  # Auto turn off timer

# --- Hero Header Section ---
st.markdown("""
    <div class="hero-container">
        <h1 style="margin: 0; font-size: 2.2rem;">🏫 Smart Classroom & Room Automation</h1>
        <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 1.1rem;">
            Real-time occupancy monitoring with 30s auto-cooldown and live ESP32 telemetry.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- COOLDOWN LOGIC (Automatic Turn Off) ---
if st.session_state.auto_mode:
    if not st.session_state.human_detected:
        if st.session_state.light_status == "ON":
            if st.session_state.leave_time is None:
                # Person just left, start the timer
                st.session_state.leave_time = time.time()
            
            elapsed = time.time() - st.session_state.leave_time
            remaining = int(COOLDOWN_SECONDS - elapsed)
            
            if remaining > 0:
                st.warning(f"⚠️️ Room vacant! Light will automatically turn OFF in **{remaining} seconds**.")
                time.sleep(1)
                st.rerun()  # Refresh page to keep countdown live
            else:
                # Cooldown expired, turn off light
                st.session_state.light_status = "OFF"
                st.session_state.leave_time = None
                st.rerun()
    else:
        # Human is present, reset leave timer
        st.session_state.leave_time = None

# --- Overview Metrics Row ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(label="System Mode", value="Auto (Sensor)" if st.session_state.auto_mode else "Manual Override")

with col_m2:
    presence_text = "Occupied 👤" if st.session_state.human_detected else "Vacant 🚫"
    st.metric(label="Human Presence", value=presence_text)

with col_m3:
    st.metric(label="Main Light State", value=st.session_state.light_status)

with col_m4:
    st.metric(label="Power Consumption", value="14.2 W" if st.session_state.light_status == "ON" else "0.0 W")

st.markdown("<br>", unsafe_allow_html=True)

# --- Main Dashboard Grid ---
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.subheader("📊 Live Sensor & System Status")
    
    if st.session_state.human_detected:
        st.success("🟢 **Sensor Active:** Human presence detected inside the room. Automated lighting triggered.")
    else:
        st.info("🔵 **Sensor Idle:** No human presence detected. Room is currently vacant.")

    st.markdown("###")
    
    with st.container(border=True):
        st.markdown("#### 🧪 Hardware Simulation Tools")
        st.write("Toggle the sensor to test live presence and the 30-second exit countdown:")
        if st.button("🔄 Toggle Human Presence Sensor"):
            st.session_state.human_detected = not st.session_state.human_detected
            if st.session_state.auto_mode and st.session_state.human_detected:
                st.session_state.light_status = "ON"
                st.session_state.leave_time = None
            st.rerun()

with col_right:
    st.subheader("🎛️ Control Panel & Device Telemetry")
    
    with st.container(border=True):
        mode_toggle = st.toggle("Enable Automatic Mode (PIR Sensor)", value=st.session_state.auto_mode)
        if mode_toggle != st.session_state.auto_mode:
            st.session_state.auto_mode = mode_toggle
            st.session_state.leave_time = None
            st.rerun()

        st.markdown("---")
        st.write("**Manual Secondary Override:**")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("💡 Turn Light ON", type="primary" if st.session_state.light_status == "ON" else "secondary"):
                st.session_state.light_status = "ON"
                st.auto_mode = False
                st.toast("Command sent: Light turned ON", icon="💡")
                st.rerun()

        with btn_col2:
            if st.button("🌑 Turn Light OFF", type="primary" if st.session_state.light_status == "OFF" else "secondary"):
                st.session_state.light_status = "OFF"
                st.session_state.auto_mode = False
                st.toast("Command sent: Light turned OFF", icon="🌑")
                st.rerun()

    # --- Live Hardware Telemetry Section ---
    with st.container(border=True):
        st.markdown("#### 📡 ESP32 Device Telemetry")
        t_col1, t_col2, t_col3 = st.columns(3)
        t_col1.metric("Wi-Fi Signal", "-64 dBm")
        t_col2.metric("IP Address", "192.168.1.50")
        t_col3.metric("Uptime", "4h 12m")

# --- Footer Log Section ---
st.markdown("---")
st.caption("🟢 System Status: Connected to local ESP32 Node • Auto-cooldown timer active (30s delay)")