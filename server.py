import http.server
import socketserver
import os

PORT = 8000
REPO_DIR = os.path.join(os.path.dirname(__file__), "repo")

class RepositoryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=REPO_DIR, **kwargs)

def start_server():
    if not os.path.exists(REPO_DIR):
        os.makedirs(os.path.join(REPO_DIR, "packages"))
        print(f"[0] Created repository directory structure at: {REPO_DIR}")
        print("[0] Add your index.json and tarball files there.")

    with socketserver.TCPServer(("", PORT), RepositoryHandler) as httpd:
        print(f"[*] Forge Repository Server running at http://localhost:{PORT}")
        print("[*] Serving files from: ./repo/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[0] Server stopped.")

if __name__ == "__main__":
    start_server()