"""
Sprite strip animator demo

Requires spritesheet.spritesheet and the Explode1.bmp through Explode5.bmp
found in the sprite pack at
http://lostgarden.com/2005/03/download-complete-set-of-sweet-8-bit.html

I had to make the following addition to method spritesheet.image_at in
order to provide the means to handle sprite strip cells with borders:

            elif type(colorkey) not in (pygame.Color,tuple,list):
                colorkey = image.get_at((colorkey,colorkey))
"""
import sys
import pygame
from pygame.locals import Color, KEYUP, K_ESCAPE, K_RETURN
import utilities
from scenes import Button
import colors

surface = pygame.display.set_mode((256,256))
FPS = 120
frames = FPS / 12
strips = utilities.SpriteStripAnim('zombie.png', (0,0,256,256), (6, 1), colorkey=-1, frames=frames, loop=True)

def action():
    print('hi')

pygame.init()

font = pygame.font.Font('freesansbold.ttf', 10)
button1 = Button(pygame.Rect(0, 0, 50, 30), action, font, colors.RED, 'O', colors.WHITE, colors.BLACK, 'O', colors.WHITE)
button2 = Button(pygame.Rect(10, 50, 50, 30), action, font, colors.RED, 'X', colors.WHITE, colors.BLACK, 'X', colors.WHITE)
buttons = pygame.sprite.Group()
buttons.add(button1)
buttons.add(button2)

white = Color('white')
clock = pygame.time.Clock()
strips.iter()
image = strips.next()
while True:
    for e in pygame.event.get():
        if e.type == KEYUP:
            if e.key == K_ESCAPE:
                sys.exit()
            elif e.key == K_RETURN:
                strips.iter()
    buttons.update()
    surface.fill(white)
    # surface.blit(button.image, button.rect)
    buttons.draw(surface)
    pygame.display.flip()
    clock.tick(FPS)
