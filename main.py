"""
Persona 5 Royal Save Editor — Standalone Native Desktop Application
Powered by PyWebView (Native Edge WebView2 Engine)
"""

import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

# Set up project root paths
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PROJECT_ROOT = Path(sys._MEIPASS)
else:
    PROJECT_ROOT = Path(__file__).resolve().parent

sys.path.insert(0, str(PROJECT_ROOT))

import webview
import server as web_server
from core import instances

_HTTPD = None


def start_background_server() -> int:
    """Start local backend HTTP server on an OS-assigned ephemeral port."""
    global _HTTPD
    from http.server import ThreadingHTTPServer

    class NoReuseThreadingHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = False

    server = NoReuseThreadingHTTPServer(("127.0.0.1", 0), web_server.P5RWebHandler)
    _HTTPD = server
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return port


def stop_background_server() -> None:
    """Cleanly close the background HTTP server."""
    global _HTTPD
    if _HTTPD is not None:
        try:
            _HTTPD.server_close()
        except Exception:
            pass
        _HTTPD = None


def _wait_for_server(port: int, timeout_s: float = 30.0) -> bool:
    """Ensure the local server is accepting requests before loading UI."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/build", timeout=1.0) as res:
                if res.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def main() -> None:
    # 1. Start background server on ephemeral port
    port = start_background_server()
    instances.write(port=port)

    # 2. Wait for server to become responsive
    if not _wait_for_server(port):
        instances.clear()
        stop_background_server()
        sys.exit(1)

    url = f"http://127.0.0.1:{port}/"

    # 3. Create native single desktop window (Edge WebView2)
    window = webview.create_window(
        title="PERSONA 5 ROYAL — Change of Heart Save Editor",
        url=url,
        width=1280,
        height=850,
        min_size=(1024, 700),
        background_color="#0A0A0F",
        text_select=True,
    )

    try:
        # 4. Start native GUI event loop (blocks until window is closed)
        webview.start(gui="edgechromium", debug=False)
    finally:
        # 5. Clean teardown on window exit
        instances.clear()
        stop_background_server()
    sys.exit(0)


if __name__ == "__main__":
    main()
