import tornado.web
from handlers.v1.base import BaseHandler
from controllers.prompt import PromptController
from typing import Optional
import json


class PromptHandler(BaseHandler):
    """Handler for code generation prompts"""

    def _get_controller_class(self):
        return PromptController

    async def get(self, project_id: str) -> None:
        """Get prompts for a project"""
        try:
            result = self.controller.get_prompts(int(project_id))
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def post(self, project_id: str) -> None:
        """Generate and save prompts for a project"""
        try:
            result = await self.controller.generate_and_save_prompts(int(project_id))
            self.set_status(201)
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
