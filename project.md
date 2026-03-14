# ULTRA SATISFACTORY
### Project Documentation — `project.md`

---

> The way I write code with AI is that I start with a project.md file, where I describe what I want done. I then ask it to make a plan from that project.md to describe the changes it will make (or what it will create if greenfield).
> I then iterate on that plan with the AI until it's what I want. I then ask it to execute — don't do anything else, don't ask me any questions, work until it's complete.
> I then commit the project.md along with the code.
> The main reason I do this is so that when the models get a lot better in a year, I can go back and ask them to modify the plan based on project.md and the existing code, on the assumption they might find their own mistakes.
>
> — jedberg on [https://news.ycombinator.com/item?id=47214629](https://news.ycombinator.com/item?id=47214629)

> ⚡ **Note from Luke**
>
> - The above is methodology I use for inspiration. Do not stick to it rigidly — I have the ultimate say in how we collaborate. Follow the spirit of it, offer helpful suggestions to stay on target, but otherwise do as I tell you.
> - `⚡` marks every agentic contribution — any bullet, line, or block written by AI gets this prefix. This makes it easy to see what was human intent vs. AI output at a glance.

> ⚠️ **ENVIRONMENT**: Windows machine — always use **Command Prompt** (`cmd`), never bash or PowerShell. Run Python via `python` (e.g. `python -m streamlit`).

---

## Objective

**ULTRA-SATISFACTORY** — A companion app for the factory-building game *Satisfactory* that gives you instant access to all the game data you need. Runs alongside the game for instant access to:

- **`BUILDINGS`** — purpose, unlock tier, power draw
- **`ITEMS`** — ingredient list and quantities, which machine produces it, production rate
- **`OBJECTIVES`** — focus on your current milestones, and unlocks

---

## Background

- **Game:** *Satisfactory* — a first-person open-world factory builder. Players unlock tiers of buildings and items progressively. Recipes have inputs, outputs, machines, and rates. The complexity escalates fast.
- **Data source:** The [Satisfactory Wiki](https://satisfactory.wiki.gg) and/or community-maintained JSON datasets (e.g. `satisfactory-calculator` data exports). Data is static — game patches occasionally change recipes but the core dataset is stable.
- **Stack:** Python + Streamlit + streamlit-aggrid. Single `app/app.py` file. All styling inline via `st.markdown` + AgGrid `custom_css`. Fonts: Orbitron + Share Tech Mono (Google Fonts). No database — data loaded from flat files (JSON) at startup.
- **Display:** Grayscale DC display. High-contrast black/white/gray palette only. All color decisions assume zero color rendering. (Full colour option is a future phase.)
- **Deployment (Phase 1):** Local machine, runs alongside the game. Launched manually via `cmd`. Auto-reloads on file save (`--server.runOnSave=true`).
- **Deployment (Phase N):** [Stlite](https://github.com/whitphx/stlite) — runs Streamlit entirely in the browser via WebAssembly (Pyodide). No server, no backend. Deployable as static files to GitHub Pages. Goal is a zero-install companion accessible from any device, including in-game overlay via browser.



---

## Open Questions

- ☐ Best community data source for recipes/buildings — wiki scrape, or pre-built JSON dataset?
- ☐ Does the data need to be versioned per game patch, or is the current stable release enough?
- ☐ Should the app support multiple simultaneous active objectives, or one at a time?
- ☐ Search UX — free-text search, category browse, or both?
- ☐ Should recipe chains be shown recursively (raw materials all the way down) or just one level deep?
- ☐ Stlite constraints — no filesystem writes, no subprocess, limited packages. Need to verify all required packages (e.g. `pandas`) are available in Pyodide before committing to the stack.
- ☐ Asset hosting — game data JSON files can live directly in the GitHub repo (simplest, version-controlled, free). S3 is an option if files get large or need to be updated independently of the app. Decide based on data file size once the source is confirmed.

---

## Discoveries

- ⚡ **Data source confirmed:** `greeny/SatisfactoryTools` `data.json` is the best community dataset. Single JSON file, complete recipes, ingredients, machines, rates. Raw URL: `https://raw.githubusercontent.com/greeny/SatisfactoryTools/master/data/data.json`. Verified March 2026.
- ⚡ **Wiki image URL pattern:** `https://satisfactory.wiki.gg/images/thumb/{Item_Name}.png/40px-{Item_Name}.png` where spaces become underscores. No auth required. Verified on Versatile Framework, March 2026.
- ⚡ **Wiki license:** CC BY-NC-SA 4.0. Fine for a personal/non-commercial tool.
- ⚡ **Asset hosting:** `data.json` is small enough to live directly in the repo under `data/`. No S3 needed for Phase 1.
- ⚡ **Invisible button pattern abandoned:** the `st.button` + visual overlay trick (font-size:0, negative margin) breaks when global button CSS bleeds into item rows. Pure HTML `<table>` with `onclick` + `st.query_params` is the correct pattern for clickable HTML lists in Streamlit.
- ⚡ **Query param navigation pattern:** `onclick="window.location.href='?item=Name'"` on any HTML element triggers a full page rerun; reading `st.query_params.get("item")` at the top of the script (before tabs) sets session state before widgets render. `st.query_params.clear()` removes the param without an extra rerun. Special sentinel `__clear__` used for deselection.
- ⚡ **CSS bleed fix:** removing `st.button` from the Items tab entirely eliminates the global `div.stButton > button` CSS bleed. No scoping gymnastics required — the selector simply has no targets in that tab.
- ⚡ **Stlite compatibility:** `st.query_params`, `st.session_state`, `st.cache_data`, `st.tabs`, `st.text_input`, `st.button` all work in stlite. `onclick` JS navigating via `window.location.href` works in stlite (runs in a real browser). `data.json` will need to be mounted via stlite `files` option at deploy time — not a Phase 2 concern.
- ⚡ **Streamlit `<script>` tags stripped:** `st.markdown(..., unsafe_allow_html=True)` strips `<script>` tags entirely. JS injection via `st.markdown` does not work for custom search logic. Use `st.components.v1.html()` or a proper component (e.g. AgGrid) for client-side interactivity.
- ⚡ **`st.text_input` fires on blur/Enter only:** not per-keystroke. No debounce or real-time mode available in Streamlit 1.55.0. For instant search, must use a component with its own input (e.g. AgGrid floating filter).
- ⚡ **AgGrid floating filter = true instant search:** `streamlit-aggrid` v1.2.1 with `floatingFilter=True` on a column renders a persistent filter input inside the grid component. Filtering is entirely client-side, per-keystroke, zero Python rerun. `JsCode` class-based cell renderers work for custom icon columns. Requires `allow_unsafe_jscode=True`.

---

## Decisions

- ⚡ **Data source:** `greeny/SatisfactoryTools` `data.json` — most complete, community-maintained, no scraping required.
- ⚡ **Images:** reference wiki.gg image URLs directly — no need to host images locally or in S3.
- ⚡ **Asset hosting:** `data.json` committed to `data/` in the repo — simple, version-controlled, zero infrastructure.
- ⚡ **Phase 1 deployment:** local Streamlit only. Stlite/GitHub Pages deferred to a later phase.

---

## Plan

### Phase 1 — Foundation + Item Lookup

Set up the project scaffold (nbdev, mamba env, data), build the core item lookup function, and wire it into the Streamlit UI with clickable item buttons and recipe detail panels for the 6 current in-game objective items. Proves the full stack end-to-end.

### Phase 2 — Tabs + Item Browser

Add top-level tab navigation (Objectives, Items, Buildings), a fully searchable item browser with instant per-keystroke filtering via AgGrid floating filter, icon + name columns, and inline recipe cards on row selection.

---

## Agent Conventions

_Rules for how the AI operates on this project. Applied every session._

1. ⚡ For agentic contributions, use `⚡` emoji at the start of every bullet point, line, or text for clarity.

2. ⚡ Add documentation and comments in code files for flexibility and future reproducibility.

3. ⚡ Test any new functionality with sample data to ensure it works correctly before marking a todo complete.

4. ⚡ Prepare for iteration: structure code to easily modify filters, parameters, and logic for subsequent work.

5. ⚡ **Todo formatting convention:** when a todo item is completed, change `☐` to `☑` and wrap the bold title in `<span style="color: purple">...</span>` — e.g. `☑ <span style="color: purple">**Task name**</span> — description`. This renders in VS Code preview.

6. ⚡ **Markdown style:** no em dashes; use concise bullet points; highlight key terms with `<span style="color: purple">...</span>`.

7. ⚡ **Never assume:** never assume file structure, function signatures, API shapes, or column names — always read the file or verify first before writing code that depends on it.

8. ⚡ **Collaboration convention:** if Luke makes manual edits to any file outside of this conversation (e.g. via VS Code), he will say "I've made edits" before asking for further changes — at that point, always re-read the file before touching anything. Remind Luke to say "I've made edits" if he forgets.

9. ⚡ **Git commits:** commit regularly — at natural checkpoints (end of a todo, after a key discovery, after a working implementation). Write concise but descriptive messages, e.g. `feat: add X` or `fix: correct Y`.

10. ⚡ **Auto-reorder todo list:** whenever a todo item is completed, automatically reorder the todo list so completed items (`☑`) appear at the top of their phase (in order of completion) and pending items (`☐`) follow below. Notify Luke when reordering occurs.

---

## Todo List

> 💡 **Tip:** `Ctrl+K, V` in VS Code for a live Markdown preview — no manual revert needed.
>
> **Conventions:**
> - `☐` pending → `☑` done on completion
> - On completion: wrap title in `<span style="color: purple">...</span>`
> - Completed items float to the **top** of their phase (in order of completion)
> - Each item should be small enough to complete in one session
> - `⚡` prefix on items written or added by the AI

━━━━━━━━━━━━━━━━━━━━━[ PHASE 1 ]━━━━━━━━━━━━━━━━━━━━━

1. ☑ <span style="color: purple">**Init nbdev**</span> — ran `nbdev_new`, scaffold created under `ultra_satisfactory/`; uses `pyproject.toml` (no `settings.ini` in modern nbdev); default `00_core` removed
2. ☑ <span style="color: purple">**Source and commit game data**</span> — `data/data.json` downloaded from `greeny/SatisfactoryTools`; all 6 target items and their standard recipes confirmed present
3. ☑ <span style="color: purple">**Build data loader notebook**</span> — `nbs/00_data.ipynb` written; exports `load_data`, `wiki_image_url`, `get_item_recipe` to `ultra_satisfactory/data.py` via `nbdev_export`; all 6 items tested and passing
4. ☑ <span style="color: purple">**Build item lookup function**</span> — `get_item_recipe` returns name, description, image_url, ingredients, products, machine, power, cycle_time, recipe_name, alternate flag; all target items verified
5. ☑ <span style="color: purple">**Wire up Streamlit UI**</span> — Space Elevator Phase 3 objective buttons (Versatile Framework 2500, Modular Engine 500, Adaptive Control Unit 100); each is a full-card clickable button showing wiki image + required quantity; clicking expands gold/blue recipe card below with ingredients, machine, rates
6. ☑ <span style="color: purple">**Verify wiki image URLs render**</span> — wiki.gg image URLs confirmed rendering in Streamlit for all 3 Phase 3 items via direct `<img>` tags in `st.markdown`

━━━━━━━━━━━━━━━━━━━━━[ PHASE 2 ]━━━━━━━━━━━━━━━━━━━━━

1. ☑ <span style="color: purple">**Tab navigation**</span> — `app/app.py` rewritten with `st.tabs(["OBJECTIVES", "ITEMS", "BUILDINGS"])`; logo + divider sit above tabs; Objectives content moved into tab 1 unchanged (button keys updated to `obj_btn_{i}`); Items + Buildings stubs added; tab CSS: Share Tech Mono, uppercase, `#555` inactive, `#ffffff` active with glow + `border-bottom: 2px solid #ffffff`
2. ☑ <span style="color: purple">**`list_items()` in notebook + export**</span> — `list_items(data)` added to `nbs/00_data.ipynb` and exported to `ultra_satisfactory/data.py`; returns 140 craftable items sorted A-Z, each `{class_key, name, image_url}` at 40px; raw resources excluded; verified with test script
3. ☑ <span style="color: purple">**Items tab — HTML table + query param navigation**</span> — ⚡ rewrote Items tab on branch `phase-2-items-html-table`; abandoned invisible-button pattern entirely; single `st.markdown` HTML `<table>` with 140 rows (32px icon + name); each `<tr onclick>` sets `?item=Name` in URL triggering rerun; query param handler at top of script reads param before tabs render, sets `items_selected`, calls `st.query_params.clear()`; `__clear__` sentinel handles deselection; active row highlighted server-side (inline style on matching `<tr>`); recipe card rendered below the full table; CSS bleed from Objective button styles is gone because no `st.button` widgets exist in the Items tab
4. ☑ <span style="color: purple">**Clickable ingredient/product chips in `recipe_card`**</span> — ⚡ each chip `<div>` in `item_cell()` gets `onclick="window.location.href='?item='+encodeURIComponent('Name')"`; hover via `onmouseover`/`onmouseout` inline handlers (`rgba(255,255,255,0.10)` flash, `border-radius: 6px`); same query param handler catches these clicks and sets `items_selected`
5. ☑ <span style="color: purple">**Buildings tab stub**</span> — ⚡ centred placeholder in Share Tech Mono: `// BUILDINGS DATABASE //` + `COMING SOON`; no logic
6. ☑ <span style="color: purple">**Update `project.md`**</span> — ⚡ Phase 2 todos marked complete; discoveries added
7. ☑ <span style="color: purple">**Items tab — AgGrid rewrite with instant search**</span> — ⚡ replaced fat-button list + broken JS search with `streamlit-aggrid` v1.2.1; two columns: icon (60px, `JsCode` class-based `IconCellRenderer` rendering 32x32 wiki images) + name (flex, `floatingFilter=True` with `agTextColumnFilter` "contains" mode for per-keystroke client-side filtering); `headerHeight=0` hides column headers, floating filter bar serves as the search input; single-row click selection via `GridUpdateMode.SELECTION_CHANGED` triggers rerun and renders recipe card below grid; dark grayscale theme via `custom_css` overrides on alpine base (black bg, `#cccccc` text, invisible column borders, styled scrollbar); removed all old Items CSS (`.items-search-wrap`, `.item-row-btn`, `.item-row-visual`); removed `items_selected` session state
8. ☑ <span style="color: purple">**Compact header + slow cog rotation**</span> — ⚡ header changed from vertical stacking (icon above title above subtitle) to horizontal flex layout (48px cog left, title+subtitle right in `.logo-text` wrapper); SVG shrunk from 80x80 to 48x48; title from 2.2rem to 1.4rem; subtitle from 0.85rem to 0.7rem; all padding/margins reduced; added `@keyframes slow-spin` (60s per full rotation, linear) stacked with existing `pulse-glow` via comma-separated `animation`; divider margin halved
9. ☑ <span style="color: purple">**Recipe card UX fixes**</span> — ⚡ recipe card moved above AgGrid via `st.empty()` placeholder (renders between section title and grid instead of below 500px grid box); `onFirstDataRendered` JS callback injects subtle "clear" button into icon column's floating filter area (`#555` text, lights to `#ccc` on hover); same callback adds `filterChanged` listener that calls `deselectAll()` to dismiss stale recipe card when user types a new search
10. ☑ <span style="color: purple">**Clickable ingredient/product chips in recipe card (AgGrid)**</span> — ⚡ each chip `<div>` in `item_cell()` gets `onclick="window.location.href='?item='+encodeURIComponent('Name')"` with hover highlight (`rgba(255,255,255,0.10)`); query param handler at top of Items tab reads `?item=Name`, clears param, renders recipe card into placeholder above grid; grid row click takes priority over chip navigation; no session state persistence needed — card shows for one rerun only

---

## Debug Log

_One entry per issue. Before touching any code, list hypotheses ranked by likelihood. Then instrument. Then fix. This section stays empty until there is something to debug._

---

## Phase Summaries

_Written after each phase completes. 3-5 lines. What actually happened, what was found, what was surprising. The compressed artifact for future sessions and future models._

### Phase 1

⚡ Foundation built: mamba env, nbdev scaffold, `data.json` committed, `data.py` exports (`load_data`, `wiki_image_url`, `get_item_recipe`, `list_items`). Streamlit UI with Space Elevator Phase 3 objective cards (fat invisible `st.button` + visual overlay trick). Wiki image URLs render directly via `<img>` tags. End-to-end stack proven.

### Phase 2 (in progress)

⚡ Tab navigation added (Objectives / Items / Buildings). Items tab went through three iterations: (1) HTML table with query param onclick — worked but no instant search; (2) fat-button list with JS `oninput` filtering — failed because Streamlit strips `<script>` tags from `st.markdown`; (3) **AgGrid with floating filter** — works perfectly, per-keystroke client-side filtering, icon + name columns, dark grayscale theme via `custom_css`. The key discovery: Streamlit's HTML sanitizer blocks `<script>` injection, so any client-side interactivity must go through a proper component. AgGrid's floating filter is the cleanest solution for instant search without a Python rerun.

---
