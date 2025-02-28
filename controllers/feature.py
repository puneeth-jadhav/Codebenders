from controllers.base import BaseController
from database.models import Feature, Project
from typing import Optional, Dict, Union, List
from services.feature.extractor import FeatureExtractor
from sqlalchemy.types import Enum as SAEnum
from database.models import FeatureTypeEnum


class FeatureController(BaseController):
    """Controller for handling Feature-related operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature_extractor = FeatureExtractor()

    async def extract_features(self, project_id: int) -> Dict:
        """
        Extract and suggest features for a project.

        Args:
            project_id (int): ID of the project

        Returns:
            Dict containing created features information
        """
        try:
            # Get project
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            # Get project content
            content = project.get_content()
            if not content or "project_content" not in content:
                raise ValueError("No content available for feature extraction")

            # Extract features
            features_data = self.feature_extractor.extract_and_suggest(
                content["project_content"]
            )

            # Create features in database
            created_features = []

            # Process all features
            for category in ["extracted_features", "suggested_features"]:
                for feature in features_data.get(category, []):
                    feature_dict = {
                        "name": feature["name"],
                        "type": feature["type"],
                        "is_finalized": feature.get("is_finalized", False),
                    }
                    created_features.append(feature_dict)

                    # Save description in MongoDB if provided
                    if "description" in feature:
                        feature_dict["description"] = feature["description"]

            # Create all features
            result = self.create_many(project_id, created_features)
            return result

        except Exception as e:
            raise ValueError(f"Failed to extract features: {str(e)}")

    def create_many(self, project_id: int, features: List[Dict]) -> Dict:
        """Create multiple features for a project"""
        try:
            # Check if project exists
            project = (
                self.session.query(Project).filter(Project.id == project_id).first()
            )
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")

            created_features = []
            for feature_data in features:
                # Create feature
                feature = Feature(
                    project_id=project_id,
                    name=feature_data["name"],
                    type=feature_data["type"],
                    is_finalized=feature_data.get("is_finalized", False),
                )

                self.session.add(feature)
                self.session.flush()  # Get ID without committing

                # Save summary to MongoDB if description provided
                if "description" in feature_data:
                    feature.save_summary(feature_data["description"])

                created_features.append(feature)

            self.session.commit()

            # Prepare response
            features_data = []
            for feature in created_features:
                feature_dict = feature.to_dict()
                summary = feature.get_summary()
                if summary:
                    feature_dict["description"] = summary.get("summary")
                features_data.append(feature_dict)

            return {
                "message": f"{len(features_data)} features created successfully",
                "features": features_data,
            }

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to create features: {str(e)}")

    def get_many(self, project_id: int) -> Dict:
        """Get all features for a project"""
        try:
            features = (
                self.session.query(Feature)
                .filter(Feature.project_id == project_id)
                .all()
            )

            features_data = []
            for feature in features:
                feature_dict = feature.to_dict()
                summary = feature.get_summary()
                if summary:
                    feature_dict["description"] = summary.get("summary")
                features_data.append(feature_dict)

            return {"features": features_data}

        except Exception as e:
            raise ValueError(f"Failed to fetch features: {str(e)}")

    def update(self, project_id: int, feature_id: int, updates: Dict) -> Dict:
        """Update a feature"""
        try:
            feature = (
                self.session.query(Feature)
                .filter(Feature.project_id == project_id, Feature.id == feature_id)
                .first()
            )

            if not feature:
                raise ValueError(
                    f"Feature {feature_id} not found in project {project_id}"
                )

            # Update SQL fields
            if "name" in updates:
                feature.name = updates["name"]
            if "is_finalized" in updates:
                feature.is_finalized = updates["is_finalized"]
            if "type" in updates:
                feature.type = updates["type"]

            # Update MongoDB summary if description provided
            if "description" in updates:
                feature.save_summary(updates["description"])

            self.session.commit()

            # Prepare response
            feature_dict = feature.to_dict()
            summary = feature.get_summary()
            if summary:
                feature_dict["description"] = summary.get("summary")

            return {"message": "Feature updated successfully", "feature": feature_dict}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to update feature: {str(e)}")

    def delete(self, project_id: int, feature_id: int) -> Dict:
        """Delete a feature"""
        try:
            feature = (
                self.session.query(Feature)
                .filter(Feature.project_id == project_id, Feature.id == feature_id)
                .first()
            )

            if not feature:
                raise ValueError(
                    f"Feature {feature_id} not found in project {project_id}"
                )

            self.session.delete(feature)
            self.session.commit()

            return {"message": f"Feature {feature_id} deleted successfully"}

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to delete feature: {str(e)}")

    def finalize_features(self, project_id: int, feature_ids: List[int]) -> Dict:
        """
        Finalize multiple features for a project.

        Args:
            project_id (int): ID of the project
            feature_ids (List[int]): List of feature IDs to finalize

        Returns:
            Dict containing finalized features information
        """
        try:
            # Get all features in one query
            features = (
                self.session.query(Feature)
                .filter(Feature.project_id == project_id, Feature.id.in_(feature_ids))
                .all()
            )

            # Check if all features exist
            found_ids = {feature.id for feature in features}
            missing_ids = set(feature_ids) - found_ids
            if missing_ids:
                raise ValueError(f"Features not found: {missing_ids}")

            # Update all features
            finalized_features = []
            for feature in features:
                feature.is_finalized = True
                feature_dict = feature.to_dict()
                summary = feature.get_summary()
                if summary:
                    feature_dict["description"] = summary.get("summary")
                finalized_features.append(feature_dict)

            self.session.commit()

            return {
                "message": f"{len(finalized_features)} features finalized successfully",
                "features": finalized_features,
            }

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Failed to finalize features: {str(e)}")
