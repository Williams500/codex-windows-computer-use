# Command reference

All commands emit JSON.

```text
win-cu windows [--title TEXT] [--title-regex REGEX] [--exe NAME] [--class-name NAME]
win-cu status --hwnd HWND
win-cu focus --hwnd HWND
win-cu capture [--hwnd HWND] --out FILE [--desktop]
win-cu click --hwnd HWND --x X --y Y [--button left|right|middle]
win-cu move --hwnd HWND --x X --y Y
win-cu drag --hwnd HWND --x1 X --y1 Y --x2 X --y2 Y [--seconds S]
win-cu scroll --hwnd HWND --delta N [--x X --y Y]
win-cu key --hwnd HWND KEY [--seconds S]
win-cu hotkey --hwnd HWND KEY [KEY ...]
win-cu type --hwnd HWND TEXT
win-cu uia-tree --hwnd HWND [--depth N]
win-cu uia-find --hwnd HWND [--name TEXT] [--automation-id ID] [--control-type TYPE] [--contains]
win-cu uia-invoke --hwnd HWND [selector options]
win-cu uia-set-value --hwnd HWND --value TEXT [selector options]
win-cu stop
win-cu reset-stop
```

Coordinates for target-window actions are **client-area pixels**. This keeps actions stable when the window moves on screen.
