#!/usr/bin/env python3
"""Local Responses-API proxy that forwards at most one image per request."""

import http.client
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 18021
UPSTREAM_HOST = "10.8.132.76"
UPSTREAM_PORT = 18020
HOP_BY_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade", "content-length"}
IMAGE_TYPES = {"input_image", "image_url"}


def retain_last_image(request):
    """Remove all but the latest Responses/Chat image content item in-place."""
    image_slots = []

    def walk(value):
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict) and item.get("type") in IMAGE_TYPES:
                    image_slots.append((value, index))
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)

    walk(request)
    for parent, index in reversed(image_slots[:-1]):
        del parent[index]
    return len(image_slots) - 1


class Proxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, _format, *_args):
        pass

    def _forward(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        removed = 0
        if self.command == "POST" and self.path in {"/v1/responses", "/v1/chat/completions"}:
            try:
                decoded = json.loads(body)
                removed = retain_last_image(decoded)
                body = json.dumps(decoded, separators=(",", ":")).encode()
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass

        headers = {key: value for key, value in self.headers.items() if key.lower() not in HOP_BY_HOP and key.lower() != "host"}
        headers["Host"] = f"{UPSTREAM_HOST}:{UPSTREAM_PORT}"
        headers["Content-Length"] = str(len(body))
        headers["Connection"] = "close"
        connection = http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=300)
        try:
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() not in HOP_BY_HOP:
                    self.send_header(key, value)
            if removed:
                self.send_header("X-Qwen-Vision-Images-Removed", str(removed))
            self.send_header("Connection", "close")
            self.end_headers()
            while chunk := response.read(65536):
                self.wfile.write(chunk)
                self.wfile.flush()
        except (OSError, http.client.HTTPException) as error:
            self.send_error(502, f"vision proxy upstream error: {error}")
        finally:
            connection.close()

    do_GET = _forward
    do_POST = _forward
    do_DELETE = _forward


if __name__ == "__main__":
    ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Proxy).serve_forever()
