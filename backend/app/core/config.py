from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./git_stats.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Development
    debug: bool = True
    
    # Git Analysis
    auto_fetch_before_analysis: bool = True
    git_fetch_timeout: int = 300  # 5 minutes timeout for git fetch operations
    
    class Config:
        env_file = ".env"


settings = Settings()