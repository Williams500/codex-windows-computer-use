# Codex Windows Computer Use

A generic Windows desktop control runtime for Codex and other computer-use agents.

It separates **observation**, **semantic UI inspection**, **input execution**, **safety guards**, and **verification** so the agent is not coupled to a particular application.

## Capabilities

- Enumerate/select arbitrary top-level Windows by HWND, PID, executable, title, class, or regex.
- Capture a target client area or the full virtual desktop.
- Mouse move/click/drag/scroll and relative motion.
- Keyboard keys, bounded holds, hotkeys, and Unicode text input through Win32 `SendInput`.
- Windows UI Automation tree inspection, semantic search, invoke/click fallback, and value setting.
- HWND+PID identity guards, foreground checks, physical-modifier preflight, persistent stop, and F8 emergency stop.
- A Codex skill that prefers semantic UIA actions and falls back to screenshot/coordinate interaction.

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

The runtime deliberately provides two complementary paths: **UI Automation** for standard controls and a **visual/input fallback** for custom-drawn applications, canvases, editors, games, remote desktops, and surfaces without useful accessibility semantics.

## Install

Windows 10/11 with Python 3.10+:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Quick start

```powershell
win-cu windows
win-cu windows --title-regex "Notepad|Visual Studio Code"
win-cu windows --exe notepad.exe

win-cu status --hwnd 123456
win-cu focus --hwnd 123456
win-cu capture --hwnd 123456 --out .\screen.png

win-cu click --hwnd 123456 --x 420 --y 260
win-cu type --hwnd 123456 "Hello, 世界"
win-cu hotkey --hwnd 123456 ctrl s
win-cu scroll --hwnd 123456 --delta -480
win-cu drag --hwnd 123456 --x1 200 --y1 200 --x2 600 --y2 400 --seconds 0.8
win-cu move-relative --hwnd 123456 --dx 300 --dy -80
```

Prefer UI Automation when a stable semantic element exists:

```powershell
win-cu uia-tree --hwnd 123456 --depth 3
win-cu uia-find --hwnd 123456 --name "Save" --control-type Button
win-cu uia-invoke --hwnd 123456 --name "Save" --control-type Button
win-cu uia-set-value --hwnd 123456 --automation-id "FileNameControlHost" --value "report.txt"
```

Emergency stop:

```powershell
win-cu stop
win-cu reset-stop
```

F8 is also checked while guarded input is running.

## Agent operating model

```text
resolve target -> observe -> choose UIA or visual path -> bounded action -> observe -> verify
```

Do not equate successful input delivery with successful GUI state or completion of the user's goal.

See `agents/skills/windows-computer-use/SKILL.md`, `agents/skills/windows-computer-use/references/commands.md`, and `agents/skills/windows-computer-use/references/compatibility.md`.

## Compatibility boundaries

No desktop input layer can honestly guarantee every Windows surface. Windows UIPI may block an unelevated runtime from controlling an elevated target; UAC secure desktop is intentionally isolated; Raw Input/DirectInput/anti-cheat applications can behave differently; UIA quality depends on each application's accessibility implementation; and remote/custom-rendered surfaces may require visual fallback.

The runtime treats these as explicit capability/failure boundaries rather than silently clicking elsewhere.

## Origin

Inspired by `wz1119/Codex-Minecraft-Gameplay` (Apache-2.0), particularly its bounded Win32 input, target-window guarding, screenshot observation, and cleanup philosophy. This repository generalizes those ideas into an application-independent Windows computer-use layer and adds semantic UI Automation.

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
