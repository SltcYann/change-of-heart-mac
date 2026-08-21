# Item Studio Complete Rebuild Plan — "Cheat Shop First, Truthful Fix Second"

**Status:** Proposed — 2026-08-19 (based on `handoff.md:21:00 UTC`, `AGENTS.md`, `INVENTORY_SPEC.md`, `docs/ITEM_TBL_MAP.md`, live code `web-app/static/app.js:2488` + `web-app/templates/index.html:458`)
**Goal:** Make Item Studio feel like a native P5R cheat shop, not a filtered debug list. Robust + complete to end user. No hex, no mirror, no "50 items is all there is".

---

## 1) Why the current iteration sucks (evidence, not vibes)

| Pain | Where it lives | What user sees | Why it hurts |
|------|----------------|----------------|--------------|
| **"+Add Item" is a cramped lie** | `web-app/static/app.js:2512 catalog.slice(0,50)` + `2494 filter by CURRENT_UNIFIED_CATEGORY` + `web-app/templates/index.html:463 modalCategoryTitle` | Modal says `ADD TO INVENTORY (CONSUMABLE)` with 50 rows. No total count, no pager. Feels like *only these 50 consumables exist* — and same for every tab. Switching category requires closing modal. | Game has **~2,204** knowables across 10 cats (`ITEM.TBL` 10 segs in `docs/ITEM_TBL_MAP.md`: 696 Consumables, 651 SkillCards, 512 Accessories, 301 Protectors, 296 Melee, 286 Outfits, 256 Key/Mat/Ranged). 50 is 2%. Breaks cheat mental model. |
| **Mirror leaks implementation** | `core/editor.py:get_normalized_inventory()` → `mirror_mismatches`, `web-app/static/app.js:2126 warnBadge` shows `⚠ MIRROR`, `docs/INVENTORY_SPEC.md:42` | User sees `mirror mismatch — will heal on Save` and `+0x18510`. Thinks save is scary/broken. | Mirror is *internal save redundancy* (`primary + 0x18510`). Player should see `✓ Synced` or nothing. Auto-heal silently; only log to console. |
| **One list, 10 tabs = tunnel vision** | `CURRENT_UNIFIED_CATEGORY` + `renderUnifiedItemList()` single filter | Owned Pouch shows N items; Full Catalog (S5b) exists in code but modal bypasses it. No global browse, no character scoping for 195 Melee + 106 Ranged across 9 thieves. | Cheat user wants to *browse everything*, not tune one tab. |
| **Quick-array phantom still surfaced as badge** | `conflicts`/`mirror_mismatches` badges on pill | Extra badges clutter every row even when save is healthy. | Should be collapsed to one footer status, not per-row. |

**Design axiom from `AGENTS.md`:** Cheat editor is *inherently for cheating* — make it *easy* to cheat. Truthful read stays, but UI should scream "Shop", not "Debugger".

---

## 2) Principles for the rebuild

1. **Cheat Shop first:** Browse-first, not filter-first. Search across all cats, see total, one-click own/max.
2. **No hex, no mirror, no offsets in user-facing text.** Engineering terms (`0x3230`, `+0x18510`, `SEG6`) stay in `handoff.md`/`research/`. UI says `Synced`, `In Bag`, `Not Owned`.
3. **Complete catalog, not 50.** Full 2.2k virtualized list with correct `Showing 50 of 512 — scroll for more`.
4. **Three buckets stay, but per cheat action:** Gear `◆ Owned/◇ Not owned` toggle (writes `0x00/0x01`+mirror), Stacks `- [qty] +` (0..99), Key `🔒 Guarded` (confirm). But *inside the shop* they share one browse surface.
5. **Zero-paste handoff:** Any Hermes/Antigravity reads `AGENTS.md → handoff.md:20-55 → ITEM_TBL_MAP.md` to continue.

---

## 3) Target UX — "Cheat Shop" modal (surgical single-item injection only)

### A. Rename + behavior

- Modal title `ADD TO INVENTORY (CONSUMUTABLE)` → **`CHEAT SHOP — [Category] Items`**.
  The `[Category]` is the *active main-tab category* — no `All (2,204)` desync. Modal
  inherits `CURRENT_UNIFIED_CATEGORY` + active `who` chip on open (not `All | <char>`).
  This preserves reset-pressure flow: I'm on Melee → I open → I see Melee, filtered to Joker.
- Search inside shop is scoped to the inherited category (`name` + `ID 0x...`), debounced 180ms.
  No global cross-category search — keeps mental model tight to the gear being fixed.
