"""
Environment, Safety, and Steam Auto-Discovery Manager for P5R Save Editor
"""

import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


def get_appdata_dir() -> Path:
    """Get Windows %APPDATA% directory."""
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata)
    return Path.home() / "AppData" / "Roaming"


def _append_sega_account_dirs(base: Path, found_dirs: List[Path]) -> None:
    """Append account save folders found below a SEGA/P5R/Steam directory."""
    if not base.exists() or not base.is_dir():
        return
    for item in base.iterdir():
        if item.is_dir():
            savedata = item / "savedata"
            found_dirs.append(savedata if savedata.is_dir() else item)


def _append_steam_userdata(base: Path, found_dirs: List[Path]) -> None:
    """Append P5R Steam Cloud folders below one userdata directory."""
    if not base.exists() or not base.is_dir():
        return
    for user_id in base.iterdir():
        if not user_id.is_dir():
            continue
        p5r_remote = user_id / "1687950" / "remote"
        if p5r_remote.is_dir():
            savedata = p5r_remote / "savedata"
            found_dirs.append(savedata if savedata.is_dir() else p5r_remote)


def discover_steam_save_dirs(
    home: Optional[Path] = None,
    platform: Optional[str] = None,
) -> List[Path]:
    """Auto-discover P5R saves on Windows and macOS compatibility layers."""
    found_dirs = []
    home = Path(home) if home is not None else Path.home()
    platform = platform or sys.platform

    if platform == "darwin":
        # Native Steam Cloud location, useful when saves are synchronized or
        # copied to the Mac even though the game itself runs through Wine.
        _append_steam_userdata(
            home / "Library" / "Application Support" / "Steam" / "userdata",
            found_dirs,
        )

        # CrossOver and Whisky keep the Windows AppData tree inside bottles.
        bottle_roots = [
            home / "Library" / "Application Support" / "CrossOver" / "Bottles",
            home / "Library" / "Containers" / "com.isaacmarovitz.Whisky" / "Bottles",
        ]
        for bottle_root in bottle_roots:
            for sega_base in bottle_root.glob(
                "*/drive_c/users/*/AppData/Roaming/SEGA/P5R/Steam"
            ):
                _append_sega_account_dirs(sega_base, found_dirs)
            for steam_base in bottle_root.glob(
                "*/drive_c/Program Files (x86)/Steam/userdata"
            ):
                _append_steam_userdata(steam_base, found_dirs)
    else:
        # Standard Windows AppData/Roaming and LocalAppData locations.
        _append_sega_account_dirs(
            get_appdata_dir() / "SEGA" / "P5R" / "Steam", found_dirs
        )
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            _append_sega_account_dirs(
                Path(local_appdata) / "SEGA" / "P5R" / "Steam", found_dirs
            )

        for steam_base in [
            Path("C:/Program Files (x86)/Steam/userdata"),
            Path("C:/Program Files/Steam/userdata"),
            Path("D:/Steam/userdata"),
            Path("E:/Steam/userdata"),
        ]:
            _append_steam_userdata(steam_base, found_dirs)

    # Deduplicate while preserving order
    unique_dirs = []
    seen = set()
    for d in found_dirs:
        try:
            res = str(d.resolve())
            if res not in seen and d.exists():
                seen.add(res)
                unique_dirs.append(d)
        except Exception:
            pass

    return unique_dirs


def list_save_files(steam_dir: Path) -> List[Path]:
    """List all DATA*.BIN, DATA*.DAT, and SYSTEM*.DAT files in the save directory."""
    if not steam_dir.exists():
        return []

    saves = []
    # Check top-level directory and 1-level subdirectories (e.g. DATA01/DATA.DAT)
    for p in [steam_dir] + [d for d in steam_dir.iterdir() if d.is_dir()]:
        for ext in ("*.BIN", "*.DAT", "*.bin", "*.dat"):
            for f in p.glob(ext):
                if f.is_file() and not f.name.endswith(".vdf"):
                    saves.append(f)

    # Sort with slot names prioritizing DATA01..DATA16 then SYSTEM
    return sorted(list(set(saves)), key=lambda x: (x.parent.name if x.parent != steam_dir else x.stem, x.name))


def check_running_processes() -> Tuple[bool, bool]:
    """
    Check if P5R.exe or steam.exe are currently running.
    Returns (p5r_running, steam_running).
    """
    p5r_running = False
    steam_running = False

    try:
        import psutil
        for proc in psutil.process_iter(["name"]):
            name = (proc.info.get("name") or "").lower()
            if "p5r.exe" in name:
                p5r_running = True
            elif "steam.exe" in name:
                steam_running = True
    except ImportError:
        # Fallback to Windows tasklist command
        try:
            output = subprocess.check_output("tasklist", text=True, stderr=subprocess.DEVNULL).lower()
            if "p5r.exe" in output:
                p5r_running = True
            if "steam.exe" in output:
                steam_running = True
        except Exception:
            pass

    return p5r_running, steam_running


def create_timestamped_backup(save_file: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Creates an automatic timestamped ZIP backup of the target save file.
    Also permanently creates and protects an immutable '<stem>_initial_original.zip'
    the very first time a save is ever touched, so the pristine baseline is never lost.
    Returns path to created backup ZIP.
    """
    if backup_dir is None:
        backup_dir = save_file.parent / "backups"

    backup_dir.mkdir(parents=True, exist_ok=True)

    # 1. Immutable Pristine Initial Baseline (Never overwritten once created)
    initial_zip = backup_dir / f"{save_file.stem}_initial_original.zip"
    if not initial_zip.exists() and save_file.exists():
        try:
            with zipfile.ZipFile(initial_zip, "w", zipfile.ZIP_DEFLATED) as izip:
                izip.write(save_file, arcname=save_file.name)
        except Exception:
            pass

    # 2. Timestamped Incremental Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = backup_dir / f"{save_file.stem}_backup_{timestamp}.zip"
    counter = 1
    while zip_path.exists():
        zip_path = backup_dir / f"{save_file.stem}_backup_{timestamp}_{counter}.zip"
        counter += 1

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(save_file, arcname=save_file.name)

    return zip_path


def list_backups(save_file: Path, backup_dir: Optional[Path] = None) -> List[Path]:
    """
    List timestamped backup ZIPs for the given save file, newest first.
    Always includes the permanent '<stem>_initial_original.zip' if present.
    """
    if backup_dir is None:
        backup_dir = save_file.parent / "backups"
    if not backup_dir.exists():
        return []
    pattern = f"{save_file.stem}_backup_*.zip"
    backups = sorted(backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    initial = backup_dir / f"{save_file.stem}_initial_original.zip"
    if initial.exists() and initial not in backups:
        backups.append(initial)
    return backups


def restore_backup(save_file: Path, backup_zip: Path) -> Path:
    """
    Restore a save file from one of its backup ZIPs.

    Before overwriting, a fresh timestamped backup of the CURRENT state is
    created (so the restore itself is reversible). Returns the path of the
    pre-restore backup. Raises ValueError on a mismatched archive (wrong
    save name inside).
    """
    if not backup_zip.exists():
        raise FileNotFoundError(f"Backup ZIP not found: {backup_zip}")

    with zipfile.ZipFile(backup_zip, "r") as zipf:
        names = zipf.namelist()
        if save_file.name not in names:
            raise ValueError(
                f"Archive {backup_zip.name} does not contain {save_file.name} "
                f"(contains: {names[:5]})"
            )
        payload = zipf.read(save_file.name)

    # Safety net: keep the current state before overwriting it.
    safety = create_timestamped_backup(save_file)

    save_file.write_bytes(payload)
    return safety
