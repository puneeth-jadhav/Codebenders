import os
from typing import Dict

# Load secrets from environment variables or other secure sources
SECRETS = {
    "aws": {
        "region": os.getenv("AWS_REGION"),
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "access_key_id_s3": os.getenv("AWS_ACCESS_KEY_ID_S3"),
        "secret_access_key_s3": os.getenv("AWS_SECRET_ACCESS_KEY_S3"),
        "s3_bucket": os.getenv("AWS_S3_BUCKET"),
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
