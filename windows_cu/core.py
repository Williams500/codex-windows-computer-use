from __future__ import annotations

import ctypes as C
from ctypes import wintypes as W
from dataclasses import dataclass, asdict
import os, re, time
from pathlib import Path
from typing import Iterable

STOP_FILE = Path(__file__).resolve().parent / ".windows-cu-stop"
MAX_HOLD_SECONDS = 5.0

class ComputerUseError(RuntimeError):
    pass

@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    pid: int
    title: str
    class_name: str
    executable: str
    foreground: bool
    minimized: bool
    visible: bool
    def json(self): return asdict(self)

class MOUSEINPUT(C.Structure):
    _fields_=[("dx",W.LONG),("dy",W.LONG),("mouseData",W.DWORD),("dwFlags",W.DWORD),("time",W.DWORD),("dwExtraInfo",C.c_size_t)]
class KEYBDINPUT(C.Structure):
    _fields_=[("wVk",W.WORD),("wScan",W.WORD),("dwFlags",W.DWORD),("time",W.DWORD),("dwExtraInfo",C.c_size_t)]
class HARDWAREINPUT(C.Structure):
    _fields_=[("uMsg",W.DWORD),("wParamL",W.WORD),("wParamH",W.WORD)]
class INPUTUNION(C.Union):
    _fields_=[("mi",MOUSEINPUT),("ki",KEYBDINPUT),("hi",HARDWAREINPUT)]
class INPUT(C.Structure):
    _anonymous_=("u",); _fields_=[("type",W.DWORD),("u",INPUTUNION)]

KEY_VK={"backspace":0x08,"tab":0x09,"enter":0x0D,"shift":0x10,"ctrl":0x11,"alt":0x12,"pause":0x13,"capslock":0x14,"esc":0x1B,"space":0x20,"pageup":0x21,"pagedown":0x22,"end":0x23,"home":0x24,"left":0x25,"up":0x26,"right":0x27,"down":0x28,"insert":0x2D,"delete":0x2E,"win":0x5B}
KEY_VK.update({chr(c).lower():c for c in range(ord("A"),ord("Z")+1)})
KEY_VK.update({str(i):0x30+i for i in range(10)})
KEY_VK.update({f"f{i}":0x6F+i for i in range(1,25)})
BUTTON_FLAGS={"left":(0x0002,0x0004),"right":(0x0008,0x0010),"middle":(0x0020,0x0040)}

