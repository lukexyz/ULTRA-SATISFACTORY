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
- **Deployment (live):** [Streamlit Community Cloud](https://ultra-satisfactory.streamlit.app/) — full server-side Streamlit, auto-deploys from `main` on push. GitHub Pages stlite build also live at `https://lukexyz.github.io/ULTRA-SATISFACTORY/`.



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
- ⚡ **`st.markdown` strips all JS event handlers:** `onclick`, `onmouseover`, `onmouseout` are all stripped by DOMPurify even with `unsafe_allow_html=True`. Only `<a href>`, `class`, `style`, and `data-*` attributes survive. Hover effects must use CSS `:hover` rules; click navigation must use `<a href="?item=Name">` anchor tags.
- ⚡ **`components.html()` iframe sandbox blocks navigation:** clicks inside a `components.html()` iframe cannot navigate the parent page. `window.parent.location.href` and `<a target="_top">` are both blocked by the sandbox. Cannot use for clickable recipe chips.
- ⚡ **`st.tabs` `default` parameter:** `st.tabs(["A", "B", "C"], default="B")` sets the active tab programmatically on render. Added in Streamlit 1.36.0, present in 1.55.0. Accepts `None` (uses first tab). Key for landing on the correct tab after a chip-click full page reload.
- ⚡ **Query param handler must run before `st.tabs()`:** reading `st.query_params.get("item")` inside a `with tab_items:` block is too late — Streamlit has already decided which tab is active. The handler must run at module level before `st.tabs()` so `default=` can be set correctly.
- ⚡ **`st.html(unsafe_allow_javascript=True)` runs in main page:** not iframed, JS executes directly in Streamlit's document. Attempted `pushState` + `dispatchEvent(new PopStateEvent('popstate'))` to trigger reruns without a full page reload — works in isolation but unreliable in practice for Streamlit navigation. Abandoned in favour of patching `index.html`.
- ⚡ **Streamlit `index.html` white flash:** `config.toml` `backgroundColor` and all CSS injected via `st.markdown` are applied by React after the JS bundle loads — useless for the initial browser paint. The only fix is patching Streamlit's `index.html` directly, adding `<style>html,body{background:#000!important}</style>` + `<meta name="color-scheme" content="dark">` as the first elements inside `<head>`. A self-healing `_patch_streamlit_index()` function runs at app startup to re-apply the patch after `pip upgrade streamlit`.
- ⚡ **Streamlit static file serving:** requires `[server] enableStaticServing = true` in `.streamlit/config.toml`. Files in `app/static/` (sibling to `app.py`) are served at `http://localhost:8501/app/static/filename.png`. Available since Streamlit 1.18.0; project uses 1.55.0.
- ⚡ **Community Cloud iframe — fundamental breakage:** Community Cloud wraps the app in an iframe, breaking two core features: (1) `<a href="?item=Name">` chip navigation opens a new tab instead of reloading in place; (2) relative image URLs resolve relative to the iframe, not the domain root. Not fixable via config — architectural mismatch. **Modal is the correct hosting target.**
- ⚡ **Modal hosting plan:** `@modal.web_server()` wrapping `streamlit run app/app.py`. No iframe, full server, works identically to local dev. Free tier = $30/month credits, idle = $0, cold start ~5-15s.
- ⚡ **`image_slug()` function:** converts item names to wiki-compatible file slugs — spaces→underscores, apostrophes→underscores, colons→underscores. Used for both local file paths and wiki.gg URLs.
- ⚡ **Wiki image URL encoding:** non-ASCII characters in item names (e.g. ™ trademark symbol) break `urllib.request`. Must use `urllib.parse.quote(slug, safe="_")` to encode URLs. Windows cmd can't print `⚡` emoji — use ASCII alternatives in print statements.
- ⚡ **Two-size image architecture:** 64px for thumbnails/chips/grid, 256px for hero/objective cards. Directory structure: `app/static/images/64/{slug}.png` and `app/static/images/256/{slug}.png`. `local_image_url(name, size)` picks the smallest cached size >= requested size, falls back to wiki.gg.
- ⚡ **Image download results:** 135/140 items downloaded successfully at both sizes. 5 failures (Factory Cart™, Golden Factory Cart™, Hover Pack, Non-fissile Uranium, Screw) — wiki URL mismatches or 404s. None in critical recipe chains.
- ⚡ **Stlite filesystem constraint:** no actual filesystem at runtime. All files must be declared upfront in the `files:` option or loaded via `archives: [{ url: "./images.zip", format: "zip" }]`. Images must be committed to the repo (~2MB) for GitHub Pages to serve them.
- ⚡ **`__pycache__` stale after nbdev_export:** after `nbdev_export` regenerates `data.py`, stale `.pyc` files in `ultra_satisfactory/__pycache__/` can cause `ImportError` for newly exported functions. Must delete the cache directory after export.
- ⚡ **Wiki 403s with generic User-Agent:** the wiki blocks requests without a custom `User-Agent`. `scripts/download_images.py` uses `User-Agent: ULTRA-SATISFACTORY/1.0` which succeeds. Raw `urllib.request` or `curl` without that header returns 403.
- ⚡ **All FICSIT build piece image slugs confirmed:** every unconfirmed variant slug (`Ramp_Wall_2m_(FICSIT)`, `Ramp_Wall_4m_(FICSIT)`, `Inv._Ramp_Wall_2m/4m_(FICSIT)`, `Inner/Outer_Corner_Roof_2m_(FICSIT)`, `Conveyor_Wall_x2/x3_(FICSIT)`) returned HTTP 200 with exact size-matched slugs — no fallbacks needed.
- ⚡ **Tilted Wall variants needed overrides:** `Tilted Concave Wall 4m/8m`, `Tilted Corner Wall 4m/8m`, `Tilted Wall 4m/8m` were missing from the initial override map. Added as `Tilted_*_(FICSIT)` slugs. Final result: 0 failures across all 477 buildings at both 64px and 512px.
- ⚡ **`local_image_url()` missing leading `/`:** `data.py` was returning `app/static/images/64/{slug}.png` (no leading slash). AgGrid's image renderer resolved paths relative to its own frontend build directory (`st_aggrid/frontend/build/app/static/...`), causing `FileNotFoundError` floods. Fixed by adding the leading `/`. The notebook `nbs/00_data.ipynb` already had the correct form — `data.py` had drifted out of sync. Committed `533a4dd`.

---

## Decisions

- ⚡ **Data source:** `greeny/SatisfactoryTools` `data.json` — most complete, community-maintained, no scraping required.
- ⚡ **Images:** local image cache at two sizes (64px, 256px) served via Streamlit static serving. Falls back to wiki.gg for uncached items. Images committed to repo for stlite compatibility.
- ⚡ **Asset hosting:** `data.json` committed to `data/` in the repo — simple, version-controlled, zero infrastructure.
- ⚡ **Phase 1 deployment:** local Streamlit only. Stlite/GitHub Pages deferred to a later phase.
- ⚡ **Chip navigation:** `<a href="?item=Name">` anchor tags inside `st.markdown` — native browser links, not stripped by DOMPurify. Full page reload is unavoidable; mitigated by patching `index.html` for a dark background and a CSS fade-in animation on load.

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

10. ⚡ **GitHub profile:** Luke's GitHub username is `lukexyz` and the repo URL is `https://github.com/lukexyz/ULTRA-SATISFACTORY`. Always use this in any URL, config, or generated content -- never guess or infer a different username.

11. ⚡ **Auto-reorder todo list:** whenever a todo item is completed, automatically reorder the todo list so completed items (`☑`) appear at the top of their phase (in order of completion) and pending items (`☐`) follow below. Notify Luke when reordering occurs.

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

1. ☑ <span style="color: purple">**Tab navigation**</span> — `app/app.py` rewritten with `st.tabs(["OBJECTIVES", "ITEMS", "BUILDINGS"])`; logo + divider sit above tabs; Objectives content moved into tab 1; tab CSS: Share Tech Mono, uppercase, per-tab neon glow pills (purple/pink/blue), gradient indicator line
2. ☑ <span style="color: purple">**`list_items()` in notebook + export**</span> — `list_items(data)` added to `nbs/00_data.ipynb` and exported to `ultra_satisfactory/data.py`; returns 140 craftable items sorted A-Z, each `{class_key, name, image_url}` at 40px; raw resources excluded; verified with test script
3. ☑ <span style="color: purple">**Items tab — HTML table + query param navigation**</span> — rewrote Items tab on branch `phase-2-items-html-table`; abandoned invisible-button pattern; single `st.markdown` HTML `<table>` with 140 rows; each `<tr onclick>` sets `?item=Name`; query param handler reads before tabs render
4. ☑ <span style="color: purple">**Buildings tab stub**</span> — centred placeholder in Share Tech Mono: `// BUILDINGS DATABASE //` + `COMING SOON`; no logic
5. ☑ <span style="color: purple">**Items tab — AgGrid rewrite with instant search**</span> — replaced HTML table with `streamlit-aggrid` v1.2.1; icon column (`JsCode` `IconCellRenderer`, 32x32 wiki images) + name column (`floatingFilter=True`, `agTextColumnFilter` "contains", per-keystroke client-side); `headerHeight=0`; single-row `SELECTION_CHANGED` triggers rerun + recipe card; dark grayscale `custom_css`
6. ☑ <span style="color: purple">**Compact header + slow cog rotation**</span> — horizontal flex layout (48px cog + title/subtitle); `@keyframes slow-spin` at 60s per rotation; title 1.4rem; divider margin halved
7. ☑ <span style="color: purple">**Recipe card UX fixes**</span> — card moved above AgGrid via `st.empty()` placeholder; `onFirstDataRendered` JS injects clear button into floating filter; `filterChanged` listener calls `deselectAll()` to dismiss stale card on new search
8. ☑ <span style="color: purple">**Clickable ingredient/product chips in recipe card**</span> — chips changed from `<div onclick>` (JS stripped by DOMPurify) to `<a class="recipe-chip" href="?item=Name">` anchor tags; hover via CSS `:hover` (not stripped); `text-decoration: none !important` on chip and all children; `chip_item` session state persists clicked item across reruns; consolidated priority logic: grid row click clears chip state, chip click persists until grid interaction
9. ☑ <span style="color: purple">**Chip navigation tab fix**</span> — query param handler moved from inside `with tab_items:` to module level before `st.tabs()`; `st.tabs([...], default="ITEMS")` set when chip was just clicked so page reloads land on the correct tab
10. ☑ <span style="color: purple">**Dark background on chip reload**</span> — `_patch_streamlit_index()` at app startup injects `<style>html,body{background:#000!important}</style>` + `<meta name="color-scheme" content="dark">` into Streamlit's `index.html` as first `<head>` children; idempotent, self-healing after `pip upgrade`; `.streamlit/config.toml` added with matching dark theme; CSS `fadeIn` animation (0.3s ease-in) on `[data-testid="stApp"]`
11. ☑ <span style="color: purple">**Objective card polish**</span> — images enlarged (256px source, `width: calc(100% - 24px)`, `max-width: 200px`); card layout changed to `flex-start` with equal `16px 20px` padding; quantity colour changed to `#7c3aed` (deep violet) with purple glow; quantity font-weight set to 400; name font-size bumped to 0.84rem; first objective open by default on tab load
12. ☑ <span style="color: purple">**Update `project.md`**</span> — discoveries, decisions, and todos updated to reflect all `phase-2-chip-navigation` work

━━━━━━━━━━━━━━━━━━━━━[ PHASE 3 ]━━━━━━━━━━━━━━━━━━━━━

**Goal:** CRT exit transition polish + full Buildings tab (production grid + upgrade progression chains).

**Key decisions:**
- ⚡ Group selector in UPGRADES view: neon sub-tabs (matching top-level tab style)
- ⚡ PRODUCTION grid filter: functional buildings only (`powerConsumption > 0` + miners dict entries)
- ⚡ Default progression group: Miners
- ⚡ Unlock cost chips in detail panel: plain (non-navigable) — unlock costs are items but not recipe-lookup targets in this context

5. ☑ <span style="color: purple">**Image cache — local static serving**</span> — 135/140 item images downloaded at two sizes (64px thumbnails, 256px hero cards) to `app/static/images/{size}/`. `local_image_url(name, size=64)` picks smallest cached size >= requested, falls back to wiki.gg. `enableStaticServing = true` in config.toml. All call sites swapped in `app.py` and `data.py`. 5 failures (Factory Cart™, Golden Factory Cart™, Hover Pack, Non-fissile Uranium, Screw) — none in critical recipe chains. ~2MB committed to repo for stlite/GitHub Pages compatibility.
   - Stlite note: images committed to repo are served as static assets by GitHub Pages. When deploying to stlite, mount via `archives: [{ url: "./app/static/images.zip", format: "zip" }]` in the HTML wrapper.

7. ⚡ ☑ <span style="color: purple">**Scrape missing building images**</span> — added `WIKI_NAME_OVERRIDES` dict to `scripts/download_images.py`; maps 92 `data.json` display names to correct wiki image slugs (FICSIT variant names, renamed generators, Pipeline Junction Cross). All 477 buildings now have cached 64px + 512px images; 0 failures. Committed `d57061b`.

2. ⚡ ☑ <span style="color: purple">**Data functions — notebook + export**</span> — three new functions in `nbs/00_data.ipynb`, exported to `ultra_satisfactory/data.py`:
   - `list_buildings(data)` — functional buildings: `powerConsumption > 0` + all miners dict entries. Each: `{className, name, slug, description, powerConsumption, powerConsumptionExponent}`. Sorted A-Z.
   - `get_building_unlock(class_name, data)` — reverse-lookup: `schematics → unlock.recipes[] → recipe.products[].item == class_name`. Returns `{schematic_name, tier, type, cost: [{name, amount}]}` or `None`.
   - `get_upgrade_chain(slug_pattern, data)` — finds buildings whose `slug` contains pattern + `"mk-"`, sorted by Mk number, each enriched with `get_building_unlock` result.

3. ⚡ ☑ <span style="color: purple">**Buildings tab — PRODUCTION inner tab**</span> — AgGrid (same pattern as Items tab): icon column (wiki image), name, power (MW), tier columns. Floating filter on name. Row click → building detail card above grid. Card: header (name + image, gold/blue theme matching recipe card), body rows (description snippet, power draw, unlock schematic name + tier, unlock cost as plain text chips).

4. ⚡ ☑ <span style="color: purple">**Buildings tab — UPGRADES inner tab**</span> — neon sub-tabs for each progression group (Miners, Conveyor Belts, Pipelines, Storage Containers — groups with only one member hidden). Each group: horizontal card row (one card per Mk tier) showing Mk badge, building image, power draw (`—` for 0MW), unlock tier badge. Selected card highlighted gold. Detail panel below: full unlock cost (item name + amount), schematic name + tier, Prev/Next navigation buttons to step through the chain.
   - Known groups: Miners (Mk.1→2→3), Conveyor Belts (Mk.1→2→3→4→5), Pipelines (Mk.1→2), Storage Containers (Mk.I→II)

6. ⚡ ☑ <span style="color: purple">**Update `project.md`**</span> — Phase 3 discoveries added, todos #2/#3/#4/#6/#8/#9 marked complete, completed items reordered to top.

8. ⚡ ☑ <span style="color: purple">**Fix card corner pixel glitch**</span> — removed `border-radius:9px 9px 0 0` from the header `<div>` in both `recipe_card()` and `building_card()`. The outer wrapper's `overflow:hidden` + `border-radius:10px` now clips the header cleanly with no sub-pixel Chromium compositing artifact. Committed `15d04f7`.

9. ⚡ ☑ <span style="color: purple">**BUILDINGS search bar position**</span> — `_bld_on_ready_js` updated to reorder the DOM after render: `insertBefore(floatingRow, colHeaderRow)` moves `.ag-header-row-floating-filter` above `.ag-header-row-column`. Column headers (BUILDING / CATEGORY / POWER / TIER) remain visible below the search bar. Added `border-bottom` on `.ag-header-row-floating-filter` for visual separation. Committed `8a677d5`.

1. ☐ **CRT exit transition** *(parked — hopefully not needed once images are local)* — two `st.html` injections after logo block (before session state init). CSS injection: `@keyframes crt-flicker` (brightness/contrast pulses, ~250ms, ends at `brightness(0)`); `body.crt-exit [data-testid="stApp"]` triggers animation; `body.crt-exit::before` renders scanline overlay (`position:fixed; inset:0; repeating-linear-gradient; z-index:9999; pointer-events:none`). JS injection (`unsafe_allow_javascript=True`, wrapped in `<div style="display:none;">`): event delegation on `document` for `.recipe-chip` clicks — `preventDefault()`, add `crt-exit` to `document.body`, `setTimeout(260ms)` then `window.location.href`.

---

━━━━━━━━━━━━━━━━━━━━━[ PHASE 4 ]━━━━━━━━━━━━━━━━━━━━━

**Goal:** Smart phase picker for Objectives tab — remembers user's Space Elevator phase across sessions.

1. ⚡ ☐ **Phase picker — collapsed pill** — centered pill above objective cards showing `PHASE 3 · Versatile Framework · Modular Engine · Adaptive Control Unit ▾`. Phase number in gold, item names small + dim monospace. Hidden `st.button` underneath (overlay pattern). Clicking → `phase_picker_open = True` + `st.rerun()`.

2. ⚡ ☐ **Phase picker — expanded overlay** — `position: fixed; z-index: 9999` centered panel. 5 rows, one per phase. Each row: 3 small item icons (32px local static images), gold phase badge, item names in dim monospace. Hidden `st.button` per row. Selected phase gets gold left border. Full-screen transparent backdrop `div` behind panel triggers hidden "close" button on click.

3. ⚡ ☐ **Fresh visit behaviour** — no `localStorage` value → picker opens expanded by default, phase defaults to 3. Return visit → picker loads collapsed, saved phase already set.

4. ⚡ ☐ **`localStorage` persistence** — `st.components.v1.html(height=0)` JS snippet: on load reads `localStorage.getItem("ultra_sat_phase")`, if found does one-time redirect to `?phase=N`; on phase select writes `localStorage.setItem("ultra_sat_phase", N)` fire-and-forget.

5. ⚡ ☐ **Read `?phase=` param on first session load** — sets `st.session_state.selected_phase` before rendering. After reading, param is no longer needed (session state drives everything).

6. ⚡ ☐ **Images always local static** — use `local_image_url()` only, no wiki fallback in picker. Fix any missing images separately.

---

## Debug Log

_One entry per issue. Before touching any code, list hypotheses ranked by likelihood. Then instrument. Then fix. This section stays empty until there is something to debug._

---

## Phase Summaries

_Written after each phase completes. 3-5 lines. What actually happened, what was found, what was surprising. The compressed artifact for future sessions and future models._

### Phase 1

⚡ Foundation built: mamba env, nbdev scaffold, `data.json` committed, `data.py` exports (`load_data`, `wiki_image_url`, `get_item_recipe`, `list_items`). Streamlit UI with Space Elevator Phase 3 objective cards (fat invisible `st.button` + visual overlay trick). Wiki image URLs render directly via `<img>` tags. End-to-end stack proven.

### Phase 2 (in progress)

⚡ Tab navigation added (Objectives / Items / Buildings). Items tab went through three iterations: (1) HTML table with query param onclick; (2) fat-button list with JS `oninput` filtering (failed — Streamlit strips `<script>`); (3) **AgGrid with floating filter** — per-keystroke client-side filtering, icon + name columns, dark `custom_css` theme. Clickable ingredient/product chips added to recipe cards using `<a href="?item=Name">` anchor tags (DOMPurify strips `onclick` but not `href`); hover via CSS `:hover`. Chip navigation fixed to land on the Items tab via `st.tabs(default="ITEMS")` set from module-level query param handler. White flash on reload eliminated by patching Streamlit's `index.html` with an inline dark background style at startup. Objective cards polished: larger images, purple quantity colour, first card open by default.

---
