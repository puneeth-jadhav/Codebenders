import tornado.web
from handlers.v1.base import BaseHandler
from controllers.epic import EpicController
from typing import Optional
import json


class EpicHandler(BaseHandler):
    """Handler for epic operations"""

    def _get_controller_class(self):
        return EpicController

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

    def _validate_update_data(self, data: dict) -> None:
        """Validate epic update data"""
        if "name" in data and not data["name"]:
            raise tornado.web.HTTPError(400, "Epic name cannot be empty")

    async def get(self, project_id: str, epic_id: Optional[str] = None) -> None:
        """Get epic details or all epics"""
        try:
            if epic_id:
                # Get single epic
                result = self.controller.get_epic(int(project_id), int(epic_id))
            else:
                # Get all epics
                result = self.controller.get_project_epics(int(project_id))

            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def put(self, project_id: str, epic_id: str) -> None:
        """Update epic"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            self._validate_update_data(self.json_data)

            result = self.controller.update_epic(
                int(project_id), int(epic_id), self.json_data
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")


class EpicGenerationHandler(BaseHandler):
    """Handler for epic generation"""

    def _get_controller_class(self):
        return EpicController

    async def post(self, project_id: str, feature_id: str) -> None:
        """Generate epic for a feature"""
        try:
            result = await self.controller.generate_epic(
                int(project_id), int(feature_id)
            )

            self.set_status(201)
            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
