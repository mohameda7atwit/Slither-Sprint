"""
Tests for GameMode enum
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.game_mode import GameMode


class TestGameMode(unittest.TestCase):
    """Test cases for GameMode enum"""

    def test_game_mode_values(self):
        """Test game mode enum has correct values"""
        self.assertEqual(GameMode.MENU.value, 0)
        self.assertEqual(GameMode.PLAYING.value, 1)
        self.assertEqual(GameMode.PAUSED.value, 2)

    def test_game_mode_members(self):
        """Test all expected game modes exist"""
        modes = [mode.name for mode in GameMode]
        self.assertIn("MENU", modes)
        self.assertIn("PLAYING", modes)
        self.assertIn("PAUSED", modes)

    def test_game_mode_count(self):
        """Test there are exactly 3 game modes"""
        self.assertEqual(len(GameMode), 3)

    def test_game_mode_equality(self):
        """Test game mode equality comparison"""
        mode1 = GameMode.MENU
        mode2 = GameMode.MENU
        mode3 = GameMode.PLAYING

        self.assertEqual(mode1, mode2)
        self.assertNotEqual(mode1, mode3)

    def test_game_mode_identity(self):
        """Test game mode identity"""
        mode = GameMode.PLAYING
        self.assertIs(mode, GameMode.PLAYING)
        self.assertIsNot(mode, GameMode.PAUSED)


if __name__ == "__main__":
    unittest.main()