- Character chips (`All | Joker | Skull | Mona | … | Violet`) inherit the main tab's `who`
  selection; do **not** offer a separate shop-only `All`. Chips appear only for
  `CHIP_SUPPORT_CATS` (`0x1000 Melee | 0x7000 Ranged | 0x5000 Protector`), sourced from
  `REFERENCE_DB` `ITEM_OWNER_BY_ID` (`...Owner)` suffix) — not hardcoded.

### B. Catalog truth (only wired categories are writable)

- Header: `Showing 1–50 of 512 Accessories — 12 Owned · 500 Missing` + progress.
- Rows: dimmed `◇ Not owned` vs green `◆ Owned` / `x count`.
- Controls per row — **ONLY enabled for diff-verified categories**:
  - Gear (Melee `0x1000` / Ranged `0x7000` / Protector `0x5000`): `◆ Owned` toggle (writes `0x00/0x01`), count=1 not 99.
  - Stacks (Consumable `0x2000` / Accessory `0x3000`): `+1` / `+99` (clamped 0..99).
  - **ALL OTHER rows (SkillCard `0x4000` / Tool `0x6000` / Treasure `0x8000` / KeyItem `0x9000` / Outfit `0xA000`)**:
    read-only row — shows count/totals only, controls **disabled**. Tooltip:
    `Offset unverified — diff via tools/diff_mapper.py before wiring`.
- **NO footer bulk actions** (`Own All Visible`, `Max All Visible`, `Add All Missing`
  removed — see Risks §8). Eliminates cross-category write surface.

### C. Interaction details

- **Virtualized list** (incremental "Load 50 more" acceptable) — no `slice(0,50)` hard wall.
  Measure: scroll 696 Consumables without DOM thrash.
- **Click row → select** (highlights, updates dossier). **Double-click → instant own**
  for gear, **+1** for stacks — but only fires on wired rows (no-op elsewhere).
- Clicking `BROWSE IN SHOP` dot on empty Pouch (`POCKET IS EMPTY` empty-state) opens the
  shop pre-scoped to the pouch's active category — ties dual views together (`Owned Pouch ↔ Catalog`
  per `docs/adr/0002`). No "Full Catalog" naming collision.
- Staged edits share buffer with main lists: owning in Shop instantly shows yellow `● STAGED`
  dot on active category pill + footer `● N STAGED · DISCARD STAGED`. No reload needed.

### D. Mirror & conflict — persistent visible flag (NO silent heal)

- **KEEP** existing per-row `⚠ MIRROR` / `⚠ CONFLICT` badges on affected pills.
- **DO NOT** replace with a transient footer toast.
- **DO NOT** silent-heal on save. Retain current `activeItemDescText` warning so the user
  sees the structural mismatch flag *until they explicitly save & re-sign*.
- Console-only log of `mirror_mismatches`/`conflicts` kept for dev diagnostics, but the
  user-facing red flag stays sticky until resolved by an intentional save.

---

## 4) Information architecture (minimal reshuffle)

```
Stage: Hideout & Inventory
├─ Top: [ 🎒 Owned Pouch | 📚 Full Catalog ] toggle + search + dirty badge
├─ Tab row: 10 cats (badge counts mode-aware) + category-scoped search + counter
├─ Chips: Character filter (visible for gear cats, sticky, hash-persisted)
├─ Main grid: Left 640px virtual list (pill: glyph + name + owned/stepper/guarded) | Right Dossier Inspector
├─ Footer deck: ● N STAGED + Discard staged / Save & Re-sign
└─ Shop (replaces Add Item modal): CHEAT SHOP — category pills + search + virtual list + footer bulk actions
```

Hash persists `#inv=pouch|shop&cat=...&who=...&q=...` so back/refresh is stable (already does for inventory view).

---

## 5) Technical approach

**Files:**
- `web-app/templates/index.html:458-478` — retitle modal, widen to `900px`? Add internal pill row `#shopCategoryPills` + counters. No nav change.
- `web-app/static/app.js:2488-2562 renderModalCatalog()` — biggest change: decouple from `CURRENT_UNIFIED_CATEGORY`, add `SHOP_CATEGORY / SHOP_SEARCH / SHOP_CHARA` state, reuse `getItemSortRank`, add virtual scroll, footer bulk handlers (`ownAllVisible`, `maxAllVisible`, `addMissingInCategory`). Keep `addItemFromModal` but rename to `cheatOwnFromShop`.
- `web-app/static/app.js:2113-2133 getItemDescription` — keep, add owner tag line already parsed via `ITEM_OWNER_BY_ID`.
- `core/editor.py` + `server.py` — **no change**. Mirror heal + `get_normalized_inventory()` = `{owned_gear, stacks, key_flags, unknown, conflicts, mirror_mismatches}` stay single source of truth. JS just stops showing raw mismatches.
- `docs/INVENTORY_SPEC.md §7` — mark `S5b` as `Shop regression: +Add Item 50-limit → full virtual catalog`.
- `AGENTS.md` where-to-look — ensure `docs/ITEM_TBL_MAP.md` stays listed (already).

