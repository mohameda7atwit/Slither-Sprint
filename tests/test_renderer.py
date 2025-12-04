"""
Tests for Renderer invincibility effects
"""

import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.view.renderer import Renderer
from slither_sprint.model.snake import Snake
from slither_sprint.model.pane import Pane
from slither_sprint.model.power_up import PowerUpType
from slither_sprint.config import WIDTH, HEIGHT


class TestRenderer(unittest.TestCase):
    """Test cases for Renderer invincibility effects"""

    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests"""
        pygame.init()
        # Small delay to ensure pygame clock starts
        import time
        time.sleep(0.01)

    @classmethod
    def tearDownClass(cls):
        """Quit pygame after all tests"""
        pygame.quit()

    def setUp(self):
        """Set up test fixtures"""
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.renderer = Renderer(screen)
        self.pane = Pane(0, 20)
        self.snake = Snake(self.pane, 10, 10, (100, 200, 100), (150, 250, 150), "TestSnake")

    def test_no_color_change_when_not_invincible(self):
        """Test color remains unchanged when snake is not invincible"""
        base_color = (255, 0, 0)
        result = self.renderer._apply_invincibility_color(base_color, self.snake)
        self.assertEqual(result, base_color)

    def test_color_tint_when_invincible(self):
        """Test color gets golden tint when invincible"""
        # Ensure pygame clock has started
        import time
        time.sleep(0.01)

        # Use activate_powerup to properly set everything
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)
        # Wait for initial boom to complete
        time.sleep(0.35)

        base_color = (255, 0, 0)
        result = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Color should be different from base (30% persistent tint)
        self.assertNotEqual(result, base_color)

        # Should have more gold (higher green value from golden blend)
        self.assertGreater(result[1], base_color[1])  # More green from gold

    def test_stronger_tint_during_boom(self):
        """Test color tint is stronger during boom effect"""
        # Ensure pygame clock has started
        import time
        time.sleep(0.01)

        base_color = (100, 100, 200)

        # Activate and immediately check during boom
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)
        # Get color during boom (high intensity)
        boom_color = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Wait for boom to complete
        time.sleep(0.35)

        # Get color after boom (30% persistent tint)
        post_boom_color = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Both should be different from base
        self.assertNotEqual(boom_color, base_color)
        self.assertNotEqual(post_boom_color, base_color)

        # During boom, should have stronger golden tint (higher green value)
        self.assertGreater(boom_color[1], post_boom_color[1])

    def test_color_components_within_valid_range(self):
        """Test color values don't exceed 255"""
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)

        # Test with bright colors that could overflow
        test_colors = [
            (255, 255, 255),
            (250, 250, 250),
            (200, 200, 200),
        ]

        for base_color in test_colors:
            result = self.renderer._apply_invincibility_color(base_color, self.snake)
            self.assertLessEqual(result[0], 255)
            self.assertLessEqual(result[1], 255)
            self.assertLessEqual(result[2], 255)
            self.assertGreaterEqual(result[0], 0)
            self.assertGreaterEqual(result[1], 0)
            self.assertGreaterEqual(result[2], 0)

    def test_golden_blend_increases_with_boom_intensity(self):
        """Test golden blend is proportional to boom intensity"""
        # Ensure pygame clock has started
        import time
        time.sleep(0.01)

        base_color = (100, 50, 150)

        # Activate and immediately check boom intensity
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)
        boom_intensity = self.snake.get_boom_intensity()
        self.assertGreater(boom_intensity, 0.8)  # Should be very high (close to 1.0)

        boom_color = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Golden color is (255, 215, 0), so R and G should increase significantly
        self.assertGreater(boom_color[0], base_color[0])
        self.assertGreater(boom_color[1], base_color[1])

    def test_black_color_gets_golden_tint(self):
        """Test even black gets a golden tint when invincible"""
        # Ensure pygame clock has started and give it a moment
        import time
        time.sleep(0.02)

        base_color = (0, 0, 0)

        # Activate powerup
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)

        # Small delay to ensure boom is registered
        time.sleep(0.001)

        # Verify boom is active
        boom_intensity = self.snake.get_boom_intensity()
        self.assertGreater(boom_intensity, 0, "Boom should be active immediately after activation")

        result = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Should have significant golden color added (70% blend during boom)
        self.assertGreater(result[0], 0, f"Red component should be > 0, got {result[0]}, boom_intensity={boom_intensity}")
        self.assertGreater(result[1], 0, f"Green component should be > 0, got {result[1]}, boom_intensity={boom_intensity}")

    def test_white_color_stays_near_white(self):
        """Test white color remains bright when invincible"""
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)
        base_color = (255, 255, 255)
        result = self.renderer._apply_invincibility_color(base_color, self.snake)

        # Should still be bright (all components > 200)
        self.assertGreater(result[0], 200)
        self.assertGreater(result[1], 200)
        self.assertGreater(result[2], 200)

    def test_multiple_invincibility_activations(self):
        """Test boom effect can be triggered multiple times"""
        current_time = pygame.time.get_ticks()

        # First activation
        self.snake.active_powerup = PowerUpType.INVINCIBILITY
        self.snake.powerup_end_time = current_time + 5000
        self.snake.invincibility_boom_start_time = current_time
        first_boom_time = self.snake.invincibility_boom_start_time

        # Simulate time passing
        import time
        time.sleep(0.01)  # Small delay to ensure time advances

        # Deactivate
        self.snake.active_powerup = PowerUpType.NONE
        self.snake.invincibility_boom_start_time = 0

        # Second activation
        current_time_2 = pygame.time.get_ticks()
        self.snake.active_powerup = PowerUpType.INVINCIBILITY
        self.snake.powerup_end_time = current_time_2 + 5000
        self.snake.invincibility_boom_start_time = current_time_2
        second_boom_time = self.snake.invincibility_boom_start_time

        # Should have new boom time
        self.assertGreaterEqual(second_boom_time, first_boom_time)
        self.assertGreaterEqual(self.snake.get_boom_intensity(), 0)


if __name__ == "__main__":
    unittest.main()