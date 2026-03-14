import streamlit as st
import sys
from pathlib import Path

# Add project root to path so we can import ultra_satisfactory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ultra_satisfactory.data import load_data, wiki_image_url, get_item_recipe

st.set_page_config(
    page_title="SATISFACTORY CONTROL",
    page_icon="⚙️",
    layout="centered",
)

# --- DATA ---
@st.cache_data
def get_data():
    return load_data()

data = get_data()

# Space Elevator Phase 3 objectives
OBJECTIVES = [
    {"name": "Versatile Framework",    "required": 2500},
    {"name": "Modular Engine",         "required": 500},
    {"name": "Adaptive Control Unit",  "required": 100},
]

# --- RECIPE CARD FUNCTION (shared across tabs) ---
def recipe_card(result: dict) -> str:
    """Return an HTML crafting card styled like the Satisfactory wiki (gold/blue theme)."""
    name = result['name']
    img = result['image_url']
    machine = result['machine']
    power = result['machine_power']
    cycle = result['cycle_time']
    recipe_name = result['recipe_name']

    def item_cell(entries):
        parts = []
        for e in entries:
            e_img = wiki_image_url(e['name'], 48)
            parts.append(
                f'<div style="display:inline-flex;align-items:center;gap:4px;margin:4px 6px;">'
                f'<span style="font-weight:600;color:#e8d44d;">{e["amount"]}&times;</span>'
                f'<img src="{e_img}" width="40" height="40" '
                f'style="image-rendering:pixelated;border:1px solid #555;border-radius:4px;background:#1a1a2e;">'
                f'<span style="font-size:0.82em;color:#ccc;">{e["name"]}<br>'
                f'<span style="color:#7ec8e3;">{e["rate_per_min"]}/min</span></span>'
                f'</div>'
            )
        return ''.join(parts)

    return f'''
    <div style="background:linear-gradient(135deg,#0f0f23,#1a1a2e);border:1px solid #e8d44d;
                border-radius:10px;margin:12px 0;padding:0;font-family:Segoe UI,sans-serif;
                color:#eee;overflow:hidden;max-width:820px;
                box-shadow:0 0 15px #e8d44d44, 0 0 30px #e8d44d22;">
      <div style="background:linear-gradient(90deg,#e8d44d,#d4a017);padding:8px 16px;
                  display:flex;align-items:center;gap:12px;">
        <img src="{img}" width="48" height="48"
             style="image-rendering:pixelated;border:2px solid #fff;border-radius:6px;background:#1a1a2e;">
        <div>
          <div style="font-size:1.2em;font-weight:700;color:#0f0f23;">{name}</div>
          <div style="font-size:0.8em;color:#333;">Recipe: {recipe_name}</div>
        </div>
      </div>
      <table style="width:100%;border-collapse:collapse;margin:0;">
        <tr style="background:#12122a;">
          <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #333;color:#e8d44d;
                     font-size:0.85em;width:40%;">Ingredients</th>
          <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #333;color:#e8d44d;
                     font-size:0.85em;width:25%;">Produced in</th>
          <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #333;color:#e8d44d;
                     font-size:0.85em;width:35%;">Products</th>
        </tr>
        <tr>
          <td style="padding:10px 12px;vertical-align:middle;border-right:1px solid #222;">
            {item_cell(result['ingredients'])}
          </td>
          <td style="padding:10px 12px;text-align:center;vertical-align:middle;border-right:1px solid #222;">
            <div style="font-weight:600;font-size:1.05em;color:#fff;">{machine}</div>
            <div style="font-size:0.82em;color:#7ec8e3;">{cycle}s cycle &bull; {power} MW</div>
          </td>
          <td style="padding:10px 12px;vertical-align:middle;">
            {item_cell(result['products'])}
          </td>
        </tr>
      </table>
    </div>'''


