import json
import os
from controllers.base import BaseController
from database.models import Project
from config import settings

class FrontendGenerationController(BaseController):

    def __init__(self):
        super().__init__()
    
    def generate_code(self, project_id, frontend_prompt, base_path):
        # write code to return over here.
        return "hello"