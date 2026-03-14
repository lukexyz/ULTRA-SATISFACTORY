import streamlit as st

st.set_page_config(
    page_title="SATISFACTORY CONTROL",
    page_icon="⚙️",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    /* Force dark background everywhere */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #000000 !important;
    }

    [data-testid="stMain"] {
        background-color: #000000 !important;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #000000;
    }

    /* Logo container */
    .logo-container {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .logo-svg {
        filter: drop-shadow(0 0 20px #ffffff) drop-shadow(0 0 40px #aaaaaa);
        animation: pulse-glow 2.5s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 15px #cccccc) drop-shadow(0 0 35px #888888); }
        50%       { filter: drop-shadow(0 0 35px #ffffff) drop-shadow(0 0 70px #bbbbbb); }
    }

    .logo-title {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 2.8rem;
        color: #ffffff;
        letter-spacing: 0.35em;
        text-shadow:
            0 0 10px #ffffff,
            0 0 30px #cccccc,
            0 0 60px #888888;
        margin: 0.5rem 0 0.1rem 0;
        line-height: 1;
    }

    .logo-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #aaaaaa;
        letter-spacing: 0.5em;
        text-transform: uppercase;
        margin-bottom: 0;
    }

    /* Divider */
    .hacker-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffffff, #cccccc, #ffffff, transparent);
        margin: 1.5rem auto;
        max-width: 600px;
        box-shadow: 0 0 8px #ffffff;
    }

    /* Button panel */
    .btn-panel-title {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: #aaaaaa;
        letter-spacing: 0.4em;
        text-align: center;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* Streamlit buttons */
    div.stButton > button {
        width: 100%;
        height: 90px;
        font-family: 'Orbitron', monospace !important;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.15em;
        color: #000000 !important;
        background: linear-gradient(135deg, #ffffff, #cccccc) !important;
        border: 2px solid #ffffff !important;
        border-radius: 6px !important;
        cursor: pointer;
        text-transform: uppercase;
        box-shadow:
            0 0 12px #ffffff,
            0 4px 15px rgba(255,255,255,0.3),
            inset 0 1px 0 rgba(255,255,255,0.5);
        transition: all 0.15s ease;
        position: relative;
        overflow: hidden;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    div.stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.4s ease;
    }

    div.stButton > button:hover::before {
        left: 100%;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #ffffff, #ffffff) !important;
        box-shadow:
            0 0 30px #ffffff,
            0 0 60px #cccccc,
            0 6px 20px rgba(255,255,255,0.4),
            inset 0 1px 0 rgba(255,255,255,0.6) !important;
        transform: translateY(-2px);
    }

    div.stButton > button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 0 8px #ffffff, 0 2px 8px rgba(255,255,255,0.3) !important;
    }

    /* Status box */
    .status-box {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #ffffff;
        background: #111111;
        border: 1px solid #ffffff;
        border-radius: 4px;
        padding: 0.75rem 1rem;
        text-align: center;
        letter-spacing: 0.1em;
        box-shadow: 0 0 12px #ffffff55, inset 0 0 10px #ffffff22;
        margin-top: 1.5rem;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-4px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Corner decorations */
    .corner-deco {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.65rem;
        color: #666666;
        letter-spacing: 0.2em;
        text-align: center;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown("""
<div class="logo-container">
    <svg class="logo-svg" width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
        <!-- Outer hexagon -->
        <polygon points="60,4 110,32 110,88 60,116 10,88 10,32"
                 fill="none" stroke="#ffffff" stroke-width="3"/>
        <!-- Inner hexagon -->
        <polygon points="60,18 96,38 96,82 60,102 24,82 24,38"
                 fill="#000000" stroke="#aaaaaa" stroke-width="1.5"/>
        <!-- Gear teeth outer ring -->
        <circle cx="60" cy="60" r="28" fill="none" stroke="#ffffff" stroke-width="2.5"
                stroke-dasharray="8 4"/>
        <!-- Center cog body -->
        <circle cx="60" cy="60" r="18" fill="#333333" stroke="#ffffff" stroke-width="2"/>
        <!-- Center hole -->
        <circle cx="60" cy="60" r="7" fill="#000000" stroke="#ffffff" stroke-width="2"/>
        <!-- Gear spokes -->
        <line x1="60" y1="42" x2="60" y2="36" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="60" y1="78" x2="60" y2="84" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="42" y1="60" x2="36" y2="60" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="78" y1="60" x2="84" y2="60" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="47.5" y1="47.5" x2="43.4" y2="43.4" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="72.5" y1="72.5" x2="76.6" y2="76.6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="72.5" y1="47.5" x2="76.6" y2="43.4" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <line x1="47.5" y1="72.5" x2="43.4" y2="76.6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
        <!-- Corner circuit nodes -->
        <circle cx="60" cy="10" r="3" fill="#ffffff"/>
        <circle cx="104" cy="35" r="3" fill="#ffffff"/>
        <circle cx="104" cy="85" r="3" fill="#ffffff"/>
        <circle cx="60" cy="110" r="3" fill="#ffffff"/>
        <circle cx="16" cy="85" r="3" fill="#ffffff"/>
        <circle cx="16" cy="35" r="3" fill="#ffffff"/>
    </svg>
    <div class="logo-title">SATISFACTORY</div>
    <div class="logo-subtitle">Control Terminal v1.0</div>
</div>
<hr class="hacker-divider">
<div class="btn-panel-title">// TOUCH INPUT PANEL //</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "last_action" not in st.session_state:
    st.session_state.last_action = None

# --- BUTTONS ---
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    if st.button("INITIATE\nBUILD", key="btn1", use_container_width=True):
        st.session_state.last_action = "BUILD SEQUENCE INITIATED"

with col2:
    if st.button("POWER\nGRID", key="btn2", use_container_width=True):
        st.session_state.last_action = "POWER GRID ONLINE"

with col3:
    if st.button("EXTRACT\nORE", key="btn3", use_container_width=True):
        st.session_state.last_action = "EXTRACTION STARTED"

# --- STATUS ---
if st.session_state.last_action:
    st.markdown(f"""
    <div class="status-box">
        &gt; {st.session_state.last_action} &lt;
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="corner-deco">
    &#9632;&#9632;&#9632; FICSIT INC. AUTHORIZED TERMINAL &#9632;&#9632;&#9632;
</div>
""", unsafe_allow_html=True)
