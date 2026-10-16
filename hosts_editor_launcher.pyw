import sys, os, time, traceback, ctypes, logging
from pathlib import Path


def _uninst_log(text: str) -> None:
    try:
        path = Path(os.environ.get("TEMP", Path.home())) / "hots_uninstall.log"
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass


def _uninstall_password_ok(pw_file: str) -> bool:
    # True when no password is set, or the password in pw_file matches. Fails closed on any error.
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\HOTS Hosts") as k:
            stored_hash, _ = winreg.QueryValueEx(k, "AppPasswordHash")
    except FileNotFoundError:
        return True  # no key / no value = no password set
    except Exception:
        return False

    if not stored_hash:
        return True

    try:
        with open(pw_file, "r", encoding="utf-8") as f:
            entered = f.read()
    except Exception:
        return False

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from hosts_editor.password_utils import verify_password
    except Exception:
        return False
    return verify_password(entered, stored_hash)


def _remove_quietly(path: str) -> None:
    try:
        os.remove(path)
    except Exception:
        pass


if len(sys.argv) >= 3 and sys.argv[1] == "--verify-uninstall-password":
    def _verify_uninstall_password() -> int:
        pw_file = sys.argv[2]
        try:
            return 0 if _uninstall_password_ok(pw_file) else 1
        finally:
            _remove_quietly(pw_file)

    sys.exit(_verify_uninstall_password())


# Uninstall, step 1 (shown by the uninstaller before anything is removed).
# Exit code: 0 = confirmed (choices saved), 3 = cancelled, 2 = wrong password, 1 = error.
if len(sys.argv) >= 3 and sys.argv[1] == "--uninstall-wizard":
    def _run_uninstall_wizard() -> int:
        import json

        choices_path = sys.argv[2]
        auth_path = sys.argv[3] if len(sys.argv) > 3 else ""
        if not _uninstall_password_ok(auth_path):
            return 2

        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            from PySide6.QtWidgets import QApplication, QDialog
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QIcon

            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

            from hosts_editor.constants import load_settings
            from hosts_editor.i18n import set_lang, pick_lang
            from hosts_editor.widgets_qt import apply_global_style
            from hosts_editor.resource_utils import resource_path
            from hosts_editor import uninstall_flow

            settings = load_settings()
            set_lang(pick_lang(settings))

            app = QApplication.instance() or QApplication(sys.argv)
            apply_global_style(app)
            try:
                icon_path = resource_path("graphic/logo.ico")
                if os.path.exists(icon_path):
                    app.setWindowIcon(QIcon(icon_path))
            except Exception:
                pass

            counts = {
                "antispy": uninstall_flow.count_active_antispy_items(),
                "backups": uninstall_flow.count_hosts_backups(),
                "custom_domains": uninstall_flow.custom_domains_file_exists(),
            }

            from hosts_editor.dialogs.uninstall_wizard import UninstallWizardDialog
            dlg = UninstallWizardDialog(counts=counts)
            if dlg.exec() != QDialog.Accepted or not dlg.choices:
                return 3

            with open(choices_path, "w", encoding="utf-8") as f:
                json.dump(dlg.choices, f)
            return 0
        except Exception:
            _uninst_log("[wizard] failed:\n" + traceback.format_exc())
            return 1

    sys.exit(_run_uninstall_wizard())


# Uninstall, step 2 (run by hots_uninstall_cleanup.cmd): applies the saved choices.
# Needs the password (when one is set), so it cannot be used to strip the protections by hand.
if len(sys.argv) >= 4 and sys.argv[1] == "--uninstall-apply":
    def _run_uninstall_apply() -> int:
        import json

        choices_path, result_path = sys.argv[2], sys.argv[3]
        auth_path = sys.argv[4] if len(sys.argv) > 4 else ""
        report = {"errors": [], "delete_data": False}

        try:
            if not _uninstall_password_ok(auth_path):
                report["errors"].append("password check failed")
            else:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from hosts_editor import uninstall_flow

                try:
                    with open(choices_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    choices = {k: bool(v) for k, v in data.items()} if isinstance(data, dict) else {}
                except Exception:
                    _uninst_log("[apply] cannot read choices file:\n" + traceback.format_exc())
                    choices = {}

                report = uninstall_flow.apply_uninstall_choices(choices)
        except Exception as e:
            _uninst_log("[apply] failed:\n" + traceback.format_exc())
            report.setdefault("errors", []).append(f"fatal: {e}")

        _remove_quietly(auth_path)
        try:
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(report, f)
        except Exception:
            pass

        return 0

    sys.exit(_run_uninstall_apply())


log_path = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts" / "error.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
try:
    _log_mode = "w" if log_path.stat().st_size > 250_000 else "a"
except OSError:
    _log_mode = "a"
_log = open(log_path, _log_mode, encoding="utf-8", buffering=1)
sys.stderr = _log
sys.stdout = _log


def _stamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


logging.basicConfig(stream=sys.stderr, level=logging.WARNING,
                    format="%(asctime)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def _is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def _set_app_user_model_id():
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Darsono.HOTS.HostsEditor.1"
        )
    except Exception:
        pass

_set_app_user_model_id()

def _low_integrity_security_attributes():
    try:
        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("nLength", ctypes.c_ulong),
                ("lpSecurityDescriptor", ctypes.c_void_p),
                ("bInheritHandle", ctypes.c_int),
            ]

        sddl = "D:(A;;GA;;;WD)S:(ML;;NW;;;LW)"
        p_sd = ctypes.c_void_p()
        ok = ctypes.windll.advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            ctypes.c_wchar_p(sddl), 1, ctypes.byref(p_sd), None
        )
        if not ok or not p_sd:
            return None

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
        sa.lpSecurityDescriptor = p_sd
        sa.bInheritHandle = False
        return sa
    except Exception:
        return None


