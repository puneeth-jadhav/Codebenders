from datetime import datetime
import os
import tornado.web
from handlers.v1.base import BaseHandler
from controllers.project import ProjectController
import json
from typing import Optional, Any


class ProjectItemHandler(BaseHandler):
    """Handler for single project operations"""

    def _get_controller_class(self):
        return ProjectController

    def _get_file_extension(self, filename: str) -> str:
        """Get the file extension from filename"""
        return os.path.splitext(filename)[1].lower()

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx"}
        return self._get_file_extension(filename) in ALLOWED_EXTENSIONS

    def _save_uploaded_file(self, file_data) -> tuple[str, str]:
        """
        Save uploaded file and return the file path and type.

        Returns:
            tuple: (file_path, file_type)
        """
        filename = file_data["filename"]
        if not self._is_allowed_file(filename):
            raise tornado.web.HTTPError(
                400, f"File type not allowed. Allowed types: pdf, txt, doc, docx"
            )

        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"

        # Ensure upload directory exists
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_data["body"])

        # Get file type without the dot
        file_type = self._get_file_extension(filename)[1:]

        return file_path, file_type

    def prepare(self) -> None:
        """Prepare the request"""
        super().prepare()
        content_type = self.request.headers.get("Content-Type", "")

        # Handle JSON data
        if content_type.startswith("application/json"):
            try:
                self.json_data = json.loads(self.request.body)
            except json.JSONDecodeError:
                raise tornado.web.HTTPError(400, "Invalid JSON in request body.")
        # Handle multipart/form-data
        elif content_type.startswith("multipart/form-data"):
            self.json_data = None
            # File data will be available in self.request.files
            # Form fields will be available in self.request.arguments
        else:
            self.json_data = None

    async def get(self, project_id: str) -> None:
        """Returns a single project"""
        try:
            result = self.controller.get(int(project_id))
            self.write(json.dumps(result))
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def delete(self, project_id: str) -> None:
        """Deletes a single project"""
        try:
            result = self.controller.delete(int(project_id))
            self.write(json.dumps(result))
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    def _validate_update_data(self, data: dict) -> None:
        """
        Validate project update data

        Args:
            data (dict): The project data to validate

        Raises:
            HTTPError: If validation fails
        """
        # Validate SQL fields
        if "name" in data:
            if not data["name"]:
                raise tornado.web.HTTPError(400, "Project name cannot be empty.")
            if len(data["name"]) > 100:
                raise tornado.web.HTTPError(
                    400, "Project name must be less than 100 characters."
                )

        if "description" in data:
            if data["description"] and len(data["description"]) > 2048:
                raise tornado.web.HTTPError(
                    400, "Project description must be less than 2048 characters."
                )

        # Validate content fields are strings if provided
        content_fields = ["step1", "step2", "step3", "step4", "erd_schema"]
        for field in content_fields:
            if field in data and not isinstance(data[field], str):
                raise tornado.web.HTTPError(400, f"{field} must be a string.")

    def process_file_content(self, file_path: str, file_type: str) -> str:
        """Process the uploaded file and extract content"""
        try:
            from langchain_community.document_loaders import (
                PyPDFLoader,
                TextLoader,
                Docx2txtLoader,
            )

            if file_type == "pdf":
                loader = PyPDFLoader(file_path)
                pages = loader.load_and_split()
                return "\n".join([page.page_content for page in pages])

            elif file_type == "txt":
                loader = TextLoader(file_path)
                documents = loader.load()
                return "\n".join([doc.page_content for doc in documents])

            elif file_type in ["doc", "docx"]:
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                return "\n".join([doc.page_content for doc in documents])

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    async def put(self, project_id: str) -> None:
        """
        Updates a project. Handles both JSON updates and file uploads.
        """
        try:
            updates = {}
            # Handle file upload
            if self.request.files and "document" in self.request.files:
                file_data = self.request.files["document"][0]

                # Save file and get path and type
                file_path, file_type = self._save_uploaded_file(file_data)

                try:
                    # Process file content
                    content = self.process_file_content(file_path, file_type)

                    # Add file-related updates
                    updates.update(
                        {
                            "project_content": content,
                            "document_url": file_path,
                            "document_type": file_type,
                        }
                    )

                finally:
                    # Optionally remove the file after processing
                    # os.remove(file_path)
                    pass

                # Add any form fields if provided
                for field in ["name", "description"]:
                    if field in self.request.arguments:
                        updates[field] = self.request.arguments[field][0].decode(
                            "utf-8"
                        )

            # Handle JSON updates
            elif self.json_data:
                self._validate_update_data(self.json_data)
                updates = self.json_data

                # If project_content is provided in JSON, set empty document fields
            if "project_content" in updates:
                updates.update({"document_url": "", "document_type": ""})
            # else:
            #     raise tornado.web.HTTPError(
            #         400, "Request must contain either JSON data or file upload."
            #     )

            # Ensure at least one valid field is being updated
            valid_fields = [
                "name",
                "description",
                "step1",
                "step2",
                "step3",
                "step4",
                "erd_schema",
                "project_content",
                "document_url",
                "document_type",
            ]

            if not any(field in updates for field in valid_fields):
                raise tornado.web.HTTPError(
                    400, "At least one valid field must be provided for update."
                )

            # Update project using controller
            result = self.controller.update(project_id=int(project_id), updates=updates)

            # Send response
            self.write(json.dumps(result))

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")


class ProjectCollectionHandler(BaseHandler):
    """Handler for multiple project operations"""

    def _get_controller_class(self):
        return ProjectController

    async def get(self) -> None:
        """Returns list of projects"""
        try:
            projects = self.controller.get_many()
            self.write(json.dumps(projects))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    def prepare(self) -> None:
        """Prepare the request"""
        super().prepare()
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                self.json_data = json.loads(self.request.body)
            except json.JSONDecodeError:
                raise tornado.web.HTTPError(400, "Invalid JSON in request body.")
        else:
            self.json_data = None

    def _validate_project_data(self, data: dict) -> None:
        """
        Validate project data

        Args:
            data (dict): The project data to validate

        Raises:
            HTTPError: If validation fails
        """
        if not data.get("name"):
            raise tornado.web.HTTPError(400, "Project name is required.")

        if len(data["name"]) > 100:
            raise tornado.web.HTTPError(
                400, "Project name must be less than 100 characters."
            )

        if (
            "description" in data
            and data["description"]
            and len(data["description"]) > 2048
        ):
            raise tornado.web.HTTPError(
                400, "Project description must be less than 2048 characters."
            )

    async def post(self) -> None:
        """
        Creates a new project

        Request body should be JSON with the following structure:
        {
            "name": "Project Name",
            "description": "Project Description" (optional)
        }
        """
        try:
            # Ensure we have JSON data
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON.")

            # Validate the data
            self._validate_project_data(self.json_data)

            # Create project using controller
            result = self.controller.create(
                name=self.json_data["name"],
                description=self.json_data.get("description"),
            )

            # Set status and send response
            self.set_status(201)
            self.write(json.dumps(result))

        except ValueError as e:
            raise tornado.web.HTTPError(400, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def delete(self) -> None:
        """Deletes multiple projects"""
        try:
            if not self.json_data or not isinstance(
                self.json_data.get("project_ids"), list
            ):
                raise tornado.web.HTTPError(
                    400, "Request must include project_ids list."
                )

            project_ids = self.json_data["project_ids"]
            if not all(isinstance(pid, int) for pid in project_ids):
                raise tornado.web.HTTPError(400, "All project IDs must be integers.")

            result = self.controller.delete_many(project_ids)
            self.write(json.dumps(result))

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
