from controllers.base import BaseController
import os
import subprocess
from config.settings import PROJECTS_PATH

class FileController(BaseController):

    def read_directory(self, dir_path, project_id, base_path=''):
            if not dir_path:
                dir_path = PROJECTS_PATH + '/' + str(project_id)
            if not os.path.exists(dir_path):
                return []

            files_list = []
            for item in os.listdir(dir_path):
                full_path = os.path.join(dir_path, item)
                relative_path = os.path.join(base_path, item) if base_path else item

                if os.path.isdir(full_path):
                    files_list.append({
                        'name': item,
                        'type': 'folder',
                        'expanded': False,
                        'path': relative_path,
                        'children': self.read_directory(full_path, relative_path)
                    })
                else:
                    try:
                        with open(full_path, 'r') as file:
                            content = file.read()
                        files_list.append({
                            'name': item,
                            'type': 'file',
                            'path': relative_path,
                            'content': content
                        })
                    except Exception as e:
                        print(f"Error reading file {item}: {str(e)}")
                        files_list.append({
                            'name': item,
                            'type': 'file',
                            'path': relative_path,
                            'content': f"Error reading file: {str(e)}"
                        })

            return files_list


    def execute_command(self, command, project_id):

        working_dir = PROJECTS_PATH + '/' + str(project_id)
        if not os.path.exists(working_dir):
            response = {
                    'output': working_dir,
                    'error': ''
                }
            return response

        if command.strip() == 'pwd':
                response = {
                    'output': working_dir,
                    'error': ''
                }
                return response

        # Execute command in the specified directory
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()
        response = {
            'output': stdout,
            'error': stderr,
            'cwd': working_dir  # Send current directory back
        }

        return response