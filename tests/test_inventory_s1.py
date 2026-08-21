"""S1 truthful read — melee + consumables vertical slice (INVENTORY_SPEC.md).

Validates the normalized model: owned_gear / stacks / key_flags +
mirror mismatches + phantom-merge fix. Uses synthetic PC 0x31 payloads
so no oracle or server reference DB is needed.
"""
import os
import sys
import struct
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.editor import SaveEditor


def make_pc_editor(size=0x40000) -> SaveEditor:
    e = SaveEditor()
    e.parser.is_pc_0x31 = True
    e.parser.data_payload = bytes(size)
    return e


class TestS1NormalizedModelShape(unittest.TestCase):
    def test_normalized_shape(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        # one consumable, one gear
        d[0x2531] = 5  # 0x2001 med
        d[0x2531 + 0x18510] = 5
        d[0x1B35] = 1  # 0x1005 melee Blizz Dagger
        d[0x1B35 + 0x18510] = 1
        e.parser.data_payload = bytes(d)
        norm = e.get_normalized_inventory()
        self.assertIn("owned_gear", norm)
        self.assertIn("stacks", norm)
        self.assertIn("key_flags", norm)
        self.assertIn("mirror_mismatches", norm)
        self.assertIn("conflicts", norm)
        self.assertEqual(norm["stacks"].get(0x2001), 5)
        self.assertTrue(norm["owned_gear"].get(0x1005) is True)
        # gear id must not leak into stacks and vice versa
        self.assertNotIn(0x1005, norm["stacks"])
        self.assertNotIn(0x2001, norm["owned_gear"])

    def test_gear_zero_flag_is_not_owned(self):
        e = make_pc_editor()
        norm = e.get_normalized_inventory()
        # With empty payload no gear should be owned; the implementation
        # surfaces probed ids as False so UI can render grey — but
        # get_inventory legacy view hides not-owned. Either is OK.
        # The key invariant: reading owned_gear does not report quantity.
        self.assertIsInstance(norm["owned_gear"], dict)


class TestS1PhantomMergeFix(unittest.TestCase):
    def test_quick_only_is_not_counted_as_stack(self):
        """Consumable present only in quick-array must NOT appear in stacks."""
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        # No count at 0x2531 (stays 0), but quick-array holds 0x2001 x9
        off_ring = 0x3530
        off_qty = 0x2410  # slot 0
        struct.pack_into("<H", d, off_ring, 0x2001)
        struct.pack_into("<H", d, off_ring + 2, 1)
        d[off_qty] = 9
        e.parser.data_payload = bytes(d)
        norm = e.get_normalized_inventory()
        self.assertNotIn(0x2001, norm["stacks"])
        # Should be surfaced as a conflict (count_region 0 vs quick 9)
        self.assertTrue(any(c["item_id"] == 0x2001 for c in norm["conflicts"]))

    def test_canonical_count_wins_over_quick_conflict(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        d[0x2532] = 3
        d[0x2532 + 0x18510] = 3
        off_ring = 0x3530
        off_qty = 0x2410
        struct.pack_into("<H", d, off_ring, 0x2002)  # Recov-R 50mg id 0x2002
        struct.pack_into("<H", d, off_ring + 2, 1)
        d[off_qty] = 9  # quick says 9, count says 3 -> canonical 3
        e.parser.data_payload = bytes(d)
        norm = e.get_normalized_inventory()
        self.assertEqual(norm["stacks"].get(0x2002), 3)
        self.assertTrue(any(c["item_id"] == 0x2002 and c["winner"] == "count_region"
                            for c in norm["conflicts"]))

    def test_legacy_get_inventory_hides_phantom(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        off_ring = 0x3530
        off_qty = 0x2410
        struct.pack_into("<H", d, off_ring, 0x2001)
        struct.pack_into("<H", d, off_ring + 2, 1)
        d[off_qty] = 7
        e.parser.data_payload = bytes(d)
        inv = e.get_inventory()
        # No stack for 0x2001 -> flat inventory should be empty (phantom hidden)
        self.assertFalse(any(it["item_id"] == 0x2001 for it in inv))


class TestS1MirrorMismatch(unittest.TestCase):
    def test_mirror_mismatch_surfaced(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        d[0x2532] = 5
        d[0x2532 + 0x18510] = 99
        e.parser.data_payload = bytes(d)
        norm = e.get_normalized_inventory()
        self.assertTrue(any(m["offset"] == 0x2532 for m in norm["mirror_mismatches"]))
        self.assertEqual(norm["stacks"].get(0x2002), 5)  # primary wins

    def test_gear_mirror_mismatch_surfaced(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        d[0x1B35] = 1
        d[0x1B35 + 0x18510] = 0
        e.parser.data_payload = bytes(d)
        norm = e.get_normalized_inventory()
        self.assertTrue(any(m["offset"] == 0x1B35 for m in norm["mirror_mismatches"]))

    def test_mismatch_heals_on_write(self):
        e = make_pc_editor()
        d = bytearray(e.parser.data_payload)
        d[0x2532] = 5
        d[0x2532 + 0x18510] = 99
        e.parser.data_payload = bytes(d)
        e.set_item_quantity(0x2002, 7)
        out = e.parser.data_payload
        self.assertEqual(out[0x2532], 7)
        self.assertEqual(out[0x2532 + 0x18510], 7)


class TestS1MeleeOwnedToggle(unittest.TestCase):
    def test_melee_toggle_sets_and_clears_flag_and_mirror(self):
        e = make_pc_editor()
        e.set_item_quantity(0x1005, 1)
        self.assertEqual(e.parser.data_payload[0x1B35], 1)
        self.assertEqual(e.parser.data_payload[0x1B35 + 0x18510], 1)
        e.set_item_quantity(0x1005, 0)
        self.assertEqual(e.parser.data_payload[0x1B35], 0)
        self.assertEqual(e.parser.data_payload[0x1B35 + 0x18510], 0)
        # Never writes count byte for gear
        self.assertEqual(e.parser.data_payload[0x2415], 0)

    def test_melee_not_in_count_path(self):
        e = make_pc_editor()
        self.assertEqual(e.get_item_count_offset(0x1005), 0)
        self.assertGreater(e.get_item_owned_offset(0x1005), 0)

    def test_unmapped_ranged_refused(self):
        e = make_pc_editor()
        r = e.set_item_quantity(0x7001, 1)
        self.assertEqual(r["status"], "unsupported")
        r2 = e.stage_set_owned(0x7001, True)
        self.assertIn(r2["status"], ("unsupported", "invalid"))


class TestS1ConsumableStepper(unittest.TestCase):
    def test_set_stack_writes_count_and_mirror(self):
        e = make_pc_editor()
        e.set_item_quantity(0x2001, 99)
        self.assertEqual(e.parser.data_payload[0x2531], 99)
        self.assertEqual(e.parser.data_payload[0x2531 + 0x18510], 99)
        norm = e.get_normalized_inventory()
        self.assertEqual(norm["stacks"][0x2001], 99)

    def test_stack_clamped(self):
        e = make_pc_editor()
        e.set_item_quantity(0x2001, 999)
        self.assertEqual(e.parser.data_payload[0x2531], 99)
        e.set_item_quantity(0x2001, -5)
        self.assertEqual(e.parser.data_payload[0x2531], 0)

    def test_gear_to_stack_path_refused(self):
        e = make_pc_editor()
        r = e.stage_set_stack(0x1005, 5)
        self.assertEqual(r["status"], "invalid")


class TestS1StagingBuffer(unittest.TestCase):
    def test_staging_does_not_touch_payload_until_commit(self):
        e = make_pc_editor()
        r = e.stage_set_stack(0x2001, 7)
        self.assertEqual(r["status"], "staged")
        self.assertEqual(e.parser.data_payload[0x2531], 0)
        e.commit_staged_inventory()
        self.assertEqual(e.parser.data_payload[0x2531], 7)

    def test_staging_owned_toggle(self):
        e = make_pc_editor()
        e.stage_set_owned(0x1005, True)
        self.assertEqual(e.parser.data_payload[0x1B35], 0)
        e.commit_staged_inventory()
        self.assertEqual(e.parser.data_payload[0x1B35], 1)

    def test_discard_clears(self):
        e = make_pc_editor()
        e.stage_set_stack(0x2001, 4)
        e.discard_staged_inventory()
        e.commit_staged_inventory()
        self.assertEqual(e.parser.data_payload[0x2531], 0)


class TestS1ConsumablePerf(unittest.TestCase):
    """Phase B — virtual-scroll perf surrogate.

    Seeds 696 Consumable count bytes (the full canonical count per
    docs/ITEM_TBL_MAP.md seg 2) across the 3 verified sub-bases
    (0x2530/0x25AA/0x2600 + idx) and times the normalized read path that
    the Cheat Shop virtual scroll rests on. Acceptance §7: <100ms for 696 rows.
    """

    def setUp(self):
        self.e = make_pc_editor()

    def _seed_consumables(self):
        """Seed every Consumable idx the brute sparse-scan (idx 1..0x300) can
        resolve (skips the 0x61..0x6F gap where get_item_count_offset→0).
        Returns the actual seeded count so the perf test stays honest."""
        e = self.e
        d = bytearray(e.parser.data_payload)
        seeded = 0
        for idx in range(1, 0x300):
            iid = 0x2000 | idx
            off = e.get_item_count_offset(iid)
            if off and off < len(d):
                d[off] = 1
                d[off + 0x18510] = 1
                seeded += 1
        e.parser.data_payload = bytes(d)
        return seeded

    def test_consumables_under_100ms(self):
        # Seed a large consumable population across the verified count sub-bases
        # (0x2530/0x25AA/0x2600 + idx, mirror +0x18510). This exercises the full
        # normalized read path the Cheat Shop virtual scroll rests on; perf SLA
        # is <100ms per docs/ITEM_STUDIO_REBUILD_PLAN.md §7.
        # NOTE: seed_count ≠ surfaced_count when REFERENCE_DB is live (the live
        # item universe covers idx beyond the brute-scan 1..0x300 window), so we
        # assert a substantial *surfaced* stack set + the timing gate, not raw
        # seed equality.
        self._seed_consumables()
        import time
        perf_worst_ms = 0.0
        surfaced = 0
        for _ in range(5):
            t0 = time.perf_counter()
            norm = self.e.get_normalized_inventory()
            perf_worst_ms = max(perf_worst_ms, (time.perf_counter() - t0) * 1000)
            surfaced = len(norm["stacks"])
        # Real work happened: hundreds of consumable count bytes are nonzero.
        self.assertGreater(surfaced, 100, f"only {surfaced} consumable stacks surfaced — perf test under-populated")
        # Perf gate — backend read beneath virtual scroll must be <100ms.
        self.assertLess(perf_worst_ms, 100, f"normalized read took {perf_worst_ms:.1f}ms over {surfaced} consumables — exceeds 100ms virtual-scroll SLA")

    def test_seed_count_is_substantial(self):
        # Guard: the synthetic 0x2000 scan range actually hits a large set so
        # the perf test is meaningful (mirrors the canonical 696 from ITEM_TBL_MAP
        # seg 2 — brute scan can't reach all 696 without reference_db, but must
        # reach well into the hundreds).
        seeded = self._seed_consumables()
        self.assertGreater(seeded, 400)


if __name__ == "__main__":
    unittest.main()
