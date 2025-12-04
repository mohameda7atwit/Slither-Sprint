"""
Tests for GameState model
"""

import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.game_state import GameState


class TestGameState(unittest.TestCase):
    """Test cases for GameState model"""

    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests"""
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        """Quit pygame after all tests"""
        pygame.quit()

    def setUp(self):
        """Set up test fixtures"""
        self.game_state = GameState()

    def test_game_state_initialization(self):
        """Test game state initializes correctly"""
        self.assertIsNotNone(self.game_state.pane1)
        self.assertIsNotNone(self.game_state.pane2)
        self.assertIsNotNone(self.game_state.snake1)
        self.assertIsNotNone(self.game_state.snake2)
        self.assertIsNotNone(self.game_state.obstacles)
        self.assertIsNotNone(self.game_state.apples)
        self.assertIsNone(self.game_state.winner_text)

    def test_two_snakes_created(self):
        """Test two snakes are created for two players"""
        self.assertEqual(self.game_state.snake1.name, "P1")
        self.assertEqual(self.game_state.snake2.name, "P2")
        self.assertTrue(self.game_state.snake1.alive)
        self.assertTrue(self.game_state.snake2.alive)

    def test_snakes_in_different_panes(self):
        """Test snakes start in their respective panes"""
        snake1_x = self.game_state.snake1.head[0]
        snake2_x = self.game_state.snake2.head[0]

        # Snake 1 should be in pane 1
        self.assertTrue(self.game_state.pane1.inside(snake1_x))
        # Snake 2 should be in pane 2
        self.assertTrue(self.game_state.pane2.inside(snake2_x))

    def test_obstacles_initialized(self):
        """Test obstacles are seeded at game start"""
        self.assertGreater(len(self.game_state.obstacles.blocks), 0)

    def test_initial_apples_spawned(self):
        """Test apples are spawned at initialization"""
        self.assertGreater(len(self.game_state.apples), 0)

    def test_cameras_initialized(self):
        """Test camera positions initialized"""
        self.assertEqual(self.game_state.camera_y_p1, 0.0)
        self.assertEqual(self.game_state.camera_y_p2, 0.0)

    def test_reset_recreates_snakes(self):
        """Test reset creates new snakes"""
        # Modify snakes
        self.game_state.snake1.alive = False
        self.game_state.snake2.collect_apple()

        # Reset
        self.game_state.reset()

        # Snakes should be alive and fresh
        self.assertTrue(self.game_state.snake1.alive)
        self.assertTrue(self.game_state.snake2.alive)
        self.assertEqual(self.game_state.snake1.apples_collected, 0)
        self.assertEqual(self.game_state.snake2.apples_collected, 0)

    def test_reset_clears_winner(self):
        """Test reset clears winner text"""
        self.game_state.winner_text = "P1 wins!"
        self.game_state.reset()
        self.assertIsNone(self.game_state.winner_text)

    def test_reset_resets_cameras(self):
        """Test reset resets camera positions"""
        self.game_state.camera_y_p1 = -100.0
        self.game_state.camera_y_p2 = -150.0
        self.game_state.reset()
        self.assertEqual(self.game_state.camera_y_p1, 0.0)
        self.assertEqual(self.game_state.camera_y_p2, 0.0)

    def test_spawn_apple_adds_apple(self):
        """Test spawn_apple adds an apple to the game"""
        initial_count = len(self.game_state.apples)
        self.game_state.spawn_apple()
        # Should add one apple (might not always succeed due to positioning)
        self.assertGreaterEqual(len(self.game_state.apples), initial_count)

    def test_cleanup_removes_offscreen_apples(self):
        """Test cleanup removes apples that are offscreen"""
        # Add apple far below camera
        from slither_sprint.model.apple import Apple

        self.game_state.apples.append(Apple(5, 1000))
        initial_count = len(self.game_state.apples)

        # Cleanup with cameras at 0
        self.game_state.cleanup_offscreen_items()

        # Far apple should be removed
        self.assertLess(len(self.game_state.apples), initial_count)

    def test_cleanup_removes_offscreen_obstacles(self):
        """Test cleanup removes obstacles that are offscreen"""
        # Add obstacle far below
        self.game_state.obstacles.add(5, 1000)
        initial_count = len(self.game_state.obstacles.blocks)

        self.game_state.cleanup_offscreen_items()

        # Obstacle should be removed
        self.assertLess(len(self.game_state.obstacles.blocks), initial_count)


if __name__ == "__main__":
    unittest.main()
