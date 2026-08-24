"""UI-liveness heartbeat tests (WebView2 watchdog, 2026-08-24).

The frontend pings /api/ui-heartbeat after boot; main.py's watchdog falls back
to the system browser if no heartbeat ever arrives. These tests verify the
server-side contract.
"""

import json
import threading
import time
import unittest
import urllib.request

import server as web_server


class TestUiHeartbeat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = web_server.HTTPServer(("127.0.0.1", 0), web_server.P5RWebHandler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))

    def test_heartbeat_before_any_ping_never_seen(self):
        # Reset module state so this test is order-independent
        old = web_server.LAST_UI_HEARTBEAT
        web_server.LAST_UI_HEARTBEAT = 0.0
        try:
            status = self._get("/api/heartbeat-status")
            self.assertFalse(status["ever_seen"])
            self.assertIsNone(status["last_heartbeat_age_s"])
        finally:
            web_server.LAST_UI_HEARTBEAT = old

    def test_heartbeat_ping_records_liveness(self):
        resp = self._get("/api/ui-heartbeat")
        self.assertEqual(resp["status"], "alive")
        status = self._get("/api/heartbeat-status")
        self.assertTrue(status["ever_seen"])
        self.assertIsNotNone(status["last_heartbeat_age_s"])
        self.assertLess(status["last_heartbeat_age_s"], 5.0)


if __name__ == "__main__":
    unittest.main()
