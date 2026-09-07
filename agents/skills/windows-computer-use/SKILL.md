---
name: windows-computer-use
description: Operate arbitrary visible Windows desktop applications using screenshots, Windows UI Automation, and bounded keyboard/mouse input. Use for local Windows GUI tasks across browsers, editors, Explorer, settings, office applications, terminals, and custom-drawn applications.
license: Apache-2.0
---

# Windows computer use

Use the `win-cu` CLI from this repository. Resolve paths relative to the repository root.

## Operating loop

1. **Resolve target**: call `win-cu windows` and select by stable HWND/PID/executable where possible.
2. **Observe**: capture the target. For standard Windows controls also inspect `uia-tree` or `uia-find`.
3. **Plan one bounded milestone**: prefer semantic UIA invoke/value operations; otherwise use client-relative mouse and keyboard actions.
4. **Act**: use `focus`, `click`, `drag`, `scroll`, `key`, `hotkey`, `type`, `uia-invoke`, or `uia-set-value`.
5. **Verify**: capture/inspect again and verify the user's requested state, not merely successful input delivery.
6. **Recover**: if target identity, focus, dialog state, layout, or assumptions change, discard stale coordinates and re-observe.

## Selection rules

Prefer `--hwnd` after discovering a window because titles can change. A command using HWND revalidates that the handle still belongs to the expected live window.

Do not automate hidden/background controls by guessing coordinates. Bring the target to foreground before SendInput-based actions.

## Semantic versus visual control

Prefer UIA when a stable element exists:

```powershell
win-cu uia-find --hwnd 1234 --name "Save" --control-type Button
win-cu uia-invoke --hwnd 1234 --name "Save" --control-type Button
```

Use screenshots/client coordinates for canvas, games, remote desktops, rendered web content without accessible semantics, or custom controls.

## Safety

- `win-cu stop` creates a persistent emergency-stop marker checked before input.
- Do not act while physical Ctrl/Alt/Shift/Win modifiers are held unless they are part of the requested hotkey.
- Input commands verify HWND/PID identity and foreground ownership.
- Key/button holds are bounded and released in `finally` cleanup.
- Do not attempt to interact with secure-desktop/UAC prompts or bypass privilege boundaries.

See `references/commands.md` for CLI examples and `references/compatibility.md` for platform boundaries.
