from pico2d import *
import math

open_canvas(800,600)

character = load_image("character.png")

def draw_Character(x,y):
    clear_canvas()
    character.draw(x,y)
    update_canvas()
    delay(0.01)
    pass

def move_Circle():
    #print("Circle")
    for degree in range(361):
        theta=math.radians(degree)
        x = 400 + 200 * math.cos(theta)
        y = 300 + 200 * math.sin(theta)
        draw_Character(x,y)
    pass

def move_Top():
    for y in range(100, 501, 5):
        draw_Character(100, y)
    pass
def move_Right():
    for x in range(100,701,5):
        draw_Character(x,500)
    pass
def move_Down():
    for y in range(500, 101, -5):
        draw_Character(700,y)
    pass
def move_Left():
    for x in range(700, 101, -5):
        draw_Character(x,100)
    pass

def normalize(x,y):
    v = math.sqrt(abs(x)+abs(y))
    return (0,0)

def get_Direction(x1,y1,x2,y2):
    x,y = x2-x1, y2-y1
    x,y = normalize(x,y)
    return (x,y)

def move_RightSide():
    x,y = get_Direction(400,500,700,100)
    pass
def move_BottomSide():
    pass
def move_LeftSide():
    pass

def move_Rectangle():
    #print("Rect")
    move_Top()
    move_Right()
    move_Down()
    move_Left()
    pass

def move_Triangle():
    #print("Tri")
    move_RightSide()
    #move_BottomSide()
    #move_LeftSide()
    pass

while True:
    #move_Circle()
    #move_Rectangle()
    move_Triangle()
    pass


close_canvas()