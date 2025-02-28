from handlers.v1.base import BaseHandler
from controllers.codegen import CodeGenController

class BackendGenerationHandler(BaseHandler):

    def post(self):
        body = self._request_body()

        if not body or not body.get('project_id') or not body.get('backend_prompt') or not body.get('base_path'):
            self.set_status(400)
            self.finish()
            return
        
        project_id = body.get('project_id')
        backend_prompt = body.get('backend_prompt')
        base_path = body.get('base_path')

        self.controller.start_flow(project_id, backend_prompt, base_path)