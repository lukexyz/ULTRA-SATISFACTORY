import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path so we can import ultra_satisfactory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ultra_satisfactory.data import load_data, wiki_image_url, get_item_recipe, list_items
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

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
            e_name_encoded = e['name'].replace(' ', '%20').replace("'", "%27")
            parts.append(
                f'<a class="recipe-chip" href="?item={e_name_encoded}">'
                f'<span style="font-weight:600;color:#e8d44d;">{e["amount"]}&times;</span>'
                f'<img src="{e_img}" width="40" height="40" '
                f'style="image-rendering:pixelated;border:1px solid #555;border-radius:4px;background:#1a1a2e;">'
                f'<span style="font-size:0.82em;color:#ccc;">{e["name"]}<br>'
                f'<span style="color:#7ec8e3;">{e["rate_per_min"]}/min</span></span>'
                f'</a>'
            )
        return ''.join(parts)

    return f'''
    <style>
        .recipe-chip {{
            text-decoration: none;
            color: inherit;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin: 4px 6px;
            border-radius: 6px;
            padding: 2px 4px;
            cursor: pointer;
            transition: background 0.15s;
        }}
        .recipe-chip:hover {{
            background: rgba(255,255,255,0.10);
        }}
    </style>
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

    /* ⚡ Fade-in on page load — masks visual jank during chip navigation reloads */
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    [data-testid="stApp"] {
        animation: fadeIn 0.3s ease-in;
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Main container — zero top padding */
    .main .block-container {
        padding-top: 0.15rem !important;
        padding-bottom: 2rem;
        background-color: #000000;
    }
    /* Kill Streamlit's internal top spacing */
    [data-testid="stMain"] > div:first-child {
        padding-top: 0 !important;
    }
    section[data-testid="stMain"] {
        padding-top: 0 !important;
    }

    /* Logo container — centered vertical stack */
    .logo-container {
        text-align: center;
        padding: 0.15rem 0 0.2rem 0;
    }
    .logo-svg {
        filter: drop-shadow(0 0 25px #ffffff) drop-shadow(0 0 50px #cccccc) drop-shadow(0 0 80px #888888);
        animation: pulse-glow 2.5s ease-in-out infinite, slow-spin 60s linear infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { filter: drop-shadow(0 0 20px #cccccc) drop-shadow(0 0 50px #aaaaaa) drop-shadow(0 0 80px #666666); }
        50%       { filter: drop-shadow(0 0 40px #ffffff) drop-shadow(0 0 80px #cccccc) drop-shadow(0 0 120px #999999); }
    }
    @keyframes slow-spin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }
    .logo-title {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 1.9rem;
        color: #ffffff;
        letter-spacing: 0.1em;
        margin: 0.25rem 0 0.05rem 0;
        line-height: 1;
    }
    .logo-title .ultra {
        color: #00cfff;
        text-shadow:
            0 0 8px #00cfff,
            0 0 20px #00cfff,
            0 0 45px #0099cc,
            0 0 80px #006699;
    }
    .logo-title .satisfactory {
        text-shadow:
            0 0 10px #ffffff,
            0 0 30px #ffffff,
            0 0 60px #cccccc,
            0 0 100px #888888;
    }
    .logo-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: #aaaaaa;
        letter-spacing: 0.5em;
        text-transform: uppercase;
        text-shadow: 0 0 8px #aaaaaa;
        margin: 0.1rem 0 0 0;
    }

    /* Divider */
    .hacker-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ffffff, #cccccc, #ffffff, transparent);
        margin: 0.3rem auto;
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

    div[data-testid="stTabs"] {
        background: transparent;
    }
    div[data-testid="stTabs"] > div:first-child {
        gap: 0;
        margin-bottom: 1.5rem;
        justify-content: center !important;
        border-bottom: 2px solid transparent !important;
        border-image: linear-gradient(90deg, #a855f7, #ec4899, #38bdf8) 1 !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stTabs"] [role="tablist"] {
        justify-content: center !important;
    }

    /* Individual tab buttons — base state */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3em !important;
        text-transform: uppercase !important;
        color: #444444 !important;
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.4rem !important;
        margin: 0 4px !important;
        transition: all 0.2s ease !important;
        position: relative !important;
    }

    /* ---- Per-tab colours — OBJECTIVES (purple) ---- */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(1):hover {
        color: #d8b4fe !important;
        background: rgba(168,85,247,0.10) !important;
        border: 1px solid #a855f7 !important;
        box-shadow: 0 0 8px #a855f755, 0 0 22px #a855f733, 0 0 45px #a855f711,
                    inset 0 0 10px #a855f711 !important;
        text-shadow: 0 0 10px #a855f7, 0 0 25px #a855f788 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"]:nth-child(1) {
        color: #f3e8ff !important;
        background: rgba(168,85,247,0.18) !important;
        border: 1px solid #c084fc !important;
        box-shadow: 0 0 12px #a855f777, 0 0 30px #a855f744, 0 0 60px #a855f722,
                    inset 0 0 14px #a855f722 !important;
        text-shadow: 0 0 8px #c084fc, 0 0 20px #a855f7, 0 0 40px #a855f788 !important;
    }

    /* ---- Per-tab colours — ITEMS (hot pink) ---- */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(2):hover {
        color: #fbcfe8 !important;
        background: rgba(236,72,153,0.10) !important;
        border: 1px solid #ec4899 !important;
        box-shadow: 0 0 8px #ec489955, 0 0 22px #ec489933, 0 0 45px #ec489911,
                    inset 0 0 10px #ec489911 !important;
        text-shadow: 0 0 10px #ec4899, 0 0 25px #ec489988 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"]:nth-child(2) {
        color: #fce7f3 !important;
        background: rgba(236,72,153,0.18) !important;
        border: 1px solid #f472b6 !important;
        box-shadow: 0 0 12px #ec489977, 0 0 30px #ec489944, 0 0 60px #ec489922,
                    inset 0 0 14px #ec489922 !important;
        text-shadow: 0 0 8px #f472b6, 0 0 20px #ec4899, 0 0 40px #ec489988 !important;
    }

    /* ---- Per-tab colours — BUILDINGS (electric blue) ---- */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(3):hover {
        color: #bae6fd !important;
        background: rgba(56,189,248,0.10) !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 0 8px #38bdf855, 0 0 22px #38bdf833, 0 0 45px #38bdf811,
                    inset 0 0 10px #38bdf811 !important;
        text-shadow: 0 0 10px #38bdf8, 0 0 25px #38bdf888 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"][data-baseweb="tab"]:nth-child(3) {
        color: #e0f2fe !important;
        background: rgba(56,189,248,0.18) !important;
        border: 1px solid #7dd3fc !important;
        box-shadow: 0 0 12px #38bdf877, 0 0 30px #38bdf844, 0 0 60px #38bdf822,
                    inset 0 0 14px #38bdf822 !important;
        text-shadow: 0 0 8px #7dd3fc, 0 0 20px #38bdf8, 0 0 40px #38bdf888 !important;
    }

    /* Streamlit tab indicator line — neon cyan matching ULTRA title */
    div[data-testid="stTabs"] [data-testid="stTabBar"] [role="presentation"],
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-testid="stTabBar"] > div:last-child,
    div[data-testid="stTabs"] [role="tablist"] > div[role="presentation"] {
        display: block !important;
        height: 3px !important;
        border-radius: 2px !important;
        background: #00cfff !important;
        background-color: #00cfff !important;
        box-shadow: 0 0 8px #00cfff88, 0 0 20px #00cfff44 !important;
        filter: drop-shadow(0 0 6px #00cfff66) !important;
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

    /* ---- ITEMS TAB (AgGrid) ---- */

    /* Hide AgGrid's outer border and blend into dark bg */
    .ag-root-wrapper {
        border: none !important;
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
    <div class="logo-title"><span class="ultra">ULTRA</span><span class="satisfactory">SATISFACTORY</span></div>
    <div class="logo-subtitle">Control Terminal v1.0</div>
</div>
<hr class="hacker-divider">
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None
if "chip_item" not in st.session_state:
    st.session_state.chip_item = None

# ⚡ Query param handler: clicking a recipe chip sets ?item=Name
# Must run BEFORE st.tabs() so we can set the default tab to ITEMS
_queried_item = st.query_params.get("item")
if _queried_item:
    st.session_state.chip_item = _queried_item
    st.query_params.clear()

# --- TABS ---
_default_tab = "ITEMS" if _queried_item else None
tab_objectives, tab_items, tab_buildings = st.tabs(
    ["OBJECTIVES", "ITEMS", "BUILDINGS"], default=_default_tab
)

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
# TAB 2 — ITEMS (AgGrid with instant floating filter)
# ================================================================
with tab_items:
    st.markdown('<div class="section-title">// ITEM DATABASE //</div>',
                unsafe_allow_html=True)

    # Reserve a placeholder for the recipe card ABOVE the grid.
    recipe_placeholder = st.empty()

    # Build DataFrame from item list
    all_items = list_items(data)
    df_items = pd.DataFrame([
        {"icon": it["image_url"], "name": it["name"]}
        for it in all_items
    ])

    # --- JS cell renderer for icon column ---
    icon_renderer = JsCode("""
    class IconCellRenderer {
        init(params) {
            this.eGui = document.createElement('span');
            this.eGui.style.cssText = 'display:flex;align-items:center;justify-content:center;height:100%;';
            if (params.value) {
                var img = document.createElement('img');
                img.src = params.value;
                img.style.cssText = 'width:32px;height:32px;object-fit:contain;image-rendering:pixelated;border-radius:4px;border:1px solid #333;background:#111;';
                this.eGui.appendChild(img);
            }
        }
        getGui() { return this.eGui; }
        refresh() { return false; }
    }
    """)

    # --- Grid options ---
    gb = GridOptionsBuilder.from_dataframe(df_items)

    # Icon column — narrow, no filter/sort, image renderer
    gb.configure_column(
        field="icon",
        header_name="",
        cellRenderer=icon_renderer,
        width=60,
        maxWidth=60,
        minWidth=60,
        sortable=False,
        filter=False,
        resizable=False,
        suppressMovable=True,
    )

    # Name column — instant floating filter for per-keystroke search
    gb.configure_column(
        field="name",
        header_name="ITEM",
        floatingFilter=True,
        filter="agTextColumnFilter",
        filterParams=JsCode("""{
            filterOptions: ['contains'],
            defaultOption: 'contains',
            maxNumConditions: 1,
        }"""),
        flex=1,
        suppressMovable=True,
    )

    # Single-row click selection (no checkbox)
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
    )

    # JS callback: inject a "clear" button into the icon column's floating filter area,
    # and deselect rows when the filter changes (so the old recipe card disappears)
    on_ready_js = JsCode("""
    function(params) {
        // Deselect all rows whenever the filter model changes (user types new search)
        params.api.addEventListener('filterChanged', function() {
            params.api.deselectAll();
        });

        setTimeout(function() {
            var wrapper = params.api.gridOptionsService
                ? params.api.gridOptionsService.eGridDiv
                : document.querySelector('.ag-root-wrapper');
            if (!wrapper) wrapper = document.querySelector('.ag-root-wrapper');
            var firstFilter = wrapper.querySelector('.ag-floating-filter');
            if (firstFilter) {
                firstFilter.style.visibility = 'visible';
                firstFilter.innerHTML = '';
                firstFilter.style.display = 'flex';
                firstFilter.style.alignItems = 'center';
                firstFilter.style.justifyContent = 'center';
                var btn = document.createElement('button');
                btn.innerText = 'clear';
                btn.style.cssText = 'background:none;border:1px solid #333;border-radius:4px;color:#555;font-family:Share Tech Mono,monospace;font-size:0.65rem;letter-spacing:0.08em;cursor:pointer;padding:2px 8px;transition:color 0.15s,border-color 0.15s;line-height:1.4;';
                btn.onmouseover = function() { btn.style.color='#ccc'; btn.style.borderColor='#666'; };
                btn.onmouseout  = function() { btn.style.color='#555'; btn.style.borderColor='#333'; };
                btn.onclick = function() {
                    params.api.setFilterModel(null);
                    // Also clear the floating filter input text
                    var input = wrapper.querySelector('.ag-floating-filter-input input');
                    if (input) {
                        input.value = '';
                        input.dispatchEvent(new Event('input', {bubbles: true}));
                    }
                };
                firstFilter.appendChild(btn);
            }
        }, 200);
    }
    """)

    # Grid-level options
    gb.configure_grid_options(
        rowHeight=52,
        headerHeight=0,
        floatingFiltersHeight=40,
        suppressHorizontalScroll=True,
        suppressCellFocus=True,
        suppressRowDeselection=False,
        domLayout="normal",
        onFirstDataRendered=on_ready_js,
    )

    grid_options = gb.build()

    # --- Custom CSS for dark grayscale theme ---
    aggrid_css = {
        # Overall wrapper
        ".ag-root-wrapper": {
            "background-color": "#000000 !important",
            "border": "none !important",
            "font-family": "'Share Tech Mono', monospace !important",
        },
        # Header row (hidden via headerHeight=0 but just in case)
        ".ag-header": {
            "background-color": "#000000 !important",
            "border-bottom": "none !important",
        },
        # Floating filter bar (the search input row)
        ".ag-floating-filter": {
            "background-color": "#000000 !important",
            "border-bottom": "1px solid #222222 !important",
        },
        ".ag-floating-filter-input": {
            "background-color": "#111111 !important",
            "color": "#cccccc !important",
            "border": "1px solid #333333 !important",
            "border-radius": "4px !important",
            "font-family": "'Share Tech Mono', monospace !important",
            "font-size": "0.85rem !important",
        },
        # Hide the icon column's floating filter (no filter for icon)
        ".ag-floating-filter:first-child": {
            "visibility": "hidden !important",
        },
        # Body / viewport
        ".ag-body-viewport": {
            "background-color": "#000000 !important",
        },
        # Rows
        ".ag-row": {
            "background-color": "#000000 !important",
            "border-bottom": "1px solid #111111 !important",
            "color": "#cccccc !important",
            "font-family": "'Share Tech Mono', monospace !important",
            "font-size": "0.85rem !important",
            "letter-spacing": "0.05em !important",
            "cursor": "pointer !important",
        },
        ".ag-row-hover": {
            "background-color": "rgba(255,255,255,0.04) !important",
        },
        ".ag-row-selected": {
            "background-color": "rgba(255,255,255,0.08) !important",
            "color": "#ffffff !important",
        },
        # Cells — hide column borders
        ".ag-cell": {
            "border-right": "none !important",
            "line-height": "52px !important",
        },
        # No rows overlay
        ".ag-overlay-no-rows-center": {
            "color": "#555555 !important",
            "font-family": "'Share Tech Mono', monospace !important",
            "font-size": "0.75rem !important",
            "letter-spacing": "0.2em !important",
        },
        # Scrollbar styling
        ".ag-body-viewport::-webkit-scrollbar": {
            "width": "6px !important",
        },
        ".ag-body-viewport::-webkit-scrollbar-track": {
            "background": "#000000 !important",
        },
        ".ag-body-viewport::-webkit-scrollbar-thumb": {
            "background": "#333333 !important",
            "border-radius": "3px !important",
        },
    }

    # --- Render the grid ---
    grid_response = AgGrid(
        df_items,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=500,
        allow_unsafe_jscode=True,
        theme="alpine",
        custom_css=aggrid_css,
    )

    # --- Determine which item to display in the recipe card ---
    # Priority: grid row click > chip click (session state)
    selected_rows = grid_response.get("selected_rows", None)
    selected_name = None

    if selected_rows is not None:
        # v1.x returns a DataFrame
        if isinstance(selected_rows, pd.DataFrame) and len(selected_rows) > 0:
            selected_name = selected_rows.iloc[0]["name"]
        # v0.x returns a list of dicts
        elif isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_name = selected_rows[0]["name"]

    # Decide what to display: grid selection clears chip state; chip persists otherwise
    if selected_name:
        display_item = selected_name
        st.session_state.chip_item = None  # grid click overrides chip
    elif st.session_state.chip_item:
        display_item = st.session_state.chip_item
    else:
        display_item = None

    # Render the recipe card into the placeholder above the grid
    if display_item:
        with recipe_placeholder.container():
            result = get_item_recipe(display_item, data)
            if result:
                st.markdown(f"""
                <div style="text-align:center;margin-bottom:4px;">
                    <span style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
                                 color:#e8d44d;letter-spacing:0.3em;text-transform:uppercase;
                                 text-shadow:0 0 8px #e8d44d, 0 0 20px #d4a01788;">
                    &gt;&gt; {display_item} &lt;&lt;</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(recipe_card(result), unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="status-box">
                    &gt; No craftable recipe found for {display_item} &lt;
                </div>
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
