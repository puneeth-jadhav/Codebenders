from controllers.base import BaseController
from database.models import Epic, Feature, Project, Story
from services.epic.generator import EpicGenerator
from typing import Dict, List, Optional


class EpicController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.epic_generator = EpicGenerator()

    async def generate_epic(self, project_id: int, feature_id: int) -> Dict:
        """Generate and create epic for a feature"""
        try:
            # Get feature and verify it's finalized
            feature = (
                self.session.query(Feature)
                .filter(
                    Feature.project_id == project_id,
                    Feature.id == feature_id,
                    Feature.is_finalized == True,
                )
                .first()
            )

            if not feature:
                raise ValueError(f"Finalized feature {feature_id} not found")

            # Get project and tech stack
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Generate epic
            epic_data = self.epic_generator.generate_epic(
                feature=feature.to_dict(),
                tech_stack=project.tech_bundle_id,  # Assuming this is the tech stack ID
                requirements=project.get_content().get("project_content", ""),
            )

            # Create epic
            epic = Epic(feature_id=feature.id, name=epic_data["name"])
            self.session.add(epic)
            self.session.flush()

            # Save description to MongoDB
            epic.save_description(epic_data["description"])

            self.session.commit()

            epic_data["id"] = epic.id

            return {"message": "Epic generated successfully", "epic": epic_data}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to generate epic: {str(e)}")

    def get_epic(self, project_id: int, epic_id: int) -> Dict:
        """Get epic details"""
        try:
            epic = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Epic.id == epic_id)
                .first()
            )

            if not epic:
                raise ValueError(f"Epic {epic_id} not found")

            epic_dict = epic.to_dict()
            description = epic.get_description()
            if description:
                epic_dict["description"] = description.get("description")

            return {"epic": epic_dict}

        except Exception as e:
            raise ValueError(f"Failed to get epic: {str(e)}")

    def update_epic(self, project_id: int, epic_id: int, updates: Dict) -> Dict:
        """Update epic details"""
        try:
            epic = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Epic.id == epic_id)
                .first()
            )

            if not epic:
                raise ValueError(f"Epic {epic_id} not found")

            if "name" in updates:
                epic.name = updates["name"]

            if "description" in updates:
                epic.save_description(updates["description"])

            self.session.commit()

            epic_dict = epic.to_dict()
            description = epic.get_description()
            if description:
                epic_dict["description"] = description.get("description")

            return {"message": "Epic updated successfully", "epic": epic_dict}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to update epic: {str(e)}")

    def get_project_epics(self, project_id: int) -> Dict:
        """
        Get all epics for a project.

        Args:
            project_id (int): ID of the project

        Returns:
            Dict containing list of epics
        """
        try:
            # Get all epics for the project through Feature relationship
            epics = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id)
                .all()
            )

            epics_data = []
            for epic in epics:
                epic_dict = epic.to_dict()
                description = epic.get_description()
                if description:
                    epic_dict["description"] = description.get("description")
                epics_data.append(epic_dict)

            return {
                "message": f"Retrieved {len(epics_data)} epics",
                "epics": epics_data,
            }

        except Exception as e:
            raise ValueError(f"Failed to fetch epics: {str(e)}")

    def get_all_project_epics_and_stories(self, project_id: int) -> List[Dict]:
        """
        Get all epics and their stories for a project in Testingaide format.

        Args:
            project_id (int): ID of the project

        Returns:
            List[Dict]: Epics with their stories in Testingaide format
        """
        try:
            # Get all epics for the project
            epics = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Feature.is_finalized == True)
                .all()
            )

            formatted_epics = []

            for epic in epics:
                # Get epic details
                epic_dict = {"id": epic.id, "name": epic.name, "description": ""}

                # Get epic description from MongoDB
                epic_content = epic.get_description()
                if epic_content and "description" in epic_content:
                    epic_dict["description"] = epic_content["description"]

                # Get all stories for this epic
                stories = (
                    self.session.query(Story).filter(Story.epic_id == epic.id).all()
                )
                formatted_stories = []

                for story in stories:
                    story_dict = {
                        "id": story.id,
                        "name": story.title,
                        "description": "",
                    }

                    # Get story description from MongoDB
                    story_content = story.get_description()
                    if story_content and "description" in story_content:
                        story_dict["description"] = story_content["description"]

                    formatted_stories.append(story_dict)

                epic_dict["stories"] = formatted_stories
                formatted_epics.append(epic_dict)

            return formatted_epics

        except Exception as e:
            raise ValueError(f"Failed to get epics and stories: {str(e)}")
