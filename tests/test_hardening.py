"""Regression tests for the 2026-08-16 in-game feedback hardening pass.

Covers (from the Reddit tester report + dual-oracle + AG review):
- Teammate LV u8 write (no +0x3D clobber) and u8 read
- Dummy/BLANK skill id rejection (stock + equipped)
- P5-legacy persona id rejection (stock + equipped)
- Teammate persona story-lock
- Compendium dead-bit rejection + 224-bit safe unlock
- GOD_BUILDS presets reference real table IDs
"""

import os
import re
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.editor import SaveEditor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_pc_editor() -> SaveEditor:
    e = SaveEditor()
    e.parser.is_pc_0x31 = True
    e.parser.data_payload = bytes(0x40000)
    return e


class TestMemberLevelU8(unittest.TestCase):
    def test_member_level_write_preserves_unk_byte(self):
        e = make_pc_editor()
        off = 0x2C + 1 * 0x2B0
        d = bytearray(e.parser.data_payload)
        d[off + 0x3D] = 0xAB  # unk byte (persona struct +0x05)
        e.parser.data_payload = bytes(d)
        r = e.set_party_stat(1, level=42)
        self.assertEqual(r["status"], "success")
        self.assertEqual(e.parser.data_payload[off + 0x3C], 42)
        self.assertEqual(e.parser.data_payload[off + 0x3D], 0xAB,
                         "member LV u16 write clobbered the +0x3D unk byte")

    def test_member_level_read_is_u8(self):
        e = make_pc_editor()
        off = 0x2C + 1 * 0x2B0
        d = bytearray(e.parser.data_payload)
        d[off + 0x3C] = 20
        d[off + 0x3D] = 0x01  # nonzero unk byte: u16 read would give 276
        e.parser.data_payload = bytes(d)
        stats = e.get_party_stats()
        self.assertEqual(stats[1]["level"], 20)

    def test_leader_level_still_u16_path(self):
        e = make_pc_editor()
        r = e.set_party_stat(0, level=25)
        self.assertEqual(r["status"], "success")
        self.assertEqual(e.get_party_stats()[0]["level"], 25)


