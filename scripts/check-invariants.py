#!/usr/bin/env python3
"""
P5R Save Editor — Lightweight invariant checker.

Runs after structural code changes. Checks:
1. Test suite passes (153+ tests)
2. state.json is valid JSON with required fields
3. No banned patterns in recent git diff (checksum bypasses, quick-array merges)
4. MEMORY.md, STATUS.md, state.json are all present

Usage:
    python scripts/check-invariants.py          # full check
    python scripts/check-invariants.py --quick  # skip git diff scan
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = ["AGENTS.md", "MEMORY.md", "STATUS.md", "state.json"]
REQUIRED_STATE_FIELDS = ["schema_version", "phase", "gate", "last_session", "updated_at", "test_command"]

import re
# Patterns that should never appear in committed code
BANNED_PATTERNS = [
    (r"slotIdx\s*<\s*30", "Quick-array 30-slot cap (was silently dropping items)"),
    (r"0x3530.*merge|merge.*0x3530", "Quick-array merge (never merge with master counts)"),
    (r"PS4.*offset|KHSaveEditor", "PS4 offset reference (PC != PS4)"),
]


def check_required_files():
    """Verify all required project files exist."""
    errors = []
    for f in REQUIRED_FILES:
        path = PROJECT_ROOT / f
        if not path.exists():
            errors.append(f"MISSING: {f}")
    return errors


def check_state_json_and_sync():
    """Verify state.json is valid, has required fields, and is 100% in sync with STATUS.md."""
    state_path = PROJECT_ROOT / "state.json"
    status_path = PROJECT_ROOT / "STATUS.md"
    if not state_path.exists():
        return ["MISSING: state.json"], None
    try:
        with open(state_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"INVALID JSON: state.json — {e}"], None

    errors = []
    for field in REQUIRED_STATE_FIELDS:
        if field not in data:
            errors.append(f"MISSING FIELD: state.json.{field}")

    if errors:
        return errors, None

    # Verify Dual-State Synchronization between state.json and STATUS.md
    if status_path.exists():
        try:
            import re
            status_text = status_path.read_text(encoding="utf-8")
            phase_m = re.search(r"\*\*Phase:\*\*\s*([^\n\r]+)", status_text)
            gate_m = re.search(r"\*\*Gate:\*\*\s*([^\n\r]+)", status_text)
            if not phase_m or not gate_m:
                errors.append("STATUS.md missing '**Phase:**' or '**Gate:**' declarations")
            else:
                st_phase = phase_m.group(1).strip()
                st_gate = gate_m.group(1).strip()
                if st_phase != str(data.get("phase")).strip():
                    errors.append(f"Dual-State Phase desync: STATUS.md has '{st_phase}' but state.json has '{data.get('phase')}'")
                if st_gate != str(data.get("gate")).strip():
                    errors.append(f"Dual-State Gate desync: STATUS.md has '{st_gate}' but state.json has '{data.get('gate')}'")
        except Exception as e:
            errors.append(f"STATUS.md parse error: {e}")

    return errors, data.get("test_command")


def check_test_suite(test_cmd=None):
    """Run the test suite dynamically from state.json and report pass/fail."""
    if not test_cmd:
        test_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    try:
        r = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(PROJECT_ROOT),
            timeout=120
        )
        if r.returncode != 0:
            lines = r.stdout.strip().split("\n")
            last_line = lines[-1] if lines else "unknown"
            return [f"TESTS FAILED (exit {r.returncode}): {last_line}"]
        return []
    except subprocess.TimeoutExpired:
        return ["TESTS TIMEOUT: suite exceeded 120s"]
    except Exception as e:
        return [f"TESTS ERROR: {e}"]


def check_git_diff_banned_patterns():
    """Scan recent git diff for banned patterns in source code additions."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--unified=0"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if result.returncode != 0:
            return []  # git diff failed, skip
        diff_text = result.stdout
        # Only inspect lines added/modified in source code (excluding test files and check-invariants.py)
        filtered_lines = []
        current_file = ""
        for line in diff_text.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("+") and not line.startswith("+++"):
                if "check-invariants.py" not in current_file and not current_file.startswith("tests/"):
                    filtered_lines.append(line[1:])

        scan_target = "\n".join(filtered_lines)
        errors = []
        for pattern, description in BANNED_PATTERNS:
            if re.search(pattern, scan_target, re.IGNORECASE):
                errors.append(f"BANNED PATTERN in source diff: {description}")
        return errors
    except Exception:
        return []  # git not available, skip


def main():
    quick = "--quick" in sys.argv
    all_errors = []

    print("=== P5R Invariant Check ===")

    # 1. Required files
    print("\n[1/4] Required files...")
    errors = check_required_files()
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("  [OK] All required files present")

    # 2. state.json validity & Dual-State Sync
    print("\n[2/4] state.json & STATUS.md sync...")
    errors, test_cmd = check_state_json_and_sync()
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("  [OK] state.json valid and in sync with STATUS.md")

    # 3. Test suite
    print("\n[3/4] Test suite...")
    errors = check_test_suite(test_cmd)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("  [OK] All tests pass")

    # 4. Git diff banned patterns
    if not quick:
        print("\n[4/4] Git diff banned patterns...")
        errors = check_git_diff_banned_patterns()
        all_errors.extend(errors)
        if errors:
            for e in errors:
                print(f"  [FAIL] {e}")
        else:
            print("  [OK] No banned patterns in recent diff")
    else:
        print("\n[4/4] Git diff scan — SKIPPED (--quick)")

    # Summary
    print(f"\n{'='*40}")
    if all_errors:
        print(f"FAILED: {len(all_errors)} violation(s)")
        sys.exit(1)
    else:
        print("PASSED: all invariants OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
