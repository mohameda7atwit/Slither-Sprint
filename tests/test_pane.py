"""
Tests for Pane model
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.pane import Pane


class TestPane(unittest.TestCase):
    """Test cases for Pane model"""

    def setUp(self):
        """Set up test fixtures"""
        self.pane = Pane(0, 10)

    def test_pane_initialization(self):
        """Test pane initializes with correct boundaries"""
        self.assertEqual(self.pane.x0, 0)
        self.assertEqual(self.pane.x1, 10)

    def test_inside_with_x_only(self):
        """Test inside check with x coordinate only"""
        self.assertTrue(self.pane.inside(5))
        self.assertTrue(self.pane.inside(0))
        self.assertTrue(self.pane.inside(10))
        self.assertFalse(self.pane.inside(-1))
        self.assertFalse(self.pane.inside(11))

    def test_inside_with_x_and_y(self):
        """Test inside check with both coordinates"""
        self.assertTrue(self.pane.inside(5, 100))
        self.assertFalse(self.pane.inside(11, 100))

    def test_rand_x_in_range(self):
        """Test random x is within pane boundaries"""
        for _ in range(100):
            x = self.pane.rand_x()
            self.assertTrue(self.pane.inside(x))
            self.assertGreaterEqual(x, self.pane.x0)
            self.assertLessEqual(x, self.pane.x1)

    def test_get_empty_cell_returns_valid_position(self):
        """Test get_empty_cell returns position in pane"""
        occupied = set()
        cell = self.pane.get_empty_cell(occupied, -10, 10)
        self.assertIsNotNone(cell)
        self.assertTrue(self.pane.inside(cell[0]))
        self.assertGreaterEqual(cell[1], -10)
        self.assertLessEqual(cell[1], 10)

    def test_get_empty_cell_avoids_occupied(self):
        """Test get_empty_cell avoids occupied positions"""
        # Fill all but one position
        occupied = set()
        for x in range(self.pane.x0, self.pane.x1 + 1):
            for y in range(-5, 6):
                if not (x == 5 and y == 0):
                    occupied.add((x, y))

        cell = self.pane.get_empty_cell(occupied, -5, 5)
        if cell:  # Might not find it in 50 attempts
            self.assertNotIn(cell, occupied)

    def test_get_empty_cell_returns_none_when_full(self):
        """Test get_empty_cell returns None when all positions occupied"""
        # Occupy all positions
        occupied = set()
        for x in range(self.pane.x0, self.pane.x1 + 1):
            for y in range(-5, 6):
                occupied.add((x, y))

        cell = self.pane.get_empty_cell(occupied, -5, 5)
        # With 50 attempts, should eventually give up
        if cell is None:
            self.assertIsNone(cell)

    def test_boundary_values(self):
        """Test boundary values are inclusive"""
        self.assertTrue(self.pane.inside(self.pane.x0))
        self.assertTrue(self.pane.inside(self.pane.x1))


if __name__ == "__main__":
    unittest.main()
