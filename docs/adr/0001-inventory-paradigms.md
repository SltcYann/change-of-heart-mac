# ADR 0001 — Inventory storage paradigms (10 prefixes over 2 meta-paradigms)

- Status: **Accepted** — 2026-08-19 (Hermes + Antigravity; oracle DeepSeek V4 + Gemini)
- Supersedes: INVENTORY_SPEC §2 four-row summary
- Context: `BATTLE/TABLEITEM.TBL` 168,416B decompressed → 10 segs (512/301/696/256/256/296/286/651/256) + `get_normalized_inventory()` live.
- Decision: Model as 10 prefixes → 2 meta-paradigms: `owned-flag 0x00/0x01 + mirror +0x18510` for `0x1000/0x7000/0xA000` (and optionally `0x3000`), vs `count 0..99 + mirror` for `0x2000/0x4000/0x5000/0x6000/0x8000`, with `0x9000` as `KEY_ITEM_OFFSET_BY_DB_ID` (583). `Four paradigms` in early spec was useful shorthand; this is the extended form.
- Consequences: Gear rows never show `x99`; Ranged 106 are first-class (no `unknown` placeholder); Outfits 286 are shippable.

Links: `docs/ITEM_TBL_MAP.md`, `research/RESEARCH.md §1.4.1`, `handoff.md:57-72`.
