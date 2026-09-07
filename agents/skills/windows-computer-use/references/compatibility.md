# Compatibility model

| UI type | Preferred path | Notes |
|---|---|---|
| Win32/WPF/UWP standard controls | UI Automation | Most semantic and robust |
| Chromium/Electron accessibility tree | UIA first, visual fallback | Accessibility exposure varies |
| Office/Explorer/Settings | UIA + keyboard | Usually strong coverage |
| Terminal/editor canvas | keyboard + visual/UIA mix | Text surface semantics vary |
| Browser web page | browser accessibility/UIA where exposed, otherwise visual | Native browser chrome is usually easier than page canvas |
| Games/custom GPU canvas | visual + SendInput | UIA may be empty |
| Remote Desktop/Citrix | visual + SendInput | Remote app elements usually not local UIA elements |
| Elevated app from unelevated runtime | unsupported by default | Run at matching integrity only when user intentionally chooses it |
| UAC secure desktop | unsupported | Intentional Windows security boundary |