**Backend cheap wins (no schema change):**
- Reuse `build_reference_db()` `CATEGORY_MAPPING` 10 cats (includes `0xA000 Outfits` 286) + `REFERENCE_DB['items']` 2.2k.

---

## 6) Phased execution (cheap → visible)

**Phase A — Shop shell (no data change, behind same modal id):**
Inherit `CURRENT_UNIFIED_CATEGORY` + active `who` chip on open (no internal All desync). Show `Showing 1–50 of M`, add "Load more". Disable controls on unwired rows. ½ session.

**Phase B — Virtualize (no bulk actions):**
Swap `slice(0,50)` → virtualized/incremental render for full category (max 696 Consumables). No footer bulk buttons. 1 session.

**Phase C — Preserve persistent mirror flag + sync UX:**
KEEP existing per-row `⚠ MIRROR` / `⚠ CONFLICT` badges + `activeItemDescText` warning. NO silent heal, NO footer toast replacement. Verify shared staged buffer reflects Shop actions on main tab. ½ session.

**Phase D — Shared polish:**
Hash persistence for shop category+search (inherit, not override), empty-state CTA scoped to inherited category, `node --check` + `146/146` + freeze-proof `dist/P5R_Save_Editor.exe` verify at `http://127.0.0.1:3000`. ½ session.

*All phases behind same modal id — no migration.*

---

## 7) Acceptance criteria (must hold before Done stamp)

- [ ] Shop header shows `Showing 1–N of M` for the inherited category only; unwired categories (`0x4000/0x6000/0x8000/0x9000/0xA000`) display counts but controls are disabled.
- [ ] Shop inherits main-tab category + `who` chip on open; does NOT offer independent `All` desync. Search is category-scoped (not global).
- [ ] Owning in Shop instantly marks `● STAGED` + perseveres across Pouch↔Catalog↔Shop switches (shared staged buffer); `Save & Re-sign` clears dirty and reload shows same.
- [ ] Persistent per-row `⚠ MIRROR` / `⚠ CONFLICT` badges + `activeItemDescText` warning retained; NO silent heal / NO footer toast replacement.
- [ ] Gear rows are `◆ Owned` toggles (0/1), never quantity; stack rows are `± 0..99` with clamp; unwired rows disabled with `Offset unverified` tooltip.
- [ ] Virtual scroll performs (<100ms class) for 696 rows (largest wired category); unwired rows never rendered as live actions.

---

## 8) Risks & mitigations

- Outfits 286 vs old constants (301 Protectors vs 286 Outfits) — counts verified, but **save offset `0x3230+idx` frozen until diff**. Shop shows totals only, never enables write controls on `0xA000` rows.
- Ranged filler rows (DB→save 256 shift) — shop dimmed if `RANGED_SAVE_IDX_BY_DB_ID` miss, show `Unknown owner — safe (read-only)`. Non-verified IDs never stage.
- Bulk action surface — **removed entirely** (no Own All / Max All / Add All Missing). Highest corruption vector eliminated per speedrunner review.
- Silent heal surface — **removed** (no silent `+0x18510` heal on save). Persistent `⚠ MIRROR/CONFLICT` flag retained until user explicitly saves.
- Dual-view buffer split — Shop and main tabs **share** single staged buffer per `docs/adr/0002`. Verified by test: stage in Shop → main pill shows `● STAGED`.

---

## 9) What next

Plan revised per speedrunner review (Gemini 3.7 Flash + DeepSeek v4 Pro) — bulk actions, silent heal, and `All`-desync all removed to eliminate silent-corruption vectors across unwired (`0xA000+` / `0x9000` / `0x4000` / `0x6000` / `0x8000`) ranges.

On approval I'll arm a **single persisted `create_goal` (Item Studio — Cheat Shop complete, max 25 rounds)** and execute the constrained Phases A-D (no bulk / no silent heal / no unwired writes). `handoff.md` stays single source, `README.md` GitHub-clean.

*Reply `approve` to arm, or `revise: <note>` and I'll adjust.*
