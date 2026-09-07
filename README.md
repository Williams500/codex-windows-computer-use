# Codex Windows Computer Use

A generic Windows desktop control runtime for Codex and other computer-use agents.

It separates **observation**, **semantic UI inspection**, **input execution**, **safety guards**, and **verification** so the agent is not coupled to a particular application.

## Capabilities

- Enumerate and select arbitrary top-level Windows by HWND, PID, executable, title, class, or regex.
- Capture a target window's client area or the full virtual desktop.
- Mouse move/click/drag/scroll and relative mouse motion.
- Keyboard keys, bounded holds, hotkeys, and Unicode text input via Win32 `SendInput`.
- Windows UI Automation (UIA) tree inspection, semantic element search, invoke, click, focus, and value setting.
- Target identity guards (HWND + PID), foreground checks, physical-modifier preflight, persistent stop, and F8 emergency stop.
- Codex skill instructions that prefer semantic UIA actions and fall back to screenshot/coordinate interaction.

## Architecture

```text
Codex / computer-use agent
          |
     observe + plan
       /       \
 screenshot    UI Automation
       \       /
        bounded actions
             |
       WindowsBackend
             |
 Win32 SendInput / window APIs
             |
        visible desktop
```

The runtime deliberately provides two complementary paths:

1. **Semantic path** — UI Automation for standard Windows controls. This is preferred because it is less sensitive to layout and resolution.
2. **Visual/input path** — screenshots plus Win32 input for custom-drawn applications, canvases, editors, games, remote desktops, and controls that do not expose useful accessibility semantics.

## Install

Windows 10/11 with Python 3.10+:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Quick start

Discover windows instead of hard-coding a stale HWND:

```powershell
win-cu windows
win-cu windows --title-regex "Notepad|Visual Studio Code"
win-cu windows --exe notepad.exe
```

Inspect and capture a chosen target:

```powershell
win-cu status --hwnd 123456
win-cu focus --hwnd 123456
win-cu capture --hwnd 123456 --out .\screen.png
```

Perform bounded input:

```powershell
win-cu click --hwnd 123456 --x 420 --y 260
win-cu type --hwnd 123456 "Hello, 世界"
win-cu hotkey --hwnd 123456 ctrl s
win-cu scroll --hwnd 123456 --delta -480
win-cu drag --hwnd 123456 --x1 200 --y1 200 --x2 600 --y2 400 --seconds 0.8
win-cu relative --hwnd 123456 --dx 300 --dy -80 --seconds 0.4
```

Prefer UI Automation when a native semantic element is available:

```powershell
win-cu uia-tree --hwnd 123456 --depth 3
win-cu uia-find --hwnd 123456 --name "Save" --control-type Button
win-cu uia-invoke --hwnd 123456 --name "Save" --control-type Button
win-cu uia-set --hwnd 123456 --automation-id "FileNameControlHost" --value "report.txt"
```

Stop all subsequent input attempts:

```powershell
win-cu stop
```

or press **F8** while an action is being guarded. Clear a persistent stop with:

```powershell
win-cu reset-stop
```

## Agent operating model

A robust agent should use this loop:

```text
resolve target -> observe -> choose UIA or visual path -> bounded action -> observe -> verify
```

Do not equate a successful `SendInput` call with successful GUI state or successful completion of the user's goal.

See `agents/skills/windows-computer-use/SKILL.md` for the Codex-facing policy and `references/compatibility.md` for platform boundaries.

## Compatibility boundaries

No desktop input layer can honestly guarantee every Windows surface.

- Windows UIPI can prevent a non-elevated process from controlling an elevated target.
- UAC secure desktop is intentionally isolated.
- Some games use Raw Input/DirectInput or anti-cheat mechanisms and may not behave like normal desktop applications.
- UIA quality depends on the target application's accessibility implementation.
- Remote/Citrix/custom-rendered surfaces may require the screenshot/input fallback.

The runtime exposes these as capability/failure boundaries rather than silently clicking elsewhere.

## Origin

The design is inspired by `wz1119/Codex-Minecraft-Gameplay`, particularly its bounded Win32 input, target-window guarding, screenshot observation, and cleanup philosophy. This repository generalizes those ideas into an application-independent Windows computer-use layer and adds semantic UI Automation.

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
