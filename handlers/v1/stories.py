import tornado.web
from handlers.v1.base import BaseHandler
from controllers.story import StoryController
from typing import Optional
import json


class StoryHandler(BaseHandler):
    """Handler for story operations"""

    def _get_controller_class(self):
        return StoryController

    def prepare(self) -> None:
        """Prepare the request"""
        super().prepare()
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            try:
                self.json_data = json.loads(self.request.body)
            except json.JSONDecodeError:
                raise tornado.web.HTTPError(400, "Invalid JSON in request body")
        else:
            self.json_data = None

    def _validate_story_data(self, data: dict) -> None:
        """
        Validate story data.

        Args:
            data (dict): Story data to validate

        Raises:
            HTTPError: If validation fails
        """
        # Validate title
        if "title" not in data:
            raise tornado.web.HTTPError(400, "Story title is required")

        if not data["title"]:
            raise tornado.web.HTTPError(400, "Story title cannot be empty")

        if len(data["title"]) > 200:
            raise tornado.web.HTTPError(
                400, "Story title must be less than 200 characters"
            )

        # Validate description
        if "description" not in data:
            raise tornado.web.HTTPError(400, "Story description is required")

        if not data["description"]:
            raise tornado.web.HTTPError(400, "Story description cannot be empty")

    def _validate_update_data(self, data: dict) -> None:
        """
        Validate story update data.

        Args:
            data (dict): Update data to validate

        Raises:
            HTTPError: If validation fails
        """
        if "title" in data:
            if not data["title"]:
                raise tornado.web.HTTPError(400, "Story title cannot be empty")

            if len(data["title"]) > 200:
                raise tornado.web.HTTPError(
                    400, "Story title must be less than 200 characters"
                )

        if "description" in data and not data["description"]:
            raise tornado.web.HTTPError(400, "Story description cannot be empty")

    async def get(
        self, project_id: str, epic_id: str, story_id: Optional[str] = None
    ) -> None:
        """Get story or stories"""
        try:
            if story_id:
                # Get single story
                result = self.controller.get_story(
                    int(project_id), int(epic_id), int(story_id)
                )
            else:
                # Get all stories for epic
                result = self.controller.get_epic_stories(int(project_id), int(epic_id))

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def post(self, project_id: str, epic_id: str) -> None:
        """Create a new story"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            self._validate_story_data(self.json_data)

            result = self.controller.create_story(
                int(project_id), int(epic_id), self.json_data
            )

            self.set_status(201)
            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def put(self, project_id: str, epic_id: str, story_id: str) -> None:
        """Update a story"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            self._validate_update_data(self.json_data)

            result = self.controller.update_story(
                int(project_id), int(epic_id), int(story_id), self.json_data
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def delete(self, project_id: str, epic_id: str, story_id: str) -> None:
        """Delete a story"""
        try:
            result = self.controller.delete_story(
                int(project_id), int(epic_id), int(story_id)
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")


class StoryGenerationHandler(BaseHandler):
    """Handler for story generation"""

    def _get_controller_class(self):
        return StoryController

    async def post(self, project_id: str, epic_id: str) -> None:
        """Generate stories for an epic"""
        try:
            result = await self.controller.generate_stories(
                int(project_id), int(epic_id)
            )

            self.set_status(201)
            self.write_json(result)

        except ValueError as e:
            if "not found" in str(e):
                raise tornado.web.HTTPError(404, str(e))
            else:
                raise tornado.web.HTTPError(400, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
