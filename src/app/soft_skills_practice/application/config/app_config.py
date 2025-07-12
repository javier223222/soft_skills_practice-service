from pydantic_settings import BaseSettings
from typing import Optional


class AppConfig(BaseSettings):
    # Gemini AI Configuration
    gemini_api_key: str=""
    gemini_model: str = "gemini-1.5-flash"
    
    # MongoDB Configuration
    mongodb_url: str = ""
    mongodb_db_name: str = "soft_skills_practice"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Queue Names
    points_queue_name: str = "points_updates"
    achievements_queue_name: str = "achievements_updates"
    profile_queue_name: str = "profile_updates"
    
    # External Services
    profile_service_url: str = "http://localhost:3000"
    
    # App Configuration
    app_name: str = "soft-skills-practice-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = AppConfig()