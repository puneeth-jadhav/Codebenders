import tornado.web
from handlers.v1.base import BaseHandler
from controllers.erd import ERDController
import json


class ERDHandler(BaseHandler):
    """Handler for ERD operations"""

    def _get_controller_class(self):
        return ERDController

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

    async def get(self, project_id: str) -> None:
        """Get current ERD"""
        try:
            result = self.controller.get_erd(int(project_id))
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def post(self, project_id: str) -> None:
        """Generate initial ERD"""
        try:
            result = await self.controller.generate_erd(int(project_id))
            self.set_status(201)
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def put(self, project_id: str) -> None:
        """Refine ERD based on feedback"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            feedback = self.json_data.get("feedback")
            if not feedback:
                raise tornado.web.HTTPError(400, "Feedback is required")

            result = await self.controller.refine_erd(int(project_id), feedback)

            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
