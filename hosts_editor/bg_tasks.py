import threading
import time
from typing import Optional

_lock = threading.Lock()
_active_threads = []
_active_qthreads = []
_wakeups = []
_shutting_down = threading.Event()

def is_shutting_down() -> bool:
    return _shutting_down.is_set()

def start_bg_thread(target, *args, **kwargs) -> Optional[threading.Thread]:
    if _shutting_down.is_set():
        return None

    def _wrapper():
        try:
            target(*args, **kwargs)
        finally:
            with _lock:
                try:
                    _active_threads.remove(threading.current_thread())
                except ValueError:
                    pass

    t = threading.Thread(target=_wrapper, daemon=True)
    with _lock:
        _active_threads.append(t)
    t.start()
    return t

def start_bg_timer(interval, target, *args, **kwargs) -> Optional[threading.Timer]:
    if _shutting_down.is_set():
        return None

    def _wrapper():
        try:
            if is_shutting_down():
                return
            target(*args, **kwargs)
        finally:
            with _lock:
                try:
                    _active_threads.remove(t)
                except ValueError:
                    pass

    t = threading.Timer(interval, _wrapper)
    t.daemon = True
    with _lock:
        _active_threads.append(t)
    t.start()
    return t

def register_wakeup(callback) -> None:
    with _lock:
        _wakeups.append(callback)

def register_qthread(qthread) -> None:
    with _lock:
        _active_qthreads.append(qthread)

    def _unregister():
        with _lock:
            try:
                _active_qthreads.remove(qthread)
            except ValueError:
                pass

    qthread.finished.connect(_unregister)

def begin_shutdown_and_wait(total_timeout: float = 6.0,
                             qthread_timeout: float = 9.0) -> None:
    _shutting_down.set()

    with _lock:
        wakeups = list(_wakeups)
        threads = list(_active_threads)
        qthreads = list(_active_qthreads)

    for cb in wakeups:
        try:
            cb()
        except Exception:
            pass

    deadline = time.monotonic() + total_timeout
    for t in threads:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            t.join(timeout=remaining)
        except Exception:
            pass

    for qt_thread in qthreads:
        try:
            if qt_thread.isRunning():
                qt_thread.wait(int(qthread_timeout * 1000))
        except Exception:
            pass

    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            for _ in range(5):
                app.processEvents()
    except Exception:
        pass
