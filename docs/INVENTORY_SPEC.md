# Inventory Web-App Spec — P5R Save Studio (Change of Heart)

Status: **LIVE-VERIFIED 2026-08-19** — 10/10 categories mapped via ITEM.TBL (docs/ITEM_TBL_MAP.md) + live purchase diffs (research/RESEARCH.md §1.3-1.4.1). Prior oracle-verified (DeepSeek V4 + Gemini) core still holds; extended by Antigravity.

> **Spec sync — 2026-08-19 (post-ITEM.TBL):** Outfits `0xA000+` is now 286 rows (stride 32, seg6) — was [CANDIDATE]. All 10 prefixes map 1:1 to ITEM.TBL segments. `S5b: Dual View + Character Chips` (this rebuild) is the approved extension; rationale in `docs/adr/0002-item-studio-dual-view.md`.

Owner: Hermes + Antigravity. Read this before any inventory work.
Grounding: reverse-engineered save mechanics are [VERIFIED] via live purchase diffs (see research/RESEARCH.md §1.3) + ITEM.TBL ground truth (`J:\...\P5R\CPK\BATTLE/TABLEITEM.TBL` 168,416B, 10 segs). The GameBanana cheat save layout is INVALID as a reference — only live diffs count.

---

## 1. User story

> As a P5R player who loves the game but hates the grind, I want to load my save,
> see the **real** state of my owned gear and stack counts, and make targeted edits —
> own a weapon, set an item count — without my changes disappearing or corrupting
> the save.

Two non-negotiables:
1. **Truthful read** — what the UI shows is what's actually in the save.
2. **Safe lasting write** — edits stick in-game (equipment = owned-flags, not counts).

**Killer feature = "see and fix your bag."** One-click max-everything presets are a
LATER convenience layer, only after correct read/write is proven. (Both oracles.)

---

## 2. Save mechanics this spec rests on (all [VERIFIED] via live diffs 2026-08-19)

Item id = `category_prefix << 12 | index` (10 prefixes now, per ITEM.TBL — docs/ITEM_TBL_MAP.md). Storage is two meta-paradigms (owned-flag vs count) applied per-prefix:

| Prefix | Type | Seg (ITEM.TBL) | Rows | Save storage | Base | Status |
|---|---|---|---|---|---|---|
| 0x1000 | Melee | 5 MeleeWeapons | 296×48 | OWNED-FLAG (0x01/0x00) | `0x1B30 + idx` | ✅ VERIFIED (3 pts) |
| 0x2000 | Consumable | 2 Consumables | 696×48 | COUNT-ARRAY (0..99) | `0x2410..0x2800` (sub-bases) | ✅ primary sub-bases verified |
| 0x3000 | Accessory | 0 Accessories | 512×64 | OWNED-FLAG / COUNT* | `0x2330+idx` (owned) / `0x2490` [INFERRED count side] | ✅ owned verified |
| 0x4000 | Skill card | 7 SkillCards | 651×24 | COUNT-ARRAY (dupes stack) | `0x2E30 + idx` (`addr-0x0226F024`) | ✅ VERIFIED |
| 0x5000 | Protector | 1 Armor | 301×48 | COUNT/STACK `0x1F30+idx` | `0x1F30 + idx` (0..99) + mirror `0x1A440` | ✅ VERIFIED 301 |
| 0x6000 | Tool | — (no seg) | — | COUNT (stacks) | `TOOL_OFFSET_BY_DB_ID` | ✅ VERIFIED |
| 0x7000 | Ranged | 8 RangedWeapons | 256×132 | OWNED-FLAG | `0x3430 + save-idx` | ✅ VERIFIED (106 via addr-0x02272456) |
| 0x8000 | Treasure/material | 4 Materials | 256×44 | COUNT-ARRAY (stacks) | `0x2A30 + idx` (`addr-0x0226F024`) | ✅ VERIFIED |
| 0x9000 | Key item | 3 KeyItems | 256×12 | COUNT/FLAG | `KEY_ITEM_OFFSET_BY_DB_ID` (`addr-0x0226F024`) | ✅ VERIFIED (583 mapped, live 28) |
| 0xA000 | Outfits | 6 Outfits | 286×32 | OWNED-FLAG | `0x3230 + idx` (0/1) + mirror `0x1B740` | ✅ VERIFIED 286 |

