"""Entry point for running the Pick BASIC LSP server."""

from .server import server


def main():
    server.start_io()


if __name__ == "__main__":
    main()
