"""
Game State model - contains all game data
"""

import random
from model.snake import Snake
from model.obstacles import Obstacles
from model.apple import Apple
from model.pane import Pane
from settings import load_player_colors
from config import (
    PANE1_X0,
    PANE1_X1,
    PANE2_X0,
    PANE2_X1,
    OBSTACLE_SEED,
    GOLDEN_APPLE_SPAWN_CHANCE,
)


class GameState:
    """Contains all game state data"""

    def __init__(self):
        self.pane1 = Pane(PANE1_X0, PANE1_X1)
        self.pane2 = Pane(PANE2_X0, PANE2_X1)

        self.snake1 = None
        self.snake2 = None
        self.obstacles = None
        self.apples = []

        self.camera_y_p1 = 0.0
        self.camera_y_p2 = 0.0
        self.winner_text = None
        self.minigame_triggered = False

        # Score tracking (persists across rounds)
        self.score_p1 = 0
        self.score_p2 = 0

        self.reset()

    def reset(self):
        """Reset game to initial state"""
        # Load any customized player colors
        colors = load_player_colors()

        # Create snakes with customized colors and names
        self.snake1 = Snake(
            self.pane1,
            (self.pane1.x0 + self.pane1.x1) // 2,
            0,
            colors["P1"]["body"],
            colors["P1"]["head"],
            colors["P1"].get("name", "P1"),
        )
        self.snake2 = Snake(
            self.pane2,
            (self.pane2.x0 + self.pane2.x1) // 2,
            0,
            colors["P2"]["body"],
            colors["P2"]["head"],
            colors["P2"].get("name", "P2"),
        )

        # Create obstacles
        self.obstacles = Obstacles()
        for _ in range(OBSTACLE_SEED):
            x = self.pane1.rand_x() if random.random() < 0.5 else self.pane2.rand_x()
            y = random.randint(-80, -30)
            self.obstacles.add(x, y)

        # Create initial apples
        self.apples = []
        for _ in range(10):
            pane = self.pane1 if random.random() < 0.5 else self.pane2
            occupied = self.obstacles.blocks.copy()
            pos = pane.get_empty_cell(occupied, -100, -10)
            if pos:
                self.apples.append(Apple(pos[0], pos[1]))

        # Reset camera and state
        self.camera_y_p1 = 0.0
        self.camera_y_p2 = 0.0
        self.winner_text = None
        self.minigame_triggered = False

    def spawn_apple(self):
        """Spawn a new apple in a random pane"""
        pane = self.pane1 if random.random() < 0.5 else self.pane2
        occupied = self.obstacles.blocks.copy()
        occupied.update((a.x, a.y) for a in self.apples)
        furthest_y = min(self.snake1.head[1], self.snake2.head[1])
        pos = pane.get_empty_cell(occupied, furthest_y - 60, furthest_y - 10)
        if pos:
            is_golden = random.random() < GOLDEN_APPLE_SPAWN_CHANCE
            self.apples.append(Apple(pos[0], pos[1], is_golden))

    def cleanup_offscreen_items(self):
        """Remove off-screen obstacles and apples"""
        screen_bottom = max(self.camera_y_p1, self.camera_y_p2) + 35  # GRID_H + 5
        self.obstacles.cleanup(screen_bottom)

        min_camera = min(self.camera_y_p1, self.camera_y_p2)
        self.apples = [a for a in self.apples if a.y > min_camera - 5]
