"""View Sonic sprite animations with Pico2D."""

from pico2d import close_canvas, open_canvas


CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800


def main():
    """Application entry point."""
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        pass
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
