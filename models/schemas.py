"""
Game Data Models
Pydantic models for type safety and validation
"""

from pydantic import BaseModel, Field
from typing import List, Tuple, Literal
from enum import Enum


class Direction(str, Enum):
    """Snake movement directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Position(BaseModel):
    """2D position coordinates"""
    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))


class GameState(BaseModel):
    """Complete game state"""
    snake: List[Position] = Field(default_factory=list, description="Snake body segments")
    food: Position = Field(..., description="Food position")
    direction: Direction = Field(default=Direction.RIGHT, description="Current movement direction")
    score: int = Field(default=0, ge=0, description="Current score")
    is_running: bool = Field(default=True, description="Game running status")
    is_paused: bool = Field(default=False, description="Game paused status")
    board_size: int = Field(default=20, gt=0, description="Board size in cells")
    
    class Config:
        use_enum_values = True


class GameStats(BaseModel):
    """Game statistics and records"""
    current_score: int = Field(default=0, ge=0)
    high_score: int = Field(default=0, ge=0)
    games_played: int = Field(default=0, ge=0)
    total_food_eaten: int = Field(default=0, ge=0)