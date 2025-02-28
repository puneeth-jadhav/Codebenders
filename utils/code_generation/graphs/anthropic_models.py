from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import boto3
import os
from typing import Dict
from .tools import CodingTools
from .structured_output import AttemptCompletionInput
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

LLM_MODELS = {
    "us.anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "provider": "bedrock",
        "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "temperature": 0,
    },
    "us.anthropic.claude-3-5-haiku-20241022-v1:0": {
        "provider": "bedrock",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "temperature": 0,
    },
    "anthropic.claude-3-5-sonnet-20240620-v1:0": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "temperature": 0,
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
        "temperature": 0,
    },
    "gpt-4o-2024-11-20": {
        "provider": "openai",
        "model_id": "gpt-4o-2024-11-20",
        "temperature": 0,
        "max_tokens": None,
        "timeout": None,
    },
}

# Load secrets from environment variables or other secure sources
SECRETS = {
    "aws": {
        "region": os.getenv("AWS_REGION"),
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    },
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
}


def get_secrets(provider: str) -> Dict:
    """Get secrets for a specific provider"""
    if provider not in SECRETS:
        raise ValueError(f"No secrets configured for provider: {provider}")
    return SECRETS[provider]


class AnthropicModel:

    def __init__(self, system_message: str, model_name: str):
        
        self.tools = CodingTools.get_tools()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message),
                MessagesPlaceholder(variable_name="messages", optional=True),
            ]
        )

        self.model_config = LLM_MODELS[model_name]
        self.aws_secrets = get_secrets("aws")
        
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.aws_secrets["region"],
            aws_access_key_id=self.aws_secrets["access_key_id"],
            aws_secret_access_key=self.aws_secrets["secret_access_key"],
        )

        self.llm = ChatBedrock(
            model_id=self.model_config["model_id"],
            client=self.bedrock_client,
            model_kwargs={"temperature": self.model_config["temperature"]},
        )
        
        # Here we keep making the models seperate.
        self.bindable_tools = []
        self.model = None

    def make_model(self):

        self.bindable_tools = [convert_to_openai_tool(t) for t in self.tools]
        self.bindable_tools.append(convert_to_openai_tool(AttemptCompletionInput))

        self.model = {"messages": RunnablePassthrough()} | self.prompt | self.llm.bind_tools(self.bindable_tools)

        return self.model
    
    def get_model(self):
        return self.model
    
    def get_llm(self):
        return self.llm