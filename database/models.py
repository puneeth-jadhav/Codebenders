import datetime
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, func, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import (
    Base,
    project_content_collection,
    codegen_collection,
    feature_summary_collection,
    tech_bundle_collection,
    epic_description_collection,
    story_description_collection,
    theme_collection,
    prompt_collection,
    deploy_credentials_collection,
    deploy_project_metadata_collection
)
from bson.objectid import ObjectId  # type: ignore
from sqlalchemy.types import Enum as SAEnum
import enum


class BaseModel(Base):
    """Base model class with common fields and methods."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# class User(BaseModel):
#     """User model for storing user account information."""
#     __tablename__ = "users"

#     username = Column(String(64), unique=True, index=True, nullable=False)
#     email = Column(String(120), unique=True, index=True, nullable=False)
#     password_hash = Column(String(128), nullable=False)
#     is_active = Column(Boolean, default=True)

#     # Relationship with projects
#     projects = relationship("Project", back_populates="owner")

#     def __repr__(self):
#         return f"<User {self.username}>"


# ----------------------------------
# Project Model
# ----------------------------------
class Project(BaseModel):
    """Project model for storing project metadata."""

    __tablename__ = "projects"

    name = Column(String(100), nullable=False)
    description = Column(String(2048))
    mongo_content_id = Column(String(24), index=True)  # MongoDB ObjectId as string
    tech_bundle_id = Column(String(24), index=True)  # Reference to selected tech bundle
    theme_id = Column(String(24), index=True)  # Column for theme reference
    prompts_id = Column(String(24), index=True)  # Column for prompts reference

    features = relationship("Feature", back_populates="project")
    data_models = relationship("DataModel", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"

    def select_tech_bundle(self, tech_bundle_id: str) -> None:
        """
        Select a tech bundle for the project.
        """
        self.tech_bundle_id = tech_bundle_id

    def save_content(self, **kwargs):
        """
        Save or update specific fields of project content in MongoDB.
        Only updates fields that are provided in kwargs.
        kwargs can look like :
        content_doc = {
                "step1": step1,
                "step2": step2,
                "step3": step3,
                "step4": step4,
                "erd_schema": erd_schema,
                "project_content": project_content,
                "document_url": document_url,
                "document_type" : document_type,
                "testingaide_project_id": self.id
                "project_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
        """
        if not self.mongo_content_id:
            content_doc = {
                "project_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                **kwargs,
            }
            result = project_content_collection.insert_one(content_doc)
            self.mongo_content_id = str(result.inserted_id)
            return self.mongo_content_id
        else:
            update_data = {"updated_at": self.updated_at}
            update_data.update(kwargs)

            project_content_collection.update_one(
                {"_id": ObjectId(self.mongo_content_id)}, {"$set": update_data}
            )
            return self.mongo_content_id

    def get_content(self):
        """
        Retrieve project content from MongoDB.
        """
        if not self.mongo_content_id:
            return None

        content = project_content_collection.find_one(
            {"_id": ObjectId(self.mongo_content_id)}
        )
        if content:
            content["_id"] = str(content["_id"])  # Convert ObjectId to string
        return content

    def save_theme(self, theme_data: dict) -> str:
        """
        Save or update theme data in MongoDB.

        Args:
            theme_data (dict): Theme data containing:
                - primary_color (str): Hex color code
                - background_color (str): Hex color code
                - secondary_background_color (str): Hex color code
                - text_color (str): Hex color code
                - font (str): Font family name
                - logo_url (str, optional): S3 URL for logo

        Returns:
            str: MongoDB document ID
        """
        if not self.theme_id:
            theme_doc = {
                "project_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                **theme_data,
            }
            result = theme_collection.insert_one(theme_doc)
            self.theme_id = str(result.inserted_id)
            return self.theme_id
        else:
            update_data = {"updated_at": self.updated_at}
            update_data.update(theme_data)

            theme_collection.update_one(
                {"_id": ObjectId(self.theme_id)}, {"$set": update_data}
            )
            return self.theme_id

    def get_theme(self) -> Optional[dict]:
        """
        Retrieve theme data from MongoDB.

        Returns:
            Optional[dict]: Theme data or None if not set
        """
        if not self.theme_id:
            return None

        theme = theme_collection.find_one({"_id": ObjectId(self.theme_id)})
        if theme:
            theme["_id"] = str(theme["_id"])
        return theme

    def save_prompts(
        self, frontend_prompt: str, backend_prompt: str, apis: list
    ) -> str:
        """
        Save or update prompts in MongoDB.
        """
        if not self.prompts_id:
            prompt_doc = {
                "project_id": self.id,
                "frontend_prompt": frontend_prompt,
                "backend_prompt": backend_prompt,
                "apis": apis,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            result = prompt_collection.insert_one(prompt_doc)
            self.prompts_id = str(result.inserted_id)
            return self.prompts_id
        else:
            update_data = {
                "frontend_prompt": frontend_prompt,
                "backend_prompt": backend_prompt,
                "apis": apis,
                "updated_at": self.updated_at,
            }
            prompt_collection.update_one(
                {"_id": ObjectId(self.prompts_id)}, {"$set": update_data}
            )
            return self.prompts_id

    def get_prompts(self) -> Optional[dict]:
        """
        Retrieve prompts from MongoDB.
        """
        if not self.prompts_id:
            return None

        prompts = prompt_collection.find_one({"_id": ObjectId(self.prompts_id)})
        if prompts:
            prompts["_id"] = str(prompts["_id"])
        return prompts


# ----------------------------------
# Feature Model
# ----------------------------------
class FeatureTypeEnum(str, enum.Enum):
    EXTRACTED = "EXTRACTED"
    SUGGESTED = "SUGGESTED"


class Feature(BaseModel):
    """
    Feature model:
      - project_id: FK to Project (if you want a direct link)
      - name: String
      - summary: stored in MongoDB
      - type: 'EXTRACTED' or 'SUGGESTED'
      - is_finalized: boolean
    """

    __tablename__ = "features"

    # If you want to link a Feature to a Project:
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    name = Column(String(100), nullable=False)
    type = Column(
        SAEnum(FeatureTypeEnum), default=FeatureTypeEnum.EXTRACTED, nullable=False
    )
    is_finalized = Column(Boolean, default=False)

    project = relationship("Project", back_populates="features")

    # We'll store the summary in MongoDB:
    mongo_summary_id = Column(String(24), index=True)

    def __repr__(self):
        return f"<Feature {self.name}>"

    def save_summary(self, summary: str) -> str:
        """
        Save or update the feature summary in MongoDB.
        """
        if not self.mongo_summary_id:
            doc = {
                "summary": summary,
                "feature_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            result = feature_summary_collection.insert_one(doc)
            self.mongo_summary_id = str(result.inserted_id)
            return self.mongo_summary_id
        else:
            feature_summary_collection.update_one(
                {"_id": ObjectId(self.mongo_summary_id)},
                {"$set": {"summary": summary, "updated_at": self.updated_at}},
            )
            return self.mongo_summary_id

    def get_summary(self):
        """
        Retrieve the feature summary from MongoDB.
        """
        if not self.mongo_summary_id:
            return None

        doc = feature_summary_collection.find_one(
            {"_id": ObjectId(self.mongo_summary_id)}
        )
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc


# ----------------------------------
# TechBundle Model (MongoDB Only)
# ----------------------------------
class TechBundle:
    """
    This is purely a MongoDB-based entity.
    We won't store anything in MySQL.
    We'll only insert once, no updates.
    """

    @staticmethod
    def initialize_tech_bundle(data: dict) -> str:
        """
        Insert a new TechBundle document into MongoDB (once).
        Returns the inserted document ID as a string.
        """
        result = tech_bundle_collection.insert_one(data)
        return str(result.inserted_id)


# ----------------------------------
# Epic Model
# ----------------------------------
class Epic(BaseModel):
    """
    Epics:
      - feature_id: one-to-one with Feature (or one-to-many, if needed)
      - name: string
      - description: stored in MongoDB if large
    """

    __tablename__ = "epics"

    # If each Feature has exactly one Epic, we can enforce unique=True
    feature_id = Column(Integer, ForeignKey("features.id"), unique=True)
    name = Column(String(200), nullable=False)

    # We'll store the epic description in MongoDB:
    mongo_description_id = Column(String(24), index=True)

    def __repr__(self):
        return f"<Epic {self.name}>"

    def save_description(self, description: str) -> str:
        """
        Save or update the epic description in MongoDB.
        """
        if not self.mongo_description_id:
            doc = {
                "description": description,
                "epic_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            result = epic_description_collection.insert_one(doc)
            self.mongo_description_id = str(result.inserted_id)
            return self.mongo_description_id
        else:
            epic_description_collection.update_one(
                {"_id": ObjectId(self.mongo_description_id)},
                {"$set": {"description": description, "updated_at": self.updated_at}},
            )
            return self.mongo_description_id

    def get_description(self):
        """
        Retrieve the epic description from MongoDB.
        """
        if not self.mongo_description_id:
            return None

        doc = epic_description_collection.find_one(
            {"_id": ObjectId(self.mongo_description_id)}
        )
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc


# ----------------------------------
# Story Model
# ----------------------------------
class Story(BaseModel):
    """
    Story:
      - epic_id: references Epic (one Epic -> many Stories)
      - description: stored in MongoDB
    """

    __tablename__ = "stories"

    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=False)
    title = Column(String(200), nullable=False)
    mongo_description_id = Column(String(24), index=True)

    def __repr__(self):
        return f"<Story ID={self.id}>"

    def save_description(self, description: str) -> str:
        """
        Save or update the story description in MongoDB.
        """
        if not self.mongo_description_id:
            doc = {
                "description": description,
                "story_id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            result = story_description_collection.insert_one(doc)
            self.mongo_description_id = str(result.inserted_id)
            return self.mongo_description_id
        else:
            story_description_collection.update_one(
                {"_id": ObjectId(self.mongo_description_id)},
                {"$set": {"description": description, "updated_at": self.updated_at}},
            )
            return self.mongo_description_id

    def get_description(self):
        """
        Retrieve the story description from MongoDB.
        """
        if not self.mongo_description_id:
            return None

        doc = story_description_collection.find_one(
            {"_id": ObjectId(self.mongo_description_id)}
        )
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc


class DataModel(BaseModel):
    """Represents a database table in a project"""

    __tablename__ = "data_models"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    table_name = Column(String(100), nullable=False, unique=False)

    columns = relationship(
        "DataColumn", back_populates="table", cascade="all, delete-orphan"
    )
    project = relationship("Project", back_populates="data_models")

    def __repr__(self):
        return f"<DataModel {self.table_name}>"


class DataColumn(BaseModel):
    """Represents a column within a database table"""

    __tablename__ = "data_columns"

    table_id = Column(
        Integer, ForeignKey("data_models.id"), nullable=False
    )  # Relationship to DataModel
    column_name = Column(String(100), nullable=False)
    column_type = Column(String(255), nullable=False)
    is_nullable = Column(Boolean, default=True)
    # is_primary_key = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    relationships = Column(String(255))

    table = relationship("DataModel", back_populates="columns")

    def __repr__(self):
        return f"<DataColumn {self.column_name} ({self.column_type})>"


# class Codegen(BaseModel):
#     """Codegen model for storing code metadata."""
#     __tablename__ = "codegen"

#     name = Column(String(100), nullable=False)
#     description = Column(String(500))
#     mongo_content_id = Column(String(24), index=True)  # MongoDB ObjectId as string
#     owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

#     # Relationship with user
#     owner = relationship("User", back_populates="projects")

#     def __repr__(self):
#         return f"<Project {self.name}>"

#     def save_content(self, erd_schema, requirement_code):
#         """
#         Save large project content to MongoDB.

#         Args:
#             erd_schema (str): ERD schema for the project
#             requirement_code (str): Code requirements specification

#         Returns:
#             str: MongoDB document ID
#         """
#         if not self.mongo_content_id:
#             content_doc = {
#                 "erd_schema": erd_schema,
#                 "requirement_code": requirement_code,
#                 "project_id": self.id,
#                 "created_at": self.created_at,
#                 "updated_at": self.updated_at
#             }
#             result = project_content_collection.insert_one(content_doc)
#             self.mongo_content_id = str(result.inserted_id)
#             return self.mongo_content_id
#         else:
#             project_content_collection.update_one(
#                 {"_id": ObjectId(self.mongo_content_id)},
#                 {"$set": {
#                     "erd_schema": erd_schema,
#                     "requirement_code": requirement_code,
#                     "updated_at": self.updated_at
#                 }}
#             )
#             return self.mongo_content_id

class DeployCredentials(BaseModel):
    """Deploy Credentials with single MongoDB collection"""

    __tablename__ = "deploy_credentials"

    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    project_name = Column(String(200), nullable=False)

    def __repr__(self):
        return f"<DeployCredentials project={self.project_name}_{self.project_id}>"

    def save_credentials(self, credentials: dict) -> bool:
        """Save or update credentials in MongoDB using project_id"""
        doc = deploy_credentials_collection.find_one({"project_id": self.project_id})

        if not doc:
            # Create new record
            new_doc = {
                "project_id": self.project_id,
                "project_name": self.project_name,
                "github": self._encrypt_data(credentials.get("github", {})),
                "docker": self._encrypt_data(credentials.get("docker", {})),
                "aws": self._encrypt_data(credentials.get("aws", {})),
                "kubernetes": self._encrypt_data(credentials.get("kubernetes", {})),
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            deploy_credentials_collection.insert_one(new_doc)
            return True

        # Update existing record
        deploy_credentials_collection.update_one(
            {"project_id": self.project_id},
            {
                "$set": {
                    "github": self._encrypt_data(credentials.get("github", {})),
                    "docker": self._encrypt_data(credentials.get("docker", {})),
                    "aws": self._encrypt_data(credentials.get("aws", {})),
                    "kubernetes": self._encrypt_data(credentials.get("kubernetes", {})),
                    "updated_at": self.updated_at,
                }
            }
        )
        return True

    def get_credentials(self, cred_type: str = None) -> dict:
        """Retrieve credentials from MongoDB using project_id"""
        doc = deploy_credentials_collection.find_one({"project_id": self.project_id})
        if not doc:
            return None

        doc.pop("_id", None)  # Remove MongoDB _id
        if cred_type:
            return self._decrypt_data(doc.get(cred_type, {}))
        return {k: self._decrypt_data(v) for k, v in doc.items() if k not in ['created_at', 'updated_at', 'project_id', 'project_name']}

    def update_specific_credentials(self, cred_type: str, cred_data: dict) -> bool:
        """Update specific credential type using project_id"""
        if cred_type not in ['github', 'docker', 'aws', 'kubernetes']:
            return False

        deploy_credentials_collection.update_one(
            {"project_id": self.project_id},
            {"$set": {cred_type: self._encrypt_data(cred_data), "updated_at": self.updated_at}}
        )
        return True

    def delete_credentials(self) -> bool:
        """Delete credentials using project_id"""
        result = deploy_credentials_collection.delete_one({"project_id": self.project_id})
        return result.deleted_count > 0
    
    def _encrypt_data(self, data: dict) -> dict:
        """Encrypt sensitive data before storing"""
        # TODO: Implement encryption
        return data

    def _decrypt_data(self, data: dict) -> dict:
        """Decrypt sensitive data after retrieval"""
        # TODO: Implement decryption
        return data

# deployment model for storing deployment metadata
class DeployProjectMetadata(BaseModel):
    """Deploy Project Metadata with single MongoDB collection"""

    __tablename__ = "deploy_project_metadata"

    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)

    def __repr__(self):
        return f"<DeployProjectMetadata project_id={self.project_name}_{self.project_id}>"

    def save_metadata(self, metadata: dict) -> str:
        """Save or update metadata in MongoDB"""
        """Save or update credentials in MongoDB using project_id"""
        project_id_int = int(self.project_id) 
        doc = deploy_project_metadata_collection.find_one({"project_id": project_id_int})
        if not doc:
            doc = { #for one project 
                "project_id": project_id_int,
                "github": metadata.get("github", {}),
                "docker": metadata.get("docker", {}),
                "aws": metadata.get("aws", {}),
                "BasePath": "",
                "frontend_folder_name": "",
                "backend_folder_name":"",
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
            deploy_project_metadata_collection.insert_one(doc)
            return True
        
        deploy_project_metadata_collection.update_one(
            {"project_id": project_id_int},
            {
                "$set": {
                    "github": metadata.get("github", {}),
                    "docker": metadata.get("docker", {}),
                    "aws": metadata.get("aws", {}),
                    "updated_at": self.updated_at
                }
            }
        )
        return True

    def get_metadata(self) -> dict:
        """Retrieve all metadata from MongoDB"""
        try:
            project_id_int = int(self.project_id)  # Ensure it's an integer
            doc = deploy_project_metadata_collection.find_one({"project_id": project_id_int})
            if doc:
                doc.pop("_id", None)  # Remove MongoDB _id
                return doc
            else:
                return {"error": "No Metadata Found"}
        except Exception as e:
            return {"error": str(e)}


    def update_github_metadata(self, github_data: dict) -> bool:
        """Update only GitHub metadata"""
        project_id_int = int(self.project_id) 
        deploy_project_metadata_collection.update_one(
            {"project_id": project_id_int},
            {"$set": {"github": github_data, "updated_at": self.updated_at}}
        )
        return True

    def update_docker_metadata(self, docker_data: dict) -> bool:
        """Update only Docker metadata"""
        project_id_int = int(self.project_id) 
        deploy_project_metadata_collection.update_one(
            {"project_id": project_id_int}, 
            {"$set": {"docker": docker_data, "updated_at": self.updated_at}}
        )
        return True

    def update_aws_metadata(self, aws_data: dict) -> bool:
        """Update only AWS metadata"""
        project_id_int = int(self.project_id) 
        deploy_project_metadata_collection.update_one(
            {"project_id": project_id_int},
            {"$set": {"aws": aws_data, "updated_at": self.updated_at}}
        )
        return True

    def delete_metadata(self):
        """Delete the Project Metadata"""
        project_id_int = int(self.project_id) 
        result=deploy_project_metadata_collection.delete_one(
            {"project_id": project_id_int}
        )
        return result.deleted_count > 0