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

try:
    import webview
except ImportError:
    webview = None

import server as web_server
from core import instances
import webbrowser

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

    # 3. If webview is available, create native desktop window (Edge WebView2)
    if webview is not None:
        browser_fallback_used = []
        window = None

        def ui_watchdog(timeout_s: float = 45.0) -> None:
            """If the native window's JS never pings /api/ui-heartbeat, the
            WebView2 UI booted dead (broken runtime — silent no-buttons, dead
            file picker). Close the dead window and auto-open the system
            browser instead of leaving the user with a window that does
            nothing.

            45s (not 30s): slow machines can take >30s just to reach DOM
            ready, and discovery runs after that — a healthy-but-slow window
            must not be misidentified as dead (Gruphius case, 2026-08-25).
            """
            deadline = time.time() + timeout_s
            while time.time() < deadline:
                if web_server.LAST_UI_HEARTBEAT > 0:
                    return  # UI is alive; native window is healthy
                time.sleep(1.0)
            print(
                f"[Change of Heart] Native UI showed no signs of life after "
                f"{int(timeout_s)}s — likely a broken WebView2 Runtime on this "
                f"machine. Opening the editor in your default browser instead "
                f"and closing the dead window.",
                flush=True,
            )
            browser_fallback_used.append(True)
            try:
                for w in list(webview.windows):
                    w.destroy()  # kill the dead native window — browser replaces it
            except Exception:
                pass
            webbrowser.open(url)

        try:
            threading.Thread(target=ui_watchdog, daemon=True).start()
            window = webview.create_window(
                title="PERSONA 5 ROYAL — Change of Heart Save Editor",
                url=url,
                width=1280,
                height=850,
                min_size=(1024, 700),
                background_color="#0A0A0F",
                text_select=True,
            )
            webview.start(gui="edgechromium", debug=False)
            if not browser_fallback_used:
                # Normal exit: user closed a healthy native window.
                instances.clear()
                stop_background_server()
                return
            # Watchdog fell back to the browser: keep serving until the user
            # is done. Idle shutdown prevents orphaned server processes from
            # accumulating across launches (Gruphius report, 2026-08-25):
            # exit after 3h with zero requests.
            print("[Change of Heart] Serving browser session — it will stay available while this window is open.", flush=True)
            last_activity = time.time()
            while True:
                time.sleep(60)
                if web_server.LAST_REQUEST_TS > 0:
                    last_activity = max(last_activity, web_server.LAST_REQUEST_TS)
                if time.time() - last_activity > 3 * 3600:
                    print("[Change of Heart] No activity for 3h — shutting down browser-session server.", flush=True)
                    instances.clear()
                    stop_background_server()
                    return
        except Exception as e:
            print(f"[Change of Heart] WebView2 init notice ({e}), launching in browser: {url}")
            instances.clear()
            stop_background_server()

    # 4. Fallback: Launch in default web browser
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        instances.clear()
        stop_background_server()
    sys.exit(0)


if __name__ == "__main__":
    main()
