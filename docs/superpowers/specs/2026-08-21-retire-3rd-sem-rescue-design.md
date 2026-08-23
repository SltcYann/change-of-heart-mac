# Design Spec: Retiring 3rd Semester Emergency Rescue & Refactoring Backups Vault

**Date:** 2026-08-21  
**Status:** APPROVED DESIGN SPEC  
**Goal:** Remove the unfeasible "3rd Semester Guarantee" rescue feature, delete buggy dead code, and clean Stage 5 into a dedicated Reversible Backups & Safety Vault.

---

## 1. Problem & Rationale

In P5R, unlocking the 3rd Semester requires reaching Dr. Maruki Rank 9 on or before the **11/18** school departure event, which sets internal story progression bits in the 43,008-bit Event Flag Matrix (`0x2F200–0x30700`). 

The old "Apply 3rd Sem Rescue" button:
1. Gave players false hope that a simple rank write in December (past 11/18) could retroactively trigger the 3rd Semester.
2. Had a bug where calling `/api/emergency-rescue` modified in-memory state without writing to disk, then immediately reloaded the untouched disk file, discarding changes.
3. Confidant rank adjustments are already fully supported with deadline warnings in the **💖 CONFIDANTS & ROMANCE** tab.

---

## 2. Proposed Changes

### Component 1: Frontend Template (`web-app/templates/index.html`)
- In `<nav class="p5-nav-list">`:
  - Rename button text from `🛡️ RESCUE & BACKUPS` to `🛡️ BACKUPS & SAFETY`.
- In `<section id="stage-rescue_vault">`:
  - Update headline to: `🛡️ REVERSIBLE BACKUPS & SAFETY VAULT`.
  - Subtitle: `Automated timestamped ZIP snapshots before every save write, with 1-click state rollback.`
  - Remove the entire `<!-- 3rd Sem Rescue -->` card and `triggerRescueThirdSemester()` button.
  - Expand the `<!-- 1-Click Backups -->` card into a full-width or dual-card layout focusing on snapshot restoration and cryptographic save health.

### Component 2: Client Controller (`web-app/static/app.js`)
- Delete the `triggerRescueThirdSemester()` function.

### Component 3: Backend Server (`server.py`)
- Remove the `elif parsed.path == "/api/emergency-rescue":` route handler block.

### Component 4: Core Engine (`core/editor.py`)
- Deprecate / remove `unlock_third_semester()` method from `SaveEditor`.

### Component 5: Documentation & Hygiene
- Update `SAFETY.md`, `MEMORY.md`, and `STATUS.md` to reflect the removal of the unfeasible rescue button.
- Ensure all 161+ tests pass and `check-invariants.py` passes all 4 gates.

---

## 3. Verification Plan

- **Syntax Check:** `node --check web-app/static/app.js` → Exit 0.
- **Unit Test Suite:** `python -m unittest discover -s tests` → All tests green.
- **Hygiene Gate:** `python scripts/check-invariants.py` → All 4 invariant gates pass.
