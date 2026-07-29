import os
import sys
import ctypes
import traceback
import faulthandler
from pathlib import Path


def _setup_error_log():
    try:
        log_dir = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        sys.stderr = open(log_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr
        faulthandler.enable(file=sys.stderr, all_threads=True)
    except Exception:
        pass

_setup_error_log()


def _log_unhandled_exception(exc_type, exc_value, exc_tb):
    try:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=sys.stderr)
    except Exception:
        pass

sys.excepthook = _log_unhandled_exception


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def _set_app_user_model_id():
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Darsono.HOTS.HostsEditor.1"
        )
    except Exception:
        pass

_set_app_user_model_id()


REG_KEY = r"Software\HOTS Hosts"
REG_VAL = "AppPasswordHash"

def _reg_get_password() -> str:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY) as k:
            val, _ = winreg.QueryValueEx(k, REG_VAL)
            return val or ""
    except Exception:
        return ""

def _reg_set_password(hash_value: str):
    try:
        import winreg
        if hash_value:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY) as k:
                winreg.SetValueEx(k, REG_VAL, 0, winreg.REG_SZ, hash_value)
        else:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY,
                                0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, REG_VAL)
    except Exception:
        pass


def _resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def _make_splash():
    from PySide6.QtWidgets import QSplashScreen, QApplication
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt

    path = _resource_path("logo1.png")
    if not os.path.exists(path):
        return None
    pix = QPixmap(path)
    if pix.isNull():
        return None

    splash = QSplashScreen(pix, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.setWindowOpacity(0.0)

    screen = QApplication.primaryScreen()
    geo = screen.availableGeometry() if screen else None
    if geo is not None:
        splash.move(geo.center().x() - pix.width() // 2,
                    geo.center().y() - pix.height() // 2)
    return splash


def _fade_splash(app, splash, start: float, end: float, duration_ms: int, steps: int = 20):
    import time
    step_delay = (duration_ms / 1000.0) / steps
    for i in range(steps + 1):
        t = i / steps
        splash.setWindowOpacity(start + (end - start) * t)
        app.processEvents()
        time.sleep(step_delay)


def main():
    try:
        _set_app_user_model_id()
        _run()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        _show_crash(tb)
        sys.exit(1)


def _run():
    password_hash = _reg_get_password()

    try:
        from .constants import load_settings
        from .i18n import set_lang
        _s = load_settings()
        set_lang(_s.get("language", "en"))
    except Exception:
        pass

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from .widgets_qt import apply_global_style, NoScrollbarContextMenuFilter

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("HOTS Hosts")
    app.setQuitOnLastWindowClosed(False)

    app._no_sb_ctx_filter = NoScrollbarContextMenuFilter(app)
    app.installEventFilter(app._no_sb_ctx_filter)

    _icon_path = _resource_path("logo.ico")
    _icon = QIcon(_icon_path) if os.path.exists(_icon_path) else QIcon()
    if not _icon.isNull():
        app.setWindowIcon(_icon)

    apply_global_style(app)

    splash = _make_splash()

    def _show_splash_fadein():
        if splash is not None:
            splash.setWindowOpacity(0.0)
            splash.show()
            app.processEvents()
            _fade_splash(app, splash, 0.0, 1.0, 350)

    def _before_show():
        if splash is not None:
            splash.close()

    if password_hash:
        from .dialogs import PasswordPromptDialog

        def _launch():
            _show_splash_fadein()

            from .app import HostsEditor
            win = HostsEditor(on_before_show=_before_show)
            if not _icon.isNull():
                win.setWindowIcon(_icon)
            app.setQuitOnLastWindowClosed(True)

        dlg = PasswordPromptDialog(None, password_hash,
                                   on_success=_launch, on_cancel=app.quit)
        dlg.show()
    else:
        _show_splash_fadein()

        from .app import HostsEditor
        win = HostsEditor(on_before_show=_before_show)
        if not _icon.isNull():
            win.setWindowIcon(_icon)
        app.setQuitOnLastWindowClosed(True)

    sys.exit(app.exec())


def _show_crash(tb: str):
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        _app = QApplication.instance() or QApplication(sys.argv)
        msg = QMessageBox()
        msg.setWindowTitle("HOTS Hosts — Startup Error")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("The program failed to start.")
        log_path = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts" / "error.log"
        msg.setInformativeText(
            f"Error details:\n{tb[:800]}\n\n"
            f"Full log: {log_path}"
        )
        msg.exec()
    except Exception:
        pass


if __name__ == "__main__":
    main()
