# ADR 0002 — Item Studio: Owned Pouch vs Full Catalog + Character Chips

- Status: **Accepted** — 2026-08-19
- Context: Flat `INVENTORY_ITEM_COUNTS` list behind one tab conflates "my bag" with "the shop". Melee 296 + Ranged 256 span 9 thieves; no owner scoping. Users need audit (missing gear) as well as fix (owned qty/flag).
- Options considered:
  - (A) Single list + richer filters — keeps one render path, but Owned vs Catalog remain indistinct.
  - (B) **Dual view (Chosen):** Global `Owned Pouch | Full Catalog` toggle + `All | Joker | Skull | Mona | Panther | Fox | Queen | Noir | Oracle | Crow | Violet` chips for `0x1000/0x7000(/0xA000)`; three buckets preserved inside each view; shared staged buffer; URL hash sync.
- Decision: Implement (B) as `S5b` per `docs/INVENTORY_SPEC.md`. Parser for owner tags is data-driven from `data/Weapon*.txt` col 5; catalogue is `REFERENCE_DB['items']` join with normalized owned flag. Staged edits preserved across view/chip/search switches; empty pouch → "Browse Full Catalog" CTA.
- Consequences: Slightly more list-state (`mode+chara` atom), but end-user robust: browsing, auditing, and fixing are all first-class without reloading. Reuses existing `get_normalized_inventory()` + mirror/conflict surfacing.

Verification: dual-view invariants — `Pouch ⊂ Catalog`, toggling view preserves `search+chara+staged`, `146/146` stays green.
