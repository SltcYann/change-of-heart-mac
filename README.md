# Change of Heart — Persona 5 Royal Save Editor

a persona 5 royal save editor changed to execute on macos

<p align="center">
  <img src="change_of_heart_logo.jpg" alt="Change of Heart" width="360">
</p>

<p align="center">
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20arm64-black?style=for-the-badge&logo=apple" alt="macOS Apple Silicon"></a>
  <a href="https://github.com/SltcYann/change-of-heart-mac"><img src="https://img.shields.io/badge/Tests-173%20passing-brightgreen?style=for-the-badge" alt="173 tests passing"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License"></a>
</p>

## building the app

### requirements

- an apple silicon mac
- [homebrew](https://brew.sh/)
- python 3.14 installed through homebrew

```bash
brew install python@3.14
```

### automated build

clone the repository and run the build script :

```bash
git clone https://github.com/SltcYann/change-of-heart-mac.git
cd change-of-heart-mac
./Build_macOS.command
```

## finding your saves

### crossover

```text
~/Library/Application Support/CrossOver/Bottles/*/drive_c/users/*/
AppData/Roaming/SEGA/P5R/Steam/*/savedata/
```

## credits

Change of Heart is originally made by j0nny DiGITAL
go support him on ko-fi : https://ko-fi.com/j0nnydigital

## license

this project is distributed under the [MIT license](LICENSE)
