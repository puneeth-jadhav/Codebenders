from typing import Dict, List
import json
from utils.llm_helper import LLMHelper


class EpicGenerator:
    """Service for generating epics from features"""

    def __init__(self, model_name: str = None):
        self.llm = LLMHelper.get_llm(model_name) if model_name else LLMHelper.get_llm()

    @property
    def system_prompt(self) -> str:
        return """
You are a technical lead creating structured epics that balance functional and technical aspects. Your task is to:

1. Analyze the feature in context of the overall requirement document
2. Create focused epics that will be broken down into user stories
3. Include technical details only when critical for implementation
4. Maintain alignment with project requirements
5. Format description in Jira-compatible markdown
6. Create descriptive epic name by:
   - Using feature name as base
   - Adding context if name is too brief
   - Maintaining clarity and purpose
"""

    def generate_epic(self, feature: Dict, tech_stack: str, requirements: str) -> Dict:
        """Generate epic from feature"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""
Context:
Technical Stack: {tech_stack}
Requirements Document: {requirements}
Selected Feature: {feature}

Generate epic in this format:
{{
    "id": {feature["id"]},
    "name": "Feature Title",
    "description": "**Objective**\\n* {{core objective}}\\n\\n**Specifications**\\n* {{spec1}}\\n* {{spec2}}\\n\\n**Scope**\\n* {{scope1}}\\n* {{scope2}}\\n\\n**Implementation**\\n* {{impl1}}\\n* {{impl2}}"
}}
""",
            },
        ]

        response = self.llm.invoke(messages)
        return json.loads(response.content.replace("```json", "").replace("```", ""))