class TestSkillDummyRejection(unittest.TestCase):
    def test_stock_rejects_blank_skill_ids(self):
        e = make_pc_editor()
        for sid in (0x0001, 0x0005, 0x0009):
            r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50,
                                         skills=[sid, 0, 0, 0, 0, 0, 0, 0])
            self.assertEqual(r["status"], "invalid", f"skill 0x{sid:X} accepted")
        self.assertEqual(e.parser.data_payload, bytes(0x40000))

    def test_equipped_rejects_blank_skill_ids(self):
        e = make_pc_editor()
        r = e.set_equipped_persona(0, persona_id=0x16B, level=50,
                                   skills=[0x0003, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(r["status"], "invalid")

    def test_stock_accepts_zero_skill_slot(self):
        # 0 = empty skill slot, always legal
        e = make_pc_editor()
        r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50,
                                     skills=[0] * 8)
        self.assertEqual(r["status"], "success")


class TestLegacyPersonaRejection(unittest.TestCase):
    def test_stock_rejects_p5_legacy_dups(self):
        e = make_pc_editor()
        for pid in (0x0DC, 0x0E0, 0x0DB):
            r = e.set_persona_stock_slot(0, 0, persona_id=pid, level=50)
            self.assertEqual(r["status"], "invalid", f"legacy 0x{pid:X} accepted")
        self.assertEqual(e.parser.data_payload, bytes(0x40000))

    def test_equipped_rejects_p5_legacy_dups(self):
        e = make_pc_editor()
        r = e.set_equipped_persona(0, persona_id=0x0DC, level=50)
        self.assertEqual(r["status"], "invalid")

    def test_stock_accepts_metatron_and_anat(self):
        # Real personas (even if their compendium bits are never set)
        e = make_pc_editor()
        for pid in (0x001, 0x0D8):
            r = e.set_persona_stock_slot(0, 0, persona_id=pid, level=50)
            self.assertEqual(r["status"], "success", f"real persona 0x{pid:X} rejected")


class TestTeammatePersonaLock(unittest.TestCase):
    def _seed_canonical(self, e: SaveEditor):
        # Teammate stock slot 0 = their canonical persona (real saves always
        # have it; synthetic payloads start zeroed — seed it first).
        r = e.set_persona_stock_slot(1, 0, persona_id=0xCA, level=20)
        self.assertEqual(r["status"], "success")

    def test_teammate_persona_change_rejected(self):
        e = make_pc_editor()
        self._seed_canonical(e)
        r = e.set_equipped_persona(1, persona_id=0x16B, level=99)
        self.assertEqual(r["status"], "invalid")
        self.assertEqual(e.get_equipped_persona(1)["persona_id"], 0xCA)

    def test_teammate_same_persona_edit_allowed(self):
        e = make_pc_editor()
        self._seed_canonical(e)
        r = e.set_equipped_persona(1, persona_id=0xCA, level=21)
        self.assertEqual(r["status"], "success")
        self.assertEqual(e.get_equipped_persona(1)["level"], 21)


class TestGodBuildIDs(unittest.TestCase):
    def test_god_build_ids_exist_in_tables(self):
        """GOD_BUILDS in app.js must reference real Personas/Skills/Traits."""
        path = os.path.join(ROOT, "web-app", "static", "app.js")
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        m = re.search(r"const GOD_BUILDS = (\{.*?\n\});", src, re.S)
        self.assertIsNotNone(m, "GOD_BUILDS block not found")
        personas = SaveEditor()._load_table("Personas.txt")
        skills = SaveEditor()._load_table("Skill ID.txt")
        traits = SaveEditor()._load_table("Traits.txt")
        for pid in re.findall(r"persona_id: (\d+)", m.group(1)):
            self.assertIn(int(pid), personas, f"persona {pid} missing from Personas.txt")
        for sid in re.findall(r"^\s+(\d+),? //", m.group(1), re.M):
            self.assertIn(int(sid), skills, f"skill {sid} missing from Skill ID.txt")
        for tid in re.findall(r"trait_id: (\d+)", m.group(1)):
            self.assertIn(int(tid), traits, f"trait {tid} missing from Traits.txt")

    def test_god_build_names_match(self):
        """Preset personas must be the advertised personas."""
        personas = SaveEditor()._load_table("Personas.txt")
        path = os.path.join(ROOT, "web-app", "static", "app.js")
        src = open(path, encoding="utf-8").read()
        expected = {"yoshitsune": "Yoshitsune", "izanagi": "Izanagi no Okami Picaro",
                    "raoul": "Raoul"}
        for key, want in expected.items():
            m = re.search(rf"{key}: \{{.*?persona_id: (\d+)", src, re.S)
            self.assertIsNotNone(m, f"preset {key} not found")
            name = personas.get(int(m.group(1)), "")
            self.assertEqual(name.lower(), want.lower(),
                             f"preset {key} maps to {name} != {want}")


class TestTraitDummyRejection(unittest.TestCase):
    def test_stock_rejects_reserve_trait(self):
        e = make_pc_editor()
        r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50, trait_id=0x0005)
        self.assertEqual(r["status"], "invalid")
        self.assertEqual(e.parser.data_payload, bytes(0x40000))

    def test_equipped_rejects_reserve_trait(self):
        e = make_pc_editor()
        r = e.set_equipped_persona(0, persona_id=0x16B, level=50, trait_id=0x0002)
        self.assertEqual(r["status"], "invalid")

    def test_stock_accepts_real_trait(self):
        e = make_pc_editor()
        r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50, trait_id=6)  # Relentless
        self.assertEqual(r["status"], "success")

    def test_trait_zero_allowed_as_unset(self):
        e = make_pc_editor()
        r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50, trait_id=0)
        self.assertEqual(r["status"], "success")


