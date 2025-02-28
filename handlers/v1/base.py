import tornado.web
import json
from json.decoder import JSONDecodeError
from utils.json_encoder import json_dumps
from typing import Any, Optional, List


class DefaultHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")
        self.set_status(404)
        self.finish(
            json.dumps(
                {
                    "error": {
                        "status_code": 404,
                        "error_code": "Problem",
                        "reason": self._reason,
                        "params": [],
                    }
                }
            )
        )


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with CORS support"""

    def initialize(self):
        self._controller = None

    def set_default_headers(self):
        """Set default headers for CORS support"""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        )
        self.set_header("Access-Control-Max-Age", "3600")
        self.set_header("Content-Type", "application/json")

    def options(self, *args, **kwargs):
        """Handle OPTIONS requests for CORS preflight"""
        # Set CORS headers
        self.set_status(204)  # No Content
        self.finish()

    def raise405(self):
        """Handle method not allowed"""
        self.set_status(405)
        self.set_header("Content-Type", "application/json")
        self.finish(json_dumps({"error": "Method not allowed", "status": 405}))

    def get(self, *args, **kwargs):
        self.raise405()

    def post(self, *args, **kwargs):
        self.raise405()

    def delete(self, *args, **kwargs):
        self.raise405()

    def patch(self, *args, **kwargs):
        self.raise405()

    def put(self, *args, **kwargs):
        self.raise405()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()()
        return self._controller

    def _request_body(self):
        """Parse JSON request body"""
        try:
            return json.loads(self.request.body.decode("utf-8"))
        except JSONDecodeError:
            raise tornado.web.HTTPError(400, "Invalid JSON")

    def write_json(self, obj: Any) -> None:
        """
        Write JSON response with proper datetime handling.

        Args:
            obj (Any): Any JSON-serializable object
        """
        self.set_header("Content-Type", "application/json")
        self.write(json_dumps(obj))
