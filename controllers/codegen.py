import json
import os
from controllers.base import BaseController
from controllers.data_model import DataModelController
from database.models import Project
from utils.db_generator import MermaidToSQLAgent
from config import settings
from utils.code_generation.system_prompts import get_frontend_system_message, get_backend_system_message
from utils.code_generation.graphs import AnthropicGraph, OpenAIGraph
from utils.code_generation.tests import frontend_prompt
from langchain_core.messages import HumanMessage
from config.settings import PROJECTS_PATH
class CodeGenController(BaseController):

    def __init__(self):
        super().__init__()

    def start_flow(
        self, project_id: str
    ):
        # Based on project id, fetch frontend and backend prompt
        print(project_id)


        project = self.session.query(Project).filter(Project.id == project_id).first()

        if not project:
            return {"message": "Project not found", "code": 404}

        prompts = project.get_prompts()

        if not prompts:
            return {"message": "Prompts not found", "code": 404}

        frontend_document = prompts.get("frontend_prompt")
        backend_document = prompts.get("backend_prompt")

        print(frontend_document)
        print(backend_document)
        # Add this config to backend prompt
        # config = self.generate_db(project_id)

        base_path = self.get_base_path()

        backend_system_message = get_backend_system_message(base_path)
        # backend_graph = AnthropicGraph(backend_system_message, model_name='us.anthropic.claude-3-5-haiku-20241022-v1:0').generate_graph()
        # backend_graph = OpenAIGraph(backend_system_message, model_name='gpt-4o-2024-11-20').generate_graph()


        # backend_inputs = {
        #     "messages": [
        #         HumanMessage(
        #             content=backend_document
        #         )
        #     ],
        #     "base_path": base_path + "/backend"
        # }
        # try:
        #     result = backend_graph.invoke(backend_inputs)
        # except Exception as e:
        #     print("BACKEND FAILED....")

        # frontend_system_message = get_frontend_system_message(base_path)
        # # frontend_graph = AnthropicGraph(frontend_system_message, model_name='us.anthropic.claude-3-5-haiku-20241022-v1:0').generate_graph()
        # frontend_graph = OpenAIGraph(frontend_system_message, model_name='gpt-4o-2024-11-20').generate_graph()

        # frontend_inputs = {
        #     "messages": [
        #         HumanMessage(
        #             content=frontend_document
        #         )
        #     ],
        #     "base_path": base_path + "/frontend"
        # }
        # try:
        #     result = frontend_graph.invoke(frontend_inputs)
        # except Exception as e:
        #     print("FRONTEND FAILED....")


    def generate_db(self, project_id: int):
        """Add shreyas code"""
        # agent = MermaidToSQLAgent()

        # # Initialize and execute SQLAgent
        # statements = agent.process_mermaid(erd_schema)
        # agent.write_schema_file(statements)
        # agent.execute_sql_file()

        data_model_controller = DataModelController()
        config = data_model_controller.generate_db(project_id=project_id)

        return json.dumps(config, indent=4)

    def generate_code(
        self,
        frontend_document: str,
        backend_document: str,
        erd_schema: str,
        config: dict,
    ):
        """Add akhil code"""

        # Gets project id too
        base_path, project_id = self.get_base_path()

        # Generate frontend code
        if not self.gen_frontend(frontend_document, project_id, base_path):
            return "", 0, {"message": "Code generation failed", "code": 500}

        # Generate backend code
        if not self.gen_backend(
            backend_document, erd_schema, project_id, base_path, config
        ):
            return "", 0, {"message": "Code generation failed", "code": 500}

        return (
            base_path,
            project_id,
            {"message": "Code generation successful", "code": 200},
        )

    def get_base_path(self, project_id: int = 1):

        # Code to get a base path for a particular project id, delete existing directory if it exists
        base_path = PROJECTS_PATH
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        if os.path.exists(base_path + "/" + str(project_id)):
            os.system("rm -rf " + base_path + "/" + str(project_id))

        return base_path + "/" + str(project_id)

    def gen_frontend(self, frontend_document: str, project_id: int, base_path: str):
        return True

    def gen_backend(
        self,
        backend_document: str,
        erd_schema: str,
        project_id: int,
        base_path: str,
        config: dict,
    ):
        return True


# class CodeGenAsyncController(BaseAsyncController):