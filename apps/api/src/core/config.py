from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SMMS-Agent API"
    environment: str = "local"
    log_level: str = "INFO"
    rate_limit_default: str = "20/minute"
    database_url: str = "postgresql+asyncpg://localhost:5432/smms_dev"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o-main"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    azure_openai_api_version: str = "2024-10-21"
    mcp_calendar_url: str = "http://localhost:8801/mcp"


settings = Settings()
