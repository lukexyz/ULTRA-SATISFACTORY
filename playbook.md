# `playbook.md`

> Compiled from the trenches — HN thread [`47214629`](https://news.ycombinator.com/item?id=47214629) + battle scars from a real voucher-validation project.

---

## 0x00 — The Core Loop

```
project.md  →  plan.md  →  todo list  →  execute  →  commit all artifacts
     ↑                                                       |
     └───────────── re-run with smarter models ──────────────┘
```

The original idea (jedberg): describe what you want in `project.md`, have the AI produce a `plan.md`, iterate on the plan until it's right, generate a todo list, then tell the AI to execute without asking questions. Commit everything. The plan is the artifact — reproducible, reviewable, re-runnable when models improve.

**Why it works:** you front-load the thinking. The AI writes better code when it already agreed to a plan. You catch bad ideas before they become bad commits.

---

## 0x01 — The Three-Doc Split

> *jumploops — 100% vibe-coded success rate, greenfield and legacy*

Don't cram everything into one file. Split by purpose:

| Doc | Purpose | Naming |
|-----|---------|--------|
| **Design** | What and why. Open questions. Decisions. | `design/<feature>.md` |
| **Plan** | How, in phases. Tech choices. Dependencies. | `plan/<feature>/phase-N-<desc>.md` |
| **Debug** | Hypotheses first, then instrument, then fix. | `debug/<feature>-<issue>.md` |

The debug doc is the sleeper hit. Instead of letting the AI flail, force it to list N hypotheses ranked by likelihood **before** it touches code. Instrument logging to confirm. Then fix. This alone kills 2-hour throwaway sessions.

---

## 0x02 — The Rephrase Gate

> *miki123211 — "My prompts are super sloppy, full of typos"*

Before the AI writes a single line of code:

1. Have it **rephrase your request** in its own words
2. Have it **research the relevant subsystems** and dump findings to the doc
3. Have it **spec out behaviour** (UI, CLI, expected outputs)
4. Have it **propose architecture**
5. *Then* plan. *Then* implement.

Step 1 costs almost nothing and catches misunderstandings before they compound. Step 2 catches wrong assumptions about column names, API shapes, library versions — the stuff that derails you at hour two.

---

## 0x03 — The Context Nuke Button

> *RHSeeger — "sometimes the plan was totally wrong and I want to purge"*

Keep a `context.md` alongside your plan — a compressed snapshot of **everything the AI would need to regenerate the plan from scratch**. Environment, constraints, schema discoveries, key decisions and why.

When things go sideways (and they will), you nuke the plan, open a fresh session, hand it `context.md`, and say "try again." No re-explaining. No re-discovering. Just a clean restart with full memory.

---

## 0x04 — Write Tests Before Code

> *wek — "have the agent write the test cases after writing the plan, then iterate until it passes"*

Define expected outputs as part of the plan phase:

```
Expected: df_match_rate has columns [platform, n_orders, n_matched, match_pct]
Expected: one row per platform (oneappandroid, oneappios, oneweb)
Expected: match_pct for Android < 90% if hypothesis is correct
```

The AI can write assertions from these. When implementation drifts, the tests catch it — not you, three hours later.

---

## 0x05 — Keep Sessions Small, Keep Context Fresh

> *shinycode — "Claude code only works well on small increments because context switching makes it mix and invent stuff"*

Rules of engagement:

- **One todo item per session** if it's complex. Two or three if trivial.
- **Ask the AI to write your next prompt** before you clear context — it knows what's unfinished.
- **Commit after every working state.** Not after every session. After every *working* state.
- If you edited files outside the session, **say so.** Force the AI to re-read before it touches anything.

---

## 0x06 — The Discoveries Section

> *Battle-tested on the voucher project*

Most people skip this. Don't. Keep a running log of **verified facts** about your codebase, data, APIs:

```markdown
## Discoveries
- `ordercreatedv2_uk_2026`: Platform = `OrderSourceData.ApplicationInfo.ApplicationName`
  (values: OneAppAndroid, OneAppIos, OneWeb)
- `cdna_fact_session_event`: grain is one row per (session_id, event_name)
  — n_events = n_sessions by design
- voucher_code is NOT tracked on voucher_submit (confirmed by Lois)
```

This prevents the AI from hallucinating column names, re-running schema queries, or making assumptions you already disproved. Every dead end you document is a dead end you never walk down again.

---

## 0x07 — The Final Distillation

> *danenania — "planning files tend to end up outdated by the time implementation is done"*

When a phase is complete, collapse it. Write a 3-5 line summary of what actually happened and what was found. The detailed todos served their purpose during execution — the summary serves future-you and future-models.

```markdown
### Phase 1 Summary
Compared dashboard order counts to session voucher_apply events across
8 days x 3 platforms. Android shows a 34% undercount in session events
vs. order data. iOS and web within 5%. Root cause: suspected missing
event firing on Android app builds after v4.2.1.
```

---

## 0x08 — Structure Your `project.md`

Recommended skeleton, pulling from everything above:

```markdown
# project.md

## Objective
One paragraph. What are we doing and why.

## Environment & Constraints
- OS, shell, language, key libraries
- Data access (BQ, APIs, local files)
- Tools (luketools, nbconvert, etc.)

## Open Questions
Things we don't know yet. Remove or move to Discoveries when answered.

## Discoveries
Verified facts. Schema findings. Dead ends. Source attribution.

## Plan
Numbered, phased. Tech choices explicit. Dependencies called out.

## Todo List
☐/☑ with links to implementation locations.
Completed items float to top. Each item is small enough for one session.

## Debug Log
Per-phase. Hypotheses → instrumentation → findings → fix.

## Phase Summaries
Written after completion. 3-5 lines. The actual outcome.
```

---

## 0x09 — Multi-Model Review

> *jedberg + fhub — "have another LLM review Claude's plans"*

Your markdown artifacts are portable. Feed the plan to a second model and ask it to poke holes. Different models catch different blind spots. Cheap insurance on anything non-trivial.

---

## 0x0A — The Meta Rule

> *"I spend about as much time on tooling as actual features"* — anbende

The overhead of maintaining these docs pays for itself **exactly once** — the first time you'd otherwise have spent two hours in a broken session with no way to recover. After that, it's pure profit.

---

```
EOF
```
