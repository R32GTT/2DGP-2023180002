"""View Sonic sprite animations with Pico2D."""

import math
import time
from dataclasses import dataclass
from pathlib import Path

from pico2d import (
    clear_canvas,
    close_canvas,
    delay,
    draw_rectangle,
    get_events,
    load_image,
    open_canvas,
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    update_canvas,
)


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
MAX_SPRITE_FRACTION = 0.8
BACKGROUND_COLOR = (232, 236, 242)
LOOP_DELAY = 0.01
REPEATS_PER_ANIMATION = 5
INTER_ANIMATION_PAUSE = 1.0
DEFAULT_FRAME_DURATION = 0.1


def resolve_sprite_path(script_file):
    """Resolve the adjacent sprite asset independent of the working directory."""
    return Path(script_file).resolve().with_name("sonic-sprite.png")


SPRITE_PATH = resolve_sprite_path(__file__)


@dataclass(frozen=True)
class Frame:
    """A top-left-origin crop and its playback duration."""

    x: int
    y: int
    width: int
    height: int
    duration: float = DEFAULT_FRAME_DURATION
    anchor_x: float = 0.5
    anchor_y: float = 1.0


@dataclass(frozen=True)
class Animation:
    """A named, ordered sequence of animation frames."""

    name: str
    frames: tuple


class PlaybackState:
    """Track elapsed time, repeats, and transitions for an animation list."""

    def __init__(self, animations):
        if not animations or any(not animation.frames for animation in animations):
            raise ValueError("playback needs non-empty animations")
        self.animations = tuple(animations)
        self.animation_index = 0
        self._start_current_animation()

    @property
    def animation(self):
        return self.animations[self.animation_index]

    def _start_current_animation(self):
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.cycles_completed = 0
        self.is_complete = False
        self.pause_remaining = 0.0

    @property
    def current_frame(self):
        return self.animation.frames[self.frame_index]

    def update(self, elapsed):
        elapsed = max(0.0, elapsed)
        if self.is_complete:
            self.pause_remaining = max(0.0, self.pause_remaining - elapsed)
            if self.pause_remaining == 0.0:
                self.animation_index = (
                    self.animation_index + 1
                ) % len(self.animations)
                self._start_current_animation()
            return
        self.frame_elapsed += elapsed
        while not self.is_complete and self.frame_elapsed >= self.current_frame.duration:
            self.frame_elapsed -= self.current_frame.duration
            if self.frame_index + 1 < len(self.animation.frames):
                self.frame_index += 1
            else:
                self.cycles_completed += 1
                if self.cycles_completed >= REPEATS_PER_ANIMATION:
                    self.frame_index = len(self.animation.frames) - 1
                    self.frame_elapsed = 0.0
                    self.is_complete = True
                    self.pause_remaining = INTER_ANIMATION_PAUSE
                else:
                    self.frame_index = 0


