import tornado.web
from handlers.v1.base import BaseHandler
from controllers.feature import FeatureController
from utils.json_encoder import json_dumps
import json
from typing import Optional


class FeatureCollectionHandler(BaseHandler):
    """Handler for multiple features operations"""

    def _get_controller_class(self):
        return FeatureController

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

    def _validate_feature_data(self, features: list) -> None:
        """Validate feature data"""
        if not isinstance(features, list):
            raise tornado.web.HTTPError(400, "Features must be provided as a list")

        for feature in features:
            if not isinstance(feature, dict):
                raise tornado.web.HTTPError(400, "Each feature must be an object")

            if "name" not in feature:
                raise tornado.web.HTTPError(400, "Feature name is required")

            if "type" not in feature:
                raise tornado.web.HTTPError(400, "Feature type is required")

            if feature["type"] not in ["EXTRACTED", "SUGGESTED"]:
                raise tornado.web.HTTPError(
                    400, "Feature type must be either 'EXTRACTED' or 'SUGGESTED'"
                )

    async def get(self, project_id: str) -> None:
        """Get all features for a project"""
        try:
            result = self.controller.get_many(int(project_id))
            self.write(json_dumps(result))  # Use custom JSON encoder
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def post(self, project_id: str) -> None:
        """Create features for a project"""
        try:
            # Check if this is an extraction request
            is_extract = self.get_argument("extract", None) is not None

            if is_extract:
                # Extract features from project content
                result = await self.controller.extract_features(int(project_id))
            else:
                # Regular feature creation
                if not self.json_data:
                    raise tornado.web.HTTPError(400, "Request body must be JSON")

                features = self.json_data.get("features", [])
                self._validate_feature_data(features)
                result = self.controller.create_many(int(project_id), features)

            self.set_status(201)
            self.write(json_dumps(result))  # Use custom JSON encoder

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def patch(self, project_id: str) -> None:
        """
        Finalize multiple features at once.
        """
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            feature_ids = self.json_data.get("feature_ids")
            if not isinstance(feature_ids, list):
                raise tornado.web.HTTPError(
                    400, "feature_ids must be provided as a list"
                )

            if not all(isinstance(fid, int) for fid in feature_ids):
                raise tornado.web.HTTPError(400, "All feature IDs must be integers")

            result = self.controller.finalize_features(int(project_id), feature_ids)

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")


class FeatureItemHandler(BaseHandler):
    """Handler for single feature operations"""

    def _get_controller_class(self):
        return FeatureController

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

    def _validate_update_data(self, data: dict) -> None:
        """Validate feature update data"""
        if "name" in data and not data["name"]:
            raise tornado.web.HTTPError(400, "Feature name cannot be empty")

        if "type" in data and data["type"] not in ["EXTRACTED", "SUGGESTED"]:
            raise tornado.web.HTTPError(
                400, "Feature type must be either 'EXTRACTED' or 'SUGGESTED'"
            )

    async def put(self, project_id: str, feature_id: str) -> None:
        """Update a feature"""
        try:
            if not self.json_data:
                raise tornado.web.HTTPError(400, "Request body must be JSON")

            self._validate_update_data(self.json_data)

            result = self.controller.update(
                int(project_id), int(feature_id), self.json_data
            )

            self.write_json(result)

        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")

    async def delete(self, project_id: str, feature_id: str) -> None:
        """Delete a feature"""
        try:
            result = self.controller.delete(int(project_id), int(feature_id))
            self.write_json(result)
        except ValueError as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, f"Internal server error: {str(e)}")