*Accessory is dual-nature pre-`ITEM.TBL` but currently stored as `0x2330` owned-flag per handoff.md:57 — keep spec consistent with implementation; re-prove if a count side surfaces. Outfits `0xA000` was [CANDIDATE] — now 286 rows verified, save at `0x3230` (handoff.md 21:00).*

Mirror `+0x18510` exists and is verified for both counts and ownership flags.
Write primary AND mirror. Read should detect mirror mismatch.

---

## 3. Spec items S1–S5 (oracle-reviewed)

### S1 — Truthful Inventory Read (BUILD FIRST)
Read each item from its real storage paradigm. Never merge the master count region
and the 30-slot quick array into one list (that is the current phantom-items bug).
Return a **normalized inventory model**:
- `owned_gear`: gear id -> owned bool (melee/protector/accessory/ranged).
- `stacks`: item id -> count 0..99 (consumables/skill cards/tools/treasure).
- `key_flags`: key item -> flag, story-sensitive marking.
Logic: one canonical source per item; conflict between count-region and quick-array
resolved to count-region + surfaced/logged. Mirror mismatch reported, not silently
tolerated. Unmapped ranged ids returned as `unknown` (not hidden, not editable).

### S2 — Paradigm-Correct Writes (build with S1)
Writes route by category prefix:
- Gear (0x1000/0x3000/0x5000): write owned-flag byte `0x00`/`0x01` + mirror. NEVER expose a quantity control.
- Ranged (0x7000): write via verified DB-id → save-id map. Refuse unmapped ids.
- Stacks (0x2000/0x4000/0x6000/0x8000): write count byte 0..99 + mirror.
- Key items (0x9000): write flag/bit **only through the guard** (see S4).
Clamp stack counts to 0..99. Gear writes set `0x01`, clear `0x00` — never count values.

### S3 — Round-Trip Integrity (mostly DONE — protect it)
- Save → re-sign CRC + AES.
- Auto-backup (timestamped) before first write.
- Reload shows identical normalized state.
- Failed save leaves original + backup unchanged.
Current: backup/restore + re-sign + **126/126 tests pass**. Add regression tests as S1/S2 change the write paths.

### S4 — Key-Item / Story-Flag Guard (cheap, high safety — build 2nd)
- Key items live in a GUARDED section, visually separated, **read-only by default**.
- Editing a story flag requires explicit confirmation; cancel = no bytes change.
- Known story-sensitive bits stay read-only; a restore-defaults action reverts unsaved edits.
- Backend must know safe vs story bits — this is domain data, not just a UI warning.

### S5 — Clear UI Model (build after S1/S2 — the visible rewrite)
Three sections, not two (both oracles):
1. **Gear** — filled ◆ owned / grey-outline ◇ not owned. Single click toggles owned. Batch actions later.
2. **Items** — count steppers (`- [qty] +`), type-in, max 99. Category badges.
3. **Key Items** — guarded, read-only by default, risk label.
Search + filters across all sections, preserving unsaved (staged) edits.

UI direction endorsed by both oracles: **Option A — tabbed split** (Gear / Items / Key Items),
cleanest mapping to the storage model, least prone to the flat-list bug. (Options B/C exist;
B "recreates the flat-list mental model"; C is slower for bulk.)

---

## 4. Backend redesign (the real work — oracle corrected "frontend = the rewrite")

The app is ~30–40% toward spec. The 60% that exists is crypto/backup/tests. The
missing 60–70% is the **domain inventory layer**:

1. **Normalized read model** — S1. Fix `get_inventory()` (stop merging count-region + quick-array).
2. **Editor-state staging buffer** — edits apply to an uncommitted buffer; payload bytes touched only on save. Prevents mid-edit corruption.
3. **Mirror parity** — every gear/stack write updates `+0x18510`; read detects mismatch.
4. **Complete ID-mapping tables** — full DB-id → save-id map per category. Ranged only 2/106 mapped; that is domain data, not UI.
5. **Key-item bitfield safety** — safe vs story bits in backend.
6. **Range/validation rules** — stacks 0..99; gear 0x00/0x01; ranged refuse unmapped.

---

## 5. Rebuild order (both oracles agree)

```
Phase 1: S1  truthful read (normalized backend model)   <- START HERE
Phase 2: S4  key-item guard (cheap, high safety)
Phase 3: S2+S5  paradigm writes + three-bucket UI
Phase 4: S3  already done — regression-test it
```

