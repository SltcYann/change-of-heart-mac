# Inventory Editor UX Review & Research — Why It Feels Off, and What Great Looks Like

**Date:** 2026-08-21 · **Agent:** ox-alpha (opencode)
**Inputs:** RFC 6902/7396 (patch semantics), game-inventory UX literature (WANDR menu design, TheWingless inventory guide, StraySpark inventory systems, Dredge spatial-inventory deep dive, QuantUX grid study), save-editor precedents (Gibbed BL2, KillianM00 bl2-save-editor web app), full read of `web-app/static/app.js` inventory code.

---

## 1. Diagnosis — why it feels off

The instinct is correct. Three structural reasons, in order of importance:

### 1.1 It's a field editor, but users arrive with intents
The current UI's primary loop is **per-item micro-editing**: find row → click stepper N times → see dot. But a cheat tool's actual usage is **intent-shaped**: *"refill my meds"*, *"get me the endgame gear"*, *"clean out junk"*. The Cheat Shop modal acknowledges this but bolts it on as a separate surface. The result is a debugger wearing a P5R costume — themed like the game, but interacting like a database table.

> WANDR: an inventory screen must support five tasks — *see what you have, find a specific thing, compare two things, understand what a thing does, act on it.* We cover four. **Comparison is missing entirely**, and "find" requires knowing which tab an item lives in.

### 1.2 Four overlapping state stores with no defined contract
`INVENTORY_ITEM_COUNTS` (live map), `INVENTORY_NORMALIZED` (server truth), `STAGED_DIRTY` (annotation set), `__INVENTORY_BASELINE` (load snapshot) — all mutated independently. That's why the removal bug happened: the map conflated *display state* with *save intent*, and deletion was ambiguous (RFC 6902's core lesson: omission ≠ deletion). `buildInventoryPayload()` now defines the contract (baseline = truth, live = display, payload = minimal diff), but the stores themselves remain untyped soup.

### 1.3 No feedback loop about consequences
Staged dots say *something* changed, never *what*. Before the irreversible act (RE-SIGN), the user sees no reviewable summary. Trust in a save editor comes from predictability: **show the diff, then commit it.**

---

## 2. What the research says "great" is

| Principle | Source | Ours today |
|---|---|---|
| Deletion must be explicit; omit = untouched | RFC 6902/7396 | ✅ fixed (`buildInventoryPayload`) |
| Send the net effect of changes, not whole state | Medium-editor autosave pattern | ✅ minimal diff |
| Never full-replace over incompletely-read state | save-system literature | ✅ merge-patch kept server-side |
| Grid/list + detail pane separates browsing from reading | WANDR | ✅ already right |
| Comparison vs equipped ("+6 damage", green/red) | WANDR, StraySpark | ❌ missing |
| Filter/search is a PRIMARY action when breadth is large | TheWingless, WANDR | 🟡 per-tab only |
| ≤4–6 categories; merge related types | StraySpark | ❌ 10 flat tabs |
| Quick actions: context menus, single-click common ops | StraySpark | ❌ small-button clicking only |
| Undo is core editor UX, not a nicety | Bevy #1107 | 🟡 global discard only |
| Right-click power actions (duplicate/copy/delete) | Gibbed BL2 | ❌ |
| Semantic sync actions (sync item level to char level) | Gibbed | ❌ (and safer than blind max-all) |
| Atomic writes + rotating backups + post-write verify | BL2 web editor | ✅ backups + re-sign + integrity re-read |
| Refuse writes while game runs | BL2 web editor | ✅ process watcher (README) |
| Import/export share codes | Gibbed ecosystem | ❌ (no P5R code standard exists) |
| Unusable items look unusable, with reasons | TheWingless | ✅ UNWIRED disabled rows |
| One scrollbar rule; paginate grids | TheWingless | 🟡 unvirtualized 2.2k-row catalog |

---

## 3. What we already get right (keep)

1. **Paradigm-correct controls** — gear toggles, stack steppers, guarded key items. Matches storage reality (ADR 0001).
2. **Dossier + list split** — browsing and reading separated, exactly the recommended layout.
3. **In-game sort priority** — consumables ordered like the real bag. Authenticity wins.
4. **Safety posture** — unwired categories disabled with reasons, bulk corruption vectors deleted, confirms on story flags, auto-backups, integrity pill.
5. **Baseline-diff payload** (new) — minimal, explicit, safe under incomplete reads.

---

## 4. Recommendations (ranked: cheap → big)

### R1. Pending-changes review panel ⭐ highest value / effort
Before RE-SIGN, render `buildInventoryPayload()` as human text: `Recov-R 6→0 · Own Uchigatana · Life Stone 0→99`. Confirm dialog becomes a receipt. We already compute the diff — this is presentation only. Directly converts the "what will happen?" anxiety into trust.

### R2. Per-item revert
A small `↺` on dirty rows restoring that id from baseline (and clearing its STAGED dot). Complements global DISCARD; makes experimentation cheap. Trivial with baseline present.

### R3. Global search across categories
One search box that searches all 10 categories, results grouped under category headers with counts. Kills the "which tab is Goho-M in?" tax. Keep per-tab search as-is inside tabs.

### R4. Group the 10 tabs into 3 clusters
`CONSUMABLES (Items·Tools·Cards)` / `EQUIPMENT (Melee·Guns·Armor·Accs)` / `VALUABLES (Loot·Outfits)` / `KEY 🔒`. StraySpark's 4–6 category ceiling; preserves authenticity via sub-tabs. Reduces tab-strip cognitive load and the badge noise.

### R5. Context menu + keyboard
Right-click row: Own/Max/Discard/Duplicate/Copy ID. Keys: `↑↓` navigate, `+/-` step, `M` max, `Del` discard. Power-user throughput, near-zero risk.

### R6. Gear comparison delta
Dossier shows selected weapon's stats **as delta vs currently equipped** (green/red). Requires backend to expose equipped-slot ids per character (party struct already parsed). Highest "feel like a real game menu" win.

### R7. Virtualize the main list
Same incremental batch pattern as the Cheat Shop modal (50/page, 300 DOM cap). Catalog+All currently renders ~2,200 styled rows synchronously.

### R8. Reconcile UNWIRED vs VERIFIED drift
UI freezes SkillCard/Treasure/Infiltration as unwired while MEMORY.md/INVENTORY_SPEC §7 mark those offsets ✅ VERIFIED. Either wire them (backend already writes them) or correct the docs. Dead-looking controls erode trust more than honest read-only labels.

### R9 (later). Share codes
Gibbed's ecosystem proved shareability is a killer feature. Even without a P5R code standard, export/import a single item or whole loadout as base64 JSON creates community gravity.

---

## 5. Suggested sequencing

1. **Now:** R1 + R2 (one session, builds on today's diff work)
2. **Next UI pass:** R3 + R4 + R7 (navigation/perf)
3. **With backend support:** R6 (equipped-gear read), R8 (wiring decision)
4. **Community phase:** R9

*Design axiom to hold onto: personality lives in the skin; hierarchy stays ruthlessly conventional. The P5R theme is doing its job — the model underneath it is what needs to become a tool.*
