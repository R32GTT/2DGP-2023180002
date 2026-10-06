"""View Sonic sprite animations with Pico2D."""

from dataclasses import dataclass
from pathlib import Path

from pico2d import clear_canvas, close_canvas, load_image, open_canvas, update_canvas


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800
SPRITE_PATH = Path(__file__).resolve().with_name("sonic-sprite.png")
DEFAULT_FRAME_DURATION = 0.1


@dataclass(frozen=True)
class Frame:
    """A top-left-origin crop and its playback duration."""

    x: int
    y: int
    width: int
    height: int
    duration: float = DEFAULT_FRAME_DURATION


@dataclass(frozen=True)
class Animation:
    """A named, ordered sequence of animation frames."""

    name: str
    frames: tuple


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
)


def load_sprite_sheet(path=SPRITE_PATH):
    """Load the sprite sheet and report a useful failure reason."""
    if not path.is_file():
        raise FileNotFoundError(f"sprite sheet not found: '{path}'")
    try:
        return load_image(str(path))
    except Exception as error:
        raise RuntimeError(f"cannot load sprite sheet '{path}': {error}") from error


def main():
    """Application entry point."""
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        try:
            sprite_sheet = load_sprite_sheet()
        except (FileNotFoundError, RuntimeError) as error:
            print(f"Animation viewer error: {error}")
            return
        clear_canvas()
        sprite_sheet.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
        update_canvas()
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
