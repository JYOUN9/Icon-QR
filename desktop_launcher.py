from __future__ import annotations

import os
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path


def open_browser(url: str) -> None:
    webbrowser.open(url, new=1)


def runtime_root_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def write_startup_error_log(exc: BaseException) -> None:
    log_path = runtime_root_dir() / "iconqr_startup_error.log"
    try:
        with log_path.open("w", encoding="utf-8") as fp:
            fp.write("Icon QR startup error\n")
            fp.write("=" * 60 + "\n")
            fp.write(f"python_executable={sys.executable}\n")
            fp.write(f"python_version={sys.version}\n")
            fp.write(f"cwd={os.getcwd()}\n")
            fp.write("-" * 60 + "\n")
            fp.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    except OSError:
        pass


def heartbeat_watchdog(
    get_heartbeat_state_fn,
    stale_seconds: float = 6.0,
    startup_wait_seconds: float = 300.0,
    poll_interval_seconds: float = 1.0,
) -> None:
    started_at = time.monotonic()
    while True:
        seen, age = get_heartbeat_state_fn()
        if seen and age > stale_seconds:
            os._exit(0)

        if not seen and (time.monotonic() - started_at) > startup_wait_seconds:
            os._exit(0)

        time.sleep(poll_interval_seconds)


def main() -> None:
    try:
        from app import app, get_heartbeat_state

        host = os.environ.get("ICON_QR_HOST", "127.0.0.1")
        port = int(os.environ.get("ICON_QR_PORT", "5000"))
        open_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
        url = f"http://{open_host}:{port}"

        watchdog_thread = threading.Thread(
            target=heartbeat_watchdog,
            args=(get_heartbeat_state,),
            daemon=True,
        )
        watchdog_thread.start()

        # Start browser shortly after server boot for one-click desktop behavior.
        threading.Timer(0.8, open_browser, args=(url,)).start()
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as exc:
        write_startup_error_log(exc)
        raise


if __name__ == "__main__":
    main()
