"""
Snake model - represents a player's snake
"""

import pygame
from model.pane import Pane
from model.power_up import PowerUpType
from config import (
    SNAKE_LEN,
    STEP_MS,
    SPEED_BOOST_DURATION,
    INVINCIBILITY_DURATION,
    APPLES_FOR_SPEED_BOOST,
)


class Snake:
    """Represents a player's snake with movement and power-up logic"""

    def __init__(self, pane: Pane, x: int, y: int, body_col, head_col, name: str):
        self.pane = pane
        # Body segments, index 0 is the head
        self.body = [(x, y + i) for i in range(SNAKE_LEN)]
        # Movement: always moving up (negative Y). X shifts are lane changes.
        self.dx, self.dy = 0, -1
        self.pending_dx = 0  # one-step horizontal move requested from input
        self.body_col = body_col
        self.head_col = head_col
        self.name = name
        self.alive = True
        self.steps = 0
        self.apples_collected = 0
        self.active_powerup = PowerUpType.NONE
        self.powerup_end_time = 0
        self.base_step_ms = STEP_MS
        self.current_step_ms = STEP_MS

        # History of head positions so the body can follow the path smoothly
        # Most recent positions are at the end of the list.
        self.history = [self.body[0]]
        # How many history samples to skip between each body segment
        self._history_gap = 1

    @property
    def head(self):
        """Get the head position of the snake"""
        return self.body[0]

    def steer(self, left: bool, right: bool):
        """
        Update steering direction

        Args:
            left: True if steering left
            right: True if steering right
        """
        # We interpret steering as a one-cell lane change request.
        if left:
            self.pending_dx = -1
        elif right:
            self.pending_dx = 1

    def collect_apple(self):
        """Collect a red apple and check for speed boost"""
        self.apples_collected += 1
        if self.apples_collected % APPLES_FOR_SPEED_BOOST == 0:
            self.activate_powerup(PowerUpType.SPEED_BOOST)

    def collect_golden_apple(self):
        """Collect a golden apple for invincibility"""
        self.activate_powerup(PowerUpType.INVINCIBILITY)

    def activate_powerup(self, powerup_type: PowerUpType):
        """
        Activate a power-up

        Args:
            powerup_type: Type of power-up to activate
        """
        current_time = pygame.time.get_ticks()
        self.active_powerup = powerup_type

        if powerup_type == PowerUpType.SPEED_BOOST:
            self.powerup_end_time = current_time + SPEED_BOOST_DURATION
            self.current_step_ms = int(self.base_step_ms * 0.7)  # 30% faster
        elif powerup_type == PowerUpType.INVINCIBILITY:
            self.powerup_end_time = current_time + INVINCIBILITY_DURATION
            self.current_step_ms = self.base_step_ms
        else:
            self.powerup_end_time = 0
            self.current_step_ms = self.base_step_ms

    def update_powerups(self):
        """Check if power-ups have expired"""
        if self.active_powerup != PowerUpType.NONE:
            if pygame.time.get_ticks() >= self.powerup_end_time:
                self.active_powerup = PowerUpType.NONE
                self.current_step_ms = self.base_step_ms

    def is_invincible(self):
        """Check if snake is currently invincible"""
        return self.active_powerup == PowerUpType.INVINCIBILITY

    def step(self):
        """Move the snake forward one step using head-path history."""
        if not self.alive:
            return

        self.steps += 1

        # Record current head position before moving so the body can follow it
        hx, hy = self.head
        self.history.append((hx, hy))

        # Apply any pending horizontal move for this step only
        move_dx = self.pending_dx
        self.pending_dx = 0

        nx, ny = hx + move_dx, hy + self.dy

        # Check boundary collision
        if not self.pane.inside(nx, ny):
            self.alive = False
            return

        # Move head to its new position
        self.body[0] = (nx, ny)

        # Update the rest of the body to follow the recorded head path.
        # Each segment looks further back in the history so they are spaced apart.
        for i in range(1, len(self.body)):
            # How far back in history this segment should look
            offset = i * self._history_gap
            if offset <= len(self.history):
                self.body[i] = self.history[-offset]
            else:
                # Not enough history yet, just extend from previous segment
                self.body[i] = self.body[i - 1]

        # Trim history so it doesn't grow without bound. We only need enough
        # samples to cover the current snake length plus a small buffer.
        max_history = (len(self.body) + 1) * self._history_gap
        if len(self.history) > max_history:
            self.history = self.history[-max_history:]

        # Check self-collision
        if self.head in self.body[1:]:
            self.alive = False
