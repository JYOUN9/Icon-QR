from __future__ import annotations

import os
import threading
import webbrowser

from app import app


def open_browser(url: str) -> None:
    webbrowser.open(url, new=1)


def main() -> None:
    host = os.environ.get("ICON_QR_HOST", "127.0.0.1")
    port = int(os.environ.get("ICON_QR_PORT", "5000"))
    open_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{open_host}:{port}"

    # Start browser shortly after server boot for one-click desktop behavior.
    threading.Timer(0.8, open_browser, args=(url,)).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
