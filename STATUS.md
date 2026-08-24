# STATUS.md — P5R Save Editor (Change of Heart)

> Human-readable current state. Synced from state.json on every exit.
> Updated: 2026-08-24 00:00 EDT

## Current State
- **Phase:** implementation
- **Gate:** ready
- **Mode:** single-agent

## Last Completed
- 2026-08-24: External audit fixes — fresh-clone test-suite breakage fixed (`scripts/roundtrip_harness.py` + `tools/lint_context.js` now tracked); CSRF Origin guard added to local API (loopback-only, no more `Access-Control-Allow-Origin: *`); username/SteamID scrubbed from tracked tests + harness (glob/env-based paths); dead `bottle` dep pruned, `psutil` added; root `HANDOFF.md` removed (byte-identical archived copy remains); state.json/STATUS/docs staleness synced. 168/168 tests.

## Last Completed
- 2026-08-23: Save Discovery & Manual Save Browse Fix — Implemented multi-location auto-discovery scanning Steam Userdata (`1687950/remote`), LocalAppData, and standard Roaming folders; added manual `📂 BROWSE...` button for custom/GamePass save files; verified via live process smoke test and comprehensive unit tests (168/168 passing).
- 2026-08-23: Hotfix v1.1.0 Release Binary — Diagnosed and resolved WebView2 bundling issue caused by Python environment toolchain mismatch; re-compiled standalone executable with Python 3.14.6 + PyInstaller 6.22.0 embedding full `pywebview` / `msedgewebview2` runtime; verified via live process smoke test; updated GitHub Release `v1.1.0` asset.
- 2026-08-23: Implemented Reddit community requests (`u/Gruphius`): Fixed Haru (Slot 6) / Futaba (Slot 7) party swap, added Party Persona Evolution Tier (1-3) selector, activated Level <-> EXP cubic curve auto-sync, enabled Romance route toggle (`0x02`) on PC `0x31` saves, unlocked Key Items in Cheat Shop; 168/168 unit tests pass.
- 2026-08-21: Retired 3rd Semester Emergency Rescue false-promise feature; refactored Stage 5 to dedicated Reversible Backups & Safety Vault; removed dead `/api/emergency-rescue` endpoint and in-memory reload bug; updated Safety rule 8; 161/161 tests pass.
- 2026-08-21: Inventory UX pass — receipt review before save, per-item revert, global search, tab clusters, context menu + keyboard, main-list batching, UNWIRED drift resolved (Cards/Loot/Tools now writable; Outfit honestly labeled FROZEN), COH1 share codes. 161/161 tests. Captures re-baselined + 4 UX shots.
- 2026-08-21: v1.0.10 RELEASED — compendium fix verified in-game ×2 slots; GitHub Release with asset.
- Item Studio Cheat Shop Phase A-D implemented + validated
- Equipment ownership all 4 categories verified

## Next Action
- Push updated changes to GitHub and publish hotfix release `v1.1.1` (or refresh `v1.1.0` asset).

## Blockers
- None.

## Recent Session
- 2026-08-21: inventory UX pass R1-R9 (memory/2026-08-21-inventory-ux-pass.md)
- 2026-08-21: compendium 96% fix + in-game verification ×2 slots + v1.0.10 release

## Pinned SHAs
- None (no upstream dependencies)

## Build
- Latest: `dist/P5R_Save_Editor.exe` (47.9 MB, rebuilt 2026-08-23 21:51 ET — save discovery + manual browse)
- PyInstaller 6.22.0 / Python 3.14.6
- GitHub: v1.0.10 released; local main is 1 commit ahead (save-discovery fix) — publish hotfix release `v1.1.1` next