Vertical slice first: **S1 + S2 for ONE gear category (melee) + ONE stackable
(consumables)**, end-to-end, tested. Then broaden.

Do NOT build one-click max-everything presets yet. (Exception: "max stack" for
stackable counts only is safe later.)

---

## 6. Acceptance criteria (oracle-supplied, per item)

### S1
- Save with melee `0x1B30+idx=0x01` → UI shows Owned.
- Consumable present in count-region but not quick-array → correct count, no phantom duplicate.
- Item in both regions with conflicting counts → canonical count-region wins + conflict surfaced.
- Gear flag 0x00 → "Not owned" (never "count 0").
- Mirror mismatch → warning or defined primary.

### S2
- Toggle melee owned → `0x1B30+idx` = `0x01` and mirror matches.
- Set consumable 99 → count + mirror update; reload shows 99.
- Gear item → UI offers owned toggle, NEVER a quantity control.
- Ranged with unmapped id → marked unsupported, no write attempted.
- Stack count <0 or >99 → clamped or rejected.

### S3
- Edited save passes game CRC/AES verification.
- Backup created before original modified.
- Reload → normalized state matches edits.
- Failed save → original + backup unchanged, error shown.

### S4
- Key-item/story edit → risk warning before write.
- Cancel → no key-item bytes change.
- Confirm → write proceeds, backup still created.
- Known risky bits → marked story-sensitive, read-only default.

### S5
- Gear and stacks visually separated into sections.
- Gear row = owned state, no stepper. Stack row = stepper, no owned toggle.
- Key item = guarded section with risk label.
- Search includes all sections, shows item type.

### S5b — Dual View + Character Filter Chips (added 2026-08-19, this rebuild — see docs/adr/0002)

- **Dual view:** `Owned Pouch` (only owned in this save) vs `Full Catalog` (all knowable items per ITEM.TBL, dimmed vs checked). One global toggle, shared staged buffer, search+chips preserved across switches. Pouch is default.
- **Character chips:** `All | Joker | Skull | Mona | Panther | Fox | Queen | Noir | Oracle | Crow | Violet` for gear categories (`0x1000`/`0x7000`/`0xA000`, `0x5000` where tagged). Parsed from `data/Weapon*.txt` role column, not hardcoded; disabled when no owner data.
- **Three-bucket inside each view:** Gear `◆◇` toggle / Items `- [qty] +` / Key `🔒` guarded — same pill component, mirrored in both views + virtualized lists.

---

## 7. Current-app gap log (synced to handoff 2026-08-19 21:00 — INFERRED rows now VERIFIED)

| Spec | Current | Grade |
|---|---|---|
| S1 read | `get_normalized_inventory()` normalized; no phantom merge | 🟢 PASS (10/10, 146/146) |
| S2 write | Paradigm-correct per prefix (gear `0x00/0x01` + mirror, stacks `0..99` + mirror; Ranged 106 mapped) | 🟢 PASS |
| S3 integrity | Backup/restore + re-sign; dirty-preserved save pipeline | 🟢 PASS (146/146) |
| S4 key guard | Guarded read-only + `UNLOCK` confirm; `Confirm→dirty`, `Cancel→0 bytes` | 🟢 PASS |
| S5 UI (buckets) | Three buckets in single list (Gear ◆◇ / Items stepper / Key guarded) | 🟡 HALF — needs dual-view lift |
| S5b dual view | Owned Pouch vs Full Catalog toggle missing | 🔴 FAIL — this rebuild |
| S5b character chips | Owner filter row missing | 🔴 FAIL — this rebuild |
| Staging buffer | `_staged_inventory` + `inventory_normalized` payload | 🟢 PASS |
| Mirror read-check | Surfaced as `mirror_mismatches` + banner | 🟢 PASS |
| Ranged id-table | 106/106 via `addr-0x02272456` | 🟢 PASS |

## 8. Open data gaps to close as part of S1/S2
- ITEM.TBL parse (authoritative category/subtype set + stackable-vs-unique flags) — SEH: tools/cpk_extract.py.
- Full DB-id → save-id map per category (ranged first).
- Key-item safe/story bit regions.
- Remaining consumable sub-bases (SP/revival/ailment/attack).
