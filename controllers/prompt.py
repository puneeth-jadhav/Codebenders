from bson import ObjectId
from controllers.base import BaseController
from database.models import Project
from services.prompt.generator import PromptGenerator
from typing import Dict, Optional
from database.connection import tech_bundle_collection


class PromptController(BaseController):
    """Controller for managing code generation prompts"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator = PromptGenerator()

    async def generate_and_save_prompts(self, project_id: int) -> Dict:
        """Generate and save prompts for a project"""
        try:
            # Get project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )

            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get required data
            content = project.get_content()
            if not content:
                raise ValueError("Project content not found")

            requirement_document = content.get("project_content", "")
            erd_schema = content.get("erd_schema", "")
            selected_features = [
                f.to_dict() for f in project.features if f.is_finalized
            ]
            theme = project.get_theme() or {}

            # Get tech stack
            tech_bundle = None
            if project.tech_bundle_id:
                tech_bundle = tech_bundle_collection.find_one(
                    {"_id": ObjectId(project.tech_bundle_id)}
                )

            if not tech_bundle:
                raise ValueError("Tech stack not selected for project")

            # Generate API specification first
            apis = await self.generator.generate_api_specification(
                requirement_document=requirement_document,
                selected_features=selected_features,
                erd=erd_schema,
            )

            # Save APIs to project content
            project.save_content(apis=apis)

            # Generate implementation prompts
            backend_prompt = self.generator.generate_backend_prompt(
                requirement_document=requirement_document,
                selected_features=selected_features,
                tech_stack=tech_bundle,
                erd=erd_schema,
                apis=apis,
            )

            frontend_prompt = self.generator.generate_frontend_prompt(
                requirement_document=requirement_document,
                selected_features=selected_features,
                tech_stack=tech_bundle,
                theme=theme,
                apis=apis,
            )

            project.save_prompts(frontend_prompt, backend_prompt, apis)
            self.session.commit()

            return {
                "message": "Prompts generated and saved successfully",
                "prompts": project.get_prompts(),
            }

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to generate prompts: {str(e)}")

    def get_prompts(self, project_id: int) -> Dict:
        """Get saved prompts for a project"""
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )

            if not project:
                raise ValueError(f"Project {project_id} not found")

            prompts = project.get_prompts()
            if not prompts:
                raise ValueError("No prompts found for this project")

            return {"prompts": prompts}

        except Exception as e:
            raise ValueError(f"Failed to get prompts: {str(e)}")