class TestReferenceDBCleanliness(unittest.TestCase):
    def test_database_has_no_dummy_entries(self):
        """The served reference DB must be free of RESERVE/???/dummy rows
        and duplicate names (deduped 2026-08-16, corpus-anchored ids)."""
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        db = web_server.REFERENCE_DB
        bad_names = {"", "RESERVE", "???", "BLANK", "----------", "P5 Unused", "not used"}
        bad_personas = [p for p in db["personas"] if p["name"] in bad_names]
        bad_skills = [s for s in db["skills"] if s["name"] in bad_names or s["id"] <= 0x09
                      or s["name"].lower().startswith("unused:")]
        bad_traits = [t for t in db["traits"] if t["name"] in bad_names and t["id"] != 0]
        self.assertEqual(bad_personas, [])
        self.assertEqual(bad_skills, [])
        self.assertEqual(bad_traits, [])
        # sanitized + deduped + game-name-filtered counts (2026-08-16): 287/870/93
        self.assertEqual(len(db["personas"]), 287)
        self.assertEqual(len(db["skills"]), 870)
        self.assertEqual(len(db["traits"]), 93)  # 92 named + "None (unset)"

    def test_database_has_no_duplicate_names(self):
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        db = web_server.REFERENCE_DB
        from collections import Counter
        for key in ("personas", "skills", "traits"):
            c = Counter(it["name"].lower() for it in db[key])
            dups = {n: k for n, k in c.items() if k > 1}
            self.assertEqual(dups, {}, f"{key} still has duplicate names: {dups}")


