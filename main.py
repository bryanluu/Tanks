import pygame
import time
import random
import numpy as np

pygame.init()

display_width = 800
display_height = 600

black = (0, 0, 0)
white = (255, 255, 255)

red = (200, 0, 0)
green = (0, 200, 0)

bright_red = (255, 0, 0)
bright_green = (0, 255, 0)

block_color = (53, 115, 255)

car_width = 73

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('A bit Racey')
clock = pygame.time.Clock()

carImg = pygame.image.load('racecar.png')
w, h = carImg.get_size()
scale = 0.2

carImg = pygame.image.load('racecar.png')
carImg = pygame.transform.rotate(carImg, 90)
w, h = carImg.get_size()
scale = 0.2
car_width, car_height = int(w * scale), int(h * scale)
carImg = pygame.transform.scale(carImg, (car_width, car_height))

# gameIcon = pygame.image.load('carIcon.png')

# pygame.display.set_icon(gameIcon)

pause = False


# crash = True

def things_dodged(count):
    font = pygame.font.SysFont("comicsansms", 25)
    text = font.render("Dodged: " + str(count), True, black)
    gameDisplay.blit(text, (0, 0))


def things(thingx, thingy, thingw, thingh, color):
    pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh])


def car(x, y):
    gameDisplay.blit(carImg, (x, y))


def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


##def message_display(text):
##    largeText = pygame.font.SysFont("comicsansms",115)
##    TextSurf, TextRect = text_objects(text, largeText)
##    TextRect.center = ((display_width/2),(display_height/2))
##    gameDisplay.blit(TextSurf, TextRect)
##
##    pygame.display.update()
##
##    time.sleep(2)
##
##    game_loop()



def crash():
    largeText = pygame.font.SysFont("comicsansms", 115)
    TextSurf, TextRect = text_objects("You Crashed", largeText)
    TextRect.center = ((display_width / 2), (display_height / 2))
    gameDisplay.blit(TextSurf, TextRect)

    start = time.time()
    while time.time() - start < 3:
        for event in pygame.event.get():
            pass
        pygame.display.update()
        clock.tick(15)

    #
    # while True:
    #     for event in pygame.event.get():
    #         # print(event)
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             quit()
    #
    #     # gameDisplay.fill(white)
    #
    #
    #     button("Play Again", 150, 450, 100, 50, green, bright_green, game_loop)
    #     button("Quit", 550, 450, 100, 50, red, bright_red, quitgame)
    #
    #     pygame.display.update()
    #     clock.tick(15)


def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    print("Mouse: {0}".format(mouse))
    print("Button: x: {0}, y: {1}, w: {2}, h: {3}".format(x, y, w, h))
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))
    smallText = pygame.font.SysFont("comicsansms", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurf, textRect)


def quitgame():
    pygame.quit()
    quit()


def unpause():
    global pause
    pause = False


def paused():
    largeText = pygame.font.SysFont("comicsansms", 115)
    TextSurf, TextRect = text_objects("Paused", largeText)
    TextRect.center = ((display_width / 2), (display_height / 2))
    gameDisplay.blit(TextSurf, TextRect)

    while pause:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # gameDisplay.fill(white)


        button("Continue", 150, 450, 100, 50, green, bright_green, unpause)
        button("Quit", 550, 450, 100, 50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)


def game_intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        gameDisplay.fill(white)
        largeText = pygame.font.SysFont("comicsansms", 115)
        TextSurf, TextRect = text_objects("A bit Racey", largeText)
        TextRect.center = ((display_width / 2), (display_height / 2))
        gameDisplay.blit(TextSurf, TextRect)

        button("GO!", 150, 450, 100, 50, green, bright_green, game_loop)
        button("Quit", 550, 450, 100, 50, red, bright_red, quitgame)

        pygame.display.update()
        clock.tick(15)


def game_loop():
    global pause

    x = (display_width * 0.45)
    y = (display_height * 0.8)

    x_change = 0

    thing_startx = random.randrange(display_width/2, display_width)
    thing_starty = -600
    thing_speed = 4
    thing_width = 100
    thing_height = 100

    thingCount = 1

    dodged = 0

    gameExit = False

    #### AI Code ####

    num_speeds = 5

    speeds = [-10, -5, 0, 5, 10]

    dodges = [0] * num_speeds
    crashes = [0] * num_speeds

    seen = False

    while not gameExit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        if not seen:
            seen = True
            speed = 0
            max_random = 0

            for i in range(0, num_speeds):
                random_beta = random.betavariate(dodges[i] + 1, crashes[i] + 1)
                if random_beta > max_random:
                    max_random = random_beta
                    speed = i

            x_change = speeds[speed]

        x += x_change
        gameDisplay.fill(white)

        # things(thingx, thingy, thingw, thingh, color)
        things(thing_startx, thing_starty, thing_width, thing_height, block_color)

        thing_starty += thing_speed
        car(x, y)
        things_dodged(dodged)

        # mouse_pressed = pygame.mouse.get_pressed()
        #
        # if mouse_pressed[0]:
        #     mouse_x, mouse_y = pygame.mouse.get_pos()
        #
        #     if mouse_x < x + car_width/2 - 10:
        #         x_change = (mouse_x - (x+car_width/2))*0.2
        #     elif mouse_x > x + car_width/2 + 10:
        #         x_change = (mouse_x - (x+car_width/2))*0.2
        #     else:
        #         x_change = 0
        # else:
        #     x_change = 0

        if x > display_width - car_width:
            x = display_width - car_width
        elif x < 0:
            x = 0

        if thing_starty > display_height:
            thing_starty = 0 - thing_height
            thing_startx = random.randrange(display_width/2, display_width)
            dodged += 1
            thing_speed += 1
            thing_width += (dodged * 1.2)
            dodges[speed] += 1

            seen = False

        if y < thing_starty + thing_height:

            if x > thing_startx and x < thing_startx + thing_width or x + car_width > thing_startx and x + car_width < thing_startx + thing_width:
                crash()

                x = (display_width * 0.45)
                y = (display_height * 0.8)

                x_change = 0

                thing_startx = random.randrange(display_width/2, display_width)
                thing_starty = -600
                thing_speed = 4
                thing_width = 100
                thing_height = 100

                thingCount = 1

                crashes[speed] += 1

                dodged = 0

                gameExit = False

                seen = False

        pygame.display.update()
        clock.tick(60)


# game_intro()
game_loop()
pygame.quit()
quit()