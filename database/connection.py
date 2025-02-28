from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from pymongo import MongoClient
from config.settings import MYSQL_URL, MONGO_URL, MONGO_DB
from database.tech_bundles import TECH_STACKS

# SQLAlchemy setup for MySQL
engine = create_engine(MYSQL_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)
Base = declarative_base()

# MongoDB setup
# Add more collections here if necessary

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB]
project_content_collection = mongo_db["project_content"]
codegen_collection = mongo_db["codegen"]
feature_summary_collection = mongo_db["feature_summary"]
tech_bundle_collection = mongo_db["tech_bundle"]
epic_description_collection = mongo_db["epic_description"]
story_description_collection = mongo_db["story_description"]
theme_collection = mongo_db["theme"]
prompt_collection = mongo_db["prompts"]
deploy_credentials_collection = mongo_db["deploy_credentials"]
deploy_project_metadata_collection = mongo_db["deploy_project_metadata"]

count_bundles = len(list(tech_bundle_collection.find({})))

if count_bundles == 0:
    tech_bundle_collection.insert_many(TECH_STACKS)


def get_db():
    """Get SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
