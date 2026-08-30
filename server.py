import http.server
import socketserver
from pathlib import Path

PORT = 8000
REPO_DIR = Path(__file__).parent / "repo"


class RepositoryServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server():
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=str(REPO_DIR), **kwargs
    )

    with RepositoryServer(("", PORT), handler) as httpd:
        print(f"[*] Serving repository files from {REPO_DIR} on http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_server()