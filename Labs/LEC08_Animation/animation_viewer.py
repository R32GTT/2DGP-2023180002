"""Play Aseprite-tagged animations from player.json with Pico2D.

Each JSON frame provides its own source rectangle and duration. Animation
groups come from ``meta.frameTags`` and play in tag order.
"""

import json
import math
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
    duration: float = 0.1


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


def _parse_frames(data, sheet_width, sheet_height):
    frame_records = _require_object(data.get("frames"), "frames")
    if not frame_records:
        raise AnimationFormatError("frames must contain at least one frame")

    frames = []
    for frame_name, record in frame_records.items():
        if not isinstance(frame_name, str) or not frame_name:
            raise AnimationFormatError("frame names must be non-empty strings")
        record = _require_object(record, f"frame '{frame_name}'")
        rect = _require_object(record.get("frame"), f"frame '{frame_name}'.frame")
        x = _read_non_negative_int(rect.get("x"), f"frame '{frame_name}'.x")
        y = _read_non_negative_int(rect.get("y"), f"frame '{frame_name}'.y")
        width = _read_positive_int(rect.get("w"), f"frame '{frame_name}'.w")
        height = _read_positive_int(rect.get("h"), f"frame '{frame_name}'.h")
        if x + width > sheet_width or y + height > sheet_height:
            raise AnimationFormatError(
                f"frame '{frame_name}' extends beyond the sprite sheet"
            )
        duration_ms = record.get("duration", 100)
        if (
            isinstance(duration_ms, bool)
            or not isinstance(duration_ms, (int, float))
            or not math.isfinite(duration_ms)
            or duration_ms <= 0
        ):
            raise AnimationFormatError(
                f"frame '{frame_name}'.duration must be a positive number"
            )
        frames.append(Frame(frame_name, x, y, width, height, duration_ms / 1000.0))
    return tuple(frames)


def _parse_animations(meta, frames):
    tags = meta.get("frameTags")
    if not isinstance(tags, list) or not tags:
        raise AnimationFormatError("meta.frameTags must contain animation tags")

    animations = []
    names = set()
    for tag_index, raw_tag in enumerate(tags):
        tag = _require_object(raw_tag, f"meta.frameTags[{tag_index}]")
        name = tag.get("name")
        if not isinstance(name, str) or not name.strip():
            raise AnimationFormatError(f"meta.frameTags[{tag_index}].name is required")
        if name in names:
            raise AnimationFormatError(f"animation tag '{name}' is duplicated")
        start = _read_non_negative_int(
            tag.get("from"), f"animation '{name}'.from"
        )
        end = _read_non_negative_int(tag.get("to"), f"animation '{name}'.to")
        if start > end or end >= len(frames):
            raise AnimationFormatError(
                f"animation '{name}' has an invalid frame range {start}..{end}"
            )
        animation_frames = frames[start : end + 1]
        direction = tag.get("direction", "forward")
        if direction == "reverse":
            animation_frames = animation_frames[::-1]
        elif direction == "pingpong":
            animation_frames += animation_frames[-2:0:-1]
        elif direction == "pingpong_reverse":
            animation_frames = animation_frames[::-1]
            animation_frames += animation_frames[-2:0:-1]
        elif direction != "forward":
            raise AnimationFormatError(
                f"animation '{name}' has unsupported direction '{direction}'"
            )
        animations.append(Animation(name, animation_frames))
        names.add(name)

    return tuple(animations)


def animation_load_json(json_path=None):
    manifest_path, data = _load_manifest(json_path)
    meta, image_name, sheet_width, sheet_height = _read_sheet_metadata(data)
    frames = _parse_frames(data, sheet_width, sheet_height)
    animations = _parse_animations(meta, frames)

    sheet_path = os.path.join(os.path.dirname(manifest_path), image_name)
    if not os.path.isfile(sheet_path):
        raise AnimationFormatError(f"sprite sheet not found: '{sheet_path}'")
    return load_image(sheet_path), animations




open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
