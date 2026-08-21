# In-Game Verification Checklist — Change of Heart v1.0.9-dev

**Build under test:** `dist/P5R_Save_Editor.exe` (59.9 MB, **2026-08-19 15:59 ET**) — Full 10-category inventory engine + 224 In-Game Compendium Parity + Key Items memory probing.  
**Prereq:** Backup your `DATA.DAT` (the editor auto-creates `backups/*.zip` on every save). Close `P5R.exe` before saving.

---

## 1. Compendium — 100% / In-Game 224 Parity / No Phantom

- [ ] Load save → Velvet Room → Compendium counter shows **X / 224 REGISTERED** (matching in-game Velvet Room registry, excluding non-summonable party/story entries).
- [ ] `Unlock ALL (100%)` → `Save Changes & Re-sign` → reload in game: compendium is 100% and **no greyed Satanael** at slot 210 (the `0xD3` mask bit is set, struct count is 232, not 233).
- [ ] Reload edited save in editor → `224/224` + `0xD3` set, no regression.

## 2. Gear & Costumes (OWNED-FLAG) — Melee / Ranged / Outfits

Each write is `base+idx = 0x01` + mirror `+0x18510`; `0` clears.

- [ ] **Melee:** Inventory tab → Melee sub-tab → shows owned melee weapons with `◆ OWNED` badge.
- [ ] **Ranged (Guns):** Guns sub-tab → shows owned firearms (e.g. Tkachev, Riot Police, Granelli M3).
- [ ] **Outfits:** Dedicated 👗 Outfits tab → shows all 286 costumes (School, Maid, Velvet, Featherman) with single-click `OWN / UNEQUIP` toggles.

## 3. Stacks & Equipment (COUNT-ARRAY) — Consumables / Protectors / Accessories / Skill Cards / Tools / Treasure

Count byte `0..99` + mirror; quick-array `0x3530` is ignored (no phantom).

- [ ] **Protectors (Combat Armor):** 🛡️ Armor sub-tab → shows owned battle armors (*Baseball Jacket, Shoulder Pads*, etc.) with count steppers `0..99`.
- [ ] **Consumables:** 🧪 Items sub-tab → stepper `-` / `+` / `99x` adjusts quantities cleanly without affecting other tabs.
- [ ] **Accessories:** 💍 Accs sub-tab → shows accessories with count steppers.
- [ ] **Infiltration Tools:** 🔑 Tools sub-tab → shows lockpicks, smokescreens, and crafting tools.
- [ ] **Skill Cards:** 🎴 Cards sub-tab → shows skill cards with count steppers.
- [ ] **Treasure / Loot:** 💎 Loot sub-tab → shows palace treasures and vendor loot.

## 4. Key Items (GUARDED & PROBED)

- [ ] 📜 Key Items sub-tab → accurately lists all **28 owned key items** (*DVD Player, Bio Nutrients, Fountain Pen, Grappling Hook, Stamp Book, Castle Map*, etc.).
- [ ] Guarded lock badge active to prevent accidental story flag corruption.

## 5. Integrity

- [ ] Every `Save` says `✓ Changes re-signed & saved! Auto-backup created: ...` and `AES + CRC SIGNED & VERIFIED`.
- [ ] Sidebar integrity pill stays `✔ AES + CRC SIGNED & VERIFIED` after round-trip.

---

## Pass / fail signal

- **Pass:** All of 1, 2, 3 (consumables), 4, 5 green. The three `[INFERRED]` categories in 3 either pass or you note which base still needs a diff.
- **Blocked before push:** If melee/ranged/protector/accessory fail to persist, or consumable `99` disappears, or a `KeyItem` edit happens without confirm/open guard — **do not push to GitHub** (remote is still `v1.0.8`). Paste the failing `item_id` + `0x...` offset + `CONFIDANT`/compendium symptom here and the next agent reads this file + `handoff.md`.

## Next probes (same protocol that cracked equipment — 1 unowned item, 2-save diff)

- Skill Card: duplicate 1 card via Yusuke. Tools: buy 1 Lockpick/Goho-M. Treasure: 1 material from buy/Shadow drop. Key item: 1 book (story-flag caution). Ranged: buy cheap guns across the 256-row range → extend `RANGED_SAVE_IDX_BY_DB_ID`. All new guns persist only after this probe.

*Refresh `http://127.0.0.1:3080` after any rebuild; the `web-app` Vite entry needs `dsh web`.*
