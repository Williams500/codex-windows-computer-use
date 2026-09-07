from __future__ import annotations

from .core import ComputerUseError


def _root(hwnd: int):
    try:
        from pywinauto import Desktop
        return Desktop(backend="uia").window(handle=hwnd)
    except Exception as exc:
        raise ComputerUseError(f"UI Automation connection failed: {exc}") from exc


def node_dict(w):
    try: info = w.element_info
    except Exception: info = None
    return {
        "name": getattr(info, "name", "") if info else "",
        "automation_id": getattr(info, "automation_id", "") if info else "",
        "control_type": getattr(info, "control_type", "") if info else "",
        "class_name": getattr(info, "class_name", "") if info else "",
        "rectangle": list(w.rectangle()) if hasattr(w, "rectangle") else None,
        "enabled": bool(w.is_enabled()) if hasattr(w, "is_enabled") else None,
        "visible": bool(w.is_visible()) if hasattr(w, "is_visible") else None,
    }


def tree(hwnd: int, depth=3):
    root = _root(hwnd)
    def walk(w, d):
        item = node_dict(w)
        if d > 0:
            try: item["children"] = [walk(c, d-1) for c in w.children()]
            except Exception: item["children"] = []
        return item
    return walk(root, depth)


def find(hwnd: int, *, name=None, automation_id=None, control_type=None, contains=False):
    root = _root(hwnd)
    out=[]
    try: descendants = root.descendants()
    except Exception as exc: raise ComputerUseError(f"Unable to enumerate UIA descendants: {exc}") from exc
    for w in descendants:
        d=node_dict(w)
        if name:
            lhs=(d["name"] or "").lower(); rhs=name.lower()
            if (rhs not in lhs) if contains else (lhs != rhs): continue
        if automation_id and d["automation_id"] != automation_id: continue
        if control_type and (d["control_type"] or "").lower() != control_type.lower(): continue
        out.append((w,d))
    return out


def one(hwnd: int, **selector):
    matches=find(hwnd, **selector)
    if len(matches) != 1:
        raise ComputerUseError(f"Expected exactly one UIA element; found {len(matches)}")
    return matches[0]


def invoke(hwnd: int, **selector):
    w,d=one(hwnd, **selector)
    try:
        w.invoke()
    except Exception:
        try: w.click_input()
        except Exception as exc: raise ComputerUseError(f"Element cannot be invoked/clicked: {exc}") from exc
    return d


def set_value(hwnd: int, value: str, **selector):
    w,d=one(hwnd, **selector)
    try:
        w.set_edit_text(value)
    except Exception:
        try:
            w.set_focus(); w.type_keys("^a", set_foreground=True); w.type_keys(value, with_spaces=True)
        except Exception as exc: raise ComputerUseError(f"Element value cannot be set: {exc}") from exc
    return d
