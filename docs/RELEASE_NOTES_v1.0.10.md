# Release Notes — Change of Heart: Persona 5 Royal Save Studio (v1.0.10)

## 🎭 The 96% Compendium Bug — Root-Caused, Fixed & Proven In-Game

**Change of Heart v1.0.10** fixes the last compendium reliability issue: Unlock ALL now produces a **byte-genuine 100% Velvet Room** — verified on two independent saves, in-game.

---

### 🐛 Root Cause (found 2026-08-21)

Users running `Unlock ALL` saw the editor report success but the game displayed **Completed 96%**.

1. The UI staged a **filtered** persona list (party Personas, Satanael variants, and story ids excluded under the belief "the game never registers them").
2. On save, the backend per-persona sync loop **actively cleared** every registration bit missing from that list and never wrote their Velvet Room records.
3. The save ended up with 171/232 mask bits and 225/232 records. **The game's `Completed %` counts Velvet Room records**, not the mask → 225/232 ≈ 96%.

### ✅ The Fix

- `Unlock ALL` now arms a dedicated flag that routes to the verified backend full-unlock (`unlock_compendium_100()`), producing **exact genuine-save parity**:
  - All **224 live registration bitmask bits** — including party personas (`0xCA–0xD3`) and Satanael (`0xAA`/`0xC7`), which genuine 100% saves *do* set.
  - All **232 Velvet Room records** (48-byte stride, primary `0x04270` + mirror `0x1C780`), including Metatron's slot-0 record present in genuine saves.
  - Both mask mirrors synchronized (`0x09973` / `0x21E83`).
- Granular single-persona toggles keep their existing staged path (state-preserving).
- The unlock flag resets after a successful save or compendium reset.

### 🔬 Verification

- Diffed against three genuine 100% NG++ oracle saves: **0 missing bits, 0 missing records** after unlock.
- **In-game, two independent saves:** one surgically repaired, one unlocked end-to-end via the new EXE flow — both show **Completed 100%**, Satanael summonable, no greyed ghost at slot 210.
- **157/157 unit tests**, including 4 new wiring regression tests (`TestCompendiumUnlockAllWiring`) that fail if anyone re-filters the unlock list or drops the backend flag again.
- Full invariant check passes (required files, state, test suite, banned-pattern scan).

### 📦 Download & Run

- Download `CHANGE_OF_HEART_v1.0.10.zip` (or `P5R_Save_Editor.exe`) from the Assets below.
- Run the executable — no installation required.
- Automatic timestamped backups are created before every save.

> ⚠️ Always close `P5R.exe` before saving, and keep your backups. If Steam Cloud shows a conflict dialog after an external edit, choose the local file.
