import tornado.web
from handlers.v1.base import BaseHandler
from controllers.testingaide import TestingaideController


class TestingaideSyncHandler(BaseHandler):
    """Handler for Testingaide sync operations"""

    def _get_controller_class(self):
        return TestingaideController

    async def post(self, project_id: str) -> None:
        """Sync epics and stories to Testingaide"""
        try:
            result = self.controller.sync_epics_and_stories(int(project_id))
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(400, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