_MUTEX_NAME = "Global\\HOTS_HostsEditor_SingleInstance_Mutex"
_mutex_handle = None

def _acquire_single_instance_lock() -> bool:
    global _mutex_handle
    try:
        ERROR_ALREADY_EXISTS = 183
        sa = _low_integrity_security_attributes()
        sa_arg = ctypes.byref(sa) if sa is not None else None
        _mutex_handle = ctypes.windll.kernel32.CreateMutexW(sa_arg, False, _MUTEX_NAME)
        if not _mutex_handle:
            return False
        already_running = ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS
        return not already_running
    except Exception:
        return True

def release_single_instance_lock():
    global _mutex_handle
    if _mutex_handle:
        try:
            ctypes.windll.kernel32.CloseHandle(_mutex_handle)
        except Exception:
            pass
        _mutex_handle = None


_ACTIVATE_EVENT_NAME = "Global\\HOTS_HostsEditor_ActivateEvent"

def _signal_running_instance() -> bool:
    try:
        EVENT_MODIFY_STATE = 0x0002
        SYNCHRONIZE = 0x00100000
        handle = ctypes.windll.kernel32.OpenEventW(
            EVENT_MODIFY_STATE | SYNCHRONIZE, False, _ACTIVATE_EVENT_NAME
        )
        if not handle:
            return False
        try:
            return bool(ctypes.windll.kernel32.SetEvent(handle))
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return False


def _focus_existing_instance():
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        hwnd = user32.FindWindowW(None, "HOTS Hosts")
        if not hwnd:
            return

        SW_RESTORE = 9
        SW_SHOW = 5

        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            user32.ShowWindow(hwnd, SW_SHOW)

        fg_hwnd = user32.GetForegroundWindow()
        current_tid = kernel32.GetCurrentThreadId()
        fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)

        attached_fg = False
        attached_target = False
        try:
            if fg_tid and fg_tid != current_tid:
                attached_fg = bool(user32.AttachThreadInput(current_tid, fg_tid, True))
            if target_tid and target_tid != current_tid:
                attached_target = bool(user32.AttachThreadInput(current_tid, target_tid, True))

            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        finally:
            if attached_fg:
                user32.AttachThreadInput(current_tid, fg_tid, False)
            if attached_target:
                user32.AttachThreadInput(current_tid, target_tid, False)
    except Exception:
        pass

def _relaunch_as_admin():
    is_frozen = getattr(sys, "frozen", False) or "__compiled__" in globals()
    if is_frozen:
        target = sys.argv[0]
        params = " ".join(f'"{a}"' for a in sys.argv[1:])
    else:
        script = os.path.abspath(__file__)
        target = sys.executable
        params = f'"{script}"'
    ctypes.windll.kernel32.SetLastError(0)
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        target,
        params,
        None,
        1,
    )
    if ret <= 32:
        last_err = ctypes.windll.kernel32.GetLastError()
        print(f"{_stamp()} UAC relaunch failed: ShellExecuteW={ret} GetLastError={last_err} "
              f"target={target!r} params={params!r}", flush=True)
    return ret > 32

def _tr(key: str, fallback: str, **kw) -> str:
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from hosts_editor.constants import load_settings
        from hosts_editor.i18n import T, set_lang, pick_lang
        set_lang(pick_lang(load_settings()))
        return T(key, **kw)
    except Exception:
        return fallback.format(**kw)


_exit_code = 0
try:
    if not _acquire_single_instance_lock():
        if _signal_running_instance():
            print(f"{_stamp()} already running: activated the existing window", flush=True)
        else:
            print(f"{_stamp()} already running: activation event failed, used window focus", flush=True)
            _focus_existing_instance()
        sys.exit(0)

    if not _is_admin():
        if _mutex_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(_mutex_handle)
            except Exception:
                pass
            _mutex_handle = None
        ok = _relaunch_as_admin()
        if ok:
            print(f"{_stamp()} not admin: relaunched via UAC", flush=True)
            sys.exit(0)
        else:
            print(f"{_stamp()} not admin: UAC relaunch failed or was declined, startup aborted", flush=True)
            try:
                from PySide6.QtWidgets import QApplication, QMessageBox
                app = QApplication.instance() or QApplication(sys.argv)
                m = QMessageBox()
                m.setIcon(QMessageBox.Warning)
                m.setWindowTitle("HOTS Hosts")
                m.setText(_tr(
                    "startup_admin_msg",
                    "{app} requires administrator privileges to run correctly.\n\n"
                    "Startup was cancelled. Please launch the program again and accept "
                    "the User Account Control (UAC) prompt.",
                    app="HOTS Hosts",
                ))
                m.exec()
            except Exception as e2:
                print(f"messagebox failed: {e2}", flush=True)
            sys.exit(1)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    import PySide6

    from hosts_editor.__main__ import main
    print(f"{_stamp()} started ok (admin, PySide6 {PySide6.__version__})", flush=True)
    main()

except SystemExit as _e:
    _exit_code = _e.code if isinstance(_e.code, int) else (0 if _e.code is None else 1)
except Exception:
    _exit_code = 1
    tb = traceback.format_exc()
    print(f"{_stamp()} startup error (sys.executable={sys.executable!r}, __file__={__file__!r})", flush=True)
    print(tb, flush=True)
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        m = QMessageBox()
        m.setWindowTitle(_tr("startup_error_title", "{app} — Error", app="HOTS Hosts"))
        m.setText(tb[:1000])
        m.exec()
    except Exception as e2:
        print(f"messagebox failed: {e2}", flush=True)
finally:
    _log.flush()

sys.exit(_exit_code)
