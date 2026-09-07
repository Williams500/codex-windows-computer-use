from __future__ import annotations

import time
from .core import ComputerUseError, MAX_HOLD_SECONDS, WindowInfo, WindowsBackend, utf16_units


def _ensure(seconds: float):
    if not 0.01 <= seconds <= MAX_HOLD_SECONDS:
        raise ValueError(f"hold duration must be between 0.01 and {MAX_HOLD_SECONDS} seconds")


def focus(b: WindowsBackend, t: WindowInfo):
    b.focus(t)
    return {"focused": True, "target": t.json()}


def click(b: WindowsBackend, t: WindowInfo, x: int, y: int, button="left"):
    b.focus(t); b.preflight(t); b.set_cursor_client(t, x, y); b.guard(t)
    b.button_event(button, True)
    try:
        time.sleep(0.04)
    finally:
        b.button_event(button, False)
    return {"clicked": [x, y], "button": button}


def move(b: WindowsBackend, t: WindowInfo, x: int, y: int):
    b.focus(t); b.preflight(t); b.set_cursor_client(t, x, y)
    return {"moved": [x, y]}


def drag(b: WindowsBackend, t: WindowInfo, x1: int, y1: int, x2: int, y2: int, seconds=.4, button="left"):
    _ensure(seconds); b.focus(t); b.preflight(t); b.set_cursor_client(t, x1, y1); b.button_event(button, True)
    try:
        steps = max(2, int(seconds / .015))
        for i in range(1, steps + 1):
            b.guard(t)
            x = round(x1 + (x2 - x1) * i / steps); y = round(y1 + (y2 - y1) * i / steps)
            b.set_cursor_client(t, x, y)
            time.sleep(seconds / steps)
    finally:
        b.button_event(button, False)
    return {"dragged": [x1, y1, x2, y2], "button": button}


def scroll(b: WindowsBackend, t: WindowInfo, delta: int, x=None, y=None):
    b.focus(t); b.preflight(t)
    if x is not None or y is not None:
        if x is None or y is None: raise ValueError("x and y must be supplied together")
        b.set_cursor_client(t, x, y)
    b.guard(t); b.scroll(delta)
    return {"scroll_delta": delta}


def key(b: WindowsBackend, t: WindowInfo, name: str, seconds=.05):
    _ensure(seconds); b.focus(t); b.preflight(t); b.key_event(name, True)
    try:
        time.sleep(seconds)
    finally:
        b.key_event(name, False)
    return {"key": name, "seconds": seconds}


def hotkey(b: WindowsBackend, t: WindowInfo, keys: list[str]):
    if not keys: raise ValueError("hotkey requires at least one key")
    b.focus(t); b.preflight(t); pressed=[]
    try:
        for k in keys:
            b.guard(t); b.key_event(k, True); pressed.append(k); time.sleep(.015)
        time.sleep(.04)
    finally:
        for k in reversed(pressed):
            try: b.key_event(k, False)
            except Exception: pass
    return {"hotkey": keys}


def type_text(b: WindowsBackend, t: WindowInfo, text: str, interval=.002):
    b.focus(t); b.preflight(t)
    for unit in utf16_units(text):
        b.guard(t)
        b.unicode_char(unit, True); b.unicode_char(unit, False)
        if interval: time.sleep(interval)
    return {"typed_chars": len(text)}


def move_relative(b: WindowsBackend, t: WindowInfo, dx: int, dy: int):
    b.focus(t); b.preflight(t); b.move_relative(dx, dy)
    return {"mouse_delta": [dx, dy]}
