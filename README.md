#  The Watcher - System Sentinel

**The Watcher** is a lightweight, open-source forensic monitoring tool for Windows. It tracks user-initiated process starts and file system changes in real-time while filtering out background system noise.

---

##  Key Features
* **Active Monitoring:** Logs only relevant user actions (Programs opened, files created/moved).
* **Noise Reduction:** Automatically ignores Windows telemetry, browser cache, and temp files.
* **Stealth Mode:** Runs silently in the System Tray; continues monitoring when the window is closed.
* **Search & Filter:** Dynamic search bar and User-Selector for deep-dive analysis.
* **Persistent Logging:** Clears the live view on command, but can be configured for local log files.
* **Autostart Ready:** Designed to launch on Windows startup.

## 🚀 Installation

### For Users (Fastest)
1. Go to the [Releases](../../releases) page.
2. Download `TheWatcher_Installer.exe`.
3. Run the installer. The Watcher will be added to your desktop and startup folder.

### For Developers (Source Code)
1. Clone the repository:
   ```bash
   git clone [https://github.com/uncapp3d/The-Watcher.git](https://github.com/uncapp3d/The-Watcher.git)
