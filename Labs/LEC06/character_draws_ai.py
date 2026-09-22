from pico2d import *
import math

CANVAS_W, CANVAS_H = 800, 600
CENTER = (CANVAS_W // 2, CANVAS_H // 2)
RADIUS = 200          # circle path radius
MARGIN = 100          # distance of the shapes from the canvas edges
STEP_SIZE = 5         # pixels advanced per frame

open_canvas(CANVAS_W, CANVAS_H)
character = load_image("character.png")


def render(pos):
    """Clear the canvas and draw the character at pos=(x, y)."""
    clear_canvas()
    character.draw(int(pos[0]), int(pos[1]))
    update_canvas()
    get_events()
    delay(0.01)


def circle_point(t):
    """Position on the circle at parameter t in [0, 1)."""
    angle = 2 * math.pi * t
    return (CENTER[0] + RADIUS * math.cos(angle),
            CENTER[1] + RADIUS * math.sin(angle))


def rectangle_point(t):
    """Position on the rectangle perimeter at parameter t in [0, 1).

    Walks clockwise from the top-left corner.  The perimeter is
    2 * (600 + 400) = 2000 px long, so each edge owns a slice of t
    proportional to its length.
    """
    perimeter = 2 * ((CANVAS_W - 2 * MARGIN) + (CANVAS_H - 2 * MARGIN))
    distance = t * perimeter

    edge = CANVAS_W - 2 * MARGIN
    if distance < edge:                                # top edge
        return (MARGIN + distance, CANVAS_H - MARGIN)
    distance -= edge

    edge = CANVAS_H - 2 * MARGIN
    if distance < edge:                                # right edge
        return (CANVAS_W - MARGIN, CANVAS_H - MARGIN - distance)
    distance -= edge

    edge = CANVAS_W - 2 * MARGIN
    if distance < edge:                                # bottom edge
        return (CANVAS_W - MARGIN - distance, MARGIN)
    distance -= edge

    return (MARGIN, MARGIN + distance)                 # left edge


def triangle_point(t):
    """Position on the triangle perimeter at parameter t in [0, 1).

    Vertices: (400,500) top -> (700,100) right -> (100,100) left.
    The two slanted edges are 500 px each, the base is 600 px.
    """
    total = 500 + 600 + 500
    distance = t * total

    if distance < 500:                                 # top -> right-bottom
        return (400 + 300 * (distance / 500),
                500 - 400 * (distance / 500))
    distance -= 500

    if distance < 600:                                 # bottom base
        return (700 - distance, 100)
    distance -= 600

    return (100 + 300 * (distance / 500),              # left-bottom -> top
            100 + 400 * (distance / 500))


def trace_path(point_func, steps):
    """Draw the character along a parametric path in 'steps' frames."""
    for i in range(steps + 1):
        render(point_func(i / steps))



while True:
    trace_path(circle_point, 360)
    trace_path(rectangle_point, 400)
    trace_path(triangle_point, 320)

close_canvas()
