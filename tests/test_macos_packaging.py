"""Cross-platform desktop packaging contracts."""

import tempfile
import unittest
from pathlib import Path

import main
from core.environment import discover_steam_save_dirs


class TestNativeGuiBackend(unittest.TestCase):
    def test_macos_uses_cocoa_webkit(self):
        self.assertEqual(main.native_gui_backend("darwin"), "cocoa")

    def test_windows_keeps_edge_webview2(self):
        self.assertEqual(main.native_gui_backend("win32"), "edgechromium")

    def test_other_platform_lets_pywebview_choose(self):
        self.assertIsNone(main.native_gui_backend("linux"))


class TestMacOSSaveDiscovery(unittest.TestCase):
    def test_discovers_crossover_appdata_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            savedata = (
                home
                / "Library/Application Support/CrossOver/Bottles/Steam"
                / "drive_c/users/crossover/AppData/Roaming/SEGA/P5R/Steam"
                / "76561190000000000/savedata"
            )
            savedata.mkdir(parents=True)
            self.assertIn(
                savedata,
                discover_steam_save_dirs(home=home, platform="darwin"),
            )

    def test_discovers_native_steam_userdata_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            savedata = (
                home
                / "Library/Application Support/Steam/userdata"
                / "1234/1687950/remote/savedata"
            )
            savedata.mkdir(parents=True)
            self.assertIn(
                savedata,
                discover_steam_save_dirs(home=home, platform="darwin"),
            )


if __name__ == "__main__":
    unittest.main()
