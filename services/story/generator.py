from typing import Dict, List
import json
from utils.llm_helper import LLMHelper


class StoryGenerator:
    """Service for generating user stories from epics"""

    def __init__(self, model_name: str = None):
        self.llm = LLMHelper.get_llm(model_name) if model_name else LLMHelper.get_llm()

    @property
    def system_prompt(self) -> str:
        return """
You are a technical project manager creating implementable user stories. Your task is to:
1. Break down the epic into concrete, deliverable user stories
2. Ensure stories align with technical stack and project requirements
3. Include specific acceptance criteria that can be tested
4. Make stories granular enough for 1-3 day implementation
5. Format content to be Jira-compatible
6. Return only the JSON array with no additional text
"""

    async def generate_stories(
        self, epic: Dict, tech_stack: str, requirements: str
    ) -> List[Dict]:
        """Generate user stories from epic"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""
Context:
Epic: {epic["description"]}
Technical Stack: {tech_stack}
Requirements Document: {requirements}

Generate user stories in this format:
[{{
    "id": "<numeric_story_id>",
    "title": "Story Title",
    "description": "**As a** [role], **I want** [feature], **so that** [benefit]\\n\\**Technical Notes**\\n* Tech consideration 1\\n* Tech consideration 2\\n\\n**Acceptance Criteria**\\n* Criterion 1\\n* Criterion 2",
}}]
""",
            },
        ]

        response = self.llm.invoke(messages)
        return json.loads(response.content.replace("```json", "").replace("```", ""))
