import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path so we can import ultra_satisfactory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ultra_satisfactory.data import load_data, wiki_image_url, local_image_url, get_item_recipe, list_items, list_buildings, get_building_unlock, get_upgrade_chain, get_building_produces
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# ⚡ Auto-patch Streamlit's index.html to prevent white flash on page reload
# and force all links to navigate in-place (never open new tabs).
# Injects inline dark background + color-scheme meta + MutationObserver into
# <head> before any JS/CSS loads. Idempotent — skips if already patched.
# Re-applies after upgrades.
def _patch_streamlit_index():
    _INJECT_DARK = (
        '<meta name="color-scheme" content="dark">'
        '<style>'
        'html, body, #root, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"], [data-testid="stMain"] {'
        'background-color: #000 !important;'
        '}'
        '</style>'
    )
    # ⚡ MutationObserver: Streamlit's DOMPurify injects target="_blank" on all
    # <a> tags. This script watches the DOM and flips any _blank to _self so
    # chip navigation always reloads in-place instead of opening a new tab.
    _INJECT_LINK_FIX = (
        '<script>'
        '(function(){'
        'var o=new MutationObserver(function(m){'
        'm.forEach(function(r){'
        'r.addedNodes.forEach(function(n){'
        'if(n.querySelectorAll){'
        'n.querySelectorAll("a[target=_blank]").forEach(function(a){'
        'var h=a.getAttribute("href")||"";'
        'if(h.indexOf("?item=")===0||h.indexOf("?building=")===0||h.indexOf("?phase=")===0)'
        '{a.setAttribute("target","_self")}'
        '})}'
        '})})});'
        'o.observe(document.documentElement,{childList:true,subtree:true})'
        '})()'
        '</script>'
    )
    index = Path(st.__file__).parent / "static" / "index.html"
    try:
        html = index.read_text()
        changed = False
        if 'color-scheme" content="dark"' not in html:
            html = html.replace("<head>\n", f"<head>\n    {_INJECT_DARK}\n", 1)
            changed = True
        else:
            # Re-patch if older version
            if "data-testid" not in html:
                import re
                html = re.sub(r'<meta name="color-scheme" content="dark">.*?</style>', _INJECT_DARK, html, flags=re.DOTALL)
                changed = True
                
        if _INJECT_LINK_FIX not in html:
            html = html.replace("</head>", f"    {_INJECT_LINK_FIX}\n</head>", 1)
            changed = True
        if changed:
            index.write_text(html)
    except Exception:
        pass  # non-fatal — worst case is the old white flash / new-tab links
_patch_streamlit_index()

st.set_page_config(
    page_title="ULTRA-SATISFACTORY",
    page_icon="⚙️",
    layout="centered",
)

# --- DATA ---
@st.cache_data
def get_data():
    return load_data()

data = get_data()

# ⚡ Space Elevator objectives — all 5 phases
SPACE_ELEVATOR_PHASES = {
    1: [
        {"name": "Smart Plating",           "required": 50},
        {"name": "Versatile Framework",     "required": 100},
        {"name": "Automated Wiring",        "required": 500},
    ],
    2: [
        {"name": "Automated Wiring",        "required": 500},
        {"name": "Modular Frame",           "required": 500},
        {"name": "Smart Plating",           "required": 100},
        {"name": "Versatile Framework",     "required": 500},
    ],
    3: [
        {"name": "Versatile Framework",     "required": 2500},
        {"name": "Modular Engine",          "required": 500},
        {"name": "Adaptive Control Unit",   "required": 100},
    ],
    4: [
        {"name": "Assembly Director System","required": 1000},
        {"name": "Magnetic Field Generator","required": 500},
        {"name": "Nuclear Pasta",           "required": 100},
        {"name": "Thermal Propulsion Rocket","required": 25},
    ],
    5: [
        {"name": "Biochemical Sculptor",    "required": 500},
        {"name": "AI Expansion Server",     "required": 100},
        {"name": "Neural-Quantum Processor","required": 100},
        {"name": "Ballistic Warp Drive",    "required": 100},
    ],
}

# ⚡ Concise one-line descriptions for each Space Elevator phase
PHASE_DESCRIPTIONS = {
    1: "Automation basics",
    2: "Logistics & steel",
    3: "Oil & computers",
    4: "Nuclear & endgame",
    5: "Alien tech & quantum",
}

# ⚡ Default to phase stored in session state (set by selector in tab)
if "selected_phase" not in st.session_state:
    st.session_state.selected_phase = 3

