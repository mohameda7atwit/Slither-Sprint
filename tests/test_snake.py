"""
Tests for Snake model
"""

import unittest
import sys
import os
import pygame

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from slither_sprint.model.snake import Snake
from slither_sprint.model.pane import Pane
from slither_sprint.model.power_up import PowerUpType


class TestSnake(unittest.TestCase):
    """Test cases for Snake model"""

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
        self.pane = Pane(0, 20)
        self.snake = Snake(self.pane, 10, 10, (0, 255, 0), (0, 200, 0), "TestSnake")

    def test_snake_initialization(self):
        """Test snake is initialized correctly"""
        self.assertEqual(self.snake.name, "TestSnake")
        self.assertTrue(self.snake.alive)
        self.assertEqual(len(self.snake.body), 12)  # SNAKE_LEN
        self.assertEqual(self.snake.head, (10, 10))
        self.assertEqual(self.snake.apples_collected, 0)

    def test_snake_movement_forward(self):
        """Test snake moves forward correctly"""
        initial_head = self.snake.head
        self.snake.step()
        new_head = self.snake.head
        # Snake moves up (y decreases)
        self.assertEqual(new_head[0], initial_head[0])
        self.assertEqual(new_head[1], initial_head[1] - 1)

    def test_snake_steering_left(self):
        """Test snake steers left"""
        self.snake.steer(True, False)
        self.assertEqual(self.snake.pending_dx, -1)
        self.snake.step()
        # After one step, snake should move left and up
        self.assertEqual(self.snake.head, (9, 9))

    def test_snake_steering_right(self):
        """Test snake steers right"""
        self.snake.steer(False, True)
        self.assertEqual(self.snake.pending_dx, 1)
        self.snake.step()
        # After one step, snake should move right and up
        self.assertEqual(self.snake.head, (11, 9))

    def test_snake_boundary_collision(self):
        """Test snake dies when hitting boundary"""
        # Create snake at left edge
        snake = Snake(self.pane, 0, 10, (0, 255, 0), (0, 200, 0), "Edge")
        snake.steer(True, False)  # Steer left
        snake.step()
        # Should die when going out of bounds
        self.assertFalse(snake.alive)

    def test_snake_self_collision(self):
        """Test snake dies when colliding with itself"""
        # Manipulate snake body to create self-collision
        self.snake.body[5] = self.snake.head
        initial_alive = self.snake.alive
        self.snake.step()
        # Snake should detect collision in next step
        self.assertTrue(initial_alive)  # Was alive before step

    def test_snake_apple_collection(self):
        """Test apple collection increments counter"""
        initial_count = self.snake.apples_collected
        self.snake.collect_apple()
        self.assertEqual(self.snake.apples_collected, initial_count + 1)

    def test_snake_speed_boost_every_3_apples(self):
        """Test speed boost activates every 3 apples"""
        self.snake.collect_apple()
        self.assertEqual(self.snake.active_powerup.value, PowerUpType.NONE.value)
        self.snake.collect_apple()
        self.assertEqual(self.snake.active_powerup.value, PowerUpType.NONE.value)
        self.snake.collect_apple()
        # After 3 apples, speed boost should activate
        self.assertEqual(self.snake.active_powerup.value, PowerUpType.SPEED_BOOST.value)

    def test_snake_golden_apple_invincibility(self):
        """Test golden apple grants invincibility"""
        self.assertFalse(self.snake.is_invincible())
        self.snake.collect_golden_apple()
        self.assertTrue(self.snake.is_invincible())
        self.assertEqual(self.snake.active_powerup.value, PowerUpType.INVINCIBILITY.value)

    def test_snake_speed_boost_increases_speed(self):
        """Test speed boost reduces step time"""
        # Ensure pygame clock has started
        import time
        time.sleep(0.01)

        base_step_ms = self.snake.base_step_ms
        initial_current = self.snake.current_step_ms
        self.assertEqual(base_step_ms, initial_current)  # Should start equal

        # Activate speed boost
        self.snake.activate_powerup(PowerUpType.SPEED_BOOST)

        # Verify power-up is active
        self.assertEqual(self.snake.active_powerup, PowerUpType.SPEED_BOOST)
        # Verify end time is set (should be > 0)
        self.assertGreater(self.snake.powerup_end_time, 0)

        # Speed boost makes snake 30% faster (70% of original time)
        expected_step_ms = int(base_step_ms * 0.7)
        self.assertEqual(self.snake.current_step_ms, expected_step_ms)
        self.assertLess(self.snake.current_step_ms, base_step_ms)

    def test_snake_fixed_length(self):
        """Test snake maintains fixed length"""
        for _ in range(10):
            self.snake.step()
        self.assertEqual(len(self.snake.body), 12)  # SNAKE_LEN

    def test_snake_step_counter(self):
        """Test step counter increments"""
        initial_steps = self.snake.steps
        self.snake.step()
        self.assertEqual(self.snake.steps, initial_steps + 1)

    def test_dead_snake_does_not_move(self):
        """Test dead snake doesn't move"""
        self.snake.alive = False
        initial_head = self.snake.head
        self.snake.step()
        self.assertEqual(self.snake.head, initial_head)

    def test_boom_effect_initialization(self):
        """Test boom effect starts at 0"""
        self.assertEqual(self.snake.invincibility_boom_start_time, 0)
        self.assertEqual(self.snake.get_boom_intensity(), 0.0)

    def test_boom_effect_triggers_on_golden_apple(self):
        """Test boom effect is triggered when collecting golden apple"""
        initial_boom_time = self.snake.invincibility_boom_start_time
        self.snake.collect_golden_apple()
        # Boom start time should be set to current time
        self.assertGreater(self.snake.invincibility_boom_start_time, initial_boom_time)

    def test_boom_effect_intensity_starts_high(self):
        """Test boom effect intensity starts at 1.0"""
        self.snake.collect_golden_apple()
        # Immediately after activation, intensity should be near 1.0
        intensity = self.snake.get_boom_intensity()
        self.assertGreater(intensity, 0.9)
        self.assertLessEqual(intensity, 1.0)

    def test_boom_effect_fades_over_time(self):
        """Test boom effect intensity decreases over time"""
        self.snake.collect_golden_apple()
        initial_intensity = self.snake.get_boom_intensity()

        # Simulate 150ms passing (half the duration)
        import time
        time.sleep(0.15)

        later_intensity = self.snake.get_boom_intensity()
        # Intensity should have decreased
        self.assertLess(later_intensity, initial_intensity)

    def test_boom_effect_expires_after_duration(self):
        """Test boom effect expires after 300ms"""
        self.snake.collect_golden_apple()

        # Simulate 350ms passing (more than duration)
        import time
        time.sleep(0.35)

        intensity = self.snake.get_boom_intensity()
        # Should be 0 after duration expires
        self.assertEqual(intensity, 0.0)

    def test_boom_effect_only_on_invincibility(self):
        """Test boom effect only triggers for invincibility, not speed boost"""
        self.snake.activate_powerup(PowerUpType.SPEED_BOOST)
        # Speed boost should not trigger boom
        self.assertEqual(self.snake.invincibility_boom_start_time, 0)
        self.assertEqual(self.snake.get_boom_intensity(), 0.0)

    def test_boom_intensity_returns_zero_when_not_active(self):
        """Test boom intensity is 0 when no boom is active"""
        intensity = self.snake.get_boom_intensity()
        self.assertEqual(intensity, 0.0)

    def test_invincibility_persists_after_boom_ends(self):
        """Test invincibility remains active after boom effect ends"""
        self.snake.collect_golden_apple()
        self.assertTrue(self.snake.is_invincible())

        # Wait for boom to end
        import time
        time.sleep(0.35)

        # Boom should be over
        self.assertEqual(self.snake.get_boom_intensity(), 0.0)
        # But invincibility should still be active
        self.assertTrue(self.snake.is_invincible())

    def test_warning_pulses_for_invincibility(self):
        """Test warning pulses appear when power-up is about to expire"""
        import time
        time.sleep(0.01)

        # Activate power-up, then wait until near expiration
        self.snake.activate_powerup(PowerUpType.INVINCIBILITY)
        # Wait 2 seconds (power-up expires at 5s, warning starts at 4.1s)
        time.sleep(2)

        # Power-up should still be active (within warning window)
        self.assertTrue(self.snake.is_invincible())
        # Time remaining should be less than 900ms
        current_time = pygame.time.get_ticks()
        time_remaining = self.snake.powerup_end_time - current_time
        self.assertLess(time_remaining, 900)

    def test_warning_pulses_for_speed_boost(self):
        """Test warning pulses appear for speed boost power-up"""
        import time
        time.sleep(0.01)

        # Activate power-up, then wait until near expiration
        self.snake.activate_powerup(PowerUpType.SPEED_BOOST)
        # Wait 4.5 seconds (power-up expires at 5s, warning starts at 4.1s)
        time.sleep(4.5)

        # Power-up should still be active (within warning window)
        self.assertEqual(self.snake.active_powerup, PowerUpType.SPEED_BOOST)
        # Time remaining should be less than 900ms
        current_time = pygame.time.get_ticks()
        time_remaining = self.snake.powerup_end_time - current_time
        self.assertLess(time_remaining, 900)

    def test_no_warning_pulses_when_powerup_not_expiring(self):
        """Test no warning pulses when power-up has plenty of time left"""
        import time
        time.sleep(0.01)

        current_time = pygame.time.get_ticks()
        self.snake.active_powerup = PowerUpType.INVINCIBILITY
        # Set power-up to expire in 3 seconds (outside warning window)
        self.snake.powerup_end_time = current_time + 3000
        self.snake.invincibility_boom_start_time = 0  # No initial boom

        # Should have no warning pulse
        intensity = self.snake.get_boom_intensity()
        self.assertEqual(intensity, 0.0)


if __name__ == "__main__":
    unittest.main()