import geometry as geo
import pygame
import utilities
import math
import random
from enum import Enum
import time
import colors


class Weapon(Enum):
    CANNON = 0
    BOMB = 1
    MACHINE_GUN = 2
    LASER = 3


class Tank(pygame.sprite.Sprite):

    MACHINE_GUN_RELOAD_TIME = 0.5

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
        self.weapon = Weapon.CANNON
        self.ammo = 0
        self.lastShootTime = time.time()
        self.ammoText = pygame.font.Font('freesansbold.ttf', 8)

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

        if self.weapon.value < Weapon.MACHINE_GUN.value:
            # Draw the power meter
            pygame.draw.rect(self.surface, (0, 255, 0), (5, h - 15 - int(self.power*10), 5, int(self.power*10)))

        if self.ammo > 0:
            ammoSurf = self.ammoText.render("{0}".format(self.ammo), True, (0, 0, 0))
            ammoRect = ammoSurf.get_rect()
            ammoRect.x, ammoRect.y = 5, 5
            self.surface.blit(ammoSurf, ammoRect)

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

        if self.weapon == Weapon.CANNON:
            ball_speed = 30

            ball = Cannonball(pos, geo.Vector2D(self.power * ball_speed * math.cos(math.radians(self.angle)), -self.power * ball_speed * math.sin(math.radians(self.angle))))

            pygame.mixer.Sound.play(self.cannon_sound)
        else:
            if self.weapon == Weapon.BOMB:
                ball_speed = 30

                ball = Bomb(pos, geo.Vector2D(self.power * ball_speed * math.cos(math.radians(self.angle)), -self.power * ball_speed * math.sin(math.radians(self.angle))))

                pygame.mixer.Sound.play(self.cannon_sound)
            elif self.weapon == Weapon.MACHINE_GUN:
                ball_speed = 50

                ball = Bullet(pos, geo.Vector2D(self.power * ball_speed * math.cos(math.radians(self.angle)), -self.power * ball_speed * math.sin(math.radians(self.angle))))

                pygame.mixer.Sound.play(ball.sound)
            else:
                info = pygame.display.Info()
                screenWidth, screenHeight = info.current_w, info.current_h

                ball = Laser(pos, geo.Vector2D(2*screenWidth*math.cos(math.radians(self.angle)), -2*screenHeight*math.sin(math.radians(self.angle))))

                pygame.mixer.Sound.play(ball.sound)

            self.ammo -= 1

            if self.ammo == 0:
                self.weapon = Weapon.CANNON

        self.lastShootTime = time.time()

        return ball


class Projectile(pygame.sprite.Sprite):

    def __init__(self, pos, velocity):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.v = velocity
        self.initGraphics(pos)

    def initGraphics(self, pos):
        self.img = pygame.Surface((5, 5))
        self.rect = self.img.get_rect()
        self.rect.center = pos

    def draw(self, screen):
        screen.blit(self.img, self.rect)

    def pos(self):
        return self.rect.center

    def explode(self):
        return None

    @staticmethod
    def collided(left, right):
        x, y, w, h = left.rect
        x2, y2, w2, h2 = right.rect

        radius = 15

        if x + radius > x2 and x - radius < x2 + w2 and y + radius > y2 and y - radius < y2 + h2:
            return True
        else:
            return False


class Cannonball(Projectile):

    def initGraphics(self, pos):
        self.img = utilities.load_image('ball.png')
        self.img = pygame.transform.scale(self.img, (5, 5))
        self.img.set_colorkey((255, 255, 255))
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.sound = utilities.load_sound('explosion.wav')

    def explode(self):
        pygame.mixer.Sound.play(self.sound)

        strips = utilities.SpriteStripAnim('explosion.png', (0, 0, 256, 256), (8,7), colorkey=-1, frames=1)
        strips.iter()

        return strips


class Bomb(Projectile):
    BOMB_FUSE_TIME = 5
    def initGraphics(self, pos):
        self.strips = utilities.SpriteStripAnim('bomb.png', (0, 0, 60, 60), (12, 1), colorkey=-1, frames=5)
        self.strips.iter()
        self.img = self.strips.next()
        self.img = pygame.transform.scale(self.img, (5, 5))
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.sound = utilities.load_sound('bomb.wav')
        self.start = time.time()

    def explode(self):
        pygame.mixer.Sound.play(self.sound)

        return self.strips

    @staticmethod
    def collided(left, right):
        x, y, w, h = left.rect
        x2, y2, w2, h2 = right.rect

        radius = 30

        if time.time() - left.start > Bomb.BOMB_FUSE_TIME and x + radius > x2 and x - radius < x2 + w2 and y + radius > y2 and y - radius < y2 + h2:
            return True
        else:
            return False


class Bullet(Projectile):

    def initGraphics(self, pos):
        self.img = utilities.load_image('ball.png')
        self.img = pygame.transform.scale(self.img, (5, 5))
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.sound = utilities.load_sound('bullet.wav')

    def explode(self):
        pygame.mixer.Sound.play(self.sound)

    @staticmethod
    def collided(left, right):
        x, y, w, h = left.rect
        x2, y2, w2, h2 = right.rect

        radius = 3

        if x + radius > x2 and x - radius < x2 + w2 and y + radius > y2 and y - radius < y2 + h2:
            return True
        else:
            return False


class Laser(Projectile):
    LASER_TIME = 0.2
    def initGraphics(self, pos):
        self.rect = pygame.Rect(*pos, 1, 1)
        self.sound = utilities.load_sound('laser.wav')

    def draw(self, screen):
        pygame.draw.line(screen, colors.RED, self.rect.topleft, (geo.Vector2D(*self.pos()) + self.v).tuple())

    @staticmethod
    def collided(left, right):

        topline = geo.Vector2D(*right.rect.topleft) - geo.Vector2D(*left.pos())
        bottomline = geo.Vector2D(*right.rect.bottomleft) - geo.Vector2D(*left.pos())

        if geo.Vector2D.angle_between(left.v, topline) < 0 < geo.Vector2D.angle_between(left.v, bottomline):
            return True
        else:
            return False


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
        self.x = float(self.rect.x)

    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)


class Balloon(pygame.sprite.Sprite):

    def __init__(self, pos, color):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.pop_sound = utilities.load_sound('balloon_pop.wav')

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface((10, 20))
        self.image.fill(color)
        self.color = color

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.y = self.rect.y

    def update(self):
        # move upwards
        self.y += random.normalvariate(-1, 0.5)
        self.rect.y = int(self.y)

        if self.rect.y < -self.rect.h:
            self.kill()


    def pop(self):
        pygame.mixer.Sound.play(self.pop_sound)
