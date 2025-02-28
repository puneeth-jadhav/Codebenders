from controllers.base import BaseController
from database.models import Story, Epic, Feature, Project
from services.story.generator import StoryGenerator
from database.connection import tech_bundle_collection
from bson.objectid import ObjectId  # type: ignore
from typing import Dict, List


class StoryController(BaseController):
    """Controller for handling Story operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.story_generator = StoryGenerator()

    async def generate_stories(self, project_id: int, epic_id: int) -> Dict:
        """Generate stories for an epic"""
        try:
            # Get epic and verify it exists
            epic = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Epic.id == epic_id)
                .first()
            )

            if not epic:
                raise ValueError(f"Epic {epic_id} not found in project {project_id}")

            # Get epic description from MongoDB
            epic_content = epic.get_description()
            if not epic_content or "description" not in epic_content:
                raise ValueError("Epic description not found")

            epic_data = epic.to_dict()
            epic_data["description"] = epic_content["description"]

            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get tech stack info
            tech_bundle = None
            if project.tech_bundle_id:
                tech_bundle = tech_bundle_collection.find_one(
                    {"_id": ObjectId(project.tech_bundle_id)}
                )

            # Generate stories
            stories_data = await self.story_generator.generate_stories(
                epic=epic_data,
                tech_stack=tech_bundle["name"] if tech_bundle else "Not specified",
                requirements=project.get_content().get("project_content", ""),
            )

            # Create stories in database
            created_stories = []
            for story_data in stories_data:
                story = Story(epic_id=epic.id, title=story_data["title"])
                self.session.add(story)
                self.session.flush()

                # Save description
                story.save_description(story_data["description"])

                # Prepare story data for response
                story_dict = story.to_dict()
                story_dict["description"] = story_data["description"]
                created_stories.append(story_dict)

            self.session.commit()

            return {
                "message": f"{len(created_stories)} stories generated successfully",
                "stories": created_stories,
            }

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to generate stories: {str(e)}")

    def create_story(self, project_id: int, epic_id: int, story_data: Dict) -> Dict:
        """
        Create a new story manually.

        Args:
            project_id (int): ID of the project
            epic_id (int): ID of the epic
            story_data (Dict): Story data including description

        Returns:
            Dict containing created story
        """
        try:
            # Verify epic exists and belongs to project
            epic = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Epic.id == epic_id)
                .first()
            )

            if not epic:
                raise ValueError(f"Epic {epic_id} not found in project {project_id}")

            # Validate required fields
            if "title" not in story_data:
                raise ValueError("Story title is required")

            # Create story
            story = Story(epic_id=epic.id, title=story_data["title"])  # Add title
            self.session.add(story)
            self.session.flush()

            # Save description
            if "description" in story_data:
                story.save_description(story_data["description"])

            self.session.commit()

            # Prepare response
            story_dict = story.to_dict()
            description = story.get_description()
            if description:
                story_dict["description"] = description.get("description")

            return {"message": "Story created successfully", "story": story_dict}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to create story: {str(e)}")

    def get_story(self, project_id: int, epic_id: int, story_id: int) -> Dict:
        """
        Get a specific story.

        Args:
            project_id (int): ID of the project
            epic_id (int): ID of the epic
            story_id (int): ID of the story

        Returns:
            Dict containing story details
        """
        try:
            # Get story and verify it belongs to the correct epic and project
            story = (
                self.session.query(Story)
                .join(Epic)
                .join(Feature)
                .filter(
                    Feature.project_id == project_id,
                    Epic.id == epic_id,
                    Story.id == story_id,
                )
                .first()
            )

            if not story:
                raise ValueError(f"Story {story_id} not found")

            # Prepare response
            story_dict = story.to_dict()
            description = story.get_description()
            if description:
                story_dict["description"] = description.get("description")

            return {"story": story_dict}

        except Exception as e:
            raise ValueError(f"Failed to get story: {str(e)}")

    def get_epic_stories(self, project_id: int, epic_id: int) -> Dict:
        """
        Get all stories for an epic.

        Args:
            project_id (int): ID of the project
            epic_id (int): ID of the epic

        Returns:
            Dict containing list of stories
        """
        try:
            # Verify epic exists and belongs to project
            epic = (
                self.session.query(Epic)
                .join(Feature)
                .filter(Feature.project_id == project_id, Epic.id == epic_id)
                .first()
            )

            if not epic:
                raise ValueError(f"Epic {epic_id} not found in project {project_id}")

            # Get all stories
            stories = self.session.query(Story).filter(Story.epic_id == epic_id).all()

            # Prepare response
            stories_data = []
            for story in stories:
                story_dict = story.to_dict()
                description = story.get_description()
                if description:
                    story_dict["description"] = description.get("description")
                stories_data.append(story_dict)

            return {"epic_id": epic_id, "stories": stories_data}

        except Exception as e:
            raise ValueError(f"Failed to get stories: {str(e)}")

    def update_story(
        self, project_id: int, epic_id: int, story_id: int, updates: Dict
    ) -> Dict:
        """
        Update a story.

        Args:
            project_id (int): ID of the project
            epic_id (int): ID of the epic
            story_id (int): ID of the story
            updates (Dict): Updates to apply

        Returns:
            Dict containing updated story
        """
        try:
            # Get story and verify it belongs to the correct epic and project
            story = (
                self.session.query(Story)
                .join(Epic)
                .join(Feature)
                .filter(
                    Feature.project_id == project_id,
                    Epic.id == epic_id,
                    Story.id == story_id,
                )
                .first()
            )

            if not story:
                raise ValueError(f"Story {story_id} not found")

            if "title" in updates:  # Add title update
                story.title = updates["title"]

            # Update description if provided
            if "description" in updates:
                story.save_description(updates["description"])

            self.session.commit()

            # Prepare response
            story_dict = story.to_dict()
            description = story.get_description()
            if description:
                story_dict["description"] = description.get("description")

            return {"message": "Story updated successfully", "story": story_dict}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to update story: {str(e)}")

    def delete_story(self, project_id: int, epic_id: int, story_id: int) -> Dict:
        """
        Delete a story.

        Args:
            project_id (int): ID of the project
            epic_id (int): ID of the epic
            story_id (int): ID of the story

        Returns:
            Dict containing success message
        """
        try:
            # Get story and verify it belongs to the correct epic and project
            story = (
                self.session.query(Story)
                .join(Epic)
                .join(Feature)
                .filter(
                    Feature.project_id == project_id,
                    Epic.id == epic_id,
                    Story.id == story_id,
                )
                .first()
            )

            if not story:
                raise ValueError(f"Story {story_id} not found")

            self.session.delete(story)
            self.session.commit()

            return {"message": f"Story {story_id} deleted successfully"}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete story: {str(e)}")
