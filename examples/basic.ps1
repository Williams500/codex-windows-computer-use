# Discover a target first; do not hard-code HWND across sessions.
$wins = win-cu windows --title-regex "Notepad"
$wins

# Example after selecting a HWND:
# win-cu focus --hwnd 123456
# win-cu type --hwnd 123456 "Hello from Codex Windows Computer Use"
# win-cu hotkey --hwnd 123456 ctrl s
