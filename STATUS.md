# STATUS.md — P5R Save Editor (Change of Heart)

> Human-readable current state. Synced from state.json on every exit.
> Updated: 2026-08-21 05:30 EDT

## Current State
- **Phase:** implementation
- **Gate:** ready
- **Mode:** single-agent

## Last Completed
- 2026-08-23: Hotfix v1.1.0 Release Binary — Diagnosed and resolved WebView2 bundling issue caused by Python environment toolchain mismatch; re-compiled standalone executable with Python 3.14.6 + PyInstaller 6.22.0 embedding full `pywebview` / `msedgewebview2` runtime; verified via live process smoke test; updated GitHub Release `v1.1.0` asset.
- 2026-08-23: Implemented Reddit community requests (`u/Gruphius`): Fixed Haru (Slot 6) / Futaba (Slot 7) party swap, added Party Persona Evolution Tier (1-3) selector, activated Level <-> EXP cubic curve auto-sync, enabled Romance route toggle (`0x02`) on PC `0x31` saves, unlocked Key Items in Cheat Shop; 165/165 unit tests pass.
- 2026-08-21: Retired 3rd Semester Emergency Rescue false-promise feature; refactored Stage 5 to dedicated Reversible Backups & Safety Vault; removed dead `/api/emergency-rescue` endpoint and in-memory reload bug; updated Safety rule 8; 161/161 tests pass.
- 2026-08-21: Inventory UX pass — receipt review before save, per-item revert, global search, tab clusters, context menu + keyboard, main-list batching, UNWIRED drift resolved (Cards/Loot/Tools now writable; Outfit honestly labeled FROZEN), COH1 share codes. 161/161 tests. Captures re-baselined + 4 UX shots.
- 2026-08-21: v1.0.10 RELEASED — compendium fix verified in-game ×2 slots; GitHub Release with asset.
- Item Studio Cheat Shop Phase A-D implemented + validated
- Equipment ownership all 4 categories verified

## Next Action
- Await user confirmation from `u/Gruphius` on Reddit regarding v1.1.0 standalone window operation and save migration.

## Blockers
- None.

## Recent Session
- 2026-08-21: inventory UX pass R1-R9 (memory/2026-08-21-inventory-ux-pass.md)
- 2026-08-21: compendium 96% fix + in-game verification ×2 slots + v1.0.10 release

## Pinned SHAs
- None (no upstream dependencies)

## Build
- Latest: `dist/P5R_Save_Editor.exe` (61.5 MB, rebuilt 2026-08-21 05:50 ET — includes inventory UX pass R1-R9)
- PyInstaller 6.22.0 / Python 3.14.6
- NOT pushed to GitHub (v1.0.8 on GitHub predates all compendium + equipment fixes)
