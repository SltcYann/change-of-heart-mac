# ITEM.TBL — Authoritative Category Map (P5R PC, BASE.CPK)

**Source:** `J:\SteamLibrary\steamapps\common\P5R\CPK\BASE.CPK` → `BATTLE/TABLEITEM.TBL`  
**Extraction:** `tools/extract_tables_job.py` (TOC offset_base = min(TocOffset, ContentOffset), CRILAYLA decompress) → `tools/cpk_out/tables/BATTLE_TABLEITEM.TBL`  
**Size:** stored 33,640 B → decompressed 168,416 B, 10 segments (P5RTblSegmentFinder, BE length, align 16).  
**Date:** 2026-08-19

## Segment layout (verified)

| Seg | Name (Persona.Merger P5R) | Length | Stride (resolver) | Rows | Save prefix | Data file | Status |
|-----|---------------------------|--------|-------------------|------|-------------|-----------|--------|
| 0 | Accessories | 32,768 | 64 | **512** | `0x3000` | `Accessories.txt` | OWNED-FLAG `0x2330+idx` ✅ VERIFIED (2 pts) |
| 1 | Armor (Protector) | 14,448 | 48 | **301** | `0x5000` | `Clothes.txt` | OWNED-FLAG `0x1F30+idx` ✅ VERIFIED (2 pts) |
| 2 | Consumables | 33,408 | 48 | **696** | `0x2000` | `Items.txt` | COUNT-ARRAY `0x2410..0x2800` ⚠️ partial (med/protein/food) |
| 3 | KeyItems | 3,072 | 12 | **256** | `0x9000` | `Keyitems&essentials.txt` | OWNED-FLAG/bitfield, NOT count ⚠️ INFERRED — story-flag risk |
| 4 | Materials (Treasure) | 11,264 | 44 | **256** | `0x8000` | `Treasure.txt` | COUNT-ARRAY (stacks) ⚠️ INFERRED |
| 5 | MeleeWeapons | 14,208 | 48 | **296** | `0x1000` | `Weapon melee.txt` | OWNED-FLAG `0x1B30+idx` ✅ VERIFIED (3 pts) |
| 6 | Outfits | 9,152 | 32 | **286** | `0xA000+` | (no data file yet) | ❌ CANDIDATE → now VERIFIED as 286 rows, but **DO NOT wire save offset** until `ITEM.TBL`+save diff proves storage |
| 7 | SkillCards | 15,624 | 24 | **651** | `0x4000` | `Skill Cards.txt` | COUNT-ARRAY (dupes stack) ⚠️ INFERRED |
| 8 | RangedWeapons | 33,792 | 132 | **256** | `0x7000` | `Weapon ranged.txt` | OWNED-FLAG `0x3430+save-idx` ⚠️ partial (2 ids mapped, DB≠save) |
| 9 | Footer | 540 | — | — | — | — | unknown |

**Verification:** Row counts match `data/*.txt` line counts (e.g., Melee 296, Ranged 256, SkillCards 651, Accessories 512, KeyItems 256, Materials/Treasure 256), confirming this is the authoritative ground truth. The 9-prefix ID convention (`0x1000…0x9000`) maps 1:1 to these segments **except** Outfits (`0xA000`) which was previously Gemini [CANDIDATE] and is now proven as 286 rows.

## What this locks

- **Category set is complete:** 9 game categories + Outfits (0xA000+) exist. No other item category is in ITEM.TBL. The spec's "Four storage paradigms" (OWNED-FLAG vs COUNT-ARRAY vs bitfield) is orthogonal to this — this file proves the *type* side, not the save byte layout.
- **Outfits (0xA000+):** Now VERIFIED as 286 rows, stride 32, but save storage remains **unknown** — still **DO NOT wire** (see INVENTORY_SPEC.md §8). Needs a live outfit-ownership diff.
- **Stackable vs unique flag:** Not fully decoded. Each struct's first `u32` (offset 0) is mutually-exclusive bit flags per resolvers; fields at `24–26` (Consumables) and `20–26` (Melee) are `u8` sub-flags. The flag that marks `stackable (0..99)` vs `unique (owned)` is inside those bytes. Decoding requires per-row bit analysis against known in-game stackable items (e.g., `0x2001` Life Stone vs `0x1005` Blizz Dagger) — ranked as next RE step. For now we rely on the **save-dismissed oracle**: Consumables/Materials/SkillCards/Treasure are COUNT, Gear are OWNED-FLAG (verified via live 2-save diffs, research/RESEARCH.md §1.3).

## What remains for save mapping

- `0x4000` Skill Cards (651 rows) and `0x8000` Treasure/Materials (256 rows) now have **inferred** count bases wired in `core/editor.py:get_item_count_offset()` (`0x2450+idx` and `0x2490+idx` respectively) — marked `[INFERRED]` until a controlled 1-item purchase/Shadow-drop diff confirms the offset and mirror `+0x18510`.
- `0x6000` Tools (Infiltration) has **no dedicated ITEM.TBL segment** — `Tools&materials.txt` in `data/` is a composite view; its save bytes are at `0x25D0+idx` (inferred, consistent with prior work). Needs 1-item probe (lockpick/Goho-M).
- `0x2000` Consumable sub-bases (med `0x2530`, protein `0x25AA`, food `0x2600`, tools `0x25D0`) cover the 696 rows via sparse `idx` sub-ranges — SP/revival/ailment/attack sub-types still need per-subtype 1-item diffs.
- Ranged `0x7000`: only 2/256 mapped (`0x7010→0x13` Makaronov, `0x7020→0x25` Bianchi) — full `DB→save-idx` table needs buy-1-gun-per-batch diffs across the 256 rows.

## How to reproduce

```sh
python tools/extract_tables_job.py   # decompresses all BATTLE/TABLE*.TBL
# then:
python -c "import struct; d=open('tools/cpk_out/tables/BATTLE_TABLEITEM.TBL','rb').read(); off=0; [print(struct.unpack('>I', d[off:off+4])[0]) or (off:=off+4+struct.unpack('>I', d[off:off+4])[0]+(16-off%16)%16) for _ in range(10)]"
# stride/row check is in docs/ITEM_TBL_MAP.md
```
