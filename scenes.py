import pygame
import utilities
import geometry as geo
from tanks import Tank
import math

class SceneBase:
    def __init__(self):
        self.next = self

    # only needs to be called once throughout main loop
    def initGraphics(self, screen):
        self.screen = screen

    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)


class BallScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.v = geo.Vector2D.zero()
        self.a = geo.Vector2D(0, 1)
        self.elasticity = 0.8
        self.friction = 0.1

    def initGraphics(self, screen):
        self.screen = screen

        self.ball = utilities.load_image('ball.png')
        self.ballrect = self.ball.get_rect()
        self.ballrect.left, self.ballrect.top = 0, 0

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        # follow mouse drag
        if click[0]:
            currentPos = geo.Vector2D(*mouse)
            self.v = currentPos - self.lastPos
            self.lastPos = currentPos
            self.ballrect.center = mouse
            if self.ballrect.left < 0:
                self.ballrect.left = 0
            if self.ballrect.right > screenWidth:
                self.ballrect.right = screenWidth
            if self.ballrect.top < 0:
                self.ballrect.top = 0
            if self.ballrect.bottom > screenHeight:
                self.ballrect.bottom = screenHeight
        else:
            self.lastPos = geo.Vector2D(*mouse)
            self.v += self.a
            self.ballrect.move_ip(*self.v)
            if self.ballrect.left < 0:
                self.v.x = -self.v.x * self.elasticity
                self.ballrect.left = 0
            if self.ballrect.right > screenWidth:
                self.v.x = -self.v.x * self.elasticity
                self.ballrect.right = screenWidth
            if self.ballrect.top < 0:
                self.v.y = -self.v.y * self.elasticity
                self.ballrect.top = 0
            if self.ballrect.bottom > screenHeight:
                self.v.y = int(-self.v.y * self.elasticity)
                if self.v.x > 0:
                    self.v.x = int(self.v.x - self.friction)
                elif self.v.x < 0:
                    self.v.x = int(self.v.x + self.friction)

                self.ballrect.bottom = screenHeight

    def Render(self):
        # For the sake of brevity, the title scene is a blank black screen
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.ball, self.ballrect)
        pygame.display.flip()


class Tanks(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.gravity = geo.Vector2D(0, 1)
        self.elasticity = 0.8
        self.friction = 0.1
        self.tanks = []
        self.tanks.append(Tank((0, 0), (255, 0, 0)))
        self.balls = []

    def initGraphics(self, screen):
        self.screen = screen

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                p1 = self.tanks[0]
                
                ball = p1.shoot()
                self.balls.append(ball)

    def Update(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        if pressed[0]:
            p1 = self.tanks[0]
            p1.power += p1.power_dir * p1.power_speed
            if p1.power >= 1:
                p1.power_dir *= -1
                p1.power = 1
            elif p1.power <= 0:
                p1.power_dir *= -1
                p1.power = 0

        for tank in self.tanks:
            tank.v += self.gravity
            tank.rect.move_ip(*tank.v)

            if tank.rect.y > screenHeight - tank.rect.height:
                tank.rect.y = screenHeight - tank.rect.height

            if tank.rect.x < 0:
                tank.rect.x = 0
            elif tank.rect.x > screenWidth - tank.rect.width:
                tank.rect.x = screenWidth - tank.rect.width

            origin = tank.origin()
            dr = geo.Vector2D(*mouse) - geo.Vector2D(*origin)

            tank.angle = (math.degrees(geo.Vector2D.angle_between(dr, geo.Vector2D(1, 0))))
        
        for ball in self.balls:
            ball.v += self.gravity
            ball.rect.move_ip(*ball.v)
            
            if ball.rect.y > screenHeight - ball.rect.height:
                self.balls.remove(ball)

            if ball.rect.x < 0:
                self.balls.remove(ball)
            elif ball.rect.x > screenWidth - ball.rect.width:
                self.balls.remove(ball)

    def Render(self):
        # For the sake of brevity, the title scene is a blank black screen
        self.screen.fill((255, 255, 255))

        for ball in self.balls:
            ball.draw(self.screen)

        for tank in self.tanks:
            tank.draw(self.screen)

        pygame.display.flip()

