from __future__ import annotations

import argparse
import os

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
    parser.set_defaults(reload=True)
    args = parser.parse_args()

    uvicorn.run(
        "arthasutra.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    serve()

