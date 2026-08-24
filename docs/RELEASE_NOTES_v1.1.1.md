# Release Notes — Change of Heart: Persona 5 Royal Save Studio (v1.1.1)

## 🔒 Security Audit & Robustness Fixes

**v1.1.1** follows a full external audit of the project (repo hygiene, docs/state
consistency, code security, test integrity, fresh-clone reproducibility).
Every finding was fixed; no save-format behavior changed.

---

### ✨ What's in this release

#### 1. 🔒 CSRF Hardening (local API)
- The bundled backend now validates browser `Origin` headers on every request:
  only loopback origins (`127.0.0.1` / `localhost`) are accepted — anything else
  gets `403`.
- Replaced `Access-Control-Allow-Origin: *` with validated per-origin reflection
  (+ `Vary: Origin`). A malicious webpage open in your browser can **no longer**
  drive the local save editor API.
- Verified in the packaged binary via process smoke test: loopback Origin → 200,
  foreign Origin → 403.

#### 2. 🧰 Fresh-Clone Reproducibility
- `scripts/roundtrip_harness.py` and the `lint:context` shim
  (`tools/lint_context.js`) are now tracked in git. Previously both were
  gitignored, so a fresh clone got a broken test suite (ImportError) and a dead
  lint gate.

#### 3. 🕵️ Privacy Scrub
- Removed hardcoded usernames / Steam IDs from tracked test files and the
  roundtrip harness. Steam saves are now discovered by glob
  (`%APPDATA%/SEGA/P5R/Steam/*/savedata/...`) with an optional
  `P5R_ORACLE_DIR` environment variable override.

#### 4. 📦 Dependencies & Hygiene
- Dropped unused `bottle`; added `psutil` (process-watcher first choice).
- Legacy root `HANDOFF.md` removed (archived copy retained under `archive/handoffs/`).
- Project state docs fully resynced (`state.json`, `STATUS.md`, `MEMORY.md`,
  `AGENTS.md`, `PROJECT_BOOTSTRAP.md`, README changelog + badge).

#### 5. 📂 Carried over from the v1.1.0 line (if you skipped it)
- Multi-location save auto-discovery + manual `📂 BROWSE...` file picker.
- Persona Evolution Tiers (1–3), romance/friendship toggle, Level ↔ EXP auto-sync,
  Haru/Futaba slot fix, key-item catalog unlock, WebView2 bundling hotfix.

---

### 🧪 Verification
- 168/168 unit tests passing
- Invariant checker: all 4 gates pass
- `node --check` + `lint:context`: clean
- PyInstaller rebuild + live process smoke test: PASSED

### 📦 Download & Run
- Download `CHANGE_OF_HEART_v1.1.1.zip` (or `P5R_Save_Editor.exe`) from the Releases page.
- Run the executable — no installation required.
- Automatic timestamped backups are created before every save.

> ⚠️ Always close `P5R.exe` before saving, and keep your backups. If Steam Cloud
> shows a conflict dialog after an external edit, choose the local file.
