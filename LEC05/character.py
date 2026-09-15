from pico2d import *
import math

open_canvas()
grass = load_image('grass.png')
character = load_image('character.png')
x = 300
y = 200

Left = (-1,0)
Up = (0,1)
Right = (1,0)
Down = (0,-1)

Dir = ( Left,Up,Right,Down ) 
i = 0
while True:
    clear_canvas()
    if x == 500 or x == 300 or y == 400 or y == 200:
        i = (i + 1) % 4
    x += Dir[i][0]
    y += Dir[i][1]
    character.draw(x,y)
    update_canvas()
    delay(0.001)



close_canvas()