# First horizontal action row in sonic-sprite.png (top-left origin).
ANIMATIONS = (
    Animation(
        "달리기",
        (
            Frame(1, 39, 29, 39),
            Frame(31, 40, 26, 38),
            Frame(58, 39, 28, 39),
            Frame(86, 40, 30, 38),
            Frame(118, 40, 30, 38),
            Frame(150, 40, 30, 38),
            Frame(182, 40, 29, 38),
            Frame(211, 39, 29, 38),
            Frame(240, 39, 29, 38),
            Frame(270, 45, 24, 32),
            Frame(302, 51, 29, 26),
        ),
    ),
    Animation(
        "동작 02",
        (
            Frame(8, 80, 26, 37),
            Frame(37, 80, 27, 37),
            Frame(65, 80, 31, 38),
            Frame(97, 80, 37, 37),
            Frame(135, 80, 32, 35),
            Frame(170, 79, 32, 38),
            Frame(206, 79, 26, 38),
            Frame(238, 80, 24, 37),
            Frame(263, 80, 30, 37),
            Frame(295, 80, 36, 37),
            Frame(334, 80, 32, 36),
            Frame(370, 79, 29, 38),
        ),
    ),
    Animation(
        "동작 03",
        (
            Frame(1, 124, 33, 40),
            Frame(39, 124, 35, 39),
            Frame(89, 125, 35, 38),
            Frame(130, 121, 34, 42),
            Frame(181, 122, 34, 41),
            Frame(228, 122, 33, 40),
        ),
    ),
    Animation(
        "동작 04",
        (
            Frame(1, 169, 29, 30),
            Frame(35, 167, 29, 31),
            Frame(67, 169, 30, 29),
            Frame(98, 169, 31, 29),
            Frame(131, 168, 29, 30),
            Frame(162, 168, 29, 31),
            Frame(193, 170, 30, 29),
            Frame(230, 170, 31, 29),
            Frame(268, 170, 30, 30),
        ),
    ),
    Animation(
        "동작 05",
        (
            Frame(1, 206, 30, 27),
            Frame(36, 206, 29, 27),
            Frame(70, 206, 29, 27),
            Frame(105, 206, 29, 27),
            Frame(139, 206, 29, 27),
            Frame(174, 206, 29, 27),
        ),
    ),
    Animation(
        "동작 06",
        (
            Frame(1, 239, 29, 35),
            Frame(36, 239, 30, 35),
            Frame(74, 239, 31, 35),
            Frame(111, 238, 31, 36),
            Frame(149, 239, 30, 35),
            Frame(186, 238, 31, 36),
        ),
    ),
    Animation(
        "동작 07",
        (
            Frame(1, 283, 29, 35),
            Frame(36, 283, 30, 35),
            Frame(72, 286, 39, 31),
            Frame(123, 285, 39, 32),
            Frame(172, 286, 39, 31),
            Frame(218, 285, 38, 32),
        ),
    ),
    Animation(
        "동작 08",
        (
            Frame(1, 326, 24, 45),
            Frame(65, 327, 20, 44),
            Frame(90, 327, 25, 43),
            Frame(119, 327, 25, 43),
            Frame(149, 327, 20, 44),
            Frame(184, 341, 40, 28),
            Frame(232, 341, 39, 27),
        ),
    ),
    Animation(
        "동작 09",
        (
            Frame(1, 379, 27, 38),
            Frame(31, 379, 31, 36),
            Frame(64, 379, 31, 36),
            Frame(99, 377, 33, 38),
            Frame(136, 379, 32, 36),
            Frame(176, 379, 33, 36),
            Frame(217, 379, 33, 36),
            Frame(254, 378, 33, 36),
        ),
    ),
)


class AnimationFormatError(ValueError):
    """Raised when the in-file animation data cannot be played safely."""


def validate_animations(animations, sheet_width, sheet_height):
    """Validate clip definitions and crop bounds before playback starts."""
    if not animations:
        raise AnimationFormatError("animations must contain at least one clip")

    names = set()
    for animation_index, animation in enumerate(animations):
        if not isinstance(animation.name, str) or not animation.name.strip():
            raise AnimationFormatError(
                f"animation {animation_index} needs a non-empty name"
            )
        if animation.name in names:
            raise AnimationFormatError(f"duplicate animation name: {animation.name}")
        if not animation.frames:
            raise AnimationFormatError(
                f"animation '{animation.name}' has no frames"
            )
        names.add(animation.name)

        for frame_index, frame in enumerate(animation.frames):
            description = f"animation '{animation.name}' frame {frame_index}"
            for field_name in ("x", "y", "width", "height"):
                value = getattr(frame, field_name)
                minimum = 1 if field_name in ("width", "height") else 0
                if (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < minimum
                ):
                    raise AnimationFormatError(
                        f"{description}.{field_name} must be an integer >= {minimum}"
                    )
            for field_name in ("anchor_x", "anchor_y"):
                value = getattr(frame, field_name)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or not 0.0 <= value <= 1.0
                ):
                    raise AnimationFormatError(
                        f"{description}.{field_name} must be between 0 and 1"
                    )
            if (
                isinstance(frame.duration, bool)
                or not isinstance(frame.duration, (int, float))
                or not math.isfinite(frame.duration)
                or frame.duration <= 0
            ):
                raise AnimationFormatError(
                    f"{description}.duration must be a positive number"
                )
            if (
                frame.x + frame.width > sheet_width
                or frame.y + frame.height > sheet_height
            ):
                raise AnimationFormatError(
                    f"{description} extends beyond the {sheet_width}x{sheet_height} sheet"
                )


