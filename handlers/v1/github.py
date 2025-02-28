import os
from handlers.v1.base import BaseHandler
import requests
import json
from datetime import datetime
from controllers.github import GitHubController

class GitHubDeploymentsHandler(BaseHandler):
    def _get_controller_class(self):
        return GitHubController

    def get(self, project_id, action=None, extra_param=None):
        """
        GET /api/v1/projects/{project_id}/github - Fetch GitHub Actions deployments (UNCHANGED)
        GET /api/v1/projects/{project_id}/github/secrets - Fetch GitHub repository secrets (NEW)
        """
        try:
            if action == "secrets":
                # New functionality for fetching secrets
                result = self.controller.fetch_repo_secrets()
            else:
                # Original functionality for fetching actions - unchanged
                result = self.controller.fetch_actions()
            self.write(json.dumps(result))
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e), "status": "failed"})

    def post(self, project_id, action=None, extra_param=None):
        """
        POST /api/v1/projects/{project_id}/github - Push specific folders to GitHub (UNCHANGED)
            Request body: {"folders": ["frontend_folder_name", "backend_folder_name"]}

        POST /api/v1/projects/{project_id}/github/secrets - Create or update a GitHub secret (NEW)
            Request body: {"name": "SECRET_NAME", "value": "secret_value"}

        POST /api/v1/projects/{project_id}/github/test-credentials - Test GitHub credentials
            Request body: {"username": "github_username", "token": "github_token"}
        """
        try:
            data = json.loads(self.request.body)

            if action == "secrets":
                # New functionality for creating/updating secrets
                if not data.get("name") or not data.get("value"):
                    self.set_status(400)
                    self.write({"error": "Secret name and value are required", "status": "failed"})
                    return

                result = self.controller.create_or_update_secret(data.get("name"), data.get("value"))
            elif action == "test-credentials":
                if not data.get("username") or not data.get("token"):
                    self.set_status(400)
                    self.write({"error": "GitHub username and token are required", "status": "failed"})
                    return

                result = self.controller.test_github_credentials(data.get("username"), data.get("token"))
            else:
                # Original functionality for pushing code - unchanged
                result = self.controller.push_code_github(data)

            self.write(result)
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e), "status": "failed"})

    def delete(self, project_id, action=None, extra_param=None):
        """
        DELETE /api/v1/projects/{project_id}/github/secrets/{secret_name} - Delete a GitHub secret (NEW)
        """
        try:
            if action != "secrets" or not extra_param:
                self.set_status(405)  # Method Not Allowed
                self.write({"error": "Method not allowed", "status": "failed"})
                return

            result = self.controller.delete_secret(extra_param)  # extra_param contains the secret_name
            self.write(result)
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e), "status": "failed"})