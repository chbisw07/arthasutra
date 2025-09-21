from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn


def serve() -> None:
    parser = argparse.ArgumentParser(description="Run ArthaSutra API server (dev)")
    parser.add_argument("--host", default=os.getenv("ARTHASUTRA_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("ARTHASUTRA_PORT", "8000")))
    parser.add_argument(
        "--no-reload",
        dest="reload",
        action="store_false",
        help="Disable auto-reload (enabled by default)",
    )
    parser.add_argument(
        "--reload-dir",
        dest="reload_dirs",
        action="append",
        help="Additional directory to watch for reload (can be repeated)",
    )
    parser.add_argument(
        "--reload-polling",
        dest="reload_polling",
        action="store_true",
        help="Force polling reload watcher (avoids OS watch limits)",
    )
    parser.set_defaults(reload=True)
    args = parser.parse_args()

    # Limit reload watching to the package directory by default to avoid hitting OS file limits
    pkg_dir = Path(__file__).resolve().parent  # src/arthasutra
    reload_dirs = [str(pkg_dir)]
    if args.reload_dirs:
        reload_dirs.extend(args.reload_dirs)

    if args.reload and args.reload_polling:
        # Hint watchfiles to use polling backend instead of inotify/fsevents
        os.environ.setdefault("WATCHFILES_FORCE_POLLING", "true")

    uvicorn.run(
        "arthasutra.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=reload_dirs,
        reload_excludes=[".venv/*", "node_modules/*", "docs/*", "tests/*"],
    )


if __name__ == "__main__":
    serve()
