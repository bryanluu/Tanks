import pygame
import os
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('resources', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image: {0}'.format(name))
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('resources', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Cannot load sound: {0}'.format(name))
        raise SystemExit(message)
    return sound