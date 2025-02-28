import json
import os
from controllers.base import BaseController
from database.models import Project
from config import settings
from utils.code_generation.system_prompts import get_backend_system_message
from utils.code_generation import AnthropicGraph, OpenAIGraph

class BackendGenerationController(BaseController):

    def __init__(self):
        super().__init__()
    
    def generate_code(self, project_id, backendend_prompt, base_path):
        return "hello"