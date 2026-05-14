from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer

from controllers.api_controller import ApiController


ROOT = Path(__file__).resolve().parent


class TeachingHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            ApiController.handle(self)
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            ApiController.handle(self)
            return
        self.send_error(404, "Not found")


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        TCPServer.server_bind(self)
        self.server_name = self.server_address[0]
        self.server_port = self.server_address[1]


def run(host="127.0.0.1", port=8007):
    server = LocalHTTPServer((host, port), TeachingHandler)
    print(f"DB07 teaching system: http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    run()
