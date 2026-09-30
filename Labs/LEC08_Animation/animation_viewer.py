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


class PlaybackState:
    def __init__(self, animations):
        if not animations or any(not animation.frames for animation in animations):
            raise AnimationFormatError("playback needs non-empty animations")
        self.animations = animations
        self.animation_index = 0
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.cycles_completed = 0
        self.pause_remaining = 0.0

    @property
    def current_animation(self):
        return self.animations[self.animation_index]

    @property
    def current_frame(self):
        return self.current_animation.frames[self.frame_index]

    def advance_animation(self):
        self.animation_index = (self.animation_index + 1) % len(self.animations)
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.cycles_completed = 0
        self.pause_remaining = 0.0

    def update(self, elapsed):
        remaining = max(0.0, elapsed)
        while remaining > 0.0:
            if self.pause_remaining > 0.0:
                if remaining < self.pause_remaining:
                    self.pause_remaining -= remaining
                    return
                remaining -= self.pause_remaining
                self.advance_animation()
                if remaining <= 0.0:
                    return
                continue

            frame_time_left = self.current_frame.duration - self.frame_elapsed
            if remaining < frame_time_left:
                self.frame_elapsed += remaining
                return
            remaining -= frame_time_left
            self.frame_elapsed = 0.0
            if self.frame_index + 1 < len(self.current_animation.frames):
                self.frame_index += 1
            else:
                self.cycles_completed += 1
                if self.cycles_completed >= REPEATS_PER_ANIMATION:
                    self.pause_remaining = INTER_ANIMATION_PAUSE
                else:
                    self.frame_index = 0


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


def _get_display_scale(animations):
    max_width = max(frame.width for clip in animations for frame in clip.frames)
    max_height = max(frame.height for clip in animations for frame in clip.frames)
    target_scale = max(
        (CANVAS_WIDTH * 0.5) / max_width,
        (CANVAS_HEIGHT * 0.5) / max_height,
    )
    fit_scale = min(
        (CANVAS_WIDTH * 0.9) / max_width,
        (CANVAS_HEIGHT * 0.9) / max_height,
    )
    return min(target_scale, fit_scale)


def _render_frame(sheet, frame, display_scale):
    draw_width = max(1, int(round(frame.width * display_scale)))
    draw_height = max(1, int(round(frame.height * display_scale)))
    clear_canvas()
    sheet.clip_draw(
        frame.x,
        frame.y,
        frame.width,
        frame.height,
        CANVAS_WIDTH // 2,
        CANVAS_HEIGHT // 2,
        draw_width,
        draw_height,
    )
    update_canvas()




open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
