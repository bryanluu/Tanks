import pygame
from scenes import *
import os

# -------- For PiTFT calibration --------
# os.environ['SDL_VIDEODRIVER'] = 'fbcon'
# os.environ["SDL_FBDEV"] = "/dev/fb1"
# os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
# os.environ["SDL_MOUSEDRV"] = "TSLIB"

pygame.init()


def run_game(width, height, fps, starting_scene):
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene


    while active_scene:

        if not active_scene.initialized:
            active_scene.initGraphics(screen)
            active_scene.initialized = True

        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render()

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

#==============================================================================
# The rest is code where you implement your game using the Scenes model


run_game(500, 500, 60, Start())