def get_display_scale(animations):
    """Scale the largest configured frame to fit most of the canvas."""
    frames = [frame for animation in animations for frame in animation.frames]
    if not frames:
        raise ValueError("at least one animation frame is required")
    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)
    return min(
        CANVAS_WIDTH * MAX_SPRITE_FRACTION / max_width,
        CANVAS_HEIGHT * MAX_SPRITE_FRACTION / max_height,
    )


def get_baseline_y(animations, display_scale):
    """Keep the bottom anchor fixed while centering the maximum frame."""
    max_height = max(
        frame.height for animation in animations for frame in animation.frames
    )
    return (CANVAS_HEIGHT - max_height * display_scale) / 2


def load_sprite_sheet(path=SPRITE_PATH):
    """Load the sprite sheet and report a useful failure reason."""
    if not path.is_file():
        raise FileNotFoundError(f"sprite sheet not found: '{path}'")
    try:
        return load_image(str(path))
    except Exception as error:
        raise RuntimeError(f"cannot load sprite sheet '{path}': {error}") from error


def pico2d_clip_y(frame, sheet_height):
    """Convert a top-left image y-coordinate to Pico2D's bottom-left origin."""
    return sheet_height - frame.y - frame.height


def draw_frame(sheet, frame, anchor_x, anchor_y, scale=1.0):
    """Draw a frame using its normalized bottom-center pivot."""
    draw_width = max(1, int(round(frame.width * scale)))
    draw_height = max(1, int(round(frame.height * scale)))
    center_x = anchor_x + (0.5 - frame.anchor_x) * draw_width
    center_y = anchor_y + (frame.anchor_y - 0.5) * draw_height
    sheet.clip_draw(
        frame.x,
        pico2d_clip_y(frame, sheet.h),
        frame.width,
        frame.height,
        center_x,
        center_y,
        draw_width,
        draw_height,
    )


def render_frame(sheet, frame, scale, baseline_y):
    """Render a centered frame over a high-contrast solid background."""
    clear_canvas()
    draw_rectangle(
        0,
        0,
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
        BACKGROUND_COLOR[0],
        BACKGROUND_COLOR[1],
        BACKGROUND_COLOR[2],
        255,
        True,
    )
    draw_frame(sheet, frame, CANVAS_WIDTH // 2, baseline_y, scale)
    update_canvas()


def process_events():
    """Return False when the user requests application shutdown."""
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def tick_clock(previous_time):
    """Return the current monotonic time and non-negative elapsed seconds."""
    current_time = time.perf_counter()
    return current_time, max(0.0, current_time - previous_time)


def main():
    """Application entry point."""
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        try:
            sprite_sheet = load_sprite_sheet()
        except (FileNotFoundError, RuntimeError) as error:
            print(f"Animation viewer error: {error}")
            return
        try:
            validate_animations(ANIMATIONS, sprite_sheet.w, sprite_sheet.h)
        except AnimationFormatError as error:
            print(f"Animation viewer error: {error}")
            return
        playback = PlaybackState(ANIMATIONS)
        display_scale = get_display_scale(ANIMATIONS)
        baseline_y = get_baseline_y(ANIMATIONS, display_scale)
        render_frame(sprite_sheet, playback.current_frame, display_scale, baseline_y)
        previous_time = time.perf_counter()
        while process_events():
            previous_time, elapsed = tick_clock(previous_time)
            playback.update(elapsed)
            render_frame(
                sprite_sheet,
                playback.current_frame,
                display_scale,
                baseline_y,
            )
            delay(LOOP_DELAY)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
