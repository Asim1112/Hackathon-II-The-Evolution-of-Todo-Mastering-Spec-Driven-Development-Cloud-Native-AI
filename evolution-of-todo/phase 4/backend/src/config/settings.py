try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./todo_app.db"  # Default to SQLite for development

    # Environment
    environment: str = "development"  # development | staging | production

    # JWT Authentication
    jwt_secret: str = "your-default-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_delta: int = 604800  # 7 days in seconds

    # Cerebras API (OpenAI-compatible)
    cerebras_api_key: str = ""  # Set via CEREBRAS_API_KEY environment variable
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "llama-3.3-70b"

    # OpenAI API (fallback for tool calling if Cerebras doesn't work with SDK)
    openai_api_key: str = ""  # Set via OPENAI_API_KEY environment variable
    openai_model: str = "gpt-4-turbo-preview"
    use_openai_for_tools: bool = False  # Set to True to force OpenAI for tool calling
    auto_detect_function_calling: bool = True  # Auto-detect if Cerebras works with SDK

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.database_url.startswith("postgresql")


settings = Settings()