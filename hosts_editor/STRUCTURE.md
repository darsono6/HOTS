# HOTS — Windows Hosts File Editor

A professional, dark-themed, and lightweight Windows system `hosts` file management utility built with Python and Tkinter. This tool allows developers and system administrators to safely modify host mappings, manage automated backups, flush DNS records natively, configure secure parental control DNS endpoints, and enforce application-level password protection.

---

## 📂 Project Directory Structure

To maintain a clean and professional repository, the project is structured as a standalone Python package. Redundant backup scripts or temporary local copies should be removed from the root directory to match the layout below:

```text
HOTS_Project/                      ← Repository Root Directory
├── requirements.txt               ← External dependencies (Pillow)
├── STRUCTURE.md                   ← Quick reference guide for codebase navigation
├── README.md                      ← Main project documentation (This file)
├── __init__.py                    ← Root namespace initialization (Enables running via -m)
│
└── hosts_editor/                  ← Core Application Package Source Directory
    ├── __init__.py                ← Package initialization marker (Enables relative imports)
    ├── __main__.py                ← Application bootloader (Console hiding, DPI, UAC elevation)
    ├── app.py                     ← Main GUI Application window and core UI assembly
    ├── constants.py               ← Centralized dark theme color palette and local I/O paths
    ├── core.py                    ← Pure data logic (Hosts parsing, text serialization, file CRUD)
    ├── core_antispy.py            ← Windows AntiSpy engine (telemetry services, registry, firewall rules)
    ├── dns_utils.py               ← Active interface lookup and Cloudflare Family DNS orchestration
    ├── widgets.py                 ← Reusable dark-themed widgets, custom titlebar, and dialog buttons
    │
    └── dialogs/                   ← Submodule for isolated modal dialog interfaces
        ├── __init__.py            ← Dialog package exposed class bindings
        ├── password_dialog.py     ← Encryption flows (Password prompt & set password dialogs)
        ├── diff_dialog.py         ← Unified diff comparison engine prior to file updates
        ├── backup_dialog.py       ← Local backup state historical restoration manager
        ├── diagnostics_dialog.py  ← Host telemetry scan and anti-malware system diagnostics
        └── parental_dialog.py     ← UI controller for Parental Cloudflare safe-search enforcement