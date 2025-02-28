import tornado.web
from handlers.v1.base import BaseHandler
from controllers.data_model import DataModelController


class DataModelItemHandler(BaseHandler):

    def _get_controller_class(self):
        return DataModelController

    def post(self, project_id):
        """Triggers database generation for a given project."""
        try:
            print(f"Starting DB generation for project ID: {project_id}")
            self.controller.generate_db(project_id)
            self.write({"message": "Database generation started successfully."})
        except Exception as e:
            print(f"Error generating database for project {project_id}: {e}")
            self.set_status(500)
            self.write({"error": "Failed to generate database."})

    def get(self, project_id):
        """Retrieves metadata of tables for a given project."""
        try:
            print(f"Fetching table metadata for project ID: {project_id}")
            metadata = self.controller.get_models(project_id)
            self.write(metadata)
        except Exception as e:
            print(f"Error fetching models for project {project_id}: {e}")
            self.set_status(500)
            self.write({"error": "Failed to retrieve metadata."})


class DataModelCollectionHandler(BaseHandler):

    def _get_controller_class(self):
        return DataModelController

    def post(self):
        """Handles the creation of new data models (Not implemented)."""
        self.set_status(501)
        self.write({"error": "POST /data_models not implemented."})

    def get(self):
        """Fetches metadata for all tables across projects."""
        try:
            print("Fetching metadata for all tables.")
            metadata = self.controller.get_many()
            self.write(metadata)
        except Exception as e:
            print(f"Error fetching all table metadata: {e}")
            self.set_status(500)
            self.write({"error": "Failed to retrieve metadata."})