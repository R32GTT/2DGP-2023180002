from pico2d import *

open_canvas()

grass = load_image('grass.png')
character = load_image('animation_sheet.png')
frame = 0
fH=300

while (True):
    for frame in range(0,8):
        clear_canvas()
        grass.draw(400,30)
        character.clip_draw(
            frame * 100, fH,100,100, 
            400,300,
        )
        update_canvas()
        frame = (frame + 1) % 8
        delay(0.05)
    fH = (fH+100) % 400
    pass


close_canvas()

