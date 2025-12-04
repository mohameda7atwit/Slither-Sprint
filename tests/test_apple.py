"""
Tests for Apple model
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.apple import Apple


class TestApple(unittest.TestCase):
    """Test cases for Apple model"""

    def test_red_apple_initialization(self):
        """Test red apple initializes correctly"""
        apple = Apple(5, 10)
        self.assertEqual(apple.x, 5)
        self.assertEqual(apple.y, 10)
        self.assertFalse(apple.is_golden)

    def test_golden_apple_initialization(self):
        """Test golden apple initializes correctly"""
        apple = Apple(7, 15, is_golden=True)
        self.assertEqual(apple.x, 7)
        self.assertEqual(apple.y, 15)
        self.assertTrue(apple.is_golden)

    def test_apple_position_property(self):
        """Test apple position returns correct tuple"""
        apple = Apple(3, 8)
        self.assertEqual(apple.position, (3, 8))

    def test_apple_position_matches_coordinates(self):
        """Test position property matches x, y coordinates"""
        apple = Apple(12, 25)
        pos = apple.position
        self.assertEqual(pos[0], apple.x)
        self.assertEqual(pos[1], apple.y)


if __name__ == "__main__":
    unittest.main()