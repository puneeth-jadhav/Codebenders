from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
import boto3
from typing import Optional, Dict, Any
from config.llm_config import LLM_MODELS, DEFAULT_MODEL
from config.secrets import get_secrets


class LLMHelper:
    """Helper class for LLM initialization and management"""

    @staticmethod
    def get_bedrock_client() -> Any:
        """Initialize AWS Bedrock client"""
        aws_secrets = get_secrets("aws")
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=aws_secrets["region"],
            aws_access_key_id=aws_secrets["access_key_id"],
            aws_secret_access_key=aws_secrets["secret_access_key"],
        )

    @staticmethod
    def get_llm(model_name: str = DEFAULT_MODEL) -> Any:
        """
        Get LLM instance based on model name.

        Args:
            model_name (str): Name of the model to use (e.g., "claude-3-sonnet", "gpt-4")

        Returns:
            LLM instance

        Raises:
            ValueError: If model configuration is not found or invalid
        """
        if model_name not in LLM_MODELS:
            raise ValueError(f"Unknown model: {model_name}")

        model_config = LLM_MODELS[model_name]
        provider = model_config["provider"]

        try:
            if provider == "bedrock":
                bedrock_client = LLMHelper.get_bedrock_client()
                return ChatBedrock(
                    model_id=model_config["model_id"],
                    client=bedrock_client,
                    model_kwargs={"temperature": model_config["temperature"]},
                )

            elif provider == "openai":
                openai_secrets = get_secrets("openai")
                return ChatOpenAI(
                    model=model_config["model_id"],
                    temperature=model_config["temperature"],
                    max_tokens=model_config["max_tokens"],
                    timeout=model_config["timeout"],
                    api_key=openai_secrets["api_key"],
                )

            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            raise ValueError(f"Error initializing {model_name}: {str(e)}")

    @staticmethod
    def get_available_models() -> Dict:
        """Get list of available models and their configurations"""
        return {
            name: {k: v for k, v in config.items() if k != "api_key"}
            for name, config in LLM_MODELS.items()
        }
