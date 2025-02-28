# LLM Models Configuration
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

# Default model to use
DEFAULT_MODEL = "gpt-4o-2024-11-20"
