"""Play Aseprite-tagged animations from player.json with Pico2D.

Each JSON frame provides its own source rectangle and duration. Animation
groups come from ``meta.frameTags`` and play in tag order.
"""

from pico2d import *
import json




def animation_load_json():
    pass

open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
