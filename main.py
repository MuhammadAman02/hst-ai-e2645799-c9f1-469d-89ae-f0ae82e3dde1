"""
Snake Game - Main Entry Point
Professional online Snake game with modern UI and smooth gameplay
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and run the application
if __name__ == "__main__":
    from app.main import start_game
    start_game()