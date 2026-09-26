from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit
import json
import os


ROOT = Path(__file__).resolve().parent
MAX_IMAGE_SIZE = 15 * 1024 * 1024


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        photo_paths = {
            "/api/home-photo": "sister-photo.jpg",
            "/api/home-photo/second": "sister-photo-2.jpg",
            "/api/home-photo/third": "sister-photo-3.jpg",
        }
        destination_name = photo_paths.get(urlsplit(self.path).path)
        if destination_name is None:
            self.send_error(404)
            return

        request_origin = urlsplit(self.headers.get("Origin", ""))
        if not request_origin.netloc or request_origin.netloc.lower() != self.headers.get("Host", "").lower():
            self.send_json(403, {"error": "The photo must be saved from this site."})
            return

        if self.headers.get_content_type() != "image/jpeg":
            self.send_json(415, {"error": "Choose a photo that can be saved as a JPEG."})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "The photo upload size is invalid."})
            return

        if content_length < 4 or content_length > MAX_IMAGE_SIZE:
            self.send_json(413, {"error": "The photo must be smaller than 15 MB."})
            return

        image_data = self.rfile.read(content_length)
        if len(image_data) != content_length or not image_data.startswith(b"\xff\xd8\xff") or not image_data.endswith(b"\xff\xd9"):
            self.send_json(400, {"error": "The uploaded file is not a valid JPEG image."})
            return

        assets_directory = ROOT / "assets"
        assets_directory.mkdir(exist_ok=True)
        destination = assets_directory / destination_name
        temporary_path = None

        try:
            with NamedTemporaryFile(dir=assets_directory, delete=False) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(image_data)
            os.replace(temporary_path, destination)
        except OSError:
            if temporary_path:
                temporary_path.unlink(missing_ok=True)
            self.send_json(500, {"error": "The photo could not be written to the project folder."})
            return

        self.send_json(200, {"saved": f"assets/{destination_name}"})

    def send_json(self, status, value):
        response = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8765), SiteHandler)
    print("Serving sister website at http://localhost:8765")
    server.serve_forever()