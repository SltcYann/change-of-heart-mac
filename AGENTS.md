# AGENTS.md — p5r-save-editor (Change of Heart)

> **Agent: read this first.** It is your map. Open deeper docs by line range only when needed.

## Where to look (on-demand)

| Need | File | Lines |
|------|------|-------|
| Durable memory | `MEMORY.md` | Full (decisions, offsets, pitfalls, session history) |
| Current state | `STATUS.md` | Full (phase, gate, next action, blockers) |
| Machine state | `state.json` | JSON (phase, gate, test count, pinned SHAs) |
| Spec | `docs/INVENTORY_SPEC.md` | 49-72 + Ready/Done header |
| Map | `docs/ITEM_TBL_MAP.md` | full (10 segs) |
| Visuals | `screenshots/current_state/` | 10 PNGs (baseline UI) |
| Checklist | `docs/IN_GAME_TEST_CHECKLIST.md` | full |
| Rebuild Plan | `docs/ITEM_STUDIO_REBUILD_PLAN.md` | full — **next build** |
| ADRs | `docs/adr/0000-template.md` | — |
| Env bootstrap | `PROJECT_BOOTSTRAP.md` | **read first — environment capabilities** |

Path costs ~5 tokens; document behind it costs 2000 only when opened.

## Startup (in order)

1. Read `AGENTS.md` (this file).
2. Read `STATUS.md` and `state.json` — verify they agree. If they disagree, STOP and fix STATUS.md.
3. Read `MEMORY.md` for durable context.
4. Read latest 1-2 session logs in `memory/`.
5. `git status` + `git log -5`.
6. Run `python scripts/check-invariants.py` (full check) or `python scripts/check-invariants.py --quick` (skip git diff).
7. `python -m unittest discover -s tests` (168 tests; oracle-corpus tests auto-skip when live saves are absent).

## Exit Contract (do this every session)

1. Run `python scripts/check-invariants.py` (or project linter).
2. Update `MEMORY.md` with new durable facts/decisions.
3. Append session log to `memory/YYYY-MM-DD-topic.md`: goal, changes, decisions, tests, blockers.
4. Update `state.json`: phase, gate, last_session, test_count, next_action, blockers, updated_at.
5. Update `STATUS.md` to match `state.json`.
6. Commit hygiene files.
7. Verify working tree cleanliness — no scratch/prototype files tracked in git.
8. If `HANDOFF.md` exists (legacy), archive it to `archive/handoffs/`.

## Repository Cleanliness & Shipping Manifest

- **Shipping Core (Tracked on GitHub):**
  - App Engine: `main.py`, `server.py`, `core/`, `data/`, `web-app/` (clean templates, styles, assets, persona portraits).
  - Test Suite: `tests/` (161+ unit tests).
  - Public Docs: `README.md` (user-facing only), `SAFETY.md`, `STATUS.md`, `state.json`, `LICENSE`, `P5R_Save_Editor.spec`.
- **Internal / Gitignored (Never Ship to GitHub):**
  - Agent state: `HANDOFF.md`, `archive/`.
  - Research & Reverse Engineering: `research/`, `diff/`, `scratch/`, `tools/`, `scripts/`.
  - Binary & visual artifacts: `screenshots/`, `dist/`, `build/`, `*.zip`.
  - Ephemeral experiments: Any `mockup_*.html`, `prototype_*.html`, or temporary test graphics must be deleted before release commits.

## Architectural Invariants (Falsifiable — each has a pass/fail test)

1. **Save integrity:** Write primary + mirror (+0x18510), read warns on mismatch. Test: `test_mirror_sync.py`
2. **No quick-array merges:** `0x3530` temp buffer never merged with master counts. Test: `check-invariants.py` banned pattern scan.
3. **Ground truth from game data:** Offsets verified via 2-save diff (`tools/diff_mapper.py`), not web research. Test: manual verification gate.
4. **Build/test gate passes:** 161+ tests pass before exit. Test: `check-invariants.py`.
5. **Frozen offsets respected:** `0xA000+` Outfits not wired until diff proves. Test: manual check in code review.
6. **Tool Output Hygiene:** Never run un-bounded terminal dump commands. Always pipe or truncate verbose outputs (`git status -s`, `pytest -q`, `head -n 50`, `tail -n 30`) to protect the context window from token bloat.

## Circuit Breaker & Git Revert Protocol

If the same test or build fails **3 consecutive times**, HALT immediately:
1. **Preserve Work to Patch:** Save ongoing changes to research scratch:
   ```bash
   git diff > research/failed_attempt.patch
   ```
2. **Reset Working Tree:** Revert working directory to the last known green commit:
   ```bash
   git checkout .
   git clean -fd
   ```
3. **Set Blocked State:** Update `state.json` and `STATUS.md` with `"gate": "blocked"`.
4. **Log Blocker:** Append the root cause and failure trace to `STATUS.md` and `memory/YYYY-MM-DD-topic.md`.
5. **Halt Execution:** Exit turn and request human guidance. Never silently change or bypass an invariant.

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
- `python -m PyInstaller P5R_Save_Editor.spec --noconfirm --clean --distpath dist` — rebuild `dist/P5R_Save_Editor.exe`.
- `python tools/capture_ui_state.py` — automated headless capture of all 10 views into `screenshots/current_state/`.
- `npm run lint:context` — token budget + path + ADR check (fails = don't report done).
- `python scripts/check-invariants.py` — run invariant checks.

## Ready/Done gates (block work if not [x])

**Ready (START) before coding:**
`[ ] stakeholders [ ] MRM is now [ ] ≥2 alternatives [ ] ITEM.TBL seg/stride cited [ ] ADR file created`

**Done before stamp:**
`[ ] 134/134 + mirror read-check warns [ ] no phantom merge [ ] STATUS.md stamped [ ] state.json updated [ ] lint:context pasted`
