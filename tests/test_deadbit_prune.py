import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.editor import SaveEditor

# Corpus-verified dead bits: never set in ANY of 21 real saves (excluding
# our own editor-polluted 232 save). 2026-08-16 full-corpus diff.
DEAD = {1, 216, 218, 219, 220, 221, 222, 224}


def make_pc_editor():
    e = SaveEditor()
    e.parser.is_pc_0x31 = True
    e.parser.data_payload = bytes(0x40000)
    return e


def set_bit(d, base, pid, val):
    idx = pid - 1
    if val:
        d[base + idx // 8] |= (1 << (idx % 8))
    else:
        d[base + idx // 8] &= ~(1 << (idx % 8))


class TestDeadBitPrune(unittest.TestCase):
    def test_read_masks_dead_bits(self):
        """get_compendium must never report dead ids as registered, but MUST
        report legitimately-registered ids like 115 (reserved-name, real)."""
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        for pid in (1, 216, 218, 224):  # truly dead (100%-save proven)
            set_bit(d, 0x09973, pid, 1)
            set_bit(d, 0x21E83, pid, 1)
        for pid in (10, 115):        # legitimately registrable
            set_bit(d, 0x09973, pid, 1)
            set_bit(d, 0x21E83, pid, 1)
        e.parser.data_payload = bytes(d)
        reg = e.get_compendium()["registered"]
        self.assertIn(10, reg)
        self.assertIn(115, reg)   # reserved-name but game-registers it
        self.assertNotIn(216, reg)
        self.assertNotIn(218, reg)
        self.assertEqual(e.get_compendium()["count"], 2)

    def test_reunlock_prunes_phantom_bits(self):
        """unlock_compendium_100 clears truly-dead bits; never clears
        legitimately-registered reserved-name (RESERVE) entries."""
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        for pid in (1, 216, 218, 224):  # truly dead (100%-save proven)
            set_bit(d, 0x09973, pid, 1)
            set_bit(d, 0x21E83, pid, 1)
        for pid in (115, 172):       # reserved-name but the game registers them
            set_bit(d, 0x09973, pid, 1)
            set_bit(d, 0x21E83, pid, 1)
        e.parser.data_payload = bytes(d)
        r = e.unlock_compendium_100()
        self.assertEqual(r["status"], "success")
        self.assertGreaterEqual(r.get("unlocked_count"), 224)
        d2 = e.parser.data_payload
        for pid in (1, 216, 218, 224):
            self.assertEqual(d2[0x09973 + (pid - 1) // 8] & (1 << ((pid - 1) % 8)), 0)
        for pid in (115, 10):
            self.assertNotEqual(d2[0x09973 + (pid - 1) // 8] & (1 << ((pid - 1) % 8)), 0)
        self.assertGreaterEqual(e.get_compendium()["count"], 224)

    def test_dead_bit_can_be_cleared_not_set(self):
        e = make_pc_editor()
        for pid in (216, 218, 224):
            self.assertEqual(e.set_compendium_registration(pid, True)["status"], "invalid")
            self.assertEqual(e.set_compendium_registration(pid, False)["status"], "success")
        # legit personas always toggleable — including reserved-name 115
        self.assertEqual(e.set_compendium_registration(115, True)["status"], "success")
        self.assertEqual(e.set_compendium_registration(10, True)["status"], "success")


if __name__ == "__main__":
    unittest.main()