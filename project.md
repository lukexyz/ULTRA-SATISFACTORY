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
- **Stack:** Python + Streamlit. Single `app/app.py` file. All styling inline via `st.markdown`. Fonts: Orbitron + Share Tech Mono (Google Fonts). No database — data loaded from flat files (JSON or CSV) at startup.
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

### Phase 2 — [Name]

_What this phase covers. What it produces._

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

2. ☐ **[Task]** — description

---

## Debug Log

_One entry per issue. Before touching any code, list hypotheses ranked by likelihood. Then instrument. Then fix. This section stays empty until there is something to debug._

---

## Phase Summaries

_Written after each phase completes. 3–5 lines. What actually happened, what was found, what was surprising. The compressed artifact for future sessions and future models._

---
