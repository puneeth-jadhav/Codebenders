import tornado.ioloop
import tornado.web
import os
import json
import subprocess
from handlers.v1.base import BaseHandler
from controllers.filesystem import FileController

class FileSystemHandler(BaseHandler):
    def _get_controller_class(self):
        return FileController


    def get(self, project_id):
        # project_dir = '/home/oshuvardhan/Work/Office_Work/aicode'  # Replace with your folder path
        project_dir = '/home/anas/Coding/codegen/New_codebenders/rest_api_server/services'

        try:
            file_structure = self.controller.read_directory(None, project_id)
            print("file_structure", len(file_structure))
            self.write(json.dumps(file_structure))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({'error': str(e)}))

class CommandExecuteHandler(BaseHandler):

    def _get_controller_class(self):
        return FileController

    def post(self, project_id):
        try:
            command_data = json.loads(self.request.body)
            command = command_data.get('command', '')
            # Get current working directory if the command is 'pwd'
            response = self.controller.execute_command(command, project_id)
            self.write(json.dumps(response))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({'error': str(e)}))