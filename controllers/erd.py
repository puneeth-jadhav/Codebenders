from controllers.base import BaseController
from database.models import Project, Feature
from services.erd.generator import ERDGenerator
from typing import Dict, Optional
import base64
import requests


class ERDController(BaseController):
    """Controller for ERD operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.erd_generator = ERDGenerator()

    def _get_project_data(self, project_id: int) -> Dict:
        """Get project data including features and tech stack"""
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        features = (
            self.session.query(Feature)
            .filter(Feature.project_id == project_id, Feature.is_finalized == True)
            .all()
        )

        tech_bundle = None
        if project.tech_bundle_id:
            from database.connection import tech_bundle_collection
            from bson.objectid import ObjectId

            tech_bundle = tech_bundle_collection.find_one(
                {"_id": ObjectId(project.tech_bundle_id)}
            )

        return {
            "project": project,
            "features": [feature.to_dict() for feature in features],
            "tech_stack": tech_bundle,
        }

    async def generate_erd(self, project_id: int) -> Dict:
        """Generate initial ERD"""
        try:
            project_data = self._get_project_data(project_id)

            mermaid_code = self.erd_generator.generate_erd(
                requirements=project_data["project"]
                .get_content()
                .get("project_content", ""),
                features=project_data["features"],
                tech_stack=project_data["tech_stack"] or {},
            )

            # Save ERD to project content
            project_data["project"].save_content(erd_schema=mermaid_code)

            return {
                "message": "ERD generated successfully",
                "erd": {
                    "mermaid_code": mermaid_code,
                    "image_url": self._generate_image_url(mermaid_code),
                },
            }

        except Exception as e:
            raise ValueError(f"Failed to generate ERD: {str(e)}")

    async def refine_erd(self, project_id: int, feedback: str) -> Dict:
        """Refine ERD based on feedback"""
        try:
            project_data = self._get_project_data(project_id)

            current_erd = project_data["project"].get_content().get("erd_schema")
            if not current_erd:
                raise ValueError("No existing ERD found to refine")

            mermaid_code = self.erd_generator.refine_erd(
                current_erd=current_erd,
                feedback=feedback,
                requirements=project_data["project"]
                .get_content()
                .get("project_content", ""),
                features=project_data["features"],
            )

            # Save refined ERD
            project_data["project"].save_content(erd_schema=mermaid_code)

            return {
                "message": "ERD refined successfully",
                "erd": {
                    "mermaid_code": mermaid_code,
                    "image_url": self._generate_image_url(mermaid_code),
                },
            }

        except Exception as e:
            raise ValueError(f"Failed to refine ERD: {str(e)}")

    def get_erd(self, project_id: int) -> Dict:
        """Get current ERD"""
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project {project_id} not found")

            content = project.get_content()
            if not content or "erd_schema" not in content:
                raise ValueError("No ERD found for this project")

            return {
                "erd": {
                    "mermaid_code": content["erd_schema"],
                    "image_url": self._generate_image_url(content["erd_schema"]),
                }
            }

        except Exception as e:
            raise ValueError(f"Failed to get ERD: {str(e)}")

    def _generate_image_url(self, mermaid_code: str) -> str:
        """Generate Mermaid.ink URL for ERD visualization"""
        graphbytes = mermaid_code.encode("utf8")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("utf8")
        return "https://mermaid.ink/svg/" + base64_string
