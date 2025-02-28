import tornado.web
from handlers.v1.base import BaseHandler
from controllers.codegen import CodeGenController
import json

class CodeGenHandler(BaseHandler):

    def _get_controller_class(self):
        return CodeGenController

    async def get(self):
        self.write("Hello, world")

    async def post(self, project_id):
        body = self._request_body()
        response = self.controller.start_flow(project_id)

        self.write(json.dumps(response))
        self.set_status(response.get('code', 200))




