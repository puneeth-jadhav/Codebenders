from controllers.base import BaseController
from database.models import Project
from utils.s3_helper import S3Helper
from typing import Dict, Optional
import re


class ThemeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3_helper = S3Helper()

    def _validate_color(self, color: str) -> bool:
        """
        Validate hex color code.

        Args:
            color (str): Color hex code to validate

        Returns:
            bool: True if valid hex color code
        """
        return bool(re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color))

    def _validate_font(self, font: str) -> bool:
        """
        Validate font choice.

        Args:
            font (str): Font name to validate

        Returns:
            bool: True if font is in supported list
        """
        from constants import Fonts

        return font in Fonts.CHOICES

    def update_theme(
        self, project_id: int, theme_data: Dict, logo_file: Optional[Dict] = None
    ) -> Dict:
        """
        Update project theme and branding.

        Args:
            project_id (int): ID of the project
            theme_data (Dict): Theme settings to update
            logo_file (Optional[Dict]): Logo file data if provided

        Returns:
            Dict: Updated theme data

        Raises:
            ValueError: If validation fails or update fails
        """
        try:
            # Get project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )

            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Validate colors
            for color_field in [
                "primary_color",
                "background_color",
                "secondary_background_color",
                "text_color",
            ]:
                if color_field in theme_data and not self._validate_color(
                    theme_data[color_field]
                ):
                    raise ValueError(f"Invalid hex color code for {color_field}")

            # Validate font
            if "font" in theme_data and not self._validate_font(theme_data["font"]):
                raise ValueError("Invalid font choice")

            # Handle logo upload
            if logo_file:
                logo_url = self.s3_helper.upload_file(
                    logo_file["body"], logo_file["filename"]
                )
                if logo_url:
                    theme_data["logo_url"] = logo_url
                else:
                    raise ValueError("Failed to upload logo")
            else:
                # Set backup logo if user didn't provide one and there's no existing logo
                existing_theme = project.get_theme()
                if not existing_theme or "logo_url" not in existing_theme:
                    theme_data["logo_url"] = (
                        "https://mlops-storage1.s3.amazonaws.com/logos/codebenders_color_logo.png"
                    )

            # Save theme data
            theme_id = project.save_theme(theme_data)
            if not theme_id:
                raise ValueError("Failed to save theme data")

            # Commit SQL changes
            self.session.commit()

            # Get complete theme data for response
            saved_theme = project.get_theme()
            if not saved_theme:
                raise ValueError("Failed to retrieve saved theme")

            # Remove internal fields from response
            saved_theme.pop("_id", None)
            saved_theme.pop("project_id", None)
            saved_theme.pop("created_at", None)
            saved_theme.pop("updated_at", None)

            return {"message": "Theme updated successfully", "theme": saved_theme}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to update theme: {str(e)}")

    def get_theme(self, project_id: int) -> Dict:
        """
        Get project theme settings.

        Args:
            project_id (int): ID of the project

        Returns:
            Dict: Theme settings

        Raises:
            ValueError: If project not found or theme retrieval fails
        """
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )

            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get theme data
            theme_data = project.get_theme()

            if theme_data:
                # Remove internal fields from response
                theme_data.pop("_id", None)
                theme_data.pop("project_id", None)
                theme_data.pop("created_at", None)
                theme_data.pop("updated_at", None)
            else:
                theme_data = {}  # Return empty dict if no theme set

            return {"theme": theme_data}

        except Exception as e:
            raise ValueError(f"Failed to get theme: {str(e)}")

    def delete_theme(self, project_id: int) -> Dict:
        """
        Delete project theme settings.

        Args:
            project_id (int): ID of the project

        Returns:
            Dict: Success message

        Raises:
            ValueError: If project not found or deletion fails
        """
        try:
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )

            if not project:
                raise ValueError(f"Project {project_id} not found")

            # If there's a logo, we might want to delete it from S3
            theme_data = project.get_theme()
            if theme_data and "logo_url" in theme_data:
                # Optionally delete logo from S3
                # self.s3_helper.delete_file(theme_data['logo_url'])
                pass

            # Clear theme reference
            project.theme_id = None
            self.session.commit()

            return {"message": "Theme deleted successfully"}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete theme: {str(e)}")
