# Android-APPS-OPTIMIZE: Android App Optimizer TUI

![Python](https://img.shields.io/badge/Python-3%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## Overview

Android-APPS-OPTIMIZE is a modern Terminal User Interface (TUI) application for optimizing Android applications using ART (Android Runtime) compilation profiles. It provides an interactive way to manage app compilation modes to improve performance, reduce storage usage, or verify app integrity on both rooted and non-rooted Android devices.

The tool offers two distinct execution methods:
- **🔥 Root-based** (`optimize-apps-root-tui.py`): Direct root access for rooted devices
- **💧 Shizuku-based** (`optimize-apps-shizuku-tui.py`): Non-root privilege escalation via Shizuku

## Key Features

- **Interactive TUI**: Modern terminal interface built with Textual framework
- **Real-time App Status**: Display current optimization status of all installed apps
- **8 Optimization Profiles**: Choose from `everything`, `everything-profile`, `speed`, `speed-profile`, `space`, `space-profile`, `verify`, and `quicken`
- **Multi-app Selection**: Select and optimize multiple apps at once with search and filtering
- **Live Progress Tracking**: Real-time optimization progress and detailed logging
- **Dual Execution Methods**: Works with root access or via Shizuku framework
- **Device Reboot Integration**: Built-in device reboot functionality
- **Diagnostic Mode**: System environment checks (root version only)

## Project Structure

```
Android-APPS-OPTIMIZE/
├── optimize-apps-root-tui.py       # Interactive TUI for rooted devices
├── optimize-apps-shizuku-tui.py    # Interactive TUI for Shizuku (non-root)
├── optimize-apps_v2.sh             # Legacy bash script (optional)
├── optimization-status.sh          # Bash utility to check optimization status
├── test_py_shizuku.py              # Testing utility for Shizuku connection
├── requirements.txt                # Python dependencies
├── README.md                        # This file
├── SETUP.md                         # Installation and usage guide
└── __pycache__/                     # Python cache directory
```

## Requirements

### General
- **Python 3** (3.7+)
- **pip** (Python package manager)

### Method 1: Root-Based (`optimize-apps-root-tui.py`)
- **Rooted Android device** or
- **Termux** with `su` access on a rooted Android device
- **passwordless sudo** if running from a PC with ADB

### Method 2: Shizuku-Based (`optimize-apps-shizuku-tui.py`)
- **Android device** with [Shizuku](https://shizuku.rikka.app/) installed and running
- **Termux** with Shizuku integration enabled

## Dependencies

All dependencies are listed in `requirements.txt`:

```
pexpect>=4.9.0      # Interactive shell control
rich>=13.7.0        # Terminal formatting and colors
questionary>=1.10.0 # Interactive prompts
textual>=0.60.0     # TUI framework
```

## Installation

### 1. Clone or Download
```bash
git clone <repository_url>
cd Android-APPS-OPTIMIZE
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install "textual>=0.60.0" "rich>=13.7.0" "pexpect>=4.9.0" "questionary>=1.10.0"
```

### 3. Make Scripts Executable
```bash
chmod +x optimize-apps-root-tui.py optimize-apps-shizuku-tui.py
```

## Quick Start

### For Rooted Devices (Root Method)

```bash
./optimize-apps-root-tui.py
```

The script will:
1. Detect if running in Termux or via PC ADB
2. Request root access
3. Display all user-installed apps with their optimization status
4. Allow you to select apps and choose an optimization profile
5. Execute the optimization with live progress tracking
6. Summarize results and recommend a device reboot

### For Non-Rooted Devices (Shizuku Method)

Ensure Shizuku is running,   
Install install [termux-shizuku-tools] (https://github.com/AlexeiCrystal/termux-shizuku-tools)  
then:
```bash
./optimize-apps-shizuku-tui.py
```

The workflow is identical to the root method, but commands are executed through Shizuku instead of direct root access.

## Optimization Profiles Explained

The following ART (Android Runtime) compilation profiles are supported:

### Performance-Focused Profiles

**`everything`**
- Fully AOT (Ahead-Of-Time) compiled to native code
- Fastest app launch and execution
- Uses maximum storage space
- Best for: Users with plenty of storage who want maximum performance

**`everything-profile`**
- Profile-guided AOT compilation
- AOT compiles only frequently-used code paths
- Excellent performance with less storage than `everything`
- Requires app usage profile data
- Best for: Balanced performance and storage

**`speed`**
- Full speed optimization without usage profiles
- Significant performance improvement
- Uses more storage than profile-guided options
- Best for: Quick performance boost without waiting for profiles

**`speed-profile`** (Recommended)
- Profile-guided speed optimization
- Best balance of performance, storage, and battery life
- Android's default optimization strategy
- Best for: Most users (set it and forget it)

### Storage-Focused Profiles

**`space`**
- Optimized for storage efficiency
- Minimal compilation, mostly runtime interpretation
- Slower performance
- Best for: Devices with limited storage

**`space-profile`**
- Profile-guided storage optimization
- Compiles only the most frequently-used code
- Better than `space` with lower overhead
- Best for: Storage-constrained devices that still want some performance

### Minimal/Diagnostic Profiles

**`verify`**
- No compilation, only verifies DEX files
- Very fast to apply
- No performance benefit
- Best for: Debugging and troubleshooting

**`quicken`**
- Minimal DEX optimizations
- Less intensive than speed profiles
- Light performance improvement
- Best for: Quick, lightweight optimization

## Usage Examples

### Select and Optimize Multiple Apps (Root)
```bash
./optimize-apps-root-tui.py
# 1. Search for apps (e.g., "com.google")
# 2. Press Space to select, A to select all, D to deselect all
# 3. Press Enter to confirm selection
# 4. Choose optimization profile (e.g., "speed-profile")
# 5. Watch real-time optimization progress
# 6. Reboot device when prompted
```

### Optimize via Shizuku
```bash
./optimize-apps-shizuku-tui.py
# Same workflow as root method
```

### Diagnostic Mode (Root Only)
```bash
./optimize-apps-root-tui.py --diagnose
# or
./optimize-apps-root-tui.py -d
```

Checks:
- Python version compatibility
- Required dependencies installation
- Root connectivity (sudo/su)
- Android shell command availability

## Logging

Both scripts create detailed log files:

- **Root version**: `root_optimizer.log`
- **Shizuku version**: `shizuku_optimizer.log`

Log files contain timestamps, debug information, and error messages useful for troubleshooting.

## Important Notes

### Reboot Required ⚠️
After optimization, **you must reboot your device**. The optimization process can interfere with Android's Scoped Storage permissions, which are restored after reboot. All optimizations are permanent and persist across reboots.

### Performance Tips

- **Use `speed-profile`** for the best balance (Android's default)
- **Batch optimize** multiple apps together (faster than one-by-one)
- **Run during idle time** - optimization is resource-intensive
- **Wait for app usage profiles** before using profile-guided modes
- **Don't optimize constantly** - once is usually enough

## Troubleshooting

### General Issues

**"ModuleNotFoundError" or "ImportError"**
- Solution: Install dependencies with `pip install -r requirements.txt`

**TUI looks garbled or distorted**
- Solution: Use a modern terminal emulator (Termux, Kitty, Windows Terminal)
- Ensure your terminal supports Unicode/UTF-8

### Root Method Issues

**"Failed to connect with sudo"**
- Problem: Running from PC without passwordless sudo
- Solution: Configure passwordless sudo for your user
- Test with: `sudo -n whoami`

**Errors during optimization**
- Check log file: `root_optimizer.log`
- Run diagnostic: `./optimize-apps-root-tui.py --diagnose`

**"python: not found" on device**
- Problem: Your ROM doesn't have Python
- Solution: Install Python via Magisk module in Termux

### Shizuku Method Issues

**"Error connecting to Shizuku"**
- Check: Is the Shizuku app running?
- Check: Is Termux authorized in the Shizuku app?
- Solution: Restart the Shizuku service

**"Command timed out"**
- Problem: Device is under heavy load or optimizing very large apps
- Solution: Try again later or optimize fewer apps at once

**Errors during optimization**
- Check log file: `shizuku_optimizer.log`

## Architecture

Both scripts follow a common pattern:

1. **Command Wrapper**: `RootWrapper` or `ShizukuWrapper` abstracts command execution
2. **TUI Screens**: Textual-based screens for different stages
   - App Selection Screen: Browse and select apps
   - Profile Selection Screen: Choose optimization profile
   - Progress Screen: Real-time optimization tracking
   - Summary Screen: Results and reboot option
3. **Status Parser**: Parses `dumpsys package dexopt` output to determine app status
4. **Logging**: Comprehensive logging for debugging

## Testing

A test utility is provided to verify Shizuku connectivity:

```bash
python test_py_shizuku.py
```

This helps diagnose Shizuku connection issues before running the full optimizer.

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the SETUP.md guide
2. Review log files for detailed error messages
3. Run diagnostic mode (root version): `./optimize-apps-root-tui.py --diagnose`
4. Open an issue on the project repository with logs and your setup details