class WindowsBackend:
    def __init__(self):
        if os.name!="nt": raise ComputerUseError("This runtime requires an interactive Windows desktop.")
        self.u=C.WinDLL("user32",use_last_error=True); self.k=C.WinDLL("kernel32",use_last_error=True)
        self.enum_cb=C.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM); self._bind()
        try: self.u.SetProcessDpiAwarenessContext(C.c_void_p(-4))
        except Exception:
            try: self.u.SetProcessDPIAware()
            except Exception: pass

    def _bind(self):
        specs=[(self.u,"EnumWindows",[self.enum_cb,W.LPARAM],W.BOOL),(self.u,"IsWindow",[W.HWND],W.BOOL),(self.u,"IsWindowVisible",[W.HWND],W.BOOL),(self.u,"IsIconic",[W.HWND],W.BOOL),(self.u,"GetWindowTextLengthW",[W.HWND],C.c_int),(self.u,"GetWindowTextW",[W.HWND,W.LPWSTR,C.c_int],C.c_int),(self.u,"GetClassNameW",[W.HWND,W.LPWSTR,C.c_int],C.c_int),(self.u,"GetWindowThreadProcessId",[W.HWND,C.POINTER(W.DWORD)],W.DWORD),(self.u,"GetForegroundWindow",[],W.HWND),(self.u,"SetForegroundWindow",[W.HWND],W.BOOL),(self.u,"GetAsyncKeyState",[C.c_int],C.c_short),(self.u,"SendInput",[W.UINT,C.POINTER(INPUT),C.c_int],W.UINT),(self.u,"GetClientRect",[W.HWND,C.POINTER(W.RECT)],W.BOOL),(self.u,"ClientToScreen",[W.HWND,C.POINTER(W.POINT)],W.BOOL),(self.u,"SetCursorPos",[C.c_int,C.c_int],W.BOOL),(self.k,"OpenProcess",[W.DWORD,W.BOOL,W.DWORD],W.HANDLE),(self.k,"QueryFullProcessImageNameW",[W.HANDLE,W.DWORD,W.LPWSTR,C.POINTER(W.DWORD)],W.BOOL),(self.k,"CloseHandle",[W.HANDLE],W.BOOL)]
        for lib,name,args,res in specs:
            fn=getattr(lib,name); fn.argtypes=args; fn.restype=res

    def _pid(self,hwnd:int)->int:
        p=W.DWORD(); self.u.GetWindowThreadProcessId(hwnd,C.byref(p)); return int(p.value)

    def describe(self,hwnd:int)->WindowInfo:
        if not self.u.IsWindow(hwnd): raise ComputerUseError(f"HWND {hwnd} is no longer valid.")
        n=self.u.GetWindowTextLengthW(hwnd); title=C.create_unicode_buffer(n+1); self.u.GetWindowTextW(hwnd,title,n+1)
        cls=C.create_unicode_buffer(256); self.u.GetClassNameW(hwnd,cls,len(cls)); pid=self._pid(hwnd); exe=""
        proc=self.k.OpenProcess(0x1000,False,pid)
        if proc:
            try:
                buf=C.create_unicode_buffer(32768); size=W.DWORD(32768)
                if self.k.QueryFullProcessImageNameW(proc,0,buf,C.byref(size)): exe=buf.value
            finally: self.k.CloseHandle(proc)
        return WindowInfo(int(hwnd),pid,title.value,cls.value,exe,self.u.GetForegroundWindow()==hwnd,bool(self.u.IsIconic(hwnd)),bool(self.u.IsWindowVisible(hwnd)))

    def windows(self,*,title=None,title_regex=None,exe=None,class_name=None):
        out=[]; rx=re.compile(title_regex,re.I) if title_regex else None
        def visit(hwnd,_):
            try:
                i=self.describe(int(hwnd))
                if not i.visible or not i.title:return True
                if title and title.lower() not in i.title.lower():return True
                if rx and not rx.search(i.title):return True
                if exe and Path(i.executable).name.lower()!=exe.lower():return True
                if class_name and i.class_name.lower()!=class_name.lower():return True
                out.append(i)
            except Exception: pass
            return True
        cb=self.enum_cb(visit)
        if not self.u.EnumWindows(cb,0): raise ComputerUseError("Unable to enumerate top-level windows.")
        return out

    def focus(self,t:WindowInfo):
        if t.minimized: raise ComputerUseError("Target is minimized; restore it first.")
        self.u.SetForegroundWindow(t.hwnd); deadline=time.monotonic()+0.75
        while time.monotonic()<deadline:
            if self.u.GetForegroundWindow()==t.hwnd:return
            time.sleep(.01)
        raise ComputerUseError("Windows did not grant foreground focus to target.")

    def guard(self,t:WindowInfo,*,require_foreground=True):
        if STOP_FILE.exists() or (self.u.GetAsyncKeyState(0x77)&0x8000): raise ComputerUseError("Stopped by F8 or persistent stop marker.")
        if not self.u.IsWindow(t.hwnd) or self._pid(t.hwnd)!=t.pid: raise ComputerUseError("Target identity changed or closed.")
        if self.u.IsIconic(t.hwnd): raise ComputerUseError("Target became minimized.")
        if require_foreground and self.u.GetForegroundWindow()!=t.hwnd: raise ComputerUseError("Target lost foreground focus.")

    def preflight(self,t:WindowInfo):
        self.guard(t)
        for vk in (0x10,0x11,0x12,0x5B,0x5C):
            if self.u.GetAsyncKeyState(vk)&0x8000: raise ComputerUseError("Release physical Shift/Ctrl/Alt/Win modifiers before agent input.")

    def client_to_screen(self,t:WindowInfo,x:int,y:int):
        rect=W.RECT(); p=W.POINT(x,y)
        if not self.u.GetClientRect(t.hwnd,C.byref(rect)): raise ComputerUseError("Cannot read client rectangle.")
        if not(0<=x<rect.right and 0<=y<rect.bottom): raise ValueError("Point is outside target client area.")
        if not self.u.ClientToScreen(t.hwnd,C.byref(p)): raise ComputerUseError("ClientToScreen failed.")
        return p.x,p.y

    def set_cursor_client(self,t:WindowInfo,x:int,y:int):
        sx,sy=self.client_to_screen(t,x,y); self.guard(t)
        if not self.u.SetCursorPos(sx,sy): raise ComputerUseError("SetCursorPos failed.")

    def _send(self,item:INPUT):
        C.set_last_error(0)
        if self.u.SendInput(1,C.byref(item),C.sizeof(INPUT))!=1: raise ComputerUseError(f"SendInput failed (Win32 error {C.get_last_error()}); integrity level may differ.")

    def key_event(self,key:str,down:bool):
        key=key.lower()
        if key not in KEY_VK: raise ValueError(f"Unsupported key: {key}")
        item=INPUT(type=1); item.ki=KEYBDINPUT(KEY_VK[key],0,0 if down else 0x0002,0,0); self._send(item)

    def unicode_char(self,char:str,down:bool):
        code=ord(char)
        if code>0xFFFF: raise ValueError("Send supplementary-plane characters as UTF-16 surrogate units.")
        item=INPUT(type=1); item.ki=KEYBDINPUT(0,code,0x0004|(0 if down else 0x0002),0,0); self._send(item)

    def button_event(self,button:str,down:bool):
        if button not in BUTTON_FLAGS: raise ValueError("button must be left, right, or middle")
        item=INPUT(type=0); item.mi=MOUSEINPUT(0,0,0,BUTTON_FLAGS[button][0 if down else 1],0,0); self._send(item)

    def move_relative(self,dx:int,dy:int):
        if abs(dx)>10000 or abs(dy)>10000: raise ValueError("relative mouse delta is unreasonably large")
        item=INPUT(type=0); item.mi=MOUSEINPUT(dx,dy,0,0x0001,0,0); self._send(item)

    def scroll(self,delta:int):
        item=INPUT(type=0); item.mi=MOUSEINPUT(0,0,C.c_ulong(delta).value,0x0800,0,0); self._send(item)

    def capture_client(self,t:WindowInfo):
        self.guard(t,require_foreground=False)
        from PIL import ImageGrab
        rect=W.RECT(); p=W.POINT(0,0)
        if not self.u.GetClientRect(t.hwnd,C.byref(rect)) or not self.u.ClientToScreen(t.hwnd,C.byref(p)): raise ComputerUseError("Unable to locate target client rectangle.")
        return ImageGrab.grab(bbox=(p.x,p.y,p.x+rect.right,p.y+rect.bottom),all_screens=True)

def utf16_units(text:str)->Iterable[str]:
    raw=text.encode("utf-16-le")
    for i in range(0,len(raw),2): yield chr(int.from_bytes(raw[i:i+2],"little"))
