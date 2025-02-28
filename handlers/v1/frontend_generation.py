from handlers.v1.base import BaseHandler
from controllers.codegen import CodeGenController

class FrontendGenerationHandler(BaseHandler):

    def post(self):
        body = self._request_body()

        if not body or not body.get('project_id') or not body.get('frontend_prompt') or not body.get('base_path'):
            self.set_status(400)
            self.finish()
            return
        
        project_id = body.get('project_id')
        frontend_prompt = body.get('frontend_prompt')
        base_path = body.get('base_path')

        self.controller.start_flow(project_id, frontend_prompt, base_path)