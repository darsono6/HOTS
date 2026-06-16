"""
Application entry point.
Run with: pythonw -m hosts_editor
Or as an .exe built by PyInstaller.
"""

import os
import sys
import ctypes
import platform

# ── Hide console window + DPI-awareness ───────────────────────────────────
if platform.system() == "Windows":
    try:
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ── Windows registry: read/write password hash ────────────────────────────
REG_KEY = r"Software\HOTS"
REG_VAL = "AppPasswordHash"

def _reg_get_password() -> str:
    """Reads password hash from registry. Returns '' if not set."""
    if platform.system() != "Windows":
        return ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY) as k:
            val, _ = winreg.QueryValueEx(k, REG_VAL)
            return val or ""
    except Exception:
        return ""

def _reg_set_password(hash_value: str):
    """Saves password hash to registry. Empty string removes the value."""
    if platform.system() != "Windows":
        return
    try:
        import winreg
        if hash_value:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY) as k:
                winreg.SetValueEx(k, REG_VAL, 0, winreg.REG_SZ, hash_value)
        else:
            # Remove value when password is disabled
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY,
                                0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, REG_VAL)
    except Exception:
        pass


# ── UAC auto-elevation ─────────────────────────────────────────────────────
def ensure_admin():
    system = platform.system()
    if system == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False
        if not is_admin:
            extra = " ".join(f'"{a}"' for a in sys.argv[1:])
            if getattr(sys, "frozen", False):
                params = extra if extra else ""
            else:
                script = os.path.abspath(sys.argv[0])
                params = f'"{script}"' + (f" {extra}" if extra else "")
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1)
            if ret > 32:
                sys.exit(0)
    elif system in ("Linux", "Darwin"):
        if os.geteuid() != 0:
            try:
                os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
            except Exception:
                pass


def main():
    ensure_admin()

    password_hash = _reg_get_password()

    # ── Load language before opening any window ────────────────────────────
    try:
        from .constants import load_settings
        from .i18n import set_lang
        _s = load_settings()
        set_lang(_s.get("language", "en"))
    except Exception:
        pass

    if password_hash:
        # ── Password set: verify first, then open main window ──────────────
        import tkinter as tk
        from .widgets import apply_dark_style, _restore_icon
        from .constants import DARK
        from .dialogs import PasswordPromptDialog

        root = tk.Tk()
        root.overrideredirect(True)
        root.configure(bg=DARK["bg"])
        root.geometry("0x0+0+0")
        apply_dark_style(root)
        root.title("HOTS")
        _restore_icon(root)

        def _launch():
            root.destroy()
            from .app import HostsEditor
            app = HostsEditor()
            app.mainloop()

        def _abort():
            root.destroy()
            sys.exit(0)

        PasswordPromptDialog(root, password_hash, on_success=_launch, on_cancel=_abort)
        root.mainloop()
    else:
        # ── No password: launch normally ───────────────────────────────────
        from .app import HostsEditor
        from .widgets import _restore_icon
        app = HostsEditor()
        app.title("HOTS")
        _restore_icon(app)
        app.mainloop()


if __name__ == "__main__":
    main()
