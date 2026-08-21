# Release Notes — Change of Heart: Persona 5 Royal Save Studio (v1.0.9)

## 🎭 In-Game Parity, Master Inventory Overhaul & Full Compendium

**Change of Heart v1.0.9** delivers complete in-game parity for all major game systems across Persona 5 Royal (PC / Steam / Game Pass). This release addresses long-standing reverse-engineering challenges around unique equipment ownership flags, dual-encoded fullwidth/Atlus name serialization, and multi-copy accessory tracking.

---

### ✨ Key Features & Highlights

#### 1. 🗃️ 10-Category Master Inventory Overhaul (S1–S5 Spec)
- **Unique Equipment & Cosmetic Flags (`◆ OWNED / ◇ NOT OWNED`)**:
  - **Melee Weapons (`0x1000`)**: Correctly writes 1-byte ownership flags (`0x1B30 + idx`) instead of invalid count values.
  - **Ranged Firearms (`0x7000`)**: All **106 playable guns** mapped across Joker, Ryuji, Morgana, Ann, Yusuke, Makoto, Haru, Akechi, and Kasumi (`0x3430 + save_idx`).
  - **Outfits & Costumes (`0xA000`)**: Dedicated **👗 Outfits** tab with all 286 DLC & story costumes tracked via unique flags at `0x3230 + idx`.
- **Stackable Quantity Counters (`0..99`)**:
  - **Protectors & Combat Armor (`0x5000`)**: 301 genuine combat armors (Dark Undershirt, Lynx Camo Vest, Tantric Oath) mapped to stackable quantities (`0x1F30 + idx`).
  - **Accessories (`0x3000`)**: Fixed storage paradigm to stackable quantities (`0x2330 + idx`). Players can now own multiple copies (e.g., 10x Black Rocks, 5x SP Adhesive 3).
  - **Consumables (`0x2000`)**: Verified sub-ranges across recovery medicines, stat proteins, and combat food items.
  - **Skill Cards (`0x4000`)**: Mapped to verified engine memory offsets (`0x2E30 + idx`).
  - **Infiltration Tools (`0x6000`)**: Crafting items (Lockpicks, Perma-Pick, Goho-M, Megido Bombs) mapped via direct offsets.
  - **Treasure & Palace Loot (`0x8000`)**: Mapped to verified engine memory offsets (`0x2A30 + idx`).
- **Zero Phantom Items**: Eliminated the legacy bug that merged the 30-slot pouch quick-array into inventory views.
- **Engine Mirror Auto-Healing**: Every write synchronizes both primary and secondary mirror slots (`+0x18510`).

#### 2. 🖋️ Full-Spectrum In-Game Name & Phantom Thief Team Changer
- **Dual Unicode & Atlus Font Encoding**:
  - Encodes First, Last, Full, and Phantom Thief Group names into both **Fullwidth Zen-kaku UTF-8** and Atlus's proprietary **2-byte internal font glyph table** (`0x80A1..0x80D4`).
  - Synchronizes across all 8 primary and mirror memory blocks (`0x13840..0x139B0` and `0x2BD50..0x2BEC0`).
  - Names now display flawlessly in save menus, in-game dialogue, status screens, and calling card sequences.

#### 3. 🃏 100% Clean Velvet Room Compendium
- **Full Spectrum (1..437)**: All 243 summonable Personas across Vanilla, DLC, and Royal 3rd Semester.
- **Satanael Ghost Bug Fixed**: Fixed the greyed-out duplicate Satanael at slot 210 by marking `0xD3` as mask-only (`PC31_COMPENDIUM_MASK_ONLY_IDS`), producing an authentic 232-struct compendium that matches genuine 100% NG+ saves.

#### 4. 🛡️ Security, Stability & Packaging
- **Guarded Key Items**: Sensitive story progression flags and Key Items are locked read-only by default with confirmation modals to prevent accidental soft-locks.
- **Dynamic Asset Packaging**: Dynamic data directory bundling ensures all 10 category tables are bundled into standalone binaries.
- **Automated Test Coverage**: **146/146 unit tests passing** (including roundtrip oracle tests against 10 real PC save files and multi-category structural regression tests).

---

### 📦 Download & Run
- Download `P5R_Save_Editor.exe` from the Assets below.
- Run the executable (no installation required).
- Automatic timestamped backups (`backups/*.zip`) are generated before every save.
