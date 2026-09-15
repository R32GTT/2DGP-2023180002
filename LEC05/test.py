from pico2d import *
import math

open_canvas()
grass = load_image('grass.png')
character = load_image('character.png')
x = 0
centerX = 400
y = 0
centerY = 300
halfRadius = 150
degree = 0

while True:
    clear_canvas()
    degree += 0.001
    x = centerX + halfRadius * math.sin(degree)
    y = centerY + halfRadius * math.cos(degree)
    character.draw(x,y)
    update_canvas()



close_canvas()

