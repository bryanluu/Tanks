import pygame
import utilities
import geometry as geo
from tanks import Tank, Zombie, Balloon, Weapon, Bomb
import math, random
import time

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
    BALLOON_SPAWN_TIME = 10
    ZOMBIE_RESPAWN_TIME = 2
    MAX_ZOMBIES = 5

    def __init__(self):
        SceneBase.__init__(self)
        self.gravity = geo.Vector2D(0, 1)
        self.elasticity = 0.8
        self.friction = 0.1
        self.tank = (Tank((0, 0), (255, 0, 0)))
        self.projectiles = pygame.sprite.Group()
        self.explosions = []
        self.zombies = pygame.sprite.Group()
        self.score = 0
        self.baddie_queue = []
        self.balloons = pygame.sprite.Group()
        self.startTime = time.time()
        self.lastBalloonSpawnTime = self.startTime

    def initGraphics(self, screen):
        self.screen = screen

        # add first zombie, for some reason this needs to be here
        zombie = Zombie((0, 255, 0), 10, 30, 0.3)
        self.zombies.add(zombie)
        self.timeOfLastAdd = time.time()

        self.scoreText = pygame.font.Font('freesansbold.ttf', 30)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                p1 = self.tank
                
                p = p1.shoot()
                self.projectiles.add(p)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                p1 = self.tank

                p1.power = 0.5

    def Update(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        if pressed[0]:
            p1 = self.tank
            p1.power += p1.power_dir * p1.power_speed
            if p1.power >= 1:
                p1.power_dir *= -1
                p1.power = 1
            elif p1.power <= 0.5:
                p1.power_dir *= -1
                p1.power = 0.5

        self.tank.v += self.gravity
        self.tank.rect.move_ip(*self.tank.v)

        if self.tank.rect.y > screenHeight - self.tank.rect.height:
            self.tank.rect.y = screenHeight - self.tank.rect.height

        if self.tank.rect.x < 0:
            self.tank.rect.x = 0
        elif self.tank.rect.x > screenWidth - self.tank.rect.width:
            self.tank.rect.x = screenWidth - self.tank.rect.width

        origin = self.tank.origin()
        dr = geo.Vector2D(*mouse) - geo.Vector2D(*origin)

        self.tank.angle = (math.degrees(geo.Vector2D.angle_between(dr, geo.Vector2D(1, 0))))

        collided_objects = pygame.sprite.spritecollide(self.tank, self.zombies, False)

        for zombie in collided_objects:
            self.Terminate()

        for i, p in enumerate(self.projectiles):
            p.v += self.gravity
            p.rect.move_ip(*p.v)
            
            if p.rect.y > screenHeight - p.rect.height or p.rect.x < 0 or p.rect.x > screenWidth - p.rect.width:
                if type(p) is not Bomb:
                    self.explosions.append((p.explode(), p.pos()))
                    p.kill()
                else:
                    if p.rect.y > screenHeight - p.rect.height:
                        p.rect.y = screenHeight - p.rect.height
                        p.v *= 0.9
                    if p.rect.x > screenWidth - p.rect.width:
                        p.rect.x = screenWidth - p.rect.width
                        p.v.x *= -1
                        p.v *= 0.5
                    elif p.rect.x < 0:
                        p.rect.x = 0
                        p.v.x *= -1
                        p.v *= 0.5

                    if time.time() - p.start > Bomb.BOMB_FUSE_TIME:
                        self.explosions.append((p.explode(), p.pos()))
                        p.kill()

            collided_objects = pygame.sprite.spritecollide(p, self.zombies, True, p.collided)

            for zombie in collided_objects:
                self.explosions.append((p.explode(), p.pos()))
                p.kill()

                # add next zombie
                zombie2 = Zombie((0, 255, 0), 10, 30, zombie.speed*1.1)
                zombie3 = Zombie((0, 255, 0), 10, 30, zombie.speed*1.1)
                self.baddie_queue.append(zombie2)
                self.baddie_queue.append(zombie3)

                self.incrementScore(1)

            collided_objects = pygame.sprite.spritecollide(p, self.balloons, True, p.collided)

            for balloon in collided_objects:
                self.explosions.append((p.explode(), p.pos()))
                p.kill()

                balloon.pop()

                self.tank.weapon = Weapon.BOMB

                self.incrementScore(5)


        if time.time() - self.timeOfLastAdd > self.ZOMBIE_RESPAWN_TIME:
            if len(self.baddie_queue) > 0 and len(self.zombies) < self.MAX_ZOMBIES:
                zombie = self.baddie_queue.pop(0)
                self.zombies.add(zombie)
                self.timeOfLastAdd = time.time()

        if time.time() - self.lastBalloonSpawnTime > self.BALLOON_SPAWN_TIME:
            pos = random.uniform(100, screenWidth - 100), random.uniform(100, screenHeight - 50)
            balloon = Balloon(pos, (0, 100, 0))

            self.balloons.add(balloon)
            self.lastBalloonSpawnTime = time.time()

        self.zombies.update()
        self.balloons.update()


    def incrementScore(self, inc):
        self.score += inc



    def Render(self):
        self.screen.fill((255, 255, 255))

        scoreSurf = self.scoreText.render("Score: {0}".format(self.score), True, (0, 0, 0))
        scoreRect = scoreSurf.get_rect()
        scoreRect.center = 100, 50
        self.screen.blit(scoreSurf, scoreRect)

        for i, tup in enumerate(self.explosions):
            exp, pos = tup
            if exp.i < len(exp.images):
                img = exp.next()
                img = pygame.transform.scale(img, (50, 50))
                x, y, w, h = img.get_rect()
                pos = pos[0] - int(w/2), pos[1] - int(h/2)
                self.screen.blit(img, pos)
            else:
                self.explosions.pop(i)

        for p in self.projectiles:
            p.draw(self.screen)

        self.tank.draw(self.screen)

        self.zombies.draw(self.screen)
        self.balloons.draw(self.screen)

        pygame.display.flip()

