import sys, os, traceback, ctypes
from pathlib import Path

# ---------------------------------------------------------------------------
# Tryb weryfikacji hasla wywolywany przez deinstalator (Inno Setup), ZANIM
# cokolwiek innego sie wykona - bez logowania, bez elewacji, bez ladowania
# PySide6/GUI. Ma byc szybki i nie wymagac uprawnien administratora (odczyt
# HKLM\Software\HOTS Hosts jest domyslnie dostepny do odczytu dla kazdego).
#
# Wywolanie: HostsEditor.exe --verify-uninstall-password "<sciezka_do_pliku_z_haslem>"
# Kod wyjscia: 0 = haslo poprawne (lub brak ustawionego hasla - nic nie
#              blokujemy), 1 = haslo bledne lub blad odczytu.
#
# UWAGA: klucz/wartosc rejestru ("Software\HOTS Hosts" / "AppPasswordHash")
# musza byc identyczne jak w hosts_editor/__main__.py (REG_KEY/REG_VAL) -
# jesli zmienisz jedno, zmien i drugie.
# ---------------------------------------------------------------------------
if len(sys.argv) >= 3 and sys.argv[1] == "--verify-uninstall-password":
    def _verify_uninstall_password() -> int:
        import hashlib
        import winreg

        pw_file = sys.argv[2]
        try:
            with open(pw_file, "r", encoding="utf-8") as f:
                entered = f.read()
        except Exception:
            return 1
        finally:
            try:
                os.remove(pw_file)
            except Exception:
                pass

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\HOTS Hosts") as k:
                stored_hash, _ = winreg.QueryValueEx(k, "AppPasswordHash")
        except Exception:
            stored_hash = ""

        if not stored_hash:
            return 0  # haslo nie jest ustawione - nie blokujemy

        entered_hash = hashlib.sha256(entered.encode("utf-8")).hexdigest()
        return 0 if entered_hash == stored_hash else 1

    sys.exit(_verify_uninstall_password())


log_path = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts" / "error.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
_log = open(log_path, "w", encoding="utf-8", buffering=1)
sys.stderr = _log
sys.stdout = _log

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
        # NOTE: sys.executable is unreliable in this Nuitka build (it can
        # report a non-existent "python.exe" instead of the real renamed
        # output exe) — sys.argv[0] is the actual running executable path.
        target = sys.argv[0]
        params = " ".join(f'"{a}"' for a in sys.argv[1:])
    else:
        script = os.path.abspath(__file__)
        target = sys.executable
        params = f'"{script}"'
    print(f"_relaunch_as_admin: target={target!r} params={params!r}", flush=True)
    ctypes.windll.kernel32.SetLastError(0)
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        target,
        params,
        None,
        1,
    )
    last_err = ctypes.windll.kernel32.GetLastError()
    print(f"_relaunch_as_admin: ShellExecuteW returned {ret} (GetLastError={last_err})", flush=True)
    return ret > 32

try:
    print("START", flush=True)

    if not _acquire_single_instance_lock():
        print("Program is already running — switching to existing window.", flush=True)
        if not _signal_running_instance():
            print("Event signal failed/unavailable — falling back to direct window focus.", flush=True)
            _focus_existing_instance()
        sys.exit(0)

    if not _is_admin():
        print("Not admin — relaunching with UAC...", flush=True)
        print(f"sys.executable={sys.executable!r} sys.argv={sys.argv!r} __file__={__file__!r} frozen={getattr(sys, 'frozen', False)} compiled={'__compiled__' in globals()}", flush=True)
        if _mutex_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(_mutex_handle)
            except Exception:
                pass
            _mutex_handle = None
        ok = _relaunch_as_admin()
        if ok:
            sys.exit(0)
        else:
            print("ShellExecuteW failed or was declined by the user — aborting startup.", flush=True)
            try:
                from PySide6.QtWidgets import QApplication, QMessageBox
                app = QApplication.instance() or QApplication(sys.argv)
                m = QMessageBox()
                m.setIcon(QMessageBox.Warning)
                m.setWindowTitle("HOTS Hosts")
                m.setText(
                    "HOTS Hosts requires administrator privileges to run correctly.\n\n"
                    "Startup was cancelled. Please launch the program again and accept "
                    "the User Account Control (UAC) prompt."
                )
                m.exec()
            except Exception as e2:
                print(f"messagebox failed: {e2}", flush=True)
            sys.exit(1)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    he_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosts_editor")
    print(f"hosts_editor path: {he_path}", flush=True)
    if os.path.exists(he_path):
        print(f"exists: True", flush=True)
        print(f"files: {os.listdir(he_path)}", flush=True)
    else:
        print("exists: False (package is likely bundled inside the PyInstaller archive — this is normal in --onefile mode)", flush=True)

    import PySide6
    print(f"PySide6: {PySide6.__version__}", flush=True)

    import qfluentwidgets
    print(f"qfluentwidgets OK", flush=True)

    from hosts_editor.__main__ import main
    print("main imported OK", flush=True)
    main()

except SystemExit:
    pass
except Exception:
    tb = traceback.format_exc()
    print(tb, flush=True)
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        m = QMessageBox()
        m.setWindowTitle("HOTS Hosts — Error")
        m.setText(tb[:1000])
        m.exec()
    except Exception as e2:
        print(f"messagebox failed: {e2}", flush=True)
finally:
    _log.flush()
