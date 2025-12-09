"""
Simple settings persistence for player customization.
"""

import json
from pathlib import Path
from typing import Dict, Tuple

from config import P1_COLOR, P1_HEAD, P2_COLOR, P2_HEAD


SETTINGS_PATH = Path(__file__).resolve().parent / "player_settings.json"


Color = Tuple[int, int, int]

# Preset color pairs (body, head) that both players can choose from
COLOR_PRESETS: Tuple[Tuple[Color, Color], ...] = (
    ((40, 220, 120), (20, 255, 160)),  # bright green
    ((80, 150, 255), (120, 200, 255)),  # blue
    ((255, 120, 80), (255, 180, 140)),  # orange
    ((200, 80, 200), (240, 160, 240)),  # purple
    ((255, 220, 60), (255, 255, 140)),  # yellow
    ((80, 255, 200), (160, 255, 230)),  # aqua
    ((255, 100, 190), (255, 170, 220)),  # pink
    ((160, 120, 255), (210, 180, 255)),  # violet
    ((120, 220, 60), (190, 255, 120)),  # lime
    ((255, 180, 60), (255, 220, 120)),  # gold
)


def _validate_color(value) -> Color:
    if (
        isinstance(value, (list, tuple))
        and len(value) == 3
        and all(isinstance(c, int) and 0 <= c <= 255 for c in value)
    ):
        return int(value[0]), int(value[1]), int(value[2])
    return (255, 255, 255)


def load_player_colors() -> Dict[str, Dict[str, Color]]:
    """Load player color and name settings or return defaults."""
    if not SETTINGS_PATH.exists():
        return {
            "P1": {"body": P1_COLOR, "head": P1_HEAD, "name": "P1"},
            "P2": {"body": P2_COLOR, "head": P2_HEAD, "name": "P2"},
        }

    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {
            "P1": {"body": P1_COLOR, "head": P1_HEAD, "name": "P1"},
            "P2": {"body": P2_COLOR, "head": P2_HEAD, "name": "P2"},
        }

    p1 = data.get("P1", {})
    p2 = data.get("P2", {})
    return {
        "P1": {
            "body": _validate_color(p1.get("body", P1_COLOR)),
            "head": _validate_color(p1.get("head", P1_HEAD)),
            "name": str(p1.get("name", "P1"))[:16],
        },
        "P2": {
            "body": _validate_color(p2.get("body", P2_COLOR)),
            "head": _validate_color(p2.get("head", P2_HEAD)),
            "name": str(p2.get("name", "P2"))[:16],
        },
    }


def save_player_colors(colors: Dict[str, Dict[str, Color]]) -> None:
    """Persist player colors to disk."""
    try:
        SETTINGS_PATH.write_text(json.dumps(colors, indent=2), encoding="utf-8")
    except Exception:
        # Failing to save settings should not crash the game
        pass