class TestGameNameTruth(unittest.TestCase):
    """2026-08-16: names corrected against the game's NAME.TBL, junk ids
    excluded from both the dropdown and the write validation."""

    def test_database_uses_game_skill_spellings(self):
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        skills = {s["id"]: s["name"] for s in web_server.REFERENCE_DB["skills"]}
        self.assertEqual(skills[123], "Med Burn")
        self.assertEqual(skills[164], "Med All Ail")
        self.assertEqual(skills[516], "Royal Jelly")
        self.assertEqual(skills[295], "Ultimate Support")
        # no dump-only spellings anywhere
        bad = [s for s in skills.values() if s.startswith("Mid ") or s == "Royel Jelly"]
        self.assertEqual(bad, [])

    def test_database_uses_game_trait_spellings(self):
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        traits = {t["id"]: t["name"] for t in web_server.REFERENCE_DB["traits"]}
        self.assertEqual(traits[9], "Savior Bloodline")
        self.assertEqual(traits[73], "Skillful Combo")
        self.assertEqual(traits[102], "Deathly Illness")

    def test_non_skill_ids_rejected_in_stock(self):
        e = make_pc_editor()
        for sid in (420, 568, 575, 585, 663):
            r = e.set_persona_stock_slot(0, 0, persona_id=0x16B, level=50,
                                         skills=[sid, 0, 0, 0, 0, 0, 0, 0])
            self.assertEqual(r["status"], "invalid", f"non-skill {sid} accepted")
        self.assertEqual(e.parser.data_payload, bytes(0x40000))

    def test_non_skill_ids_rejected_in_equipped(self):
        e = make_pc_editor()
        r = e.set_equipped_persona(0, persona_id=0x16B, level=50,
                                   skills=[482, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(r["status"], "invalid")

    def test_lab_personas_rejected(self):
        e = make_pc_editor()
        for pid in (440, 445, 450):
            r = e.set_persona_stock_slot(0, 0, persona_id=pid, level=50)
            self.assertEqual(r["status"], "invalid", f"Lab persona {pid} accepted")
        self.assertEqual(e.parser.data_payload, bytes(0x40000))

    def test_skill_meta_loaded(self):
        """data/SkillMeta.txt serves element/cost metadata from the game table."""
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        meta = web_server.REFERENCE_DB.get("skill_meta", {})
        self.assertEqual(len(meta), 799)
        # verified spot checks: Agi=4SP fire, Hassou Tobi=25%HP phys, Myriad Truths=40SP almighty
        self.assertEqual(meta[10]["cost"], 4.0)
        self.assertEqual(meta[10]["costtype"], 2)
        self.assertEqual(meta[10]["element"], 2)
        self.assertEqual(meta[215]["cost"], 25.0)
        self.assertEqual(meta[215]["costtype"], 1)
        self.assertEqual(meta[215]["element"], 0)
        self.assertEqual(meta[713]["cost"], 40.0)
        self.assertEqual(meta[713]["element"], 10)

    def test_item_database_clean(self):
        """Item DB: no raw-hex placeholder names, game-correct spellings."""
        import sys
        sys.path.insert(0, ROOT)
        import server as web_server
        items = {i["id"]: i["name"] for i in web_server.REFERENCE_DB["items"]}
        self.assertEqual(len(items), 2204)
        hex_junk = [n for n in items.values() if n.startswith("0x")]
        self.assertEqual(hex_junk, [])
        self.assertEqual(items[8270], "Money Distributor")
        self.assertEqual(items[8304], "Discharge Crystal")
        self.assertEqual(items[8529], "Old Man's Elixir")
        self.assertEqual(items[12400], "Vajra Belt")
        self.assertEqual(items[12782], "Dazzling Netsuke")

    def test_unjoined_member_edits_refused(self):
        """Slots that still match the game's canonical seed (not yet joined)
        refuse all writes — protects against corrupting pre-join placeholder
        data. Seed verified against June + NG+ saves."""
        e = make_pc_editor()
        # write canonical seed for slot 5 (Makoto pre-join)
        off = 0x2C + 5 * 0x2B0
        d = bytearray(e.parser.data_payload)
        struct.pack_into("<H", d, off + 0, 243)      # hp seed
        struct.pack_into("<H", d, off + 4, 142)      # sp seed
        d[off + 0x3C] = 21                            # lv seed
        struct.pack_into("<H", d, off + 0x3A, 0xCE)  # persona seed
        e.parser.data_payload = bytes(d)
        self.assertFalse(e.is_member_joined(5))
        for fn, args in ((e.set_party_stat, (5,)),
                         (lambda *a: e.set_equipped_persona(5, persona_id=0xCE, level=21), ()),
                         (lambda *a: e.set_persona_stock_slot(5, 0, persona_id=0xCE, level=21), ())):
            r = fn(*args)
            self.assertEqual(r["status"], "invalid", f"edit to un-joined slot not refused: {fn}")
        # Joker and joined slots stay editable
        self.assertTrue(e.is_member_joined(0))
        self.assertEqual(e.set_party_stat(0, level=22)["status"], "success")

    def test_joined_member_edit_allowed(self):
        """A slot differing from its seed = member joined -> editable."""
        e = make_pc_editor()
        off = 0x2C + 1 * 0x2B0
        d = bytearray(e.parser.data_payload)
        struct.pack_into("<H", d, off + 0, 246)     # differs from seed 117
        e.parser.data_payload = bytes(d)
        self.assertTrue(e.is_member_joined(1))
        self.assertEqual(e.set_party_stat(1, level=20)["status"], "success")

    def test_party_stats_join_filters_ui(self):
        """get_party_stats marks joined; server party payload hides un-joined."""
        e = make_pc_editor()
        off = 0x2C + 5 * 0x2B0
        d = bytearray(e.parser.data_payload)
        struct.pack_into("<H", d, off + 0, 243)
        struct.pack_into("<H", d, off + 4, 142)
        d[off + 0x3C] = 21
        struct.pack_into("<H", d, off + 0x3A, 0xCE)
        e.parser.data_payload = bytes(d)
        stats = e.get_party_stats()
        self.assertEqual(stats[5]["joined"], False)
        self.assertEqual(stats[5]["name"], "???")
        self.assertEqual(stats[0]["joined"], True)

    def test_preset_skills_survive_audit(self):
        """The god-build preset skill ids must not be in the excluded set."""
        import re
        src = open(os.path.join(ROOT, "web-app", "static", "app.js"), encoding="utf-8").read()
        m = re.search(r"const GOD_BUILDS = (\{.*?\n\});", src, re.S)
        preset_ids = set(int(x) for x in re.findall(r"^\s+(\d+),? //", m.group(1), re.M))
        editor = SaveEditor()
        overlap = preset_ids & editor.PC31_NON_SKILL_IDS
        self.assertEqual(overlap, set(), f"presets reference excluded ids: {overlap}")


if __name__ == "__main__":
    unittest.main()
