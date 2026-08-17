"""Tests for core/instances.py — the per-instance registry used for the
same-save soft notice. Runs against an isolated temp registry dir."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

_TMP = tempfile.mkdtemp(prefix="coh-instances-test-")
os.environ["COH_INSTANCES_DIR"] = _TMP

from core import instances  # noqa: E402


class RegistryTests(unittest.TestCase):
    def test_write_roundtrip(self):
        instances.write(port=12345, save_path="")
        data = json.load(open(instances._own_registry_path(), encoding="utf-8"))
        self.assertEqual(data["pid"], os.getpid())
        self.assertEqual(data["port"], 12345)
        self.assertEqual(data["save_path"], "")
        self.assertIn("nonce", data)
        self.assertIn("created", data)
        instances.clear()
        self.assertFalse(os.path.exists(instances._own_registry_path()))

    def test_no_conflicts_when_alone(self):
        instances.write(port=12345, save_path="")
        self.assertEqual(instances.find_conflicts("C:/saves/DATA00.DAT"), [])
        instances.clear()

    def test_stale_file_is_removed(self):
        # A killed-and-reaped pid is provably dead to the OS.
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        proc.kill()
        proc.wait()
        dead_path = os.path.join(instances._registry_dir(), f"{proc.pid}.json")
        with open(dead_path, "w", encoding="utf-8") as f:
            json.dump({"pid": proc.pid, "port": 1, "save_path": "C:/saves/DATA00.DAT",
                       "nonce": "x", "created": time.time()}, f)
        # Core invariant: a dead pid must never produce a false conflict.
        self.assertEqual(instances.find_conflicts("C:/saves/DATA00.DAT"), [])
        # The sweep deletes the stale file once the OS confirms death
        # (Windows may keep a just-exited process object openable briefly).
        for _ in range(10):
            if not os.path.exists(dead_path):
                break
            instances.find_conflicts("C:/saves/DATA00.DAT")
            time.sleep(0.5)
        self.assertFalse(os.path.exists(dead_path))

    def test_live_conflict_detected(self):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        try:
            created = instances._pid_creation_time(proc.pid) or time.time()
            fake_path = os.path.join(instances._registry_dir(), f"{proc.pid}.json")
            with open(fake_path, "w", encoding="utf-8") as f:
                json.dump({"pid": proc.pid, "port": 1, "save_path": "C:/saves/DATA00.DAT",
                           "nonce": "y", "created": created}, f)
            self.assertIn(proc.pid, instances.find_conflicts("C:/saves/DATA00.DAT"))
            self.assertEqual(instances.find_conflicts("C:/saves/OTHER.DAT"), [])
        finally:
            proc.kill()
            proc.wait()

    def test_update_save_and_clear(self):
        instances.write(port=9999, save_path="")
        instances.update_save("C:/saves/DATA01.DAT")
        data = json.load(open(instances._own_registry_path(), encoding="utf-8"))
        self.assertEqual(data["save_path"], "C:/saves/DATA01.DAT")
        instances.clear()


if __name__ == "__main__":
    unittest.main(verbosity=2)
