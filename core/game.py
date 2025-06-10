"""
Snake Game Core Logic
Handles game mechanics, collision detection, and state management
"""

import random
import asyncio
from typing import Optional, Set
from models.schemas import GameState, Position, Direction, GameStats


class SnakeGame:
    """Core Snake game logic with collision detection and state management"""
    
    def __init__(self, board_size: int = 20):
        self.board_size = board_size
        self.stats = GameStats()
        self.reset_game()
    
    def reset_game(self) -> None:
        """Reset game to initial state"""
        # Initialize snake in center
        center = self.board_size // 2
        self.state = GameState(
            snake=[
                Position(x=center, y=center),
                Position(x=center-1, y=center),
                Position(x=center-2, y=center)
            ],
            food=self._generate_food(),
            direction=Direction.RIGHT,
            score=0,
            is_running=True,
            is_paused=False,
            board_size=self.board_size
        )
    
    def _generate_food(self) -> Position:
        """Generate food at random position not occupied by snake"""
        occupied_positions: Set[Position] = set(self.state.snake) if hasattr(self, 'state') else set()
        
        while True:
            food_pos = Position(
                x=random.randint(0, self.board_size - 1),
                y=random.randint(0, self.board_size - 1)
            )
            if food_pos not in occupied_positions:
                return food_pos
    
    def change_direction(self, new_direction: Direction) -> bool:
        """Change snake direction with validation"""
        if self.state.is_paused or not self.state.is_running:
            return False
        
        # Prevent reversing into itself
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if new_direction != opposite_directions.get(self.state.direction):
            self.state.direction = new_direction
            return True
        return False
    
    def update(self) -> bool:
        """Update game state - returns True if game continues, False if game over"""
        if not self.state.is_running or self.state.is_paused:
            return self.state.is_running
        
        # Calculate new head position
        head = self.state.snake[0]
        direction_deltas = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0)
        }
        
        dx, dy = direction_deltas[self.state.direction]
        new_head = Position(x=head.x + dx, y=head.y + dy)
        
        # Check wall collision
        if (new_head.x < 0 or new_head.x >= self.board_size or 
            new_head.y < 0 or new_head.y >= self.board_size):
            return self._game_over()
        
        # Check self collision
        if new_head in self.state.snake:
            return self._game_over()
        
        # Move snake
        self.state.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.state.food:
            self.state.score += 10
            self.stats.total_food_eaten += 1
            self.state.food = self._generate_food()
        else:
            # Remove tail if no food eaten
            self.state.snake.pop()
        
        return True
    
    def _game_over(self) -> bool:
        """Handle game over logic"""
        self.state.is_running = False
        self.stats.games_played += 1
        self.stats.current_score = self.state.score
        if self.state.score > self.stats.high_score:
            self.stats.high_score = self.state.score
        return False
    
    def toggle_pause(self) -> bool:
        """Toggle game pause state"""
        if self.state.is_running:
            self.state.is_paused = not self.state.is_paused
        return self.state.is_paused
    
    def get_game_info(self) -> dict:
        """Get current game information for display"""
        return {
            "score": self.state.score,
            "high_score": self.stats.high_score,
            "is_running": self.state.is_running,
            "is_paused": self.state.is_paused,
            "snake_length": len(self.state.snake),
            "games_played": self.stats.games_played
        }