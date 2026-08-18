# 🎭 CHANGE OF HEART — Patch Notes

---

## v1.0.8 — In-Game Parity Fixes: Names, Master Items & Compendium
**Release Date:** 2026-08-18  
**Build:** `CHANGE_OF_HEART_v1.0.8.zip` (56.9 MB)

### 🔤 1. In-Game Dialogue Name Persistence
- **Fixed Name Saving:** Previously, character names only wrote to the uncompressed `0x190` header (save selection preview). First and last names now serialize directly into the in-game dialogue data payload structs at `0x13840` (Full Name), `0x138A8` (Last Name), and `0x138DC` (First Name) along with their synchronized mirrors at `0x2BD50`, `0x2BDB8`, and `0x2BDEC`.

### 🎒 2. Master Item Count Array Persistence
- **Master Count Array Writes:** Item quantity edits now serialize directly into the game's authoritative master count array at `0x2410..0x2780` (`0x2535 + item_index` for Consumables, `0x25D0 + item_index` for Tools) in addition to the 30-slot quick array.

### 📖 3. Compendium 100% Display Math
- **Authentic Registerable Denominator:** Updated the Compendium progress denominator to calculate against the true 224 registerable Personas (232 mask minus 8 dead/reserved entries). Batch unlocking now displays `224 / 224 REGISTERED (100%)`.

### 🧪 4. Automated Tests
- **122/122 Unit Tests Passing (100% Green)** including dedicated TDD regression tests in `tests/test_ingame_parity.py`.
