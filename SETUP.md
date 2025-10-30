# 🚀 Android App Optimizer TUI - Complete Setup Guide

This guide provides comprehensive instructions for setting up and using the Android App Optimizer, a powerful Textual-based TUI for optimizing Android applications.

The tool offers two distinct methods for operation, each catering to different user needs:
1.  **🔥 Root-based**: For users with rooted devices, offering direct and powerful system access.
2.  **💧 Shizuku-based**: For non-root users, leveraging the Shizuku framework for elevated permissions.

---

## 📚 Table of Contents

- [📂 Project File Structure](#-project-file-structure)
- [⚠️ Prerequisites](#️-prerequisites)
  - [General Requirements](#general-requirements)
  - [Method 1: Root-based](#method-1-root-based)
  - [Method 2: Shizuku-based](#method-2-shizuku-based)
- [⚙️ Installation](#️-installation)
- [▶️ Usage](#️-usage)
  - [Method 1: Using `optimize-apps-root-tui.py`](#method-1-using-optimize-apps-root-tuipy)
  - [Method 2: Using `optimize-apps-shizuku-tui.py`](#method-2-using-optimize-apps-shizuku-tuipy)
- [🔄 Post-Optimization Steps](#-post-optimization-steps)
- [💡 Performance & Optimization Tips](#-performance--optimization-tips)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [❤️ Support](#️-support)

---

## 📂 Project File Structure

Here is an overview of the key files in this project:

```
/home/kaos/Documents/Android-APPS-OPTIMIZE/
├── 📜 optimize-apps-root-tui.py     # 🔥 Main TUI application for ROOTED devices
├── 📜 optimize-apps-shizuku-tui.py  # 💧 Main TUI application for SHIZUKU
├── 📝 requirements.txt              # Python dependencies
├── 📖 SETUP.md                      # This setup guide
├── 📊 optimization-status.sh        # (Optional) Bash script to check app optimization status
└── 🧪 test_py_shizuku.py            # (Optional) Python script for testing Shizuku connection
```

---

## ⚠️ Prerequisites

Before you begin, ensure your environment meets the following requirements.

### General Requirements
- **Python**: Version 3.7+
- **PIP**: For installing Python packages.
- **Git**: For cloning the repository.

### Method 1: Root-based
- **Android Device**: A **rooted** Android device is mandatory.
- **Execution Environment**:
    - **On-Device (Recommended)**: [Termux](https://termux.dev/en/) app installed on your Android device. The script will use `su` to gain root privileges.
    - **From a PC**: `adb` installed and configured. You must have passwordless `sudo` access if you intend to run ADB commands that require root.

### Method 2: Shizuku-based
- **Android Device**:
    - [Shizuku](https://shizuku.rikka.app/) app installed, running, and properly configured.
    - [Termux](https://termux.dev/en/) app installed.
- **Termux-Shizuku Integration**: You must grant Termux permission to access Shizuku.

---

## ⚙️ Installation

1.  **Clone the Repository**
    Open your terminal and clone the project files.
    ```bash
    git clone <repository_url>
    cd Android-APPS-OPTIMIZE
    ```

2.  **Install Python Dependencies**
    The required Python libraries are listed in `requirements.txt`. Install them using pip.
    ```bash
    pip install -r requirements.txt
    ```
    Or, to install them manually with the latest specified versions:
    ```bash
    pip install "textual>=0.60.0" "rich>=13.7.0" "pexpect>=4.9.0"
    ```
    > **Note**: The new Textual TUI versions do not use `questionary`.

3.  **Make Scripts Executable**
    Grant execution permissions to the Python scripts for easier use.
    ```bash
    chmod +x optimize-apps-root-tui.py optimize-apps-shizuku-tui.py
    ```

---

## ▶️ Usage

Both scripts feature an identical, modern Textual interface for a seamless user experience.

### Method 1: Using `optimize-apps-root-tui.py` (🔥 Root)

This script is designed for rooted devices and offers a robust way to perform optimizations.

**To Run the Application:**
```bash
./optimize-apps-root-tui.py
```
or
```bash
python3 optimize-apps-root-tui.py
```

**TUI Workflow:**
1.  **Connection**: The script automatically detects if it's running in Termux (using `su`) or on a PC (using `sudo`). It will then request root access.
2.  **App Listing**: A list of user-installed apps appears, grouped by optimization status and color-coded for clarity.
3.  **App Selection**:
    - Use `↑` and `↓` arrow keys to navigate.
    - Press `Space` to toggle selection for an app.
    - Press `A` to select all filtered apps, and `D` to deselect all.
    - Use the search bar at the top to filter the app list in real-time.
    - Press `Enter` to confirm your selection.
4.  **Profile Selection**: Choose the desired optimization profile. `everything` is generally the fastest, while `space` is best for saving storage.
5.  **Optimization**: A progress bar and log will show the real-time status of the optimization process.
6.  **Summary**: After completion, a summary screen displays the results and provides post-optimization options.

### Method 2: Using `optimize-apps-shizuku-tui.py` (💧 Shizuku)

This script uses Shizuku, making it perfect for non-rooted devices where Shizuku is set up.

**To Run the Application:**
Ensure you are in a terminal (like Termux) where Shizuku is accessible.
```bash
./optimize-apps-shizuku-tui.py
```
or
```bash
python3 optimize-apps-shizuku-tui.py
```

**TUI Workflow:**
The user interface and workflow are **identical** to the root-based version. The script handles the Shizuku connection in the background.

---

## 🔄 Post-Optimization Steps

### ‼️ IMPORTANT: REBOOT REQUIRED ‼️

After optimizing apps, **you MUST reboot your device**.

- **Why?** The optimization process can interfere with Android's Scoped Storage permissions. A reboot is necessary to fix these permissions and ensure apps can access their storage correctly.
- **Persistence**: All optimizations are permanent and will persist across reboots.

The summary screen in the TUI provides a convenient button to reboot the device immediately.

---

## 💡 Performance & Optimization Tips

- **Batch Optimization**: Select and optimize multiple apps at once. The TUI is designed for this and it's much faster than optimizing one by one.
- **Profile Choice**:
    - For maximum performance, use `speed-profile` or `everything`.
    - For devices with limited storage, use `space` or `space-profile`.
- **Run During Idle Time**: The optimization process can be resource-intensive. Run it when you are not actively using your device for the best results.
- **Verify Status**: After rebooting, you can use the `optimization-status.sh` script (run inside Termux with Shizuku or root) to verify the new optimization status of your apps.

---

## 🛠️ Troubleshooting

### General Issues
- **"ModuleNotFoundError" / "ImportError"**: You haven't installed the required dependencies. Run `pip install -r requirements.txt`.
- **UI Looks Garbled**: Your terminal may not fully support the characters used by Textual. Ensure you are using a modern terminal emulator like Termux, Kitty, or Windows Terminal.

### Root-based Method (`optimize-apps-root-tui.py`)
- **"Failed to connect with sudo"**: If running from a PC, this means the script couldn't get root access non-interactively. Ensure you have configured **passwordless sudo** for your user.
- **Errors During Optimization**:
    1. Check the log file `root_optimizer.log` for detailed error messages.
    2. Run the script with the `--diagnose` flag for a full checkup of your environment:
       ```bash
       ./optimize-apps-root-tui.py --diagnose
       ```

### Shizuku-based Method (`optimize-apps-shizuku-tui.py`)
- **"Error connecting to Shizuku"**:
    - Verify that the Shizuku app is running on your Android device.
    - Open the Shizuku app and check if Termux is listed and authorized.
    - Try restarting the Shizuku service from within the app.
- **"Command timed out"**:
    - Your device may be under heavy load. Try again later or optimize fewer apps at once.
    - This can happen with very large apps. The default timeout is high, but older devices may struggle.
- **Errors During Optimization**: Check the log file `shizuku_optimizer.log` for detailed error messages from the Shizuku service.

---

## ❤️ Support

If you encounter issues not covered in the troubleshooting section, please feel free to open an issue on the project's GitHub page. Provide as much detail as possible, including the method you are using (Root or Shizuku) and any relevant logs.
