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
        # The launcher (.pyw) may have already opened this log, so don't reopen it.
        # faulthandler must be enabled in either case.
        if getattr(sys.stderr, "name", None) != str(log_path):
            mode = "w" if log_path.exists() and log_path.stat().st_size > 1_000_000 else "a"
            sys.stderr = open(log_path, mode, encoding="utf-8", buffering=1)
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


def _set_app_user_model_id():
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Darsono.HOTS.HostsEditor.1"
        )
    except Exception:
        pass


REG_KEY = r"Software\HOTS Hosts"
REG_VAL = "AppPasswordHash"

def _reg_get_password() -> str:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY) as k:
            val, _ = winreg.QueryValueEx(k, REG_VAL)
            if val:
                return val
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"_reg_get_password: cannot read the password hash: {e!r}", flush=True)

    return ""

def _reg_set_password(hash_value: str) -> bool:
    try:
        import winreg
        if hash_value:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY) as k:
                winreg.SetValueEx(k, REG_VAL, 0, winreg.REG_SZ, hash_value)
        else:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY,
                                0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, REG_VAL)
        return True
    except Exception:
        return False


def _resource_path(name: str) -> str:
    from .resource_utils import resource_path
    return resource_path(name)


def _make_splash():
    from PySide6.QtWidgets import QSplashScreen, QApplication
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt

    path = _resource_path("graphic/logo1.png")
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


def _fade_splash(app, splash, start: float, end: float, duration_ms: int):
    from PySide6.QtCore import QPropertyAnimation, QEventLoop

    anim = QPropertyAnimation(splash, b"windowOpacity")
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setDuration(duration_ms)

    loop = QEventLoop()
    anim.finished.connect(loop.quit)
    anim.start()
    loop.exec()


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
        from .i18n import set_lang, pick_lang
        _s = load_settings()
        set_lang(pick_lang(_s))
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

    from . import bg_tasks
    app.aboutToQuit.connect(bg_tasks.begin_shutdown_and_wait)

    app._no_sb_ctx_filter = NoScrollbarContextMenuFilter(app)
    app.installEventFilter(app._no_sb_ctx_filter)

    _icon_path = _resource_path("graphic/logo.ico")
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

    def _launch():
        _show_splash_fadein()

        from .app import HostsEditor
        win = HostsEditor(on_before_show=_before_show)
        if not _icon.isNull():
            win.setWindowIcon(_icon)
        app.setQuitOnLastWindowClosed(True)

    def _launch_after_prompt():
        try:
            _launch()
        except Exception:
            tb = traceback.format_exc()
            print(tb, flush=True)
            if splash is not None:
                splash.close()
            _show_crash(tb)
            app.exit(1)

    if password_hash:
        from .dialogs import PasswordPromptDialog
        dlg = PasswordPromptDialog(None, password_hash,
                                   on_success=_launch_after_prompt, on_cancel=app.quit)
        dlg.show()
    else:
        _launch()

    exit_code = app.exec()

    try:
        _app_instance = QApplication.instance()
        if _app_instance is not None:
            for _w in list(_app_instance.topLevelWidgets()):
                try:
                    _w.close()
                    _w.deleteLater()
                except Exception:
                    pass
            for _ in range(3):
                _app_instance.processEvents()
    except Exception:
        pass

    sys.exit(exit_code)


def _crash_texts(tb: str, log_path):
    try:
        from .constants import load_settings
        from .i18n import T, set_lang, pick_lang
        set_lang(pick_lang(load_settings()))
        return (T("startup_failed_title", app="HOTS Hosts"), T("startup_failed_msg"),
                T("startup_failed_details", details=tb[:800], path=log_path))
    except Exception:
        return ("HOTS Hosts — Startup Error", "The program failed to start.",
                f"Error details:\n{tb[:800]}\n\nFull log: {log_path}")


def _show_crash(tb: str):
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        _app = QApplication.instance() or QApplication(sys.argv)
        log_path = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts" / "error.log"
        title, text, details = _crash_texts(tb, log_path)
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setInformativeText(details)
        msg.exec()
    except Exception:
        pass


if __name__ == "__main__":
    main()