# --- GLOBAL STYLES ---
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

    /* Main container — tight top padding */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        background-color: #000000;
    }

    /* Logo container — compact */
    .logo-container {
        text-align: center;
        padding: 0.5rem 0 0.3rem 0;
    }
    .logo-svg {
        filter: drop-shadow(0 0 25px #ffffff) drop-shadow(0 0 50px #cccccc) drop-shadow(0 0 80px #888888);
        animation: pulse-glow 2.5s ease-in-out infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 20px #cccccc) drop-shadow(0 0 50px #aaaaaa) drop-shadow(0 0 80px #666666); }
        50%       { filter: drop-shadow(0 0 40px #ffffff) drop-shadow(0 0 80px #cccccc) drop-shadow(0 0 120px #999999); }
    }
    .logo-title {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 2.2rem;
        color: #ffffff;
        letter-spacing: 0.35em;
        text-shadow:
            0 0 10px #ffffff,
            0 0 30px #ffffff,
            0 0 60px #cccccc,
            0 0 100px #888888;
        margin: 0.3rem 0 0.1rem 0;
        line-height: 1;
    }
    .logo-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #aaaaaa;
        letter-spacing: 0.5em;
        text-transform: uppercase;
        text-shadow: 0 0 8px #aaaaaa;
        margin-bottom: 0;
    }

    /* Divider */
    .hacker-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffffff, #cccccc, #ffffff, transparent);
        margin: 0.6rem auto;
        max-width: 600px;
        box-shadow: 0 0 12px #ffffff, 0 0 30px #cccccc88;
    }

    /* Section title */
    .section-title {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: #aaaaaa;
        letter-spacing: 0.4em;
        text-align: center;
        text-transform: uppercase;
        text-shadow: 0 0 6px #aaaaaa88;
        margin-bottom: 1rem;
    }

    /* ---- TAB NAVIGATION ---- */

    /* Tab bar background */
    [data-testid="stTabs"] {
        background: transparent;
    }
    div[data-testid="stTabs"] > div:first-child {
        border-bottom: 2px solid #333333;
        gap: 0;
        margin-bottom: 1.5rem;
    }

    /* Individual tab buttons */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3em !important;
        text-transform: uppercase !important;
        color: #555555 !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.6rem 1.4rem !important;
        margin-bottom: -2px !important;
        transition: color 0.15s ease, text-shadow 0.15s ease !important;
    }

    /* Tab hover */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: #cccccc !important;
        text-shadow: 0 0 8px #cccccc88 !important;
        background: transparent !important;
    }

    /* Active tab */
    div[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"] {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
        text-shadow:
            0 0 8px #ffffff,
            0 0 20px #cccccc !important;
        background: transparent !important;
    }

    /* Hide the default Streamlit tab indicator line */
    div[data-testid="stTabs"] [data-testid="stTabBar"] [role="presentation"] {
        display: none !important;
    }

    /* Tab panel — no extra padding */
    div[data-testid="stTabPanel"] {
        padding-top: 0 !important;
    }

    /* --- OBJECTIVE BUTTON CARDS --- */

    /* The actual st.button — tall, visual content hidden */
    div.stButton > button {
        width: 100%;
        height: 230px !important;
        min-height: 230px !important;
        font-size: 0 !important;
        color: transparent !important;
        background: linear-gradient(145deg, #ffffff, #d0d0d0, #bbbbbb) !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        cursor: pointer;
        box-shadow:
            0 0 20px #ffffff,
            0 0 40px rgba(255,255,255,0.4),
            0 4px 20px rgba(255,255,255,0.3),
            inset 0 1px 0 rgba(255,255,255,0.8);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        padding: 0 !important;
    }
    div.stButton > button p {
        font-size: 0 !important;
        line-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div.stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        transition: left 0.5s ease;
    }
    div.stButton > button:hover::before {
        left: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(145deg, #ffffff, #eeeeee, #dddddd) !important;
        box-shadow:
            0 0 40px #ffffff,
            0 0 80px rgba(255,255,255,0.5),
            0 0 120px rgba(255,255,255,0.2),
            0 8px 30px rgba(255,255,255,0.4),
            inset 0 1px 0 rgba(255,255,255,0.9) !important;
        transform: translateY(-3px);
    }
    div.stButton > button:active {
        transform: translateY(1px) scale(0.97);
        box-shadow:
            0 0 15px #ffffff,
            0 2px 10px rgba(255,255,255,0.3) !important;
    }

    /* Visual card overlay — sits on top of button via negative margin */
    .obj-card-visual {
        position: relative;
        z-index: 2;
        pointer-events: none;
        margin-top: -235px;
        margin-bottom: 5px;
        height: 230px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 10px 8px;
    }
    .obj-card-visual img {
        border-radius: 10px;
        border: 2px solid #555;
        background: #1a1a2e;
        margin-bottom: 8px;
        image-rendering: pixelated;
        filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));
    }
    .obj-card-visual .obj-name {
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 0.72rem;
        color: #000000;
        margin-bottom: 2px;
        line-height: 1.2;
    }
    .obj-card-visual .obj-qty {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .obj-card-visual .obj-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.6rem;
        color: #555;
        letter-spacing: 0.3em;
        text-transform: uppercase;
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
        box-shadow: 0 0 20px #ffffff55, inset 0 0 15px #ffffff22;
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
        text-shadow: 0 0 4px #66666644;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.markdown("""
<div class="logo-container">
    <svg class="logo-svg" width="80" height="80" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
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
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# --- TABS ---
tab_objectives, tab_items, tab_buildings = st.tabs(["OBJECTIVES", "ITEMS", "BUILDINGS"])

# ================================================================
# TAB 1 — OBJECTIVES
# ================================================================
with tab_objectives:
    st.markdown('<div class="section-title">// SPACE ELEVATOR &mdash; PHASE 3 //</div>',
                unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")

    for i, obj in enumerate(OBJECTIVES):
        with cols[i]:
            img_url = wiki_image_url(obj["name"], 128)

            # The actual st.button — tall, text hidden via CSS
            if st.button("select", key=f"obj_btn_{i}", use_container_width=True):
                if st.session_state.selected_item == obj["name"]:
                    st.session_state.selected_item = None
                else:
                    st.session_state.selected_item = obj["name"]

            # Visual overlay — pulled up over the button via negative margin
            st.markdown(f"""
            <div class="obj-card-visual">
                <img src="{img_url}" width="96" height="96">
                <div class="obj-name">{obj["name"]}</div>
                <div class="obj-qty">{obj["required"]:,}</div>
                <div class="obj-label">required</div>
            </div>
            """, unsafe_allow_html=True)

    # Recipe display
    if st.session_state.selected_item:
        st.markdown('<hr class="hacker-divider">', unsafe_allow_html=True)
        result = get_item_recipe(st.session_state.selected_item, data)
        if result:
            st.markdown(f"""
            <div style="text-align:center;margin-bottom:4px;">
                <span style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
                             color:#e8d44d;letter-spacing:0.3em;text-transform:uppercase;
                             text-shadow:0 0 8px #e8d44d, 0 0 20px #d4a01788;">
                &gt;&gt; {st.session_state.selected_item} &lt;&lt;</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(recipe_card(result), unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-box">
                &gt; ERROR: Recipe not found for {st.session_state.selected_item} &lt;
            </div>
            """, unsafe_allow_html=True)

# ================================================================
# TAB 2 — ITEMS
# ================================================================
with tab_items:
    st.markdown('<div class="section-title">// ITEM DATABASE //</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;color:#555;font-size:0.75rem;
                text-align:center;letter-spacing:0.2em;">COMING IN TODO 3</div>
    """, unsafe_allow_html=True)

# ================================================================
# TAB 3 — BUILDINGS
# ================================================================
with tab_buildings:
    st.markdown('<div class="section-title">// BUILDINGS DATABASE //</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;color:#555;font-size:0.75rem;
                text-align:center;letter-spacing:0.2em;">COMING SOON</div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="corner-deco">
    &#9632;&#9632;&#9632; FICSIT INC. AUTHORIZED TERMINAL &#9632;&#9632;&#9632;
</div>
""", unsafe_allow_html=True)
