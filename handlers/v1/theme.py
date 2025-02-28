import tornado.web
from handlers.v1.base import BaseHandler
from controllers.theme import ThemeController
import json
from typing import Optional
from constants import Fonts


class ThemeHandler(BaseHandler):
    """Handler for theme operations"""

    def _get_controller_class(self):
        return ThemeController

    def prepare(self) -> None:
        """Prepare the request"""
        super().prepare()
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                self.json_data = json.loads(self.request.body)
            except json.JSONDecodeError:
                raise tornado.web.HTTPError(400, "Invalid JSON in request body")
        else:
            self.json_data = None

    def _validate_theme_data(self, data: dict) -> None:
        """Validate theme data"""
        required_colors = [
            "primary_color",
            "background_color",
            "secondary_background_color",
            "text_color",
        ]

        for color in required_colors:
            if color in data and not isinstance(data[color], str):
                raise tornado.web.HTTPError(400, f"{color} must be a string")

        if "font" in data and data["font"] not in Fonts.CHOICES:
            raise tornado.web.HTTPError(400, "Invalid font choice")

    async def get(self, project_id: str) -> None:
        """Get project theme"""
        try:
            result = self.controller.get_theme(int(project_id))
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def put(self, project_id: str) -> None:
        """Update project theme"""
        try:
            theme_data = {}
            logo_file = None

            # Handle multipart/form-data with logo
            if self.request.files:
                if "logo" in self.request.files:
                    logo_file = self.request.files["logo"][0]

                # Get other fields from form data
                for field in [
                    "primary_color",
                    "background_color",
                    "secondary_background_color",
                    "text_color",
                    "font",
                ]:
                    if field in self.request.arguments:
                        theme_data[field] = self.request.arguments[field][0].decode(
                            "utf-8"
                        )

            # Handle JSON data
            elif self.json_data:
                self._validate_theme_data(self.json_data)
                theme_data = self.json_data
            else:
                raise tornado.web.HTTPError(400, "Invalid request format")

            result = self.controller.update_theme(
                int(project_id), theme_data, logo_file
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
