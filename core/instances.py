"""Per-instance registry for the same-save soft notice (2026-08-16).

Every running app instance writes a small JSON file
(<registry_dir>/<pid>.json) with its pid, port, currently-open save path,
a random nonce, and its OS process creation time. Other instances scan this
directory (on load and on save) to show "this save is also open in another
window" — no lockout, last save wins.

Safety properties (dual-oracle reviewed 2026-08-16):
- Atomic writes: temp file + os.replace; readers tolerate corrupt files.
- Liveness = OS process check (ctypes OpenProcess), never an HTTP probe;
  pid-reuse guarded by comparing OS process creation time.
- Stale cleanup deletes a file ONLY after the OS confirms the pid is dead.
"""
import ctypes
import json
import os
import tempfile
import time
import uuid

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_CREATION_TOLERANCE_S = 2.0


def _registry_dir() -> str:
    d = os.environ.get("COH_INSTANCES_DIR") or os.path.join(
        tempfile.gettempdir(), "ChangeOfHeart-instances"
    )
    os.makedirs(d, exist_ok=True)
    return d


def _own_registry_path() -> str:
    return os.path.join(_registry_dir(), f"{os.getpid()}.json")


def _pid_alive(pid: int) -> bool:
    """OS-native liveness check. Windows: OpenProcess + GetExitCodeProcess
    (OpenProcess alone can succeed for dead processes — verified 2026-08-16).
    POSIX: kill(pid, 0)."""
    if os.name == "nt":
        STILL_ACTIVE = 259
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(
                _PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid)
            )
            if not handle:
                return False
            try:
                code = ctypes.c_ulong(0)
                ok = kernel32.GetExitCodeProcess(
                    handle, ctypes.byref(code)
                )
                return bool(ok) and code.value == STILL_ACTIVE
            finally:
                kernel32.CloseHandle(handle)
        except Exception:
            return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def _pid_creation_time(pid: int):
    """OS process creation time as epoch seconds (None when unavailable)."""
    if os.name != "nt":
        return None
    try:
        kernel32 = ctypes.windll.kernel32

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", ctypes.c_uint32),
                        ("dwHighDateTime", ctypes.c_uint32)]

        handle = kernel32.OpenProcess(
            _PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid)
        )
        if not handle:
            return None
        try:
            creation = FILETIME()
            exit_t = FILETIME()
            kernel_t = FILETIME()
            user_t = FILETIME()
            ok = kernel32.GetProcessTimes(
                handle,
                ctypes.byref(creation), ctypes.byref(exit_t),
                ctypes.byref(kernel_t), ctypes.byref(user_t),
            )
            if not ok:
                return None
            ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
            return ticks / 10_000_000.0 - 11644473600.0  # FILETIME -> epoch
        finally:
            kernel32.CloseHandle(handle)
    except Exception:
        return None


def _atomic_write(path: str, payload: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    os.replace(tmp, path)


def _read(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _record_is_live(record: dict) -> bool:
    pid = int(record.get("pid", -1))
    if not _pid_alive(pid):
        return False
    created = record.get("created")
    if created is None:
        return True
    actual = _pid_creation_time(pid)
    if actual is None:
        return True
    return abs(actual - float(created)) < _CREATION_TOLERANCE_S


def _sweep_stale() -> None:
    """Delete registry files whose pid is confirmed dead by the OS."""
    for name in os.listdir(_registry_dir()):
        path = os.path.join(_registry_dir(), name)
        if not name.endswith(".json") or name == f"{os.getpid()}.json":
            continue
        record = _read(path)
        if record is None or not _record_is_live(record):
            try:
                os.remove(path)
            except OSError:
                pass


def write(port: int, save_path: str = "") -> None:
    """Register this instance (idempotent)."""
    _sweep_stale()
    _atomic_write(_own_registry_path(), {
        "pid": os.getpid(),
        "port": int(port),
        "save_path": save_path or "",
        "nonce": uuid.uuid4().hex,
        "created": _pid_creation_time(os.getpid()) or time.time(),
    })


def update_save(save_path: str) -> None:
    """Record the currently-open save path."""
    record = _read(_own_registry_path())
    payload = {
        "pid": os.getpid(),
        "port": int((record or {}).get("port", 0)),
        "save_path": save_path or "",
        "nonce": (record or {}).get("nonce", uuid.uuid4().hex),
        "created": (record or {}).get("created", time.time()),
    }
    _atomic_write(_own_registry_path(), payload)


def clear() -> None:
    """Remove this instance's registry file (called on exit)."""
    try:
        os.remove(_own_registry_path())
    except OSError:
        pass


def find_conflicts(save_path: str):
    """Pids of OTHER live instances with the same save open."""
    if not save_path:
        return []
    _sweep_stale()
    target = os.path.normcase(os.path.normpath(save_path))
    conflicts = []
    for name in os.listdir(_registry_dir()):
        if not name.endswith(".json") or name == f"{os.getpid()}.json":
            continue
        record = _read(os.path.join(_registry_dir(), name))
        if record is None or not _record_is_live(record):
            continue
        other = record.get("save_path") or ""
        if other and os.path.normcase(os.path.normpath(other)) == target:
            conflicts.append(int(record["pid"]))
    return conflicts
