import argparse
import os
from . import __version__


def main():
    parser = argparse.ArgumentParser(description="Agntia Cyber foundation; no scanners enabled yet")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Start the private foundation API")
    serve.add_argument("--config", required=True, help="Path to server-admin JSON, containing secret references only")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8012)
    args = parser.parse_args()
    if args.command == "serve":
        os.environ["AGNTIA_CYBER_CONFIG_FILE"] = args.config
        import uvicorn
        uvicorn.run("agntia_ciberseguridad.app:create_app", factory=True, host=args.host, port=args.port, workers=1)


if __name__ == "__main__":
    main()
