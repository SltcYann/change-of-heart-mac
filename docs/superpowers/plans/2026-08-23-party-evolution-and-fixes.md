# Implementation Plan: Party Evolutions, Slot Fixes, EXP Auto-Sync & Romance Toggle

**Document ID:** `docs/superpowers/plans/2026-08-23-party-evolution-and-fixes.md`  
**Date:** 2026-08-23  
**Spec Reference:** [`docs/superpowers/specs/2026-08-23-party-evolution-and-fixes-design.md`](file:///E:/ai-workspace/knowledge-base/projects/p5r-save-editor/docs/superpowers/specs/2026-08-23-party-evolution-and-fixes-design.md)  
**Status:** PROPOSED (Pending User Review)

---

## User Review Required

> [!IMPORTANT]
> This plan addresses all 5 major items reported by `u/Gruphius` on Reddit:
> 1. **Fix Haru (Slot 6) / Futaba (Slot 7) swap** in backend and UI.
> 2. **Party Persona Evolution Tiers (1/2/3)** selector in Velvet Room & Party.
> 3. **Automatic Level $\leftrightarrow$ EXP Curve calculation** to eliminate post-battle glitching.
> 4. **Romance vs. Friendship Route flag** for Confidants.
> 5. **Catalog Key Items unlock** to allow adding missing items.

---

## Proposed Tasks Breakdown

### Task 1: Fix Haru & Futaba Slot Indices (Backend & Tests)
- **Files:** `core/editor.py`, `tests/test_editor.py`
- **Changes:**
  - In `core/editor.py`, update `PARTY_SLOT_NAMES`:
    - Slot 6: `"Haru"`
    - Slot 7: `"Futaba"`
  - In `PC31_MEMBER_SEEDS`:
    - Slot 6: `(213, 155, 30, 0xCF)` (Haru base seed)
    - Slot 7: `(316, 182, 36, 0xD0)` (Futaba base seed)
  - Add unit test `test_party_slot_names_and_seeds` verifying slots 6 & 7.

### Task 2: Implement EXP Curve Calculator & Auto-Sync on Level Writes
- **Files:** `core/exp_curve.py`, `core/editor.py`, `tests/test_editor.py`
- **Changes:**
  - Create `core/exp_curve.py` with standard Atlus $O(L^3)$ cumulative EXP curve for levels 1..99.
  - In `core/editor.py` `set_party_stat()`:
    - Whenever `level` is passed, compute `exp = get_p5r_min_exp_for_level(level)` and write to `+0x10` (Joker) or `+0x18` (teammate struct).
  - Add unit test `test_party_level_exp_autosync`.

### Task 3: Implement Party Persona Evolution Selector (Backend & API)
- **Files:** `core/editor.py`, `server.py`, `tests/test_editor.py`
- **Changes:**
  - Add `PARTY_PERSONA_EVOLUTIONS` mapping table to `core/editor.py`.
  - Add `set_party_persona_evolution(slot: int, tier: int)` method to `SaveEditor`.
  - Add `/api/party/evolution` route handler in `server.py`.
  - Add unit test `test_set_party_persona_evolution`.

### Task 4: Expose Romance Route Toggle for PC Saves
- **Files:** `core/editor.py`, `server.py`, `tests/test_editor.py`
- **Changes:**
  - In `core/editor.py` `set_confidant_rank()`: enable romance bit write (`0x02`) on PC `0x31` saves.
  - Update `get_confidant_ranks()` to return `romance: bool`.
  - Add `/api/confidant/romance` route or support `romance: true/false` in `/api/confidants`.
  - Add unit test `test_confidant_romance_toggle`.

### Task 5: Frontend UI Updates (Velvet Room & Confidants)
- **Files:** `web-app/templates/index.html`, `web-app/static/app.js`
- **Changes:**
  - In Velvet Room & Party (Stage 3):
    - Fix slot 6 & 7 character artwork and names.
    - Add **⚡ Persona Evolution Tier** selector for party members.
  - In Confidants (Stage 2):
    - Add **💖 Romance / 🤝 Friendship** toggle for Rank 9/10 romanceable female confidants.
  - In Item Catalog modal:
    - Enable adding Key Items directly to pouch.

### Task 6: End-to-End Verification & Hygiene Gate
- Run full test suite (`pytest -q` / `unittest`) — all 161+ tests passing.
- Run `python scripts/check-invariants.py --sync` to verify 100% green gate.

---

## Verification Plan

### Automated Tests
```bash
python -m unittest discover -s tests
python scripts/check-invariants.py
```

### Manual Verification
- Load test save in browser UI (`http://127.0.0.1:3080`).
- Verify Haru appears in Slot 6 with Milady, and Futaba in Slot 7 with Necronomicon.
- Switch Ryuji to Tier 3 (William) and verify equipped Persona updates.
- Toggle Romance on Makoto/Ann and verify save write.
