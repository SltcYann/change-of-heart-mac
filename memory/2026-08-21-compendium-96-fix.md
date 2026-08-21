# Session Log — 2026-08-21 Compendium 96% In-Game Bug
> Agent: ox-alpha (opencode). Trigger: user in-game test showed **Completed 96%** after Unlock ALL.

## Root Cause (verified, not inferred)
1. UI `unlockFullCompendium()` (app.js) staged a **filtered** registered list — excluded `STUB/STORY/PARTY_COMPENDIUM_IDS`.
2. On save, `server.py` per-pid loop (`set_compendium_registration(pid, is_reg)` for 1..437) **actively cleared** those mask bits and never wrote their Velvet Room records.
3. Result: user save DATA02 = 171/232 mask bits + 225/232 struct records. **The game's Completed % counts struct records** (denominator ≈232): 225/232 → 96%.
4. Genuine 100% oracle saves (DATA13/15/16, `C:\Users\kufis\p5r_buff_save`): mask = **all 224 live bits** (incl. party 0xCA-0xD3, Satanael 0xAA/0xC7/0xD3, RESERVE-named e.g. 0x47) + **232 records** (incl. Metatron slot 0x01 — bit dead but record present).
5. Prior belief "the game never registers party personas" is **WRONG** — oracle proves otherwise. Backend `unlock_compendium_100()` was already oracle-parity correct; the frontend simply never called it (`unlock_compendium` flag was dead wiring).

## Fixes
- **User save (immediate):** surgical patch 03:07 ET — OR'd 53 missing mask bits + copied 7 missing records (Metatron 0x001, Satanael 0xAA, Lucifer 0xFD, Throne 0x1AF, Surt 0x1B0, Caith Sith 0x1B4, Siegfried 0x1B5) from oracle DATA13, primary+mirror, re-signed. Verified 224/224 bits, 232/232 records, mirror synced, CRC+AES OK. Backup: `DATA.DAT.bak-pre100-20260821_030710`. Awaiting user in-game confirm.
- **Code:** app.js `unlockFullCompendium()` now arms `UNLOCK_COMPENDIUM_PENDING` → payload carries `unlock_compendium: true` → server runs verified `unlock_compendium_100()`. Flag resets after successful save and on compendium reset. No more frontend filtering of party/story ids.

## Tests
- Added `TestCompendiumUnlockAllWiring` (4 tests) in `tests/test_hardening.py`: flag armed, no party/story/stub filtering in unlock fn, payload carries flag + resets, server applies via `unlock_compendium_100()`, behavioral all-live-bits + mirror parity.
- **157/157 pass** (was 153). `node --check` ✅, `npm run lint:context` ✅.
- EXE rebuilt: `dist/P5R_Save_Editor.exe` 61.5 MB, 2026-08-21 03:21 ET.

## Decisions
- Unlock ALL = backend full unlock (single source of truth), not a staged frontend list. Granular per-persona toggles still use the staged-list path (preserves existing state).
- Did NOT add templates for the 7 pids — templates already existed; diag script's `template_exists` check was buggy (int vs JSON string keys).

## Blockers
- None.

## ✅ IN-GAME VERIFIED (user, 2026-08-21 ~04:00 ET)
1. **DATA02** (surgical patch): Velvet Room shows **Completed 100%** — Satanael Lv95 summonable, no ghost.
2. **DATA08** (new EXE Unlock ALL flow, was 96% like old DATA02): now **Completed 100%** — screenshot confirmed (Satanael ¥46,000, Arsène 93, Raoul/DLC present, party personas registered).
Fix proven general across two independent saves. Feature LOCKED.
