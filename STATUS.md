# STATUS.md — P5R Save Editor (Change of Heart)

> Human-readable current state. Synced from state.json on every exit.
> Updated: 2026-08-21 04:30 EDT

## Current State
- **Phase:** released v1.0.10 → next: UI overhaul / offset probes
- **Gate:** released — pushed + tagged + GitHub Release with asset
- **Mode:** single-agent

## Last Completed
- 2026-08-21: ✅ IN-GAME VERIFIED — DATA02 (surgical patch) + DATA08 (new EXE Unlock ALL, was 96%) both show Completed 100%. No Satanael ghost; party personas registered. Fix locked.
- 2026-08-21: Compendium 96% bug root-caused + fixed (UI Unlock ALL filtered party/story bits; server loop cleared them). Frontend arms `unlock_compendium` flag → backend `unlock_compendium_100()`. 157/157 tests (4 new wiring regressions). EXE rebuilt 03:21 ET.
- 2026-08-21: User save DATA02 surgically patched to genuine-100% parity — backup `.bak-pre100-20260821_030710`.
- Item Studio Cheat Shop Phase A-D implemented + validated
- Equipment ownership all 4 categories verified
- Compendium phantom pid-211 fixed

## Next Action
- Next build: authentic P5R UI overhaul (docs/superpowers spec — reconcile bulk-action conflict first) and/or offset probes to unfreeze SkillCard/Tool/Treasure/Outfit writes.
- Offset-dependent lifts (Outfit `0xA000+`, KeyItem mapping, SkillCard/Tool/Treasure bases) remain **frozen** until live `BASE.CPK` + paired PC saves for `tools/diff_mapper.py`.

## Blockers
- None.

## Recent Session
- 2026-08-21: **v1.0.10 RELEASED** — compendium fix verified in-game ×2 slots; pushed `main` (e3ba51a) + tag `v1.0.10` + GitHub Release with `CHANGE_OF_HEART_v1.0.10.zip` (61.3 MB). Note: repo-local git credential helper now routes via `gh` (stale OS credential for another account removed from the chain).
- 2026-08-21: compendium 96% fix + in-game verification ×2 slots (memory/2026-08-21-compendium-96-fix.md)
- 2026-08-20: Metroid Prime conventions audit, oracle SOP consult, P5R hygiene upgrade

## Pinned SHAs
- None (no upstream dependencies)

## Build
- Latest: `dist/P5R_Save_Editor.exe` (61.5 MB, rebuilt 2026-08-21 03:21 ET)
- PyInstaller 6.22.0 / Python 3.14.6
- NOT pushed to GitHub (v1.0.8 on GitHub predates all compendium + equipment fixes)
