from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


load_dotenv(PROJECT_ROOT / ".env")

class AppConfig(BaseSettings):
    
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    
    
    mongodb_url: str
    mongodb_db_name: str
    
   
   
    
    points_queue_name: str = "points_updates"
    achievements_queue_name: str = "achievements_updates"
    profile_queue_name: str = "profile_updates"
    
    
    profile_service_url: str = "http://localhost:3000"
    
    
    app_name: str = "soft-skills-practice-service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    log_level: str = "INFO"
    
    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"

config = AppConfig()