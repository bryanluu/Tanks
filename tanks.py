import geometry as geo
import pygame
import math

class Tank:
    def __init__(self, pos, color, facing_right=True):
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

    def draw(self, screen):
        x, y, w, h = self.rect

        self.surface.fill(self.transparent)
        self.gun.fill(self.transparent)

        if self.faceright:
            pygame.draw.rect(self.gun, self.color, (30, 30, 30, 5))
            gun = geo.rot_center(self.gun, self.angle)
        else:
            pygame.draw.rect(self.gun, self.color, (0, 30, 30, 5))
            gun = geo.rot_center(self.gun, -self.angle)
        gun_rect = gun.get_rect()
        gun_rect[1] = gun_rect[1] + h/2 - 10

        self.surface.blit(gun, gun_rect)

        # Draw the tank body
        pygame.draw.circle(self.surface, self.color, (int(w/2), h - 10), 10)
        pygame.draw.rect(self.surface, self.color, ((int(w/2) - 15), h - 10, 30, 10))

        screen.blit(self.surface, self.rect)

    def origin(self):
        x, y, w, h = self.rect

        return x+int(w/2), y + h-10
