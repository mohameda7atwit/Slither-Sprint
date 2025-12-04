"""
Game Mode - defines different game states
"""

from enum import Enum


class GameMode(Enum):
    """Game mode states"""

    MENU = 0
    PLAYING = 1
    PAUSED = 2
