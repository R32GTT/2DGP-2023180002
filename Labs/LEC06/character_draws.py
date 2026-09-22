from pico2d import *

open_canvas(800,600)

character = load_image("character.png")

def move_Circle():
    print("Circle")
    clear_canvas()
    for degree in range(361):
        theta=math.radians(degree)
        x = 400 + 200 * math.cos(theta)
        print(x)
    character.draw(400,300)
    update_canvas()
    
    pass

def move_Rectangle():
    #print("Rect")
    pass

def move_Triangle():
    #print("Tri")
    pass

while True:
    move_Circle()
    move_Rectangle()
    move_Triangle()
    pass


close_canvas()