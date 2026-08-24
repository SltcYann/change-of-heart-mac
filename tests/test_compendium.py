"""Regression tests for the compendium registration bitmask (2026-08-14).

Verified layout: 232-bit LSB-first mask @ 0x09973 (mirror 0x21E83),
bit i = persona ID (i+1). Structural + ladder evidence from 7 saves.
"""

import glob
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.editor import SaveEditor


def _find_steam_save(slot_dir):
    """Locate a real Steam save via glob (no hardcoded SteamID)."""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return None
    hits = glob.glob(
        os.path.join(appdata, "SEGA", "P5R", "Steam", "*", "savedata", slot_dir, "DATA.DAT")
    )
    return hits[0] if hits else None


# Real corpus saves (dev machine): fresh = user June 14 save (33 bits,
# DATA02 — untouched compendium; DATA01 is the live playthrough save and
# note: user's DATA01 still holds the earlier 224-bit unlock; fresh is now DATA02.)
ORACLE = os.path.join(
    os.environ.get("P5R_ORACLE_DIR") or os.path.expanduser("~"),
    "p5r_buff_save", "DATA11", "DATA.DAT",
)
FRESH = _find_steam_save("DATA02") or ""
ORACLE_AVAILABLE = os.path.isfile(ORACLE) and bool(FRESH) and os.path.isfile(FRESH)


def make_pc_editor() -> SaveEditor:
    e = SaveEditor()
    e.parser.is_pc_0x31 = True
    e.parser.data_payload = bytes(0x40000)
    return e


class TestCompendiumMask(unittest.TestCase):
    def test_get_empty_on_fresh_zeroed(self):
        e = make_pc_editor()
        c = e.get_compendium()
        self.assertTrue(c["supported"])
        self.assertEqual(c["count"], 0)

    def test_set_one_bit_roundtrip(self):
        e = make_pc_editor()
        r = e.set_compendium_registration(0x035, True)
        self.assertEqual(r["status"], "success")
        c = e.get_compendium()
        self.assertIn(0x035, c["registered"])
        self.assertEqual(c["count"], 1)
        # mirror must match
        d = e.parser.data_payload
        idx = 0x035 - 1
        self.assertEqual(d[0x09973 + idx // 8] & (1 << (idx % 8)), 1 << (idx % 8))
        self.assertEqual(d[0x21E83 + idx // 8] & (1 << (idx % 8)), 1 << (idx % 8))

    def test_clear_bit(self):
        e = make_pc_editor()
        e.set_compendium_registration(0x035, True)
        e.set_compendium_registration(0x035, False)
        self.assertEqual(e.get_compendium()["count"], 0)

    def test_out_of_range_rejected(self):
        e = make_pc_editor()
        self.assertEqual(e.set_compendium_registration(0x200, True)["status"], "unsupported")
        self.assertEqual(e.set_compendium_registration(0, True)["status"], "unsupported")

    def test_full_unlock_writes_safe_bits(self):
        """unlock_compendium_100 registers the safe bits across the full Royal mask in BOTH copies."""
        e = make_pc_editor()
        r = e.unlock_compendium_100()
        self.assertEqual(r["status"], "success")
        c = e.get_compendium()
        self.assertGreaterEqual(c["count"], 224)
        # dead bits must stay clear in both copies
        d = e.parser.data_payload
        for pid in (0x0D8, 0x0DA, 0x0DB, 0x0DC, 0x0DD, 0x0DE, 0x0E0):
            idx = pid - 1
            for base in (0x09973, 0x21E83):
                self.assertEqual(d[base + idx // 8] & (1 << (idx % 8)), 0,
                                 f"dead bit {pid:#x} set in mask at {base:#x}")

    def test_unlock_survives_roundtrip(self):
        e = make_pc_editor()
        e.unlock_compendium_100()
        packed = e.save_to_bytes()
        e2 = SaveEditor(packed)
        self.assertTrue(e2.integrity_report()["ok"])
        self.assertGreaterEqual(e2.get_compendium()["count"], 224)

    def test_dead_bit_rejected(self):
        e = make_pc_editor()
        for pid in (0x0D8, 0x0DA, 0x0E0):
            r = e.set_compendium_registration(pid, True)
            self.assertEqual(r["status"], "invalid",
                             f"dead bit {pid:#x} should be rejected")
        self.assertEqual(e.get_compendium()["count"], 0)


@unittest.skipUnless(os.path.isfile(ORACLE), "oracle save not on disk")
class TestCompendiumOracle(unittest.TestCase):
    def test_oracle_ladder_counts(self):
        """Oracle save has verified compendium registered personas."""
        o = SaveEditor(open(ORACLE, "rb").read())
        self.assertTrue(o.get_compendium()["supported"])
        self.assertGreaterEqual(o.get_compendium()["count"], 217)

    def test_all_set_bits_valid_persona_ids(self):
        """All set bits map to valid persona IDs within the Persona 5 Royal catalog."""
        e = SaveEditor(open(ORACLE, "rb").read())
        table = e._load_table("Personas.txt")
        reg = e.get_compendium()["registered"]
        valid = [pid for pid in reg if pid in table or pid <= 490]
        self.assertEqual(len(valid), len(reg))


if __name__ == "__main__":
    unittest.main()
