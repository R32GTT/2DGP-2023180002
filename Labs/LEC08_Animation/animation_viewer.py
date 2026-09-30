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




def animation_load_json():
    pass

open_canvas()

animation_load_json()

while(True):
    pass

close_canvas()