# --- RECIPE CARD FUNCTION (shared across tabs) ---
def recipe_card(result: dict) -> str:
    """Return an HTML crafting card styled like the Satisfactory wiki (gold/blue theme)."""
    name = result['name']
    img = result['image_url']
    machine = result['machine']
    power = result['machine_power']
    cycle = result['cycle_time']
    recipe_name = result['recipe_name']
    # ⚡ Resolve building image for the "Produced in" cell
    machine_img = local_image_url(machine)
    machine_encoded = machine.replace(' ', '%20')

    def item_cell(entries):
        parts = []
        for e in entries:
            e_img = local_image_url(e['name'])
            e_name_encoded = e['name'].replace(' ', '%20').replace("'", "%27")
            parts.append(
                f'<a class="recipe-chip" href="?item={e_name_encoded}" target="_self">'
                f'<span style="font-weight:600;color:#e8d44d;">{e["amount"]}&times;</span>'
                f'<img src="{e_img}" width="40" height="40" '
                f'style="border:1px solid #555;border-radius:4px;background:#1a1a2e;">'
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
        .recipe-chip, .recipe-chip * {{
            text-decoration: none !important;
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
             style="border:2px solid #fff;border-radius:6px;background:#1a1a2e;">
        <div>
          <div style="font-size:1.2em;font-weight:700;color:#0f0f23;">{name}</div>
          <div style="font-size:0.8em;color:#333;">Recipe: {recipe_name}</div>
        </div>
      </div>
      <table style="width:100%;border-collapse:separate;border-spacing:0;margin:0;">
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
            <a href="?building={machine_encoded}" target="_self"
               style="display:inline-flex;flex-direction:column;align-items:center;gap:6px;
                      text-decoration:none;color:inherit;"
               title="View in Buildings">
              <img src="{machine_img}" width="80" height="80"
                   style="border:2px solid #38bdf8;border-radius:8px;background:#1a1a2e;
                          box-shadow:0 0 10px #38bdf833;">
              <span style="font-weight:600;font-size:1.05em;color:#7ec8e3;
                           text-shadow:0 0 8px #38bdf844;">{machine}</span>
              <span style="font-size:0.82em;color:#7ec8e3;">{cycle}s cycle &bull; {power} MW</span>
            </a>
          </td>
          <td style="padding:10px 12px;vertical-align:middle;">
            {item_cell(result['products'])}
          </td>
        </tr>
      </table>
    </div>'''


# --- BUILDING CARD FUNCTION ---
def building_card(bld: dict) -> str:
    """Return an HTML building info card styled in gold/blue theme matching recipe_card()."""
    name = bld['name']
    img = bld['image_url_large']
    category = bld['category'].upper()
    tier = bld['tier']
    unlock_name = bld['unlock_name'] or '—'
    description = bld['description']
    cost = bld['cost']  # list of {name, amount}
    produces = bld.get('produces', [])  # list of {name, class_key}

    tier_str = f'Tier {tier}' if tier is not None else '—'

    # Build cost chips — navigable links to ITEMS tab
    def cost_chips(cost_list):
        if not cost_list:
            return '<span style="color:#555;font-size:0.82em;">Free / Starting</span>'
        parts = []
        for c in cost_list:
            img_url = local_image_url(c['name'])
            encoded = c['name'].replace(' ', '%20').replace("'", "%27")
            parts.append(
                f'<a class="recipe-chip" href="?item={encoded}" target="_self">'
                f'<img src="{img_url}" width="28" height="28" '
                f'style="border-radius:3px;border:1px solid #444;background:#111;">'
                f'<span style="font-size:0.82em;color:#ccc;">'
                f'<span style="color:#e8d44d;font-weight:600;">{int(c["amount"])}&times;</span> '
                f'{c["name"]}</span></a>'
            )
        return ''.join(parts)

    # Produces chips — navigable links to ITEMS tab, grouped by tier label
    def produces_chips(produces_list):
        if not produces_list:
            return '<span style="color:#555;font-size:0.82em;">—</span>'
        
        # Group by tier_label
        grouped = {}
        for p in produces_list:
            tier = p.get('tier_label', 'T0')
            if tier not in grouped:
                grouped[tier] = []
            grouped[tier].append(p)
        
        # Tier sort order
        tier_order = ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "MAM", "ALT", "SHOP"]
        sorted_tiers = sorted(grouped.keys(), key=lambda x: tier_order.index(x) if x in tier_order else 99)
        
        # Build HTML: one row per tier group
        rows = []
        for tier in sorted_tiers:
            items = grouped[tier]
            chips_html = []
            for p in items:
                img_url = local_image_url(p['name'])
                encoded = p['name'].replace(' ', '%20').replace("'", "%27")
                chips_html.append(
                    f'<a class="recipe-chip" href="?item={encoded}" target="_self">'
                    f'<img src="{img_url}" width="28" height="28" '
                    f'style="border-radius:3px;border:1px solid #444;background:#111;">'
                    f'<span style="font-size:0.82em;color:#ccc;">{p["name"]}</span></a>'
                )
            tier_label_html = (
                f'<span style="font-size:0.66em;color:#38bdf855;letter-spacing:0.1em;'
                f'font-family:\'Share Tech Mono\',monospace;min-width:34px;text-align:right;'
                f'padding-right:8px;margin-right:8px;border-right:1px solid #38bdf826;line-height:1.9;">{tier}</span>'
            )
            row_html = (
                f'<div style="display:flex;align-items:flex-start;gap:0;margin-bottom:6px;">'
                f'{tier_label_html}'
                f'<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">{"".join(chips_html)}</div>'
                f'</div>'
            )
            rows.append(row_html)
        
        return ''.join(rows)

    desc_snippet = (description[:160] + '…') if len(description) > 160 else description

    return f'''
    <div style="background:linear-gradient(135deg,#0f0f23,#1a1a2e);border:1px solid #38bdf8;
                border-radius:10px;margin:12px 0;padding:0;font-family:Segoe UI,sans-serif;
                color:#eee;overflow:hidden;max-width:820px;
                box-shadow:0 0 15px #38bdf844, 0 0 30px #38bdf822;">
      <!-- Header bar (blue theme for buildings) -->
      <div style="background:linear-gradient(90deg,#0ea5e9,#0284c7);padding:8px 16px;
                  display:flex;align-items:center;gap:12px;">
        <img src="{img}" width="52" height="52"
             style="border:2px solid #fff;border-radius:6px;background:#1a1a2e;object-fit:contain;">
        <div>
          <div style="font-size:1.15em;font-weight:700;color:#fff;">{name}</div>
          <div style="font-size:0.78em;color:#bae6fd;letter-spacing:0.1em;">{category} &bull; {tier_str} &bull; {unlock_name}</div>
        </div>
      </div>
      <!-- Body -->
      <div style="padding:10px 16px 4px 16px;">
        {f'<div style="font-size:0.82em;color:#aaa;margin-bottom:8px;line-height:1.5;">{desc_snippet}</div>' if desc_snippet else ''}
        <table style="width:100%;border-collapse:separate;border-spacing:0;">
          <tr>
            <td style="padding:6px 8px;border-top:1px solid #1e293b;width:50%;vertical-align:top;">
              <div style="font-size:0.72em;color:#38bdf8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px;">Build Cost</div>
              <div style="line-height:1.8;">{cost_chips(cost)}</div>
            </td>
            <td style="padding:6px 8px;border-top:1px solid #1e293b;border-left:1px solid #1e293b;width:50%;vertical-align:top;">
              <div style="font-size:0.72em;color:#38bdf8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:4px;">Produces</div>
              <div style="line-height:1.8;max-height:500px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:#1e3a4a #0a0a1a;">{produces_chips(produces)}</div>
            </td>
          </tr>
        </table>
      </div>
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
        height: 300px !important;
        min-height: 300px !important;
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
        margin-top: -305px;
        margin-bottom: 5px;
        height: 300px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        text-align: center;
        padding: 16px 20px;
    }
    .obj-card-visual img {
        border-radius: 10px;
        border: 2px solid #555;
        background: #1a1a2e;
        margin-bottom: 10px;
        filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));
        width: calc(100% - 24px);
        max-width: 200px;
        height: auto;
        aspect-ratio: 1;
        object-fit: contain;
    }
    .obj-card-visual .obj-name {
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        font-size: 0.84rem;
        color: #000000;
        margin-bottom: 2px;
        line-height: 1.3;
    }
    .obj-card-visual .obj-qty {
        font-family: 'Share Tech Mono', monospace;
        font-size: 1.5rem;
        font-weight: 400;
        color: #7c3aed;
        text-shadow: 0 0 12px #7c3aed99, 0 0 28px #7c3aed44;
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

    /* ⚡ Phase selector — centred dark selectbox */
    div[data-testid="stSelectbox"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stSelectbox"] > div {
        max-width: 320px;
        width: 100%;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #0a0a1a !important;
        border: 1px solid #2a2a3a !important;
        border-radius: 6px !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.8rem !important;
        color: #e8d44d !important;
        letter-spacing: 0.08em !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
        border-color: #e8d44d88 !important;
    }
    div[data-testid="stSelectbox"] svg {
        fill: #e8d44d88 !important;
    }
    .recipe-chip {
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
    }
    .recipe-chip, .recipe-chip * {
        text-decoration: none !important;
    }
    .recipe-chip:hover {
        background: rgba(255,255,255,0.10);
    }
    @keyframes shimmer-once {
        0%   { background-position: -200% center; }
        100% { background-position:  200% center; }
    }
    .ghost-bar {
        background: linear-gradient(90deg, #2a1548 25%, #3d1f6e 50%, #2a1548 75%) !important;
        background-size: 400% 100% !important;
        animation: shimmer-once 2s ease-in-out 1 forwards !important;
    }
    .ghost-bar-dim {
        background: linear-gradient(90deg, #1a0e2e 25%, #2a1548 50%, #1a0e2e 75%) !important;
        background-size: 400% 100% !important;
        animation: shimmer-once 2s ease-in-out 1 forwards !important;
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
    st.session_state.selected_item = None  # ⚡ default: no selection — ghost placeholder shown
if "chip_item" not in st.session_state:
    st.session_state.chip_item = None
if "chip_building" not in st.session_state:
    st.session_state.chip_building = None

# ⚡ Query param handler: clicking a recipe chip sets ?item=Name
# Must run BEFORE st.tabs() so we can set the default tab to ITEMS
_queried_item = st.query_params.get("item")
if _queried_item:
    st.session_state.chip_item = _queried_item
    st.query_params.clear()

# ⚡ Query param handler: hotlinks set ?building=Name → jump to BUILDINGS tab
_queried_building = st.query_params.get("building")
if _queried_building:
    st.session_state.chip_building = _queried_building
    st.query_params.clear()

# ⚡ Query param handler: phase pill clicks set ?phase=N → update selected phase
_queried_phase = st.query_params.get("phase")
if _queried_phase:
    try:
        _phase_val = int(_queried_phase)
        if _phase_val in SPACE_ELEVATOR_PHASES:
            st.session_state.selected_phase = _phase_val
            st.session_state.selected_item = None
    except ValueError:
        pass
    st.query_params.clear()

# --- TABS ---
_default_tab = "ITEMS" if _queried_item else ("BUILDINGS" if _queried_building else None)
tab_objectives, tab_items, tab_buildings = st.tabs(
    ["OBJECTIVES", "ITEMS", "BUILDINGS"], default=_default_tab
)

# ================================================================
# TAB 1 — OBJECTIVES
# ================================================================
with tab_objectives:

    OBJECTIVES = SPACE_ELEVATOR_PHASES[st.session_state.selected_phase]
    _active = st.session_state.selected_phase

    # ⚡ Centred phase selector — selectbox in a narrow centre column
    _sel_l, _sel_c, _sel_r = st.columns([1, 2, 1])
    with _sel_c:
        selected = st.selectbox(
            "Space Elevator Phase",
            options=[1, 2, 3, 4, 5],
            index=st.session_state.selected_phase - 1,
            format_func=lambda x: f"Phase {x}  —  {PHASE_DESCRIPTIONS[x]}",
            key="phase_selector",
            label_visibility="collapsed",
        )
        if selected != st.session_state.selected_phase:
            st.session_state.selected_phase = selected
            st.session_state.selected_item = None
            st.rerun()

    st.markdown(
        f'<div class="section-title" style="text-align:center;">'
        f'// SPACE ELEVATOR &mdash; PHASE {_active} //'
        f'</div>',
        unsafe_allow_html=True,
    )


    cols = st.columns(len(OBJECTIVES), gap="medium")

    for i, obj in enumerate(OBJECTIVES):
        with cols[i]:
            img_url = local_image_url(obj["name"], 512)

            # The actual st.button — tall, text hidden via CSS
            if st.button("select", key=f"obj_btn_{i}", use_container_width=True):
                if st.session_state.selected_item == obj["name"]:
                    st.session_state.selected_item = None
                else:
                    st.session_state.selected_item = obj["name"]

            # Visual overlay — pulled up over the button via negative margin
            st.markdown(f"""
            <div class="obj-card-visual">
                <img src="{img_url}">
                <div class="obj-name">{obj["name"]}</div>
                <div class="obj-qty">{obj["required"]:,}</div>
                <div class="obj-label">required</div>
            </div>
            """, unsafe_allow_html=True)

    # ⚡ Recipe display — always render the divider + one st.markdown() to avoid
    # layout teardown/rebuild lag when toggling selection on/off.
    st.markdown('<hr class="hacker-divider">', unsafe_allow_html=True)

    _obj_selected = st.session_state.selected_item
    if _obj_selected:
        _obj_result = get_item_recipe(_obj_selected, data)
        if _obj_result:
            st.markdown(
                f'<div style="text-align:center;margin-bottom:4px;">'
                f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;'
                f'color:#e8d44d;letter-spacing:0.3em;text-transform:uppercase;'
                f'text-shadow:0 0 8px #e8d44d, 0 0 20px #d4a01788;">'
                f'&gt;&gt; {_obj_selected} &lt;&lt;</span></div>'
                + recipe_card(_obj_result),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"""
            <div class="status-box">
                &gt; ERROR: Recipe not found for {_obj_selected} &lt;
            </div>
            """, unsafe_allow_html=True)
    else:
        # ⚡ Purple ghost placeholder — shown before any objective card is clicked
        # Shimmer styles inlined (DOMPurify strips class attributes in separate st.markdown calls)
        _sb  = "background:linear-gradient(90deg,#2a1548 25%,#3d1f6e 50%,#2a1548 75%);background-size:400% 100%;animation:shimmer-once 2s ease-in-out 1 forwards;"
        _sbd = "background:linear-gradient(90deg,#1a0e2e 25%,#2a1548 50%,#1a0e2e 75%);background-size:400% 100%;animation:shimmer-once 2s ease-in-out 1 forwards;"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0c0816,#110e1e);
                    border:1px solid #a855f718;border-radius:10px;
                    margin:12px 0;overflow:hidden;max-width:820px;
                    box-shadow:0 0 12px #a855f708, 0 0 30px #a855f704;">
          <!-- Ghost header bar -->
          <div style="background:#0e0818;padding:10px 16px;
                      display:flex;align-items:center;gap:12px;
                      border-bottom:1px solid #a855f710;">
            <div style="width:48px;height:48px;border-radius:6px;flex-shrink:0;
                         background:#1a0e2e;border:2px solid #2a1548;opacity:0.6;"></div>
            <div style="display:flex;flex-direction:column;gap:7px;">
              <div style="width:160px;height:12px;border-radius:4px;opacity:0.6;{_sb}"></div>
              <div style="width:220px;height:9px;border-radius:4px;opacity:0.45;{_sbd}"></div>
            </div>
          </div>
          <!-- Ghost table -->
          <table style="width:100%;border-collapse:collapse;margin:0;">
            <tr style="background:#0a0612;">
              <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #a855f70e;width:40%;">
                <div style="width:90px;height:9px;border-radius:4px;opacity:0.45;margin:0 auto;{_sb}"></div>
              </th>
              <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #a855f70e;width:25%;">
                <div style="width:70px;height:9px;border-radius:4px;opacity:0.45;margin:0 auto;{_sb}"></div>
              </th>
              <th style="padding:8px 12px;text-align:center;border-bottom:1px solid #a855f70e;width:35%;">
                <div style="width:60px;height:9px;border-radius:4px;opacity:0.45;margin:0 auto;{_sb}"></div>
              </th>
            </tr>
            <tr>
              <td style="padding:14px 12px;vertical-align:middle;border-right:1px solid #a855f708;">
                <div style="display:flex;flex-direction:column;gap:8px;">
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:40px;height:40px;border-radius:4px;background:#1a0e2e;border:1px solid #2a1548;opacity:0.5;flex-shrink:0;"></div>
                    <div style="display:flex;flex-direction:column;gap:5px;">
                      <div style="width:100px;height:9px;border-radius:4px;opacity:0.45;{_sb}"></div>
                      <div style="width:60px;height:7px;border-radius:4px;opacity:0.35;{_sbd}"></div>
                    </div>
                  </div>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:40px;height:40px;border-radius:4px;background:#1a0e2e;border:1px solid #2a1548;opacity:0.5;flex-shrink:0;"></div>
                    <div style="display:flex;flex-direction:column;gap:5px;">
                      <div style="width:80px;height:9px;border-radius:4px;opacity:0.45;{_sb}"></div>
                      <div style="width:50px;height:7px;border-radius:4px;opacity:0.35;{_sbd}"></div>
                    </div>
                  </div>
                </div>
              </td>
              <td style="padding:14px 12px;text-align:center;vertical-align:middle;border-right:1px solid #a855f708;">
                <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
                  <div style="width:90px;height:11px;border-radius:4px;opacity:0.5;{_sb}"></div>
                  <div style="width:110px;height:8px;border-radius:4px;opacity:0.35;{_sbd}"></div>
                </div>
              </td>
              <td style="padding:14px 12px;vertical-align:middle;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <div style="width:40px;height:40px;border-radius:4px;background:#1a0e2e;border:1px solid #2a1548;opacity:0.5;flex-shrink:0;"></div>
                  <div style="display:flex;flex-direction:column;gap:5px;">
                    <div style="width:100px;height:9px;border-radius:4px;opacity:0.45;{_sb}"></div>
                    <div style="width:60px;height:7px;border-radius:4px;opacity:0.35;{_sbd}"></div>
                  </div>
                </div>
              </td>
            </tr>
          </table>
          <!-- Prompt -->
          <div style="text-align:center;padding:10px 0 12px 0;
                       border-top:1px solid #a855f70a;
                       border-radius:0 0 10px 10px;background:#0c0816;">
            <span style="font-family:'Share Tech Mono',monospace;
                          font-size:0.68rem;letter-spacing:0.28em;
                          color:#a855f744;text-transform:uppercase;
                          text-shadow:0 0 14px #a855f722;">
              select an objective for recipe details
            </span>
          </div>
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
                img.style.cssText = 'width:32px;height:32px;object-fit:contain;border-radius:4px;border:1px solid #333;background:#111;';
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
            var filterInput = wrapper.querySelector('.ag-floating-filter-input input');
            if (filterInput) filterInput.setAttribute('placeholder', 'Search items');
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
        ".ag-root": {
            "background-color": "#000000 !important",
        },
        # Header row (hidden via headerHeight=0 but just in case)
        ".ag-header": {
            "background-color": "#000000 !important",
            "border-bottom": "none !important",
        },
        ".ag-header-viewport": {
            "background-color": "#000000 !important",
            "border": "none !important",
        },
        ".ag-pinned-left-header": {
            "background-color": "#000000 !important",
            "border": "none !important",
        },
        ".ag-pinned-right-header": {
            "background-color": "#000000 !important",
            "border": "none !important",
        },
        ".ag-floating-filter-body": {
            "background-color": "#000000 !important",
            "border": "none !important",
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
            "display": "none !important",
        },
        # Kill resize handles (source of corner/pixel artifacts)
        ".ag-header-cell-resize": {
            "display": "none !important",
        },
        ".ag-header-cell-resize::after": {
            "display": "none !important",
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
    else:
        # ⚡ Empty-state placeholder — keep layout stable, no hint box
        with recipe_placeholder.container():
            st.markdown("", unsafe_allow_html=True)

# ================================================================
# TAB 3 — BUILDINGS
# ================================================================

# ⚡ Category pill order and labels for the PRODUCTION inner tab
_BLD_CATEGORIES = ["All", "Production", "Extraction", "Power", "Logistics",
                   "Storage", "Transit", "Structure", "Decor", "Special"]

# ⚡ AgGrid icon renderer for buildings (same pattern as Items tab)
_bld_icon_renderer = JsCode("""
class IconCellRenderer {
    init(params) {
        this.eGui = document.createElement('span');
        this.eGui.style.cssText = 'display:flex;align-items:center;justify-content:center;height:100%;';
        if (params.value) {
            var img = document.createElement('img');
            img.src = params.value;
            img.style.cssText = 'width:32px;height:32px;object-fit:contain;border-radius:4px;border:1px solid #333;background:#111;';
            this.eGui.appendChild(img);
        }
    }
    getGui() { return this.eGui; }
    refresh() { return false; }
}
""")

# ⚡ Shared dark AgGrid CSS for buildings grid
_bld_aggrid_css = {
    ".ag-root-wrapper": {
        "background-color": "#000000 !important",
        "border": "none !important",
        "font-family": "'Share Tech Mono', monospace !important",
    },
    # ⚡ Header row is hidden (headerHeight=0) — zero out all rendering
    ".ag-header": {
        "background-color": "#000000 !important",
        "border-bottom": "none !important",
    },
    # ⚡ Kill column resize handles — the source of white dot pixel glitches
    ".ag-header-cell-resize": {
        "display": "none !important",
    },
    ".ag-header-cell-resize::after": {
        "display": "none !important",
    },
    # Floating filter bar — sits at top, acts as the search row
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
    ".ag-floating-filter:first-child": {
        "display": "none !important",
    },
    ".ag-body-viewport": {
        "background-color": "#000000 !important",
    },
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
        "background-color": "rgba(56,189,248,0.06) !important",
    },
    ".ag-row-selected": {
        "background-color": "rgba(56,189,248,0.12) !important",
        "color": "#ffffff !important",
    },
    ".ag-cell": {
        "border-right": "none !important",
        "line-height": "52px !important",
    },
    ".ag-overlay-no-rows-center": {
        "color": "#555555 !important",
        "font-family": "'Share Tech Mono', monospace !important",
        "font-size": "0.75rem !important",
        "letter-spacing": "0.2em !important",
    },
    ".ag-body-viewport::-webkit-scrollbar": {"width": "6px !important"},
    ".ag-body-viewport::-webkit-scrollbar-track": {"background": "#000000 !important"},
    ".ag-body-viewport::-webkit-scrollbar-thumb": {
        "background": "#1e3a4a !important",
        "border-radius": "3px !important",
    },
}

# ⚡ onFirstDataRendered JS — deselect on filter change + "clear" button in icon col
_bld_on_ready_js = JsCode("""
function(params) {
    params.api.addEventListener('filterChanged', function() {
        params.api.deselectAll();
    });
    setTimeout(function() {
        var wrapper = document.querySelector('.ag-root-wrapper');
        if (!wrapper) return;

        // ⚡ Replace icon-column floating filter cell with a "clear" button
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
            btn.onmouseover = function() { btn.style.color='#38bdf8'; btn.style.borderColor='#38bdf8'; };
            btn.onmouseout  = function() { btn.style.color='#555'; btn.style.borderColor='#333'; };
            btn.onclick = function() {
                params.api.setFilterModel(null);
                var input = wrapper.querySelector('.ag-floating-filter-input input');
                if (input) {
                    input.value = '';
                    input.dispatchEvent(new Event('input', {bubbles: true}));
                }
            };
            firstFilter.appendChild(btn);
        }
        var filterInput = wrapper.querySelector('.ag-floating-filter-input input');
        if (filterInput) filterInput.setAttribute('placeholder', 'Search buildings');
    }, 200);
}
""")

with tab_buildings:
    st.markdown('<div class="section-title">// BUILDINGS DATABASE //</div>',
                unsafe_allow_html=True)

    # ⚡ Inner sub-tabs: PRODUCTION and UPGRADES
    bld_tab_prod, bld_tab_upgrades = st.tabs(["PRODUCTION", "UPGRADES"])

    # ----------------------------------------------------------------
    # PRODUCTION inner tab
    # ----------------------------------------------------------------
    with bld_tab_prod:

        # ⚡ All buildings — no category filtering, search via AgGrid floating filter
        all_buildings = list_buildings(data)
        # ⚡ Enrich each building with produces list
        for _b in all_buildings:
            _b["produces"] = get_building_produces(_b["class_key"], data)

        # ⚡ Count label
        st.markdown(
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;'
            f'color:#38bdf866;text-align:right;margin-bottom:4px;letter-spacing:0.1em;">'
            f'{len(all_buildings)} BUILDINGS</div>',
            unsafe_allow_html=True,
        )

        # ⚡ Build DataFrame for AgGrid
        df_bld = pd.DataFrame([
            {
                "icon": b["image_url"],
                "name": b["name"],
            }
            for b in all_buildings
        ])

        # ⚡ Grid options
        gb_bld = GridOptionsBuilder.from_dataframe(df_bld)

        gb_bld.configure_column(
            field="icon", header_name="",
            cellRenderer=_bld_icon_renderer,
            width=60, maxWidth=60, minWidth=60,
            sortable=False, filter=False, resizable=False, suppressMovable=True,
        )
        gb_bld.configure_column(
            field="name", header_name="BUILDING",
            floatingFilter=True, filter="agTextColumnFilter",
            filterParams=JsCode("""{
                filterOptions: ['contains'],
                defaultOption: 'contains',
                maxNumConditions: 1,
            }"""),
            flex=2, suppressMovable=True,
        )

        gb_bld.configure_selection(selection_mode="single", use_checkbox=False)
        gb_bld.configure_grid_options(
            rowHeight=52,
            headerHeight=0,
            floatingFiltersHeight=40,
            suppressHorizontalScroll=True,
            suppressCellFocus=True,
            suppressRowDeselection=False,
            domLayout="normal",
            onFirstDataRendered=_bld_on_ready_js,
        )

        bld_grid_options = gb_bld.build()

        # ⚡ Placeholder for detail card — sits ABOVE the grid
        bld_placeholder = st.empty()

        # ⚡ Render the grid
        bld_grid_response = AgGrid(
            df_bld,
            gridOptions=bld_grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=500,
            allow_unsafe_jscode=True,
            theme="alpine",
            custom_css=_bld_aggrid_css,
        )

        # ⚡ Row click → look up full building data and render detail card
        # Always renders exactly one st.markdown() — either real card or ghost.
        # No st.empty() — avoids layout teardown/rebuild lag on deselect.
        bld_selected_rows = bld_grid_response.get("selected_rows", None)
        bld_selected_name = None

        if bld_selected_rows is not None:
            if isinstance(bld_selected_rows, pd.DataFrame) and len(bld_selected_rows) > 0:
                bld_selected_name = bld_selected_rows.iloc[0]["name"]
                st.session_state.chip_building = None  # grid click overrides hotlink
            elif isinstance(bld_selected_rows, list) and len(bld_selected_rows) > 0:
                bld_selected_name = bld_selected_rows[0]["name"]
                st.session_state.chip_building = None

        # Hotlink via ?building= takes effect if nothing clicked in grid
        if not bld_selected_name and st.session_state.chip_building:
            bld_selected_name = st.session_state.chip_building

        # ⚡ Render detail card into placeholder above the grid
        if bld_selected_name:
            bld_detail = next(
                (b for b in all_buildings if b["name"] == bld_selected_name), None
            )
            if bld_detail:
                with bld_placeholder.container():
                    st.markdown(
                        f'<div style="text-align:center;margin-bottom:4px;">'
                        f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:0.75rem;'
                        f'color:#38bdf8;letter-spacing:0.3em;text-transform:uppercase;'
                        f'text-shadow:0 0 8px #38bdf8, 0 0 20px #0ea5e988;">'
                        f'&gt;&gt; {bld_selected_name} &lt;&lt;</span></div>'
                        + building_card(bld_detail),
                        unsafe_allow_html=True,
                    )

    # ----------------------------------------------------------------
    # ⚡ UPGRADES inner tab — curated Mk.N progression chains
    # ----------------------------------------------------------------
    with bld_tab_upgrades:

        # ⚡ Curated chains: (section label, slug prefix)
        # Pipeline deduplication: filter out "(No Indicator)" variants
        _UPGRADE_CHAINS = [
            ("MINERS",          "miner"),
            ("CONVEYOR BELTS",  "conveyor-belt"),
            ("CONVEYOR LIFTS",  "conveyor-lift"),
            ("PIPELINES",       "pipeline-mk"),
            ("PIPELINE PUMPS",  "pipeline-pump"),
        ]

        def _upgrade_card_html(bld: dict) -> str:
            """Return HTML for a single Mk tier card in an upgrade chain strip."""
            img   = bld["image_url_large"]
            name  = bld["name"]
            power = bld["power_mw"]
            tier  = bld["tier"]
            cost  = bld["cost"]

            if power < 0:
                power_str = (
                    f'<span style="color:#4ade80;font-size:0.8em;">+{abs(power):.0f} MW</span>'
                )
            elif power > 0:
                power_str = (
                    f'<span style="color:#7ec8e3;font-size:0.8em;">{power:.0f} MW</span>'
                )
            else:
                power_str = '<span style="color:#444;font-size:0.8em;">— MW</span>'

            tier_str = (
                f'<span style="color:#38bdf8;font-size:0.72em;letter-spacing:0.1em;">T{tier}</span>'
                if tier else
                '<span style="color:#333;font-size:0.72em;">—</span>'
            )

            # Cost: up to 3 chips, rest truncated
            cost_parts = []
            for c in cost[:3]:
                img_c = local_image_url(c["name"], 64)
                cost_parts.append(
                    f'<span style="display:inline-flex;align-items:center;gap:3px;'
                    f'margin:2px 3px;border-radius:5px;padding:2px 5px;'
                    f'background:rgba(255,255,255,0.05);border:1px solid #2a2a3a;'
                    f'white-space:nowrap;">'
                    f'<img src="{img_c}" width="18" height="18" '
                    f'style="border-radius:2px;border:1px solid #333;background:#111;">'
                    f'<span style="font-size:0.72em;color:#aaa;">'
                    f'<span style="color:#e8d44d;">{int(c["amount"])}&times;</span>'
                    f'</span></span>'
                )
            if len(cost) > 3:
                cost_parts.append(
                    f'<span style="font-size:0.68em;color:#444;">+{len(cost)-3} more</span>'
                )
            cost_html = "".join(cost_parts) if cost_parts else (
                '<span style="font-size:0.72em;color:#444;">free</span>'
            )

            return (
                f'<div style="display:flex;flex-direction:column;align-items:center;'
                f'background:linear-gradient(160deg,#0a0a1a,#111827);'
                f'border:1px solid #1e3a4a;border-radius:10px;padding:12px 10px 10px 10px;'
                f'min-width:130px;max-width:160px;gap:6px;'
                f'box-shadow:0 0 8px #38bdf811;transition:border-color 0.2s;">'
                # Image
                f'<img src="{img}" width="72" height="72" '
                f'style="border:2px solid #1e3a4a;border-radius:8px;'
                f'background:#0a0a1a;object-fit:contain;">'
                # Name
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.78em;'
                f'color:#e0f2fe;text-align:center;line-height:1.3;'
                f'letter-spacing:0.04em;">{name}</div>'
                # Power + Tier row
                f'<div style="display:flex;gap:8px;align-items:center;justify-content:center;">'
                f'{power_str} {tier_str}</div>'
                # Cost chips
                f'<div style="display:flex;flex-wrap:wrap;justify-content:center;'
                f'gap:2px;margin-top:2px;">{cost_html}</div>'
                f'</div>'
            )

        def _arrow_html() -> str:
            """Chevron arrow between upgrade tier cards."""
            return (
                '<div style="display:flex;align-items:center;padding:0 4px;'
                'color:#38bdf866;font-size:1.4em;flex-shrink:0;">&#8250;</div>'
            )

        def _render_chain(label: str, prefix: str) -> str:
            """Build the full HTML for one upgrade chain section."""
            chain = get_upgrade_chain(prefix, data)
            # Deduplicate by Mk number — keeps first seen (standard, not No Indicator)
            seen_mk = {}
            deduped = []
            for b in chain:
                slug = b["slug"]
                try:
                    idx = slug.index("-mk-")
                    mk  = int(slug[idx + 4:].split("-")[0])
                except (ValueError, IndexError):
                    mk = 99
                if mk not in seen_mk:
                    seen_mk[mk] = True
                    deduped.append(b)

            if not deduped:
                return ""

            # Section header
            html = (
                f'<div style="font-family:\'Share Tech Mono\',monospace;'
                f'font-size:0.72rem;color:#38bdf8;letter-spacing:0.2em;'
                f'text-transform:uppercase;margin:18px 0 8px 2px;">'
                f'// {label}</div>'
                f'<div style="display:flex;align-items:center;flex-wrap:nowrap;'
                f'overflow-x:auto;gap:0;padding-bottom:8px;'
                f'scrollbar-width:thin;scrollbar-color:#1e3a4a #000;">'
            )
            for i, bld in enumerate(deduped):
                if i > 0:
                    html += _arrow_html()
                html += _upgrade_card_html(bld)
            html += "</div>"
            return html

        # ⚡ Render all chains
        all_chains_html = ""
        for chain_label, chain_prefix in _UPGRADE_CHAINS:
            all_chains_html += _render_chain(chain_label, chain_prefix)

        st.markdown(
            f'<div style="padding:4px 0 16px 0;">{all_chains_html}</div>',
            unsafe_allow_html=True,
        )

# --- FOOTER ---
st.markdown("""
<div class="corner-deco">
    &#9632;&#9632;&#9632; FICSIT INC. AUTHORIZED TERMINAL &#9632;&#9632;&#9632;
</div>
""", unsafe_allow_html=True)
