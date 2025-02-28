from controllers.base import BaseController
from database.models import Project
from typing import List, Optional, Dict, Union
from services.testingaide.client import TestingaideClient


class ProjectController(BaseController):
    """Controller for handling Project-related operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testingaide = TestingaideClient()

    def create(
        self, name: str, description: Optional[str] = None
    ) -> Dict[str, Union[str, dict]]:
        """
        Creates a new project with the given name and description.

        Args:
            name (str): Name of the project
            description (str, optional): Project description or file content

        Returns:
            Dict containing project information and success message

        Raises:
            ValueError: If project creation fails
        """
        try:
            # Create new project instance
            project = Project(name=name, description=description)

            # Add to session
            self.session.add(project)

            # Get ID without committing
            self.session.flush()

            # Create project in Testingaide
            try:
                testingaide_result = self.testingaide.create_project(
                    name=name, description=description, codebenders_id=project.id
                )

                # Store the Testingaide project ID
                project.save_content(
                    testingaide_project_id=testingaide_result["testingaide_project_id"]
                )

            except ValueError as e:
                # Log the error but don't fail the project creation
                print(f"Warning: Failed to create Testingaide project: {str(e)}")

            # Commit changes
            self.session.commit()

            # Prepare response data
            project_data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }

            # Add Testingaide project ID to response
            content = project.get_content()
            if content and "testingaide_project_id" in content:
                project_data["testingaide_project_id"] = content[
                    "testingaide_project_id"
                ]

            return {"message": "Project created successfully.", "project": project_data}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to create project: {str(e)}")

    def get(self, project_id: int) -> Dict[str, Union[str, dict]]:
        """
        Returns a single project by ID.

        Args:
            project_id (int): ID of the project to retrieve

        Returns:
            Dict containing project information

        Raises:
            ValueError: If project not found
        """
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            project_data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "tech_bundle_id": project.tech_bundle_id,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }

            content = project.get_content() or {}

            if content:
                project_data["erd_schema"] = content.get("erd_schema", "")
                project_data["step1"] = content.get("step1", {})
                project_data["step2"] = content.get("step2", {})
                project_data["step3"] = content.get("step3", {})
                project_data["step4"] = content.get("step4", {})
                project_data["project_content"] = content.get("project_content", "")
                project_data["document_url"] = content.get("document_url", "")
                project_data["document_type"] = content.get("document_type", "")

            return {
                "message": "Project retrieved successfully.",
                "project": project_data,
            }

        except Exception as e:
            raise ValueError(str(e))

    def get_many(self) -> Dict[str, Union[str, List[dict]]]:
        """
        Returns list of all projects.

        Returns:
            Dict containing list of projects
        """
        try:
            projects = self.session.query(Project).all()
            projects_data = [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "tech_bundle_id": project.tech_bundle_id,
                    "created_at": project.created_at.isoformat(),
                    "updated_at": project.updated_at.isoformat(),
                }
                for project in projects
            ]

            return {
                "message": "Projects retrieved successfully.",
                "projects": projects_data,
            }

        except Exception as e:
            raise ValueError(str(e))

    def delete(self, project_id: int) -> Dict[str, str]:
        """
        Deletes a single project.

        Args:
            project_id (int): ID of the project to delete

        Returns:
            Dict containing success message

        Raises:
            ValueError: If project not found or deletion fails
        """
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            self.session.delete(project)
            self.session.commit()

            return {"message": f"Project {project_id} deleted successfully."}

        except Exception as e:
            self.session.rollback()
            raise ValueError(str(e))

    def delete_many(self, project_ids: List[int]) -> Dict[str, str]:
        """
        Deletes multiple projects.

        Args:
            project_ids (List[int]): List of project IDs to delete

        Returns:
            Dict containing success message

        Raises:
            ValueError: If any project not found or deletion fails
        """
        try:
            deleted = (
                self.session.query(Project)
                .filter(Project.id.in_(project_ids))
                .delete(synchronize_session=False)
            )
            self.session.commit()

            return {"message": f"{deleted} projects deleted successfully."}

        except Exception as e:
            self.session.rollback()
            raise ValueError(str(e))

    def update(self, project_id: int, updates: dict) -> Dict[str, Union[str, dict]]:
        """
        Updates a project with the given data.
        """
        try:
            # Get the project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            # Update SQL fields if provided
            sql_updated = False
            if "name" in updates:
                project.name = updates["name"]
                sql_updated = True
            if "description" in updates:
                project.description = updates["description"]
                sql_updated = True

            # Handle MongoDB updates
            mongo_fields = [
                "step1",
                "step2",
                "step3",
                "step4",
                "erd_schema",
                "project_content",
                "document_url",
                "document_type",
            ]
            mongo_updates = {}

            # Get existing content to preserve non-updated fields
            existing_content = project.get_content() or {}

            if not existing_content:
                sql_updated = True

            # Flag to track if project_content is updated
            project_content_updated = False
            new_project_content = None

            # Update content from document if provided
            if "project_content" in updates:
                mongo_updates["project_content"] = updates["project_content"]
                project_content_updated = True
                new_project_content = updates["project_content"]

                if "document_url" in updates:
                    mongo_updates["document_url"] = updates["document_url"]
                if "document_type" in updates:
                    mongo_updates["document_type"] = updates["document_type"]

                # Clear existing steps if new document is uploaded
                for step in ["step1", "step2", "step3", "step4"]:
                    mongo_updates[step] = {}
            else:
                # Handle regular step updates
                for field in mongo_fields:
                    if field in updates:
                        mongo_updates[field] = updates[field]
                        if field == "project_content":
                            project_content_updated = True
                            new_project_content = updates[field]
                    elif field in existing_content:
                        mongo_updates[field] = existing_content[field]

            # Only update MongoDB if there are content updates
            if mongo_updates:
                mongo_content_id = project.save_content(**mongo_updates)

                # Ensure the mongo_content_id is saved in SQL
                if project.mongo_content_id != mongo_content_id:
                    project.mongo_content_id = mongo_content_id
                    sql_updated = True

            # Commit SQL changes if any
            if sql_updated:
                self.session.commit()

            # If project content was updated and we have a Testingaide project ID,
            # create/update the requirements document in Testingaide
            if project_content_updated and new_project_content:
                try:
                    testingaide_project_id = None
                    if (
                        existing_content
                        and "testingaide_project_id" in existing_content
                    ):
                        testingaide_project_id = existing_content[
                            "testingaide_project_id"
                        ]

                    if testingaide_project_id:
                        testingaide_result = (
                            self.testingaide.create_requirement_document(
                                project_id=testingaide_project_id,
                                content=new_project_content,
                            )
                        )

                        # Store the document ID from Testingaide
                        if "document_id" in testingaide_result:
                            project.save_content(
                                testingaide_document_id=testingaide_result[
                                    "document_id"
                                ]
                            )

                except ValueError as e:
                    # Log the error but don't fail the update
                    print(
                        f"Warning: Failed to update Testingaide requirement: {str(e)}"
                    )

            # Get complete updated project data
            project_data = project.to_dict()
            project_data["created_at"] = project.created_at.isoformat()
            project_data["updated_at"] = project.updated_at.isoformat()

            # Get MongoDB content
            mongo_content = project.get_content()
            if mongo_content:
                # Extract relevant fields for the response
                content_data = {
                    field: mongo_content.get(field)
                    for field in mongo_fields
                    if field in mongo_content and mongo_content.get(field) is not None
                }
                project_data["content"] = content_data

            return {"message": "Project updated successfully.", "project": project_data}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to update project: {str(e)}")
