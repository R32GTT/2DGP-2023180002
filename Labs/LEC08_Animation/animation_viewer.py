"""Play Aseprite-tagged animations from player.json with Pico2D.

Each JSON frame provides its own source rectangle and duration. Animation
groups come from ``meta.frameTags`` and play in tag order.
"""

import json
import os
import time
from dataclasses import dataclass

from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
DEFAULT_JSON = "player.json"
REPEATS_PER_ANIMATION = 5
INTER_ANIMATION_PAUSE = 1.0
LOOP_DELAY = 0.01


@dataclass(frozen=True)
class Frame:
    name: str
    x: int
    y: int
    width: int
    height: int
    duration: float


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple


class AnimationFormatError(ValueError):
    """Raised when the animation JSON does not describe usable frames."""


def _resolve_manifest_path(json_path=None):
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_JSON)
    return os.path.abspath(os.fspath(json_path))


def _require_object(value, description):
    if not isinstance(value, dict):
        raise AnimationFormatError(f"{description} must be a JSON object")
    return value




def animation_load_json():
    pass

open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
