from typing import Dict, Optional, List
import json
from utils.llm_helper import LLMHelper


class FeatureExtractor:
    """Service for extracting and suggesting features from project content"""

    def __init__(self, model_name: str = None):
        """
        Initialize feature extractor.

        Args:
            model_name (str, optional): Name of the LLM model to use
        """
        self.llm = LLMHelper.get_llm(model_name) if model_name else LLMHelper.get_llm()

    @property
    def system_prompt(self) -> str:
        """Get the system prompt for feature extraction"""
        return """
You are a senior software architect and business analyst. Your role is to analyze requirement documents with precision and provide structured feature analysis.

TASKS:
1. Extract Explicit Features:
   - Only include features DIRECTLY stated in the document
   - Do not interpret or assume implied features

2. Suggest Strategic Features:
   - Suggest features that clearly enhance core functionality
   - Each suggestion must include rationale tied to document requirements
   - Focus on business value and technical feasibility

3. Format the output as JSON with two categories:
   - extracted_features: Features directly mentioned in the document
   - suggested_features: Additional features you recommend

For each feature, provide:
   - name: Short, clear feature name
   - description: Detailed description
   - type: "EXTRACTED" or "SUGGESTED"
   - is_finalized: false

VALIDATION RULES:
1. Extracted features must have direct textual evidence
2. Suggestions must clearly connect to existing requirements
3. Descriptions must be complete but concise (<50 words)
4. No technical jargon in names
5. No duplicates between extracted and suggested features
"""

    def extract_and_suggest(self, document_content: str) -> Dict[str, List[Dict]]:
        """
        Extract features from document content and suggest additional features.

        Args:
            document_content (str): The project content to analyze

        Returns:
            Dict containing extracted and suggested features

        Raises:
            ValueError: If feature extraction fails
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""
                    Please analyze this document and extract features:

                    {document_content}

                    Provide the output in this format:
                    {{
                        "extracted_features": [
                            {{
                                "name": "Feature Name",
                                "description": "Feature description",
                                "type": "EXTRACTED",
                                "is_finalized": false
                            }}
                        ],
                        "suggested_features": [
                            {{
                                "name": "Suggested Feature Name",
                                "description": "Suggested feature description",
                                "type": "SUGGESTED",
                                "is_finalized": false
                            }}
                        ]
                    }}
                    """,
                },
            ]

            # Get response from LLM
            response = self.llm.invoke(messages)

            # Parse the response
            features_data = json.loads(
                response.content.replace("```json", "").replace("```", "")
            )

            # Validate the response format
            if not isinstance(features_data, dict):
                raise ValueError("Invalid response format from LLM")

            if (
                "extracted_features" not in features_data
                or "suggested_features" not in features_data
            ):
                raise ValueError("Missing required feature categories in response")

            return features_data

        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")
        except Exception as e:
            raise ValueError(f"Error extracting features: {str(e)}")
