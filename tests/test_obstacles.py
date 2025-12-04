"""
Tests for Obstacles model and collision detection
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.obstacles import Obstacles


class TestObstacles(unittest.TestCase):
    """Test cases for Obstacles model"""

    def setUp(self):
        """Set up test fixtures"""
        self.obstacles = Obstacles()

    def test_obstacles_initialization(self):
        """Test obstacles initialize empty"""
        self.assertEqual(len(self.obstacles.blocks), 0)

    def test_add_obstacle(self):
        """Test adding obstacles"""
        self.obstacles.add(5, 10)
        self.assertEqual(len(self.obstacles.blocks), 1)
        self.assertIn((5, 10), self.obstacles.blocks)

    def test_add_multiple_obstacles(self):
        """Test adding multiple obstacles"""
        self.obstacles.add(5, 10)
        self.obstacles.add(6, 10)
        self.obstacles.add(7, 10)
        self.assertEqual(len(self.obstacles.blocks), 3)

    def test_collision_detection_hit(self):
        """Test collision detection returns True on hit"""
        self.obstacles.add(5, 10)
        self.assertTrue(self.obstacles.collides((5, 10)))

    def test_collision_detection_miss(self):
        """Test collision detection returns False on miss"""
        self.obstacles.add(5, 10)
        self.assertFalse(self.obstacles.collides((6, 10)))
        self.assertFalse(self.obstacles.collides((5, 11)))

    def test_cleanup_removes_offscreen_obstacles(self):
        """Test cleanup removes obstacles below screen"""
        self.obstacles.add(5, 10)
        self.obstacles.add(6, 50)
        self.obstacles.add(7, 100)

        # Cleanup obstacles with y >= 60
        self.obstacles.cleanup(60)

        # Only obstacles with y < 60 should remain
        self.assertEqual(len(self.obstacles.blocks), 2)
        self.assertIn((5, 10), self.obstacles.blocks)
        self.assertIn((6, 50), self.obstacles.blocks)
        self.assertNotIn((7, 100), self.obstacles.blocks)

    def test_duplicate_obstacles_not_added(self):
        """Test duplicate obstacles aren't added (set behavior)"""
        self.obstacles.add(5, 10)
        self.obstacles.add(5, 10)
        self.assertEqual(len(self.obstacles.blocks), 1)

    def test_cleanup_with_negative_coordinates(self):
        """Test cleanup works with negative coordinates"""
        self.obstacles.add(5, -50)
        self.obstacles.add(6, -10)
        self.obstacles.add(7, 5)

        self.obstacles.cleanup(0)

        # Only negative y coordinates should remain
        self.assertEqual(len(self.obstacles.blocks), 2)
        self.assertIn((5, -50), self.obstacles.blocks)
        self.assertIn((6, -10), self.obstacles.blocks)


if __name__ == "__main__":
    unittest.main()
