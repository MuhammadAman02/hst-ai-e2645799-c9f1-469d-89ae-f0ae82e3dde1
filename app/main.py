"""
Snake Game UI and Game Loop
NiceGUI-based interface with real-time gameplay
"""

import asyncio
from nicegui import ui, app
from typing import Optional
from core.game import SnakeGame
from models.schemas import Direction
from app.config import settings


class SnakeGameUI:
    """Snake Game UI with real-time rendering and controls"""
    
    def __init__(self):
        self.game = SnakeGame(board_size=settings.board_size)
        self.canvas: Optional[ui.canvas] = None
        self.game_timer: Optional[ui.timer] = None
        self.score_label: Optional[ui.label] = None
        self.status_label: Optional[ui.label] = None
        self.cell_size = 20
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Setup the game user interface"""
        # Add custom CSS for modern gaming look
        ui.add_head_html('''
        <style>
            .game-container {
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 255, 65, 0.2);
                border: 2px solid #333;
            }
            .game-canvas {
                border: 3px solid #00ff41;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
                background: #0f0f0f;
            }
            .game-info {
                color: #00ff41;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
            }
            .game-button {
                background: linear-gradient(45deg, #00ff41, #00cc33);
                border: none;
                border-radius: 8px;
                color: #000;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3);
                transition: all 0.3s ease;
            }
            .game-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 255, 65, 0.4);
            }
            .controls-info {
                color: #888;
                font-size: 14px;
                text-align: center;
                margin-top: 10px;
            }
        </style>
        ''')
        
        # Main game container
        with ui.column().classes('items-center justify-center min-h-screen bg-gray-900'):
            ui.label('🐍 SNAKE GAME').classes('text-4xl font-bold text-green-400 mb-4')
            
            with ui.card().classes('game-container'):
                # Game info display
                with ui.row().classes('justify-between w-full mb-4'):
                    self.score_label = ui.label('Score: 0').classes('game-info text-xl')
                    self.status_label = ui.label('Ready to Play!').classes('game-info text-xl')
                
                # Game canvas
                canvas_size = self.cell_size * settings.board_size
                self.canvas = ui.canvas(
                    width=canvas_size, 
                    height=canvas_size
                ).classes('game-canvas')
                
                # Control buttons
                with ui.row().classes('justify-center gap-4 mt-4'):
                    ui.button('New Game', on_click=self.new_game).classes('game-button')
                    ui.button('Pause/Resume', on_click=self.toggle_pause).classes('game-button')
                
                # Controls info
                ui.html('''
                <div class="controls-info">
                    <p><strong>Controls:</strong> Use Arrow Keys or WASD to move</p>
                    <p>🔼 Up | 🔽 Down | ◀️ Left | ▶️ Right | Space: Pause</p>
                </div>
                ''')
        
        # Setup keyboard controls
        self.setup_keyboard_controls()
        
        # Start game timer
        self.start_game_loop()
        
        # Initial render
        self.render_game()
    
    def setup_keyboard_controls(self) -> None:
        """Setup keyboard event handlers"""
        async def handle_key(e):
            key = e.key.lower()
            direction_map = {
                'arrowup': Direction.UP, 'w': Direction.UP,
                'arrowdown': Direction.DOWN, 's': Direction.DOWN,
                'arrowleft': Direction.LEFT, 'a': Direction.LEFT,
                'arrowright': Direction.RIGHT, 'd': Direction.RIGHT,
            }
            
            if key in direction_map:
                self.game.change_direction(direction_map[key])
            elif key == ' ':  # Space for pause
                self.toggle_pause()
        
        ui.keyboard(on_key=handle_key)
    
    def start_game_loop(self) -> None:
        """Start the game update timer"""
        if self.game_timer:
            self.game_timer.cancel()
        
        self.game_timer = ui.timer(
            interval=settings.game_speed / 1000.0,  # Convert ms to seconds
            callback=self.game_tick
        )
    
    async def game_tick(self) -> None:
        """Single game update cycle"""
        if self.game.state.is_running and not self.game.state.is_paused:
            game_continues = self.game.update()
            self.render_game()
            self.update_ui_info()
            
            if not game_continues:
                self.game_timer.cancel()
    
    def render_game(self) -> None:
        """Render the current game state on canvas"""
        if not self.canvas:
            return
        
        # Clear canvas
        self.canvas.clear()
        
        # Draw game board background
        with self.canvas:
            self.canvas.rect(0, 0, self.canvas.size[0], self.canvas.size[1]).style(fill='#0f0f0f')
        
        # Draw snake
        for i, segment in enumerate(self.game.state.snake):
            x = segment.x * self.cell_size
            y = segment.y * self.cell_size
            
            # Head is brighter, body segments fade
            if i == 0:  # Head
                color = '#00ff41'
                border_color = '#ffffff'
            else:  # Body
                alpha = max(0.6, 1 - (i * 0.1))
                color = f'rgba(0, 255, 65, {alpha})'
                border_color = '#00cc33'
            
            with self.canvas:
                self.canvas.rect(x + 1, y + 1, self.cell_size - 2, self.cell_size - 2).style(
                    fill=color, stroke=border_color, stroke_width=1
                )
        
        # Draw food
        food_x = self.game.state.food.x * self.cell_size
        food_y = self.game.state.food.y * self.cell_size
        
        with self.canvas:
            # Pulsing red food
            self.canvas.circle(
                food_x + self.cell_size // 2,
                food_y + self.cell_size // 2,
                self.cell_size // 2 - 2
            ).style(fill='#ff4444', stroke='#ff6666', stroke_width=2)
    
    def update_ui_info(self) -> None:
        """Update score and status displays"""
        info = self.game.get_game_info()
        
        if self.score_label:
            self.score_label.text = f"Score: {info['score']} | High: {info['high_score']}"
        
        if self.status_label:
            if not info['is_running']:
                self.status_label.text = "Game Over!"
                self.status_label.classes('text-red-400')
            elif info['is_paused']:
                self.status_label.text = "Paused"
                self.status_label.classes('text-yellow-400')
            else:
                self.status_label.text = f"Length: {info['snake_length']}"
                self.status_label.classes('game-info')
    
    def new_game(self) -> None:
        """Start a new game"""
        self.game.reset_game()
        self.start_game_loop()
        self.render_game()
        self.update_ui_info()
        if self.status_label:
            self.status_label.classes('game-info')
    
    def toggle_pause(self) -> None:
        """Toggle game pause state"""
        self.game.toggle_pause()
        self.update_ui_info()


# Global game instance
game_ui: Optional[SnakeGameUI] = None


@ui.page('/')
async def index():
    """Main game page"""
    global game_ui
    game_ui = SnakeGameUI()


@ui.page('/health')
async def health():
    """Health check endpoint for deployment"""
    return {"status": "healthy", "game": "snake", "version": "1.0.0"}


def start_game():
    """Start the Snake game application"""
    ui.run(
        host=settings.host,
        port=settings.port,
        title="🐍 Snake Game - Classic Arcade Fun",
        favicon="🐍",
        dark=True,
        show=False  # Don't auto-open browser in production
    )


if __name__ == "__main__":
    start_game()