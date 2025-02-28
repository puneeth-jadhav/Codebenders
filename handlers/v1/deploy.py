import os
import tornado
from handlers.v1.base import BaseHandler
from controllers.deployment import DeployCredentialsController , DevOpsAgentController
from typing import Optional
import json
from utils.deploy_utils import broadcast_log,LogWebSocketHandler
from http import HTTPStatus
from controllers.deployment import DeploymentProjectController

class DeployMetadataHandler(BaseHandler):

    def _get_controller_class(self):
        return DeploymentProjectController

    def post(self, project_id):
        #working 
        """Create or update deployment metadata"""
        try:
            data = tornado.escape.json_decode(self.request.body)
            # project_id = int(data.get("project_id")) 
            
            if not data or not project_id:
                self.set_status(400)
                self.write({"error": "Missing required field"})
                return

            result = self.controller.save_metadata(project_id, data)
            if result:
                self.write( result)
            else:
                self.set_status(404)
                self.write({"error": "Project not found"})

        except ValueError:
            self.set_status(400)
            self.write({"error": "Invalid project_id format"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

    def get(self,project_id):
        """Fetch deployment metadata for a specific project"""
        # project_id = self.get_argument("project_id", None)
        try:
            if project_id:
                metadata = self.controller.get_metadata(project_id)
                if metadata:
                    self.write(metadata)
                else:
                    self.set_status(HTTPStatus.NOT_FOUND)
                    self.write({"error": "No metadata found"})
            else:
                self.set_status(HTTPStatus.BAD_REQUEST)
                self.write({"error": "Missing project_id"})
        except Exception as e:
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.write({"error": str(e)})

    def put(self, project_id):
        """Update entire metadata for a specific project"""
        try:
            project_id = int(project_id)  # Ensure it's an integer
            data = json.loads(self.request.body)
            metadata = data.get("metadata")

            if not metadata:
                self.set_status(400)
                self.write({"error": "Missing metadata field"})
                return

            success = self.controller.update_metadata(project_id, metadata)
            if success:
                self.write({"message": "Metadata updated successfully"})
            else:
                self.set_status(404)
                self.write({"error": "Project not found"})

        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
    
    def delete(self, project_id):
        """Delete the project metadata"""
        project_id = int(project_id)
        result = self.controller.delete_metadata(project_id)
        if result:
            self.write(result)

class DeploymentHandler(BaseHandler):
    def _get_controller_class(self):
        return DevOpsAgentController

    def post(self,project_id):
        """Main endpoint to invoke the DevOps agent"""
        try:
            broadcast_log("Starting the Devops Agent Execution")
            # Initialize the agent graph and state
            graph = self.controller.create_devops_agent()
            initial_state = self.controller.get_initial_state()
            
            # Run the DevOps agent
            output = graph.invoke(initial_state)
            result = {"success": True, "message": "Successfully Generated DockerFile and Git WorkFlows"}
            # Broadcast log upon success
            broadcast_log("DevOps Agent Execution Completed Successfully!")
            # Ensure the result is JSON serializable
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result, default=str))
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e), "status": "failed"})
            broadcast_log(f"DevOps Agent Execution Failed: {str(e)}")

    def get(self):
        pass 


class DeployCredentialsHandler(BaseHandler):
    """Handler for deployment credentials operations using project_id."""

    def _get_controller_class(self):
        return DeployCredentialsController

    def post(self, project_id):
        """Create deployment credentials."""
        body = self._request_body()
        if not body or not body.get("project_name") or not body.get("credentials"):
            self.set_status(400)
            self.finish({"message": "Invalid request"})
            return

        project_name = body["project_name"]
        credentials = body["credentials"]

        success = self.controller.create_credentials(int(project_id), project_name, credentials)
        if not success:
            self.set_status(500)
            self.finish({"message": "Failed to save credentials"})
            return

        self.finish({"success":success,"message": "Credentials saved successfully"})

    def get(self, project_id):
        """Retrieve credentials using project_id."""
        cred_type = self.get_argument("cred_type", None)

        credentials = self.controller.get_credentials(int(project_id), cred_type)
        if not credentials:
            self.finish({"success": False,"message": "Credentials not found"})
            return

        self.finish({"success": True, "credentials": credentials})

    def put(self, project_id):
        """Update specific credentials using project_id."""
        body = self._request_body()

        if not body or not body.get("cred_type") or not body.get("cred_data"):
            self.set_status(400)
            self.finish({"message": "Invalid request"})
            return

        cred_type = body["cred_type"]
        cred_data = body["cred_data"]

        updated = self.controller.update_credentials(int(project_id), cred_type, cred_data)

        if not updated:
            self.set_status(500)
            self.finish({"message": "Failed to update credentials"})
            return

        self.finish({"message": "Credentials updated successfully"})

    def delete(self, project_id):
        """Delete credentials using project_id."""
        deleted = self.controller.delete_credentials(int(project_id))

        if not deleted:
            self.set_status(500)
            self.finish({"message": "Failed to delete credentials"})
            return

        self.finish({"message": "Credentials deleted successfully"})



class DeploymentCollectionHandler(BaseHandler):

    def post(self):
        pass 

    def get(self):
        pass