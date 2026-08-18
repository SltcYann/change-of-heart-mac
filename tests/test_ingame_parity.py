import unittest
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.editor import SaveEditor


class TestInGameParityFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle_path = ROOT / "scratch_audit" / "DATA.DAT"
        if not cls.oracle_path.exists():
            # fallback to tests/oracle_saves
            oracle_files = list((ROOT / "tests" / "oracle_saves").glob("**/DATA.DAT"))
            cls.oracle_path = oracle_files[0]

    def test_name_change_persists_in_payload_structs(self):
        """First and last names must be written to 0x13840 and 0x2BD50 in data payload."""
        with open(self.oracle_path, "rb") as f:
            raw = f.read()
        editor = SaveEditor(raw)
        
        # Test changing to a distinct custom name
        res = editor.set_player_names("Akira", "Kurusu", "Phantom")
        self.assertEqual(res["status"], "ok")
        
        # Check header
        self.assertEqual(editor.parser.header.fname, "Akira")
        self.assertEqual(editor.parser.header.lname, "Kurusu")
        
        # Check data payload offsets
        d = editor.parser.data_payload
        # 0x13840 is full name, 0x138A8 is lname, 0x138DC is fname
        # plus mirror at 0x2BD50, 0x2BDB8, 0x2BDEC
        self.assertIn(b"Akira Kurusu", d[0x13840:0x13870])
        self.assertIn(b"Kurusu", d[0x138A8:0x138C8])
        self.assertIn(b"Akira", d[0x138DC:0x138FC])
        
        self.assertIn(b"Akira Kurusu", d[0x2BD50:0x2BD80])
        self.assertIn(b"Kurusu", d[0x2BDB8:0x2BDD8])
        self.assertIn(b"Akira", d[0x2BDEC:0x2BE0C])

    def test_compendium_unlock_all_count_is_224(self):
        """Compendium unlock all must register all 224 valid summonable Personas."""
        with open(self.oracle_path, "rb") as f:
            raw = f.read()
        editor = SaveEditor(raw)
        editor.unlock_compendium_100()
        
        comp = editor.get_compendium()
        self.assertTrue(comp["supported"])
        self.assertEqual(comp["count"], 224)
        self.assertEqual(len(comp["registered"]), 224)


if __name__ == "__main__":
    unittest.main()
