# Agent guidance

Use the `windows-computer-use` skill for visible Windows desktop interaction.

General policy:
1. Observe before acting. Resolve the target by HWND/PID/executable/title and capture a fresh image when visual state matters.
2. Prefer UI Automation for standard controls; use coordinate actions only when semantics are unavailable or the UI is custom drawn.
3. Keep actions bounded. Do not hold keys/buttons indefinitely and do not send long blind action chains.
4. Re-check target identity and visible state after disruptive operations.
5. Treat input success, GUI-state success, and user-goal success as different things. Verify the requested outcome.
6. If the target elevates to another integrity level, enters UAC secure desktop, or stops exposing useful UIA semantics, report the boundary instead of guessing.
