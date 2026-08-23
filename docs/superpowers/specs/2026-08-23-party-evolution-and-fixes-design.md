# Design Specification: Party Evolutions, Slot Fixes, EXP Auto-Sync & Romance Toggle

**Document ID:** `docs/superpowers/specs/2026-08-23-party-evolution-and-fixes-design.md`  
**Date:** 2026-08-23  
**Status:** PROPOSED (Pending User Review)  
**Origin:** Reddit Community Feedback (`u/Gruphius` save-migration requests)

---

## 1. Objectives

Provide 100% save-editing parity for players transferring, rescuing, or customizing late-game saves:
1. **Fix Haru (Slot 6) & Futaba (Slot 7) Party Swap:** Align internal party struct indices with authentic P5R game save layouts.
2. **Implement Party Persona Evolution Selector:** Expose authentic Tier 1 (Base), Tier 2 (Rank 10 Awakened), and Tier 3 (3rd Semester Royal) persona equipped states for all 9 teammates.
3. **Auto-Sync Level $\leftrightarrow$ EXP Curve:** Automatically write minimum cumulative EXP whenever a player's or party member's Level is edited, eliminating post-battle EXP stalling / erratic level spikes.
4. **Expose Romance vs. Friendship Route Toggle:** Enable toggling the Romance flag on PC `0x31` saves for Rank 9/10 Confidants.
5. **Enable Adding Unowned Key Items:** Allow adding missing key items from the catalog.

---

## 2. Technical Architecture & Verified Offsets

### A. Party Slot Mapping (Haru vs. Futaba)
- **Slot 6:** Haru Okumura (Seeds: `(213, 155, 30, 0xCF)` | Personas: `0x00CF` Milady, `0x00EC` Astarte, `0x00F7` Lucy).
- **Slot 7:** Futaba Sakura (Seeds: `(316, 182, 36, 0xD0)` | Personas: `0x00D0` Necronomicon, `0x00ED` Prometheus, `0x00F8` Al Azif).

### B. Party Evolution Matrix
```python
PARTY_PERSONA_EVOLUTIONS = {
    1: {"name": "Ryuji",    "t1": (0x00CA, "Captain Kidd"), "t2": (0x00D4, "Seiten Taisei"), "t3": (0x00F2, "William")},
    2: {"name": "Morgana",  "t1": (0x00CB, "Zorro"),        "t2": (0x00D5, "Mercurius"),     "t3": (0x00F3, "Diego")},
    3: {"name": "Ann",      "t1": (0x00CC, "Carmen"),       "t2": (0x00E9, "Hecate"),        "t3": (0x00F4, "Celestine")},
    4: {"name": "Yusuke",   "t1": (0x00CD, "Goemon"),       "t2": (0x00EA, "Kamu Susano-o"), "t3": (0x00F5, "Gorokichi")},
    5: {"name": "Makoto",   "t1": (0x00CE, "Johanna"),      "t2": (0x00EB, "Anat"),          "t3": (0x00F6, "Agnes")},
    6: {"name": "Haru",     "t1": (0x00CF, "Milady"),       "t2": (0x00EC, "Astarte"),       "t3": (0x00F7, "Lucy")},
    7: {"name": "Futaba",   "t1": (0x00D0, "Necronomicon"), "t2": (0x00ED, "Prometheus"),    "t3": (0x00F8, "Al Azif")},
    8: {"name": "Akechi",   "t1": (0x00D1, "Robin Hood"),   "t2": (0x00D2, "Loki"),          "t3": (0x00F9, "Hereward")},
    9: {"name": "Kasumi",   "t1": (0x00F0, "Cendrillon"),   "t2": (0x00F1, "Vanadis"),       "t3": (0x00FA, "Ella")},
}
```

### C. Atlus P5R Level $\rightarrow$ Cumulative EXP Formula
```python
def get_p5r_min_exp_for_level(level: int) -> int:
    """Calculate authentic minimum cumulative EXP threshold for Level L (1..99)."""
    # Authentic cubic curve matching Atlus EXP table
    # L=1: 0, L=20: ~15,000, L=99: ~1,050,000
    ...
```

### D. Romance Flags on PC `0x31`
- Located in `0x136A0 + arcana_idx * 16`:
  - `+0x00`: Status / lock byte (0x01 = Active, 0x02 = Romance)
  - When `romance = True`: write bit `0x02`.
  - When `romance = False`: mask out bit `0x02`.

---

## 3. UI Changes
1. **Velvet Room & Party (Stage 3):**
   - Correct avatar images and labels for Haru (Slot 6) and Futaba (Slot 7).
   - Add **Evolution Tier Dropdown**: `[⚡ Base Persona / Awakened (Tier 2) / Royal Awakened (Tier 3)]`.
   - Changing Level input dynamically displays the updated cumulative EXP.
2. **Confidants Studio (Stage 2):**
   - Add **💖 Romance Switch** next to Rank 9/10 for romanceable confidants (Ann, Makoto, Futaba, Haru, Takemi, Kawakami, Chihaya, Ohya, Hifumi, Kasumi).
3. **Item Catalog Modal:**
   - Allow adding Key Items directly to the save.

---

## 4. Verification Plan
- **Unit Tests:**
  - `test_haru_futaba_slot_indices`: Assert slot 6 returns Haru/Milady and slot 7 returns Futaba/Necronomicon.
  - `test_party_persona_evolution_write`: Assert equipping Tier 2 / Tier 3 Persona IDs writes accurately to `0x2C + slot*0x2B0 + 0x3A`.
  - `test_level_exp_autosync`: Assert level 50 write automatically sets matching EXP threshold.
  - `test_romance_flag_toggle`: Assert setting romance True/False updates `0x136A0` flags.
- **Automated Invariant Check:**
  - `python scripts/check-invariants.py` must pass 100% green.
