from __future__ import annotations

import argparse, json, sys
from pathlib import Path
from .core import ComputerUseError, STOP_FILE, WindowsBackend
from . import actions, uia


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def selector_args(p):
    p.add_argument("--name"); p.add_argument("--automation-id"); p.add_argument("--control-type"); p.add_argument("--contains", action="store_true")


def selector(ns):
    return dict(name=ns.name, automation_id=ns.automation_id, control_type=ns.control_type, contains=ns.contains)


def parser():
    p=argparse.ArgumentParser(prog="win-cu", description="Generic Windows computer-use CLI")
    s=p.add_subparsers(dest="cmd", required=True)
    w=s.add_parser("windows"); w.add_argument("--title"); w.add_argument("--title-regex"); w.add_argument("--exe"); w.add_argument("--class-name")
    for name in ("status","focus"):
        q=s.add_parser(name); q.add_argument("--hwnd", type=int, required=True)
    c=s.add_parser("capture"); c.add_argument("--hwnd", type=int); c.add_argument("--out", required=True); c.add_argument("--desktop", action="store_true")
    for name in ("click","move"):
        q=s.add_parser(name); q.add_argument("--hwnd", type=int, required=True); q.add_argument("--x",type=int,required=True);q.add_argument("--y",type=int,required=True)
        if name=="click": q.add_argument("--button",default="left",choices=["left","right","middle"])
    q=s.add_parser("drag"); q.add_argument("--hwnd",type=int,required=True);q.add_argument("--x1",type=int,required=True);q.add_argument("--y1",type=int,required=True);q.add_argument("--x2",type=int,required=True);q.add_argument("--y2",type=int,required=True);q.add_argument("--seconds",type=float,default=.4);q.add_argument("--button",default="left")
    q=s.add_parser("scroll");q.add_argument("--hwnd",type=int,required=True);q.add_argument("--delta",type=int,required=True);q.add_argument("--x",type=int);q.add_argument("--y",type=int)
    q=s.add_parser("move-relative");q.add_argument("--hwnd",type=int,required=True);q.add_argument("--dx",type=int,required=True);q.add_argument("--dy",type=int,required=True)
    q=s.add_parser("key");q.add_argument("--hwnd",type=int,required=True);q.add_argument("key");q.add_argument("--seconds",type=float,default=.05)
    q=s.add_parser("hotkey");q.add_argument("--hwnd",type=int,required=True);q.add_argument("keys",nargs="+")
    q=s.add_parser("type");q.add_argument("--hwnd",type=int,required=True);q.add_argument("text");q.add_argument("--interval",type=float,default=.002)
    q=s.add_parser("uia-tree");q.add_argument("--hwnd",type=int,required=True);q.add_argument("--depth",type=int,default=3)
    q=s.add_parser("uia-find");q.add_argument("--hwnd",type=int,required=True);selector_args(q)
    q=s.add_parser("uia-invoke");q.add_argument("--hwnd",type=int,required=True);selector_args(q)
    q=s.add_parser("uia-set-value");q.add_argument("--hwnd",type=int,required=True);q.add_argument("--value",required=True);selector_args(q)
    s.add_parser("stop");s.add_parser("reset-stop")
    return p


def main(argv=None):
    ns=parser().parse_args(argv)
    try:
        if ns.cmd=="stop": STOP_FILE.touch(); emit({"stopped":True}); return 0
        if ns.cmd=="reset-stop":
            if STOP_FILE.exists(): STOP_FILE.unlink()
            emit({"stopped":False}); return 0
        if ns.cmd=="capture" and ns.desktop:
            from PIL import ImageGrab
            im=ImageGrab.grab(all_screens=True); out=str(Path(ns.out).resolve()); im.save(out); emit({"path":out,"image_size":list(im.size),"scope":"desktop"}); return 0
        b=WindowsBackend()
        if ns.cmd=="windows": emit([x.json() for x in b.windows(title=ns.title,title_regex=ns.title_regex,exe=ns.exe,class_name=ns.class_name)]); return 0
        t=b.describe(ns.hwnd)
        if ns.cmd=="status": emit(t.json())
        elif ns.cmd=="focus": emit(actions.focus(b,t))
        elif ns.cmd=="capture":
            im=b.capture_client(t); out=str(Path(ns.out).resolve()); im.save(out); emit({"path":out,"image_size":list(im.size),"target":t.json()})
        elif ns.cmd=="click": emit(actions.click(b,t,ns.x,ns.y,ns.button))
        elif ns.cmd=="move": emit(actions.move(b,t,ns.x,ns.y))
        elif ns.cmd=="drag": emit(actions.drag(b,t,ns.x1,ns.y1,ns.x2,ns.y2,ns.seconds,ns.button))
        elif ns.cmd=="scroll": emit(actions.scroll(b,t,ns.delta,ns.x,ns.y))
        elif ns.cmd=="move-relative": emit(actions.move_relative(b,t,ns.dx,ns.dy))
        elif ns.cmd=="key": emit(actions.key(b,t,ns.key,ns.seconds))
        elif ns.cmd=="hotkey": emit(actions.hotkey(b,t,ns.keys))
        elif ns.cmd=="type": emit(actions.type_text(b,t,ns.text,ns.interval))
        elif ns.cmd=="uia-tree": emit(uia.tree(ns.hwnd,ns.depth))
        elif ns.cmd=="uia-find": emit([d for _,d in uia.find(ns.hwnd,**selector(ns))])
        elif ns.cmd=="uia-invoke": emit(uia.invoke(ns.hwnd,**selector(ns)))
        elif ns.cmd=="uia-set-value": emit(uia.set_value(ns.hwnd,ns.value,**selector(ns)))
        return 0
    except (ComputerUseError, ValueError, OSError) as exc:
        print(json.dumps({"error":str(exc)},ensure_ascii=False),file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
