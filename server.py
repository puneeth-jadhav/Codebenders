import os
from dotenv import load_dotenv
import tornado.ioloop
from tornado.web import RedirectHandler
from tornado import autoreload

from constants import urls_v1
from handlers.v1.base import DefaultHandler
from handlers.v1.projects import ProjectCollectionHandler, ProjectItemHandler
from handlers.v1.features import FeatureCollectionHandler, FeatureItemHandler
from handlers.v1.codegen import CodeGenHandler
from handlers.v1.tech_bundles import TechBundleHandler
from handlers.v1.epics import EpicGenerationHandler, EpicHandler
from handlers.v1.stories import StoryGenerationHandler, StoryHandler
from handlers.v1.erd import ERDHandler
from handlers.v1.data_models import DataModelCollectionHandler, DataModelItemHandler
from handlers.v1.theme import ThemeHandler
from handlers.v1.prompts import PromptHandler
from handlers.v1.deploy import (
    DeployCredentialsHandler,
    DeploymentHandler,
    DeployMetadataHandler,
)
from handlers.v1.github import GitHubDeploymentsHandler
from handlers.v1.filesystem import FileSystemHandler, CommandExecuteHandler
from handlers.v1.verify_credentials import ConnectionTestHandler
from handlers.v1.testingaide import TestingaideSyncHandler
from utils.deploy_utils import LogWebSocketHandler

# Load environment variables from .env file
load_dotenv()

DEFAULT_PORT = 8000

BASE_URL_PREFIX = "/restapi"
URL_PREFIX_V1 = "/restapi/v1"


def get_handlers(handler_kwargs):
    handlers = [
        (urls_v1.codegen, CodeGenHandler, handler_kwargs),
        (urls_v1.projects, ProjectCollectionHandler, handler_kwargs),
        (urls_v1.project, ProjectItemHandler, handler_kwargs),
        (urls_v1.features, FeatureCollectionHandler, handler_kwargs),
        (urls_v1.feature, FeatureItemHandler, handler_kwargs),
        (urls_v1.tech_bundles, TechBundleHandler, handler_kwargs),
        (urls_v1.project_tech_bundle, TechBundleHandler, handler_kwargs),
        (urls_v1.epic, EpicHandler, handler_kwargs),
        (urls_v1.epic_generation, EpicGenerationHandler, handler_kwargs),
        (urls_v1.story, StoryHandler, handler_kwargs),
        (urls_v1.story_generation, StoryGenerationHandler, handler_kwargs),
        (urls_v1.erd, ERDHandler, handler_kwargs),
        (urls_v1.data_models, DataModelCollectionHandler, handler_kwargs),
        (urls_v1.data_model, DataModelItemHandler, handler_kwargs),
        (urls_v1.theme, ThemeHandler, handler_kwargs),
        (urls_v1.prompts, PromptHandler, handler_kwargs),
        (urls_v1.deployment_agent, DeploymentHandler, handler_kwargs),
        (urls_v1.deployment_metadata, DeployMetadataHandler, handler_kwargs),
        (urls_v1.deployment_credentails, DeployCredentialsHandler, handler_kwargs),
        (urls_v1.github_api, GitHubDeploymentsHandler, handler_kwargs),
        (urls_v1.ws_logs, LogWebSocketHandler, handler_kwargs),
        (urls_v1.files, FileSystemHandler, handler_kwargs),
        (urls_v1.execute, CommandExecuteHandler, handler_kwargs),
        (urls_v1.test_credentials, ConnectionTestHandler, handler_kwargs),
        (urls_v1.testingaide_sync, TestingaideSyncHandler, handler_kwargs),
    ]
    return handlers


def make_app():
    handlers = get_handlers({})
    return tornado.web.Application(handlers, DefaultHandler)


def main(debug=False):
    # Verify environment variables are loaded
    required_vars = [
        "OPENAI_API_KEY",
        "AWS_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Missing required environment variables:", missing_vars)
        return

    app = make_app()

    if debug:
        app.debug = True
        autoreload.start()
        autoreload.watch(".")

    print("Starting server on port %d" % DEFAULT_PORT)
    print("Environment variables loaded successfully.")
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main(True)
