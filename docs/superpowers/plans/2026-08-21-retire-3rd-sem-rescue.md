# Retiring 3rd Semester Emergency Rescue & Refactoring Backups Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the unfeasible 3rd Semester Emergency Rescue feature, delete dead/buggy endpoints, and refactor Stage 5 into a clean, dedicated Reversible Backups & Safety Vault.

**Architecture:** Frontend template cleanup in `index.html`, deletion of dead JS event handlers in `app.js`, removal of the `/api/emergency-rescue` routing block in `server.py`, deprecation of `unlock_third_semester` in `editor.py`, followed by automated regression verification against 161 unit tests and invariant checkers.

**Tech Stack:** Python 3.14 (stdlib HTTP, unittest), Vanilla ES6 JavaScript, HTML5/CSS3.

## Global Constraints

- Truthful read + safe lasting write: Do not fake story progression or promise impossible late-game calendar rescues.
- All writes remain bounds-checked with primary + mirror (+0x18510) and CRC32 synchronization.
- All existing 161 tests must stay green.

---

### Task 1: Clean Frontend Template (`web-app/templates/index.html`)

**Files:**
- Modify: `web-app/templates/index.html:47-50, 630-668`

**Interfaces:**
- Consumes: None
- Produces: Clean Stage 5 UI without the 3rd Sem Rescue card.

- [ ] **Step 1: Update Sidebar Navigation Link**
In `web-app/templates/index.html`, update line 48 button label from `🛡️ RESCUE & BACKUPS` to `🛡️ BACKUPS & SAFETY`.

- [ ] **Step 2: Refactor Stage 5 Layout**
In `web-app/templates/index.html`, remove the `<!-- 3rd Sem Rescue -->` card. Update headline to `🛡️ REVERSIBLE BACKUPS & SAFETY VAULT` and expand the restore vault card.

---

### Task 2: Remove Dead Client Logic & Backend Endpoint

**Files:**
- Modify: `web-app/static/app.js:3175-3195`
- Modify: `server.py:717-727`

**Interfaces:**
- Consumes: None
- Produces: Removal of `triggerRescueThirdSemester()` and `/api/emergency-rescue` route.

- [ ] **Step 1: Delete `triggerRescueThirdSemester()` in `app.js`**
Remove `triggerRescueThirdSemester()` from `web-app/static/app.js`.

- [ ] **Step 2: Remove `/api/emergency-rescue` in `server.py`**
Remove `elif parsed.path == "/api/emergency-rescue":` handler from `server.py`.

- [ ] **Step 3: Verify JS Syntax**
Run: `node --check web-app/static/app.js`
Expected: Exit code 0.

---

### Task 3: Engine Cleanup & Test Suite Verification

**Files:**
- Modify: `core/editor.py:2047-2067`
- Test: `tests/test_editor.py`

**Interfaces:**
- Consumes: None
- Produces: Clean `core/editor.py` without obsolete emergency unlock method.

- [ ] **Step 1: Clean `core/editor.py`**
Remove or cleanly mark `unlock_third_semester()` as deprecated.

- [ ] **Step 2: Run Full Test Suite**
Run: `python -m unittest discover -s tests`
Expected: 161/161 tests pass.

- [ ] **Step 3: Run Invariant Check Gate**
Run: `python scripts/check-invariants.py`
Expected: All 4 gates pass (`PASSED: all invariants OK`).

---

### Task 4: Documentation & State Hygiene Updates

**Files:**
- Modify: `STATUS.md`
- Modify: `state.json`
- Modify: `SAFETY.md`
- Modify: `MEMORY.md`

- [ ] **Step 1: Update SAFETY.md and MEMORY.md**
Update docs to record the removal of the 3rd semester emergency rescue button and reiterate that Confidant rank progression is safely managed in the Confidants tab.

- [ ] **Step 2: Update state.json and STATUS.md**
Sync `state.json` and `STATUS.md` with the latest task notes.
