# Change of Heart — Persona 5 Royal Save Editor for macOS

A Persona 5 Royal save editor changed to execute on macOS

<p align="center">
  <img src="change_of_heart_logo.jpg" alt="Change of Heart" width="360">
</p>

<p align="center">
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20arm64-black?style=for-the-badge&logo=apple" alt="macOS Apple Silicon"></a>
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/Tests-173%20passing-brightgreen?style=for-the-badge" alt="173 tests passing"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License"></a>
</p>

## Building the Application

### Requirements

- an Apple Silicon Mac
- [Homebrew](https://brew.sh/)
- Python 3.14 installed through Homebrew

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

## Finding Your Saves

the app automatically find your saves if you use crossover/whisky

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

## Features

the features are the same that the original version

## Original Project and Credits

Change of Heart is originally made by j0nny DiGITAL
go support him on ko-fi : https://ko-fi.com/j0nnydigital

Persona 5 Royal is a trademark of ATLUS and SEGA. This community project is not
affiliated with or endorsed by ATLUS or SEGA.

## License

This project is distributed under the [MIT License](LICENSE).
