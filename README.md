# OPRYXX Deployment Guide

## Overview
OPRYXX provides a streamlined, automated workflow for Windows repair and driver deployment on supported hardware. It includes PowerShell automation (Apex), a lightweight Python API + dashboard, and model-specific driver packs.

## Contents
- `drivers/` - Model-specific driver folders (INF-based)
- `drivers/MSI_Summit_E16_AI_Studio_A1VFTG/` - MSI Summit E16 AI Studio A1VFTG drivers
- `drivers/Inspiron_2in1_7550/` - Dell Inspiron 2-in-1 7550 drivers
- `manifest.json` - Manifest (v2) with `models[]` and steps
- `lib/*.psm1` - Opryxx PowerShell modules (manifest, logging, executor, repair, etc.)
- `apex.ps1` - Apex orchestrator (plan/execute/report)
- `install_model_drivers.ps1` - Install model drivers (online or offline image)
- `detect_machine_model.ps1` - Standalone repair + model detection script
- `backend_api_scaffold.py` - Minimal Flask API (with SSE/Socket.IO events)
- `web/*` - Static dashboard UI

## Deployment Methods
- Apex (PowerShell) automated workflow
- Python Control Center (Flask) UI
- Manual INF installation via Device Manager or `pnputil`
- Offline image driver injection via DISM (optional)

## Quick Start (Apex)
Run a dry-run plan (no changes):
- PowerShell (Admin recommended): `powershell -ExecutionPolicy Bypass -File .\\OPRYXX\\apex.ps1 -DryRun`

Run live execution (may require elevation):
- `powershell -ExecutionPolicy Bypass -File .\\OPRYXX\\apex.ps1`

Outputs are stored under `C:\\ProgramData\\Opryxx\\Logs\\run_YYYYMMDD_HHMMSS`.

## Quick Start (Dashboard)
1) Install Python 3.9+ and dependencies: `pip install -r OPRYXX/requirements.txt`
2) Optional auth: `set OPRYXX_API_TOKEN=your-secret`
3) Start API: `python OPRYXX\\backend_api_scaffold.py`
4) Open: `http://127.0.0.1:5050/`

Features:
- Real-time metrics and logs (Socket.IO with SSE fallback)
- Actions: Dry-run plan, Full repair (Apex), Install model drivers
- Quick repairs: SFC, DISM, CHKDSK
- Boot diagnostics + safe WinRE enable and protected BCD rebuild

Notes:
- Some actions require Administrator privileges.
- When `OPRYXX_API_TOKEN` is set, include `Authorization: Bearer <token>` on POST requests. The dashboard reads `localStorage.OPRYXX_TOKEN` automatically.

## Self-Test
Run the built-in self-test (dry-run + driver enumeration):
- `powershell -ExecutionPolicy Bypass -File .\\OPRYXX\\selftest.ps1`

## Build Portable EXE (optional)
- `powershell -ExecutionPolicy Bypass -File .\\OPRYXX\\build_exe.ps1 -InstallDeps`
- Output: `OPRYXX\\dist\\OpryxxControlCenter.exe`

## Support
File issues or contact the maintainer. For advanced boot repair automation, see functions under `lib/Opryxx.Repair.psm1`.

## USB Toolkit (offline, boot-failure ready)
- Prepare a USB folder with OPRYXX and launchers:
  - `powershell -ExecutionPolicy Bypass -File .\\OPRYXX\\tools\\package_usb.ps1 -TargetRoot E:\\ -IncludePython`
  - Replace `E:\\` with your USB root. Use `-InstallAutoRepair` to register the startup auto-repair task immediately.
- On target system:
  - Run `Launch_Opryxx.cmd` for full repair or `Launch_Opryxx_DryRun.cmd` for plan only.
  - To install auto boot-repair (runs at startup and attempts safe fixes):
    - `powershell -ExecutionPolicy Bypass -File OPRYXX\\tools\\install_boot_autorepair.ps1`
- Building a WinPE USB (optional):
  - If using ADK, set `startnet.cmd` to: `wpeinit && powershell -ExecutionPolicy Bypass -File X:\\OPRYXX\\apex.ps1`

