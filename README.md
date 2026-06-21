# Battery Alarm — NVDA Add-on

[![NVDA](https://img.shields.io/badge/NVDA-2023.1+-blue.svg)](https://www.nvaccess.org/)
[![Version](https://img.shields.io/github/v/release/bastidasaul06-rgb/batteryAlarm)](https://github.com/bastidasaul06-rgb/batteryAlarm/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/bastidasaul06-rgb/batteryAlarm/total)](https://github.com/bastidasaul06-rgb/batteryAlarm/releases)
[![License](https://img.shields.io/github/license/bastidasaul06-rgb/batteryAlarm)](LICENSE)

**Battery Alarm** is an NVDA add-on that plays a sound when your battery reaches a configurable percentage. It supports **two independent alarms**: one for discharging (low battery) and one for charging (full charge).

---

## Features

- **Discharge alarm**: sounds when battery drops below a configurable threshold.
- **Charge alarm**: sounds when battery reaches a configurable percentage while charging.
- **Configurable beep**: frequency and duration are fully customizable.
- **Dismiss**: stop the alarm with a keypress; it won't sound again until the condition resets.
- **Auto-stop**: alarm stops automatically when the charger is connected (discharge) or when battery drops below the charge threshold.
- **Built-in update checker**: detects and installs new versions directly from GitHub.
- **Menu accessible**: configure everything from NVDA menu or keyboard shortcuts.

---

## Download

[Download the latest version](https://github.com/bastidasaul06-rgb/batteryAlarm/releases/latest/download/batteryAlarm.nvda-addon)

---

## Keyboard Shortcuts

| Gesture | Action |
|---------|--------|
| `NVDA+Shift+Alt+A` | Open battery alarm settings |
| `NVDA+Shift+Alt+D` | Dismiss current alarm |
| `NVDA+Shift+Alt+U` | Check for updates |

You can also access these from the NVDA menu: `NVDA+N` → **Alarma de Bateria**.

---

## Installation

1. Download the `.nvda-addon` file from the [latest release](https://github.com/bastidasaul06-rgb/batteryAlarm/releases/latest).
2. Open the file or press `NVDA+N` → Tools → Install add-on.
3. Follow the prompts and restart NVDA.

---

## Configuration

1. Press `NVDA+Shift+Alt+A` or go to NVDA menu → **Alarma de Bateria - Configurar**.
2. Set your preferences:

   - **Discharge alarm**: enable and set the threshold (e.g., 20%).
   - **Charge alarm**: enable and set the threshold (e.g., 90%).
   - **Sound**: adjust frequency (Hz) and duration (ms), then click "Test sound".
3. Press OK to save.

---

## Updating

Press `NVDA+Shift+Alt+U` or go to NVDA menu → **Alarma de Bateria - Buscar actualizaciones**. The add-on will check GitHub for new releases and install the update automatically.

---

## Changelog

### v1.2.0
- Fixed: menu items now appear correctly in NVDA menu.
- Fixed: update checker now handles network errors gracefully.
- Menu: added "Configure" and "Check for updates" entries under NVDA+N.

### v1.1.0
- New: charge alarm (second threshold for when battery is charging).
- New: reorganized settings dialog with discharge, charge, and sound sections.
- New: GitHub repository with automatic updates.

### v1.0.1
- Initial release.

---

## License

This project is licensed under the **GNU General Public License v2.0**. See the [LICENSE](LICENSE) file for details.

---

## Author

**Saúl Iturbe** — [Atlas Software](https://github.com/bastidasaul06-rgb)
