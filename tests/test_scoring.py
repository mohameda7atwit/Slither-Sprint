"""
Tests for scoring system
"""

import unittest
import sys
import os
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.game_state import GameState
from slither_sprint.controller.game_controller import GameController
from slither_sprint.config import FINISH_LINE_DISTANCE, WIDTH, HEIGHT


class TestScoring(unittest.TestCase):
    """Test cases for scoring system"""

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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.controller = GameController()

    def test_score_initialization(self):
        """Test scores start at 0"""
        self.assertEqual(self.game_state.score_p1, 0)
        self.assertEqual(self.game_state.score_p2, 0)

    def test_score_persists_after_reset(self):
        """Test scores persist across game resets"""
        self.game_state.score_p1 = 5
        self.game_state.score_p2 = 3
        self.game_state.reset()

        # Scores should persist after reset
        self.assertEqual(self.game_state.score_p1, 5)
        self.assertEqual(self.game_state.score_p2, 3)

    def test_p1_wins_by_finish_line(self):
        """Test P1 score increments when reaching finish line"""
        initial_score = self.controller.game_state.score_p1

        # Manually move P1 to finish line
        self.controller.game_state.snake1.body[0] = (10, FINISH_LINE_DISTANCE - 1)

        # Check win conditions
        self.controller._check_win_conditions()

        self.assertEqual(self.controller.game_state.score_p1, initial_score + 1)
        self.assertIsNotNone(self.controller.game_state.winner_text)

    def test_p2_wins_by_finish_line(self):
        """Test P2 score increments when reaching finish line"""
        initial_score = self.controller.game_state.score_p2

        # Manually move P2 to finish line
        self.controller.game_state.snake2.body[0] = (30, FINISH_LINE_DISTANCE - 1)

        # Check win conditions
        self.controller._check_win_conditions()

        self.assertEqual(self.controller.game_state.score_p2, initial_score + 1)
        self.assertIsNotNone(self.controller.game_state.winner_text)

    def test_p1_wins_by_p2_crash(self):
        """Test P1 score increments when P2 crashes"""
        initial_score = self.controller.game_state.score_p1

        # Kill P2
        self.controller.game_state.snake2.alive = False

        # Check win conditions
        self.controller._check_win_conditions()

        self.assertEqual(self.controller.game_state.score_p1, initial_score + 1)
        self.assertIn("P1 wins", self.controller.game_state.winner_text)

    def test_p2_wins_by_p1_crash(self):
        """Test P2 score increments when P1 crashes"""
        initial_score = self.controller.game_state.score_p2

        # Kill P1
        self.controller.game_state.snake1.alive = False

        # Check win conditions
        self.controller._check_win_conditions()

        self.assertEqual(self.controller.game_state.score_p2, initial_score + 1)
        self.assertIn("P2 wins", self.controller.game_state.winner_text)

    def test_draw_no_score_change(self):
        """Test no score change on draw"""
        initial_p1 = self.controller.game_state.score_p1
        initial_p2 = self.controller.game_state.score_p2

        # Kill both snakes
        self.controller.game_state.snake1.alive = False
        self.controller.game_state.snake2.alive = False

        # Check win conditions
        self.controller._check_win_conditions()

        # Scores should remain the same
        self.assertEqual(self.controller.game_state.score_p1, initial_p1)
        self.assertEqual(self.controller.game_state.score_p2, initial_p2)
        self.assertIn("Draw", self.controller.game_state.winner_text)

    def test_score_only_increments_once(self):
        """Test score only increments once per win"""
        initial_score = self.controller.game_state.score_p1

        # Kill P2
        self.controller.game_state.snake2.alive = False

        # Check win conditions multiple times
        self.controller._check_win_conditions()
        self.controller._check_win_conditions()
        self.controller._check_win_conditions()

        # Score should only increment once
        self.assertEqual(self.controller.game_state.score_p1, initial_score + 1)

    def test_multiple_rounds_score_accumulation(self):
        """Test scores accumulate over multiple rounds"""
        # Round 1: P1 wins
        self.controller.game_state.snake2.alive = False
        self.controller._check_win_conditions()
        self.assertEqual(self.controller.game_state.score_p1, 1)
        self.assertEqual(self.controller.game_state.score_p2, 0)

        # Reset for round 2
        self.controller.game_state.reset()

        # Round 2: P2 wins
        self.controller.game_state.snake1.alive = False
        self.controller._check_win_conditions()
        self.assertEqual(self.controller.game_state.score_p1, 1)
        self.assertEqual(self.controller.game_state.score_p2, 1)

        # Reset for round 3
        self.controller.game_state.reset()

        # Round 3: P1 wins again
        self.controller.game_state.snake2.alive = False
        self.controller._check_win_conditions()
        self.assertEqual(self.controller.game_state.score_p1, 2)
        self.assertEqual(self.controller.game_state.score_p2, 1)


if __name__ == "__main__":
    unittest.main()
