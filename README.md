# Change of Heart — Persona 5 Royal Save Editor for macOS

A Persona 5 Royal save editor packaged as a standalone macOS application for
Apple Silicon Macs.

<p align="center">
  <img src="change_of_heart_logo.jpg" alt="Change of Heart" width="360">
</p>

<p align="center">
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20arm64-black?style=for-the-badge&logo=apple" alt="macOS Apple Silicon"></a>
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/Tests-173%20passing-brightgreen?style=for-the-badge" alt="173 tests passing"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License"></a>
</p>

## macOS Edition

This edition turns the original Windows editor into a proper
`Change of Heart.app` bundle for macOS:

- native `arm64` Mach-O executable;
- Cocoa window powered by the macOS WebKit engine;
- Python runtime and all dependencies embedded in the application;
- no Python installation required on the Mac running the finished bundle;
- automatic Steam, CrossOver, and Whisky save discovery;
- internal server restricted to `127.0.0.1`, with protection against requests
  originating from external websites.

The original save-editing engine has not been rewritten in Swift. Keeping the
existing Python engine preserves its test coverage and the safeguards designed
to prevent save corruption.

## Compatibility

| Environment | Status |
|---|---|
| Apple Silicon Mac | **Supported and tested** |
| Architecture | `arm64` |
| Declared minimum macOS version | macOS 12 Monterey |
| Native window | Cocoa + WebKit |
| Intel Mac | Untested; no `x86_64` bundle is currently provided |
| CrossOver | Automatic save discovery supported |
| Whisky | Automatic save discovery supported |
| Steam for macOS | Searches the standard `userdata` directory |

Apple Silicon covers Macs equipped with Apple M-series processors. The current
bundle is not universal and does not include an Intel `x86_64` slice.

## Building the Application

### Requirements

- an Apple Silicon Mac;
- [Homebrew](https://brew.sh/);
- Python 3.14 installed through Homebrew.

```bash
brew install python@3.14
```

### Automated build

Clone the repository and run the build script:

```bash
git clone https://github.com/SltcYann/change-of-heart-mac.git
cd change-of-heart-mac
./Build_macOS.command
```

The script:

1. creates an isolated `.venv-macos` Python environment;
2. installs PyWebView, PyObjC, PyInstaller, and the cryptographic dependencies;
3. runs the complete test suite;
4. builds and locally signs the macOS application bundle.

Output:

```text
dist/Change of Heart.app
```

You can then move `Change of Heart.app` into your `Applications` folder.

## Running the Application

Double-click `Change of Heart.app`.

Locally built versions receive an ad hoc macOS signature. This is valid for
local use, but the application is not yet signed with an Apple Developer ID or
notarized by Apple.

When opening a downloaded build for the first time, macOS may display a
Gatekeeper warning. If this happens, right-click the application, select
**Open**, and confirm. Do not disable macOS security protections globally.

## Finding Your Saves

The application automatically searches the most common Persona 5 Royal save
locations.

### CrossOver

```text
~/Library/Application Support/CrossOver/Bottles/*/drive_c/users/*/
AppData/Roaming/SEGA/P5R/Steam/*/savedata/
```

### Whisky

```text
~/Library/Containers/com.isaacmarovitz.Whisky/Bottles/*/drive_c/users/*/
AppData/Roaming/SEGA/P5R/Steam/*/savedata/
```

### Steam

```text
~/Library/Application Support/Steam/userdata/*/1687950/remote/
```

If your save is stored elsewhere, use the manual file picker in the application.

## Features

### General save information

- edit the protagonist's first name, last name, and Phantom Thieves name;
- edit the yen balance;
- read the current date, player level, difficulty, and play time;
- support for the Persona 5 Royal PC/Steam save format.

### Confidants and social stats

- edit all 23 Confidants;
- preserve already accumulated bond points;
- edit all five social stats;
- guarded friendship and romance route handling;
- protection against ranks that conflict with story progression.

### Personas and party members

- edit all 12 of Joker's Persona slots;
- adjust levels, stats, skills, and traits;
- synchronize levels and EXP automatically;
- select party-member Persona evolution tiers;
- detect characters who have not yet joined the party.

### Compendium

- edit individual registrations;
- perform a full unlock matching verified PC saves;
- synchronize the primary mask and its mirror copy;
- reject dead or incompatible entries.

### Inventory

- melee and ranged weapons;
- protectors and accessories;
- consumables and infiltration tools;
- skill cards;
- treasure, materials, and key items;
- global search, filters, quantities, and a change review before writing.

Outfits remain intentionally read-only until their save-writing behavior has
been proven safe through controlled save comparisons.

## Save Safety

Change of Heart modifies encrypted binary data. The following safeguards are
built in:

- automatic ZIP backup before every write;
- permanent preservation of the initial untouched copy;
- synchronized writes to the primary and mirror regions;
- CRC recalculation and encryption after editing;
- refusal to write while Persona 5 Royal is detected as running;
- warning when the same save is open in multiple windows;
- validation of quantities, levels, identifiers, and known structures.

You should still keep a separate copy of important saves and temporarily pause
Steam Cloud synchronization during sensitive operations.

## Architecture

```text
Change of Heart.app (Mach-O arm64)
        │
        ├── Cocoa / WebKit — native macOS window
        │
        ├── local HTTP server — 127.0.0.1, ephemeral port
        │
        ├── HTML / CSS / JavaScript interface
        │
        └── embedded Python engine
              ├── P5R structure reader and writer
              ├── AES-256-CBC
              ├── CRC32
              ├── backups
              └── integrity checks
```

The internal server never listens on the local network. Save files are not sent
to any remote service.

## Development

Manual setup:

```bash
/opt/homebrew/bin/python3 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r requirements-build.txt
.venv-macos/bin/python main.py
```

Tests:

```bash
.venv-macos/bin/python -m unittest discover -s tests
.venv-macos/bin/python scripts/check-invariants.py
npm run lint:context
```

Direct PyInstaller build:

```bash
DEVELOPER_DIR=/Library/Developer/CommandLineTools \
  .venv-macos/bin/python -m PyInstaller \
  P5R_Save_Editor.spec --noconfirm --clean --distpath dist
```

## Current Limitations

- the current bundle is Apple Silicon only;
- Intel `x86_64` and `universal2` builds have not been tested;
- public Developer ID signing and Apple notarization are not yet configured;
- the editor targets Persona 5 Royal PC/Steam saves, not PlayStation saves;
- complex story data remains intentionally read-only whenever no sufficiently
  safe mapping is available.

## Original Project and Credits

The Change of Heart engine comes from the community project created by
**j0nny DiGITAL**, with reverse-engineering and validation work performed with
Hermes Agent and Antigravity. This edition adds the packaging, native window
backend, and save-discovery support required for macOS.

Persona 5 Royal is a trademark of ATLUS and SEGA. This community project is not
affiliated with or endorsed by ATLUS or SEGA.

## License

This project is distributed under the [MIT License](LICENSE).
