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


def _load_manifest(json_path=None):
    path = _resolve_manifest_path(json_path)
    try:
        with open(path, "r", encoding="utf-8") as manifest_file:
            data = json.load(manifest_file)
    except OSError as error:
        raise AnimationFormatError(f"cannot read animation JSON '{path}': {error}") from error
    except json.JSONDecodeError as error:
        raise AnimationFormatError(
            f"invalid JSON in '{path}' at line {error.lineno}, column {error.colno}"
        ) from error
    return path, _require_object(data, "animation JSON")


def _read_non_negative_int(value, description):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AnimationFormatError(f"{description} must be a non-negative integer")
    return value


def _read_positive_int(value, description):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AnimationFormatError(f"{description} must be a positive integer")
    return value


def _read_sheet_metadata(data):
    meta = _require_object(data.get("meta"), "meta")
    size = _require_object(meta.get("size"), "meta.size")
    image_name = meta.get("image")
    if not isinstance(image_name, str) or not image_name.strip():
        raise AnimationFormatError("meta.image must name a sprite sheet")
    sheet_width = _read_positive_int(size.get("w"), "meta.size.w")
    sheet_height = _read_positive_int(size.get("h"), "meta.size.h")
    return meta, image_name, sheet_width, sheet_height




def animation_load_json(json_path=None):
    return _load_manifest(json_path)

open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
