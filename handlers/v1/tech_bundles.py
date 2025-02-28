import tornado.web
from handlers.v1.base import BaseHandler
from controllers.tech_bundle import TechBundleController
from typing import Optional
import json


class TechBundleHandler(BaseHandler):
    """Handler for tech bundle operations"""

    def _get_controller_class(self):
        return TechBundleController

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

    def _validate_bundle_selection(self, data: dict) -> None:
        """Validate tech bundle selection data"""
        if not data.get("tech_bundle_id"):
            raise tornado.web.HTTPError(400, "tech_bundle_id is required")

        if not isinstance(data["tech_bundle_id"], str):
            raise tornado.web.HTTPError(400, "tech_bundle_id must be a string")

    async def get(self, project_id: Optional[str] = None) -> None:
        """
        Get tech bundles.
        If project_id is provided, get the project's selected bundle.
        Otherwise, get all available bundles.
        """
        try:
            if project_id:
                result = self.controller.get_project_bundle(int(project_id))
            else:
                result = self.controller.get_all_bundles()

            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def post(self, project_id: str) -> None:
        """Select a tech bundle for a project"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            self._validate_bundle_selection(self.json_data)

            result = self.controller.select_bundle_for_project(
                int(project_id), self.json_data["tech_bundle_id"]
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
