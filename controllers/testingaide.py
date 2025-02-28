from controllers.base import BaseController
from database.models import Project
from controllers.epic import EpicController
from services.testingaide.client import TestingaideClient
from typing import Dict
import datetime


class TestingaideController(BaseController):
    """Controller for Testingaide integrations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testingaide = TestingaideClient()
        self.epic_controller = EpicController(*args, **kwargs)

    def sync_epics_and_stories(self, project_id: int) -> Dict:
        """
        Sync all epics and stories for a project to Testingaide.

        Args:
            project_id (int): ID of the project

        Returns:
            Dict: Response with sync status

        Raises:
            ValueError: If sync fails
        """
        try:
            # Get the project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            # Get project content to find Testingaide project ID
            content = project.get_content() or {}
            testingaide_project_id = content.get("testingaide_project_id")

            if not testingaide_project_id:
                raise ValueError(
                    "Testingaide project ID not found. Make sure the project was properly synced with Testingaide."
                )

            # Get all epics and stories in Testingaide format
            epics_data = self.epic_controller.get_all_project_epics_and_stories(
                project_id
            )

            if not epics_data:
                raise ValueError("No epics or stories found for this project.")

            # Send to Testingaide
            result = self.testingaide.process_epics_and_stories(
                project_id=testingaide_project_id, epics_data=epics_data
            )

            # Save the sync information in project content
            project.save_content(
                testingaide_last_sync=datetime.datetime.now(),
                testingaide_epics_count=len(epics_data),
                testingaide_stories_count=sum(
                    len(epic.get("stories", [])) for epic in epics_data
                ),
            )

            return {
                "message": "Epics and stories successfully synced to Testingaide.",
                "epics_count": len(epics_data),
                "stories_count": sum(
                    len(epic.get("stories", [])) for epic in epics_data
                ),
                "testingaide_response": result,
            }

        except Exception as e:
            raise ValueError(f"Failed to sync epics and stories: {str(e)}")
