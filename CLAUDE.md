# AGENTS.md — p5r-save-editor (Change of Heart)

> **Agent: read this first.** It is your map. Open deeper docs by line range only when needed.

## Where to look (on-demand)

| Need | File | Lines |
|------|------|-------|
| Truth | `handoff.md` | 20-55 |
| Research | `research/RESEARCH.md` | 1-65 + §1.4.1 ITEM.TBL |
| Spec | `docs/INVENTORY_SPEC.md` | 49-72 + Ready/Done header |
| Map | `docs/ITEM_TBL_MAP.md` | full (10 segs) |
| Checklist | `docs/IN_GAME_TEST_CHECKLIST.md` | full |
| ADRs | `docs/adr/0000-template.md` | — |

Path costs ~5 tokens; document behind it costs 2000 only when opened.

## Startup (in order)

1. Read `handoff.md:20-55`, then files above by relevance.
2. `git status` + `git log -5`.
3. `python -m unittest discover -s tests` (filtered 134; full 146 needs Temp perms).

## Constraints (violating = corrupt save)

- `J:\SteamLibrary\...\P5R\CPK\BASE.CPK` via `tools/cpk_extract.py` is ground truth. Not web.
- PC ≠ PS4: KHSaveEditor `0x357C`/`0x2252` is PS4 garbage on PC. Verify via 2-save diff (`tools/diff_mapper.py`).
- Save is 4 paradigms + mirror `+0x18510`: Gear `0x1B30/0x2330/0x1F30/0x3430+save-idx` owned-flag `0x00/0x01`; Stacks `0x2410..0x2800` count `0..99`. Write primary+mirror, read must warn on mismatch.
- Quick-array `0x3530` (30×[u16 id][u16 flag]) is never merged — surface as `conflicts` where count-region wins.
- `0xA000+` Outfits (286 rows, `ITEM.TBL` seg6) — DO NOT wire save offset until diff proves.

## Build order

S1 normalized read (backend, FIRST) → S4 key guard → S2+S5 paradigm writes + three-bucket UI (Gear ◆◇ / Items steppers / Key guarded) → S3 done. Vertical slice: melee+consumables end-to-end. No max presets yet.

## Commands

- `python tools/extract_tables_job.py` — decompress `BATTLE/TABLEITEM.TBL` (168416B).
- `pyinstaller P5R_Save_Editor.spec` — rebuild `dist/P5R_Save_Editor.exe`, verify at `http://127.0.0.1:3080`.
- `npm run lint:context` — token budget + path + ADR check (fails = don't report done).

## Ready/Done gates (block work if not [x])

**Ready (START) before coding:**
`[ ] stakeholders [ ] MRM is now [ ] ≥2 alternatives [ ] ITEM.TBL seg/stride cited [ ] ADR file created`

**Done before stamp:**
`[ ] 134/134 + mirror read-check warns [ ] no phantom merge [ ] handoff.md stamped [ ] lint:context pasted`
