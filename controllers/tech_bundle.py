from controllers.base import BaseController
from database.models import Project
from database.connection import tech_bundle_collection
from bson.objectid import ObjectId  # type: ignore
from typing import Dict, List, Optional


class TechBundleController(BaseController):
    """Controller for handling TechBundle operations"""

    def get_all_bundles(self) -> List[Dict]:
        """
        Retrieve all available tech bundles.

        Returns:
            List of tech bundles
        """
        try:
            bundles = list(tech_bundle_collection.find())
            # Convert ObjectId to string for JSON serialization
            for bundle in bundles:
                bundle["_id"] = str(bundle["_id"])
            return {"tech_bundles": bundles}
        except Exception as e:
            raise ValueError(f"Failed to fetch tech bundles: {str(e)}")

    def get_bundle(self, bundle_id: str) -> Dict:
        """
        Retrieve a specific tech bundle.

        Args:
            bundle_id (str): Tech bundle ID

        Returns:
            Tech bundle details
        """
        try:
            bundle = tech_bundle_collection.find_one({"_id": ObjectId(bundle_id)})
            if not bundle:
                raise ValueError(f"Tech bundle {bundle_id} not found")

            bundle["_id"] = str(bundle["_id"])
            return {"tech_bundle": bundle}
        except Exception as e:
            raise ValueError(f"Failed to fetch tech bundle: {str(e)}")

    def select_bundle_for_project(self, project_id: int, bundle_id: str) -> Dict:
        """
        Select a tech bundle for a project.

        Args:
            project_id (int): Project ID
            bundle_id (str): Tech bundle ID

        Returns:
            Updated project information
        """
        try:
            # Verify tech bundle exists
            bundle = tech_bundle_collection.find_one({"_id": ObjectId(bundle_id)})
            if not bundle:
                raise ValueError(f"Tech bundle {bundle_id} not found")

            # Get project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Update project's tech bundle
            project.tech_bundle_id = bundle_id
            self.session.commit()

            # Prepare response
            bundle["_id"] = str(bundle["_id"])
            return {
                "message": "Tech bundle selected successfully",
                "project_id": project_id,
                "tech_bundle": bundle,
            }

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to select tech bundle: {str(e)}")

    def get_project_bundle(self, project_id: int) -> Optional[Dict]:
        """
        Get the selected tech bundle for a project.

        Args:
            project_id (int): Project ID

        Returns:
            Selected tech bundle details or None if not selected
        """
        try:
            # Get project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project {project_id} not found")

            if not project.tech_bundle_id:
                return {
                    "message": "No tech bundle selected for this project",
                    "project_id": project_id,
                    "tech_bundle": None,
                }

            # Get tech bundle
            bundle = tech_bundle_collection.find_one(
                {"_id": ObjectId(project.tech_bundle_id)}
            )
            if bundle:
                bundle["_id"] = str(bundle["_id"])

            return {"project_id": project_id, "tech_bundle": bundle}

        except Exception as e:
            raise ValueError(f"Failed to fetch project's tech bundle: {str(e)}")
