import json
import requests
from typing import Dict, List, Optional


class TestingaideClient:
    """Client for interacting with Testingaide API"""

    def __init__(self):
        self.base_url = "https://demo.testingaide.ai"
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNhaWt1bWFyLmthbnRoYWxhQGNsb3VkYW5nbGVzLmNvbSIsImlhdCI6MTc0MDY0Mjc0NSwib3JnX2FkbWluIjoxLCJvcmdhbml6YXRpb24iOiJDbG91ZEFuZ2xlcyIsInVzZXJJRCI6ImQwMjg2ZDViLTdmMjgtNDhlMy1iY2JmLTlhMWIxZTZjODY2YSJ9.TuO7X0g3YC4YPRL9pSlnnzOfHpScOCMSVEdc-3WRgHo"

    def create_project(
        self, name: str, description: Optional[str], codebenders_id: int
    ) -> Dict:
        """
        Create a project in Testingaide.

        Args:
            name (str): Project name
            description (Optional[str]): Project description
            codebenders_id (int): ID from Codebenders project

        Returns:
            Dict: Response from Testingaide API

        Raises:
            ValueError: If project creation fails
        """
        try:
            url = f"{self.base_url}/projects/create_project"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            data = {
                "project_name": name,
                "description": description or "",
                "codebenders_id": codebenders_id,
            }

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if not result.get("success"):
                raise ValueError(
                    f"Failed to create Testingaide project: {result.get('message')}"
                )

            return result

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Testingaide API: {str(e)}")

    def create_requirement_document(self, project_id: int, content: str) -> Dict:
        """
        Create a requirements document in Testingaide.

        Args:
            project_id (int): Testingaide project ID
            content (str): Project content/requirements

        Returns:
            Dict: Response from Testingaide API

        Raises:
            ValueError: If document creation fails
        """
        try:
            url = f"{self.base_url}/documents/create_requirement_document"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            data = {"project_id": project_id, "project_content": content}

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if not result.get("success"):
                raise ValueError(
                    f"Failed to create requirement document: {result.get('message')}"
                )

            return result

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Testingaide API: {str(e)}")

    def process_epics_and_stories(
        self, project_id: int, epics_data: List[Dict]
    ) -> Dict:
        """
        Send epics and stories data to Testingaide for processing.

        Args:
            project_id (int): Testingaide project ID
            epics_data (List[Dict]): List of epics with their stories

        Returns:
            Dict: Response from Testingaide API

        Raises:
            ValueError: If processing fails
        """
        try:
            url = f"{self.base_url}/documents/process_epics_and_stories"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }

            # Convert the epics data to a JSON string as required by the API
            data = {"project_id": project_id, "data": json.dumps(epics_data)}

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if not result.get("success"):
                raise ValueError(
                    f"Failed to process epics and stories: {result.get('message')}"
                )

            return result

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Testingaide API: {str(e)}")
