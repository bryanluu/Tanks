import geometry as geo
import pygame
import utilities
import math


class Tank(pygame.sprite.Sprite):

    def __init__(self, pos, color, facing_right=True):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 60, 60)
        self.rect.center = pos
        self.color = color
        self.speed = 0
        self.angle = 45
        self.transparent = (255, 0, 255)  # purple color key
        self.surface = pygame.Surface((60, 60))
        self.surface.set_colorkey(self.transparent)
        self.surface.fill(self.transparent)
        self.gun = pygame.Surface((60, 60))
        self.gun.set_colorkey(self.transparent)
        self.gun.fill(self.transparent)
        self.faceright = facing_right
        self.v = geo.Vector2D.zero()
        self.power = 0.5
        self.power_dir = 1
        self.power_speed = 0.03

        self.cannon_sound = utilities.load_sound("cannon.wav")

    def draw(self, screen):
        x, y, w, h = self.rect

        self.surface.fill(self.transparent)
        self.gun.fill(self.transparent)

        # draw the tank gun
        if self.faceright:
            pygame.draw.rect(self.gun, self.color, (30, 30, 30, 5))
            gun = geo.rot_center(self.gun, self.angle)
        else:
            pygame.draw.rect(self.gun, self.color, (0, 30, 30, 5))
            gun = geo.rot_center(self.gun, -self.angle)
        gun_rect = gun.get_rect()
        gun_rect[1] = gun_rect[1] + h/2 - 10

        self.surface.blit(gun, gun_rect)

        # Draw the power meter
        pygame.draw.rect(self.surface, (0, 255, 0), (5, h - 15 - int(self.power*10), 5, int(self.power*10)))

        # Draw the tank body
        pygame.draw.circle(self.surface, self.color, (int(w/2), h - 10), 10)
        pygame.draw.rect(self.surface, self.color, ((int(w/2) - 15), h - 10, 30, 10))

        screen.blit(self.surface, self.rect)

        self.screen = screen

    def origin(self):
        x, y, w, h = self.rect

        return x+int(w/2), y + h-10

    def shoot(self):
        pos = self.origin()

        ball_speed = 30

        ball = Cannonball(pos, geo.Vector2D(self.power * ball_speed * math.cos(math.radians(self.angle)), -self.power * ball_speed * math.sin(math.radians(self.angle))))

        ball.initGraphics()

        ball.sound = utilities.load_sound('explosion.wav')

        pygame.mixer.Sound.play(self.cannon_sound)

        return ball

class Cannonball(pygame.sprite.Sprite):

    def __init__(self, pos, velocity):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.initialPos = pos
        self.v = velocity

    def initGraphics(self):
        self.img = utilities.load_image('ball.png')
        self.img = pygame.transform.scale(self.img, (5, 5))
        self.img.set_colorkey((255, 255, 255))
        self.rect = self.img.get_rect()
        self.rect.x, self.rect.y = self.initialPos

    def draw(self, screen):
        screen.blit(self.img, self.rect)

    def pos(self):
        return self.rect.x, self.rect.y

    def explode(self):
        strips = utilities.SpriteStripAnim('explosion.png', (0, 0, 256, 256), (8,7), colorkey=-1, frames=1)
        strips.iter()

        return strips


class Zombie(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, speed):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        self.rect.x = screenWidth
        self.rect.y = screenHeight - height

        self.speed = speed

    def update(self):
        self.rect.x -= self.speed