"""
Application Configuration
Environment-driven configuration with sensible defaults
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Game Configuration
    game_speed: int = int(os.getenv("GAME_SPEED", "150"))  # milliseconds
    board_size: int = int(os.getenv("BOARD_SIZE", "20"))   # grid cells
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()