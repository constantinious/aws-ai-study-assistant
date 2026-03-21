import json
import os

import boto3
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "eu-west-1"
    bedrock_region: str = "eu-west-1"
    dynamodb_table: str = "aif-study-user-progress"
    cognito_user_pool_id: str = ""
    cognito_app_client_id: str = ""
    pinecone_secret_name: str = "aif-study/pinecone-api-key"
    pinecone_index_name: str = "aif-study-docs"
    environment: str = "prod"

    # Bedrock model IDs — use EU cross-region inference profiles for newer models
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    generation_model_id: str = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
    explanation_model_id: str = "eu.anthropic.claude-3-5-sonnet-20240620-v1:0"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_pinecone_api_key(self) -> str:
        """Fetch Pinecone API key from Secrets Manager (cached after first call)."""
        if hasattr(self, "_pinecone_api_key"):
            return self._pinecone_api_key  # type: ignore[attr-defined]

        client = boto3.client("secretsmanager", region_name=self.aws_region)
        response = client.get_secret_value(SecretId=self.pinecone_secret_name)
        secret = json.loads(response["SecretString"])
        self._pinecone_api_key: str = secret["api_key"]
        return self._pinecone_api_key


settings = Settings()
