import pygame
import utilities
import geometry as geo
from tanks import *
import math, random
import time
import colors

class SceneBase:
    def __init__(self):
        self.next = self
        self.initialized = False

    # only needs to be called once throughout main loop
    def initGraphics(self, screen):
        self.screen = screen
        self.initialized = True

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
        SceneBase.initGraphics(self, screen)

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


class Start(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

        self.options = ['Start', 'Quit']
        self.buttons = pygame.sprite.Group()

    def initGraphics(self, screen):
        SceneBase.initGraphics(self, screen)

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        font = pygame.font.Font('freesansbold.ttf', 20)

        for i, option in enumerate(self.options):
            rect = pygame.Rect(int(screenWidth/2) - 50, int(screenHeight/2) - 100 + i*50, 100, 30)
            passive_color = colors.BLACK
            active_color = colors.RED

            if i == 0:
                def action():
                    self.SwitchToScene(Tanks())
            else:
                def action():
                    self.Terminate()

            button = Button(rect, action, font, active_color, option, colors.WHITE, passive_color, option, colors.WHITE)

            self.buttons.add(button)

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        self.buttons.update()

    def Render(self):
        self.screen.fill(colors.WHITE)
        self.buttons.draw(self.screen)
        pygame.display.flip()


class Button(pygame.sprite.Sprite):
    def __init__(self, rect, action, font, active_color, active_text, active_textcolor, passive_color, passive_text, passive_textcolor):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((rect[2], rect[3]))

        self.rect = rect

        self.font = font

        self.action = action

        self.active_color = active_color
        self.active_text = active_text
        self.active_textcolor = active_textcolor
        self.passive_color = passive_color
        self.passive_text = passive_text
        self.passive_textcolor = passive_textcolor

    def update(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        if self.rect.x <= mouse[0] <= self.rect.x + self.rect.w and self.rect.y <= mouse[1] <= self.rect.y + self.rect.h:
            self.image.fill(self.active_color)
            self.renderButtonText(self.active_text, self.active_textcolor)

            if pressed[0]:
                self.action()
        else:
            self.image.fill(self.passive_color)
            self.renderButtonText(self.passive_text, self.passive_textcolor)

    def renderButtonText(self, text, color):
        textsurf = self.font.render(text, True, color)
        textrect = textsurf.get_rect()
        # Put text in the middle of button
        textrect.left = self.rect.width/2 - textrect.width/2
        textrect.top = self.rect.height/2 - textrect.height/2
        self.image.blit(textsurf, textrect)


class Tanks(SceneBase):
    BALLOON_SPAWN_TIME = 10
    ZOMBIE_RESPAWN_TIME = 2
    BAT_RESPAWN_TIME = 30
    RUNNER_RESPAWN_TIME = 45
    MAX_ZOMBIES = 5

    def __init__(self):
        SceneBase.__init__(self)
        self.gravity = geo.Vector2D(0, 1)
        self.elasticity = 0.8
        self.friction = 0.1
        self.tank = (Tank((0, 0), (255, 0, 0)))
        self.projectiles = pygame.sprite.Group()
        self.explosions = []
        self.baddies = pygame.sprite.Group()
        self.score = 0
        self.baddie_queue = []
        self.balloons = pygame.sprite.Group()
        self.startTime = time.time()
        self.lastBalloonSpawnTime = self.startTime
        self.timeOfLastAdd = {}
        self.timeOfLastAdd['bats'] = time.time()
        self.timeOfLastAdd['zombies'] = time.time()
        self.timeOfLastAdd['runners'] = time.time()
        self.speeds = {}
        self.speeds['zombies'] = 0.3
        self.speeds['bats'] = 0.5
        self.speeds['runners'] = 2
        self.bomb = None

    def initGraphics(self, screen):
        SceneBase.initGraphics(self, screen)

        # add first zombie, for some reason this needs to be here
        zombie = Zombie(self.speeds['zombies'])
        self.baddies.add(zombie)
        self.timeOfLastAdd['zombies'] = time.time()

        self.scoreText = pygame.font.Font('freesansbold.ttf', 30)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                p1 = self.tank

                if p1.weapon != Weapon.MACHINE_GUN:
                    if not self.bomb:
                        if p1.weapon == Weapon.BOMB:
                            p = self.bomb = p1.shoot()
                        else:
                            p = p1.shoot()
                        self.projectiles.add(p)
                    else:
                        self.bomb = None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                p1 = self.tank

                if self.bomb:
                    bomb = self.bomb
                    bomb.kill_on_explode = True
                    self.killBaddies(bomb)

                p1.power = 0.5

    def Update(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        info = pygame.display.Info()
        screenWidth, screenHeight = info.current_w, info.current_h

        if pressed[0]:
            p1 = self.tank

            if p1.weapon.value < Weapon.MACHINE_GUN.value:
                p1.power += p1.power_dir * p1.power_speed
                if p1.power >= 1:
                    p1.power_dir *= -1
                    p1.power = 1
                elif p1.power <= 0.5:
                    p1.power_dir *= -1
                    p1.power = 0.5
            elif p1.weapon == Weapon.MACHINE_GUN:
                if time.time() - p1.lastShootTime > p1.MACHINE_GUN_RELOAD_TIME:

                    bullet = p1.shoot()

                    self.projectiles.add(bullet)

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

        collided_objects = pygame.sprite.spritecollide(self.tank, self.baddies, False, self.tank.collided)

        for baddy in collided_objects:
            if self.score > self.loadScore('score.save'):
                self.saveScore('score.save')
            self.SwitchToScene(Start())

        for i, p in enumerate(self.projectiles):

            if type(p) is not Laser:
                p.v += self.gravity
                p.rect.move_ip(*p.v)
            else:
                if time.time() - self.tank.lastShootTime >= Laser.LASER_TIME:
                    p.kill()

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

            self.killBaddies(p)

            collided_objects = pygame.sprite.spritecollide(p, self.balloons, True, p.collided)

            for balloon in collided_objects:
                self.explosions.append((p.explode(), p.pos()))
                p.kill()

                balloon.pop()

                if balloon.color == colors.DARK_GREEN:
                    self.tank.weapon = Weapon.BOMB
                    self.tank.ammo = 2
                elif balloon.color == colors.DARK_BLUE:
                    self.tank.weapon = Weapon.MACHINE_GUN
                    self.tank.ammo = 10
                elif balloon.color == colors.DARK_RED:
                    self.tank.weapon = Weapon.LASER
                    self.tank.ammo = 1

                self.incrementScore(5)

        if time.time() - self.timeOfLastAdd['zombies'] > self.ZOMBIE_RESPAWN_TIME:
            if len(self.baddie_queue) > 0 and len(self.baddies) < self.MAX_ZOMBIES:
                baddy = self.baddie_queue.pop(0)
                self.baddies.add(baddy)
                self.timeOfLastAdd['zombies'] = time.time()

        if time.time() - self.startTime > 30:
            if time.time() - self.timeOfLastAdd['bats'] > self.BAT_RESPAWN_TIME:
                self.BAT_RESPAWN_TIME *= 0.95
                self.speeds['bats'] *= 1.1
                bat = Bat(self.speeds['bats'])
                self.baddies.add(bat)
                self.timeOfLastAdd['bats'] = time.time()

        if time.time() - self.startTime > 60:
            if time.time() - self.timeOfLastAdd['runners'] > self.RUNNER_RESPAWN_TIME:
                self.RUNNER_RESPAWN_TIME *= 0.9
                self.speeds['runners'] *= 1.2
                runner = Runner(self.speeds['runners'])
                self.baddies.add(runner)
                self.timeOfLastAdd['runners'] = time.time()

        if time.time() - self.lastBalloonSpawnTime > self.BALLOON_SPAWN_TIME:
            pos = random.uniform(100, screenWidth - 100), random.uniform(screenHeight-100, screenHeight - 50)

            if self.score < 30:
                color_list = [colors.DARK_GREEN]
            elif self.score < 100:
                color_list = [colors.DARK_BLUE, colors.DARK_GREEN]
            else:
                color_list = [colors.DARK_RED, colors.DARK_GREEN, colors.DARK_BLUE]

            color = random.choice(color_list)
            balloon = Balloon(pos, color)

            self.balloons.add(balloon)
            self.lastBalloonSpawnTime = time.time()


        self.baddies.update()
        self.balloons.update()

    def killBaddies(self, projectile):
        collided_objects = pygame.sprite.spritecollide(projectile, self.baddies, True, projectile.collided)
        for baddy in collided_objects:

            self.explosions.append((projectile.explode(), projectile.pos()))
            projectile.kill()

            if type(baddy) is Zombie:
                # add next zombie
                self.speeds['zombies'] *= 1.01
                zombie1 = Zombie(self.speeds['zombies'])
                zombie2 = Zombie(self.speeds['zombies'])
                self.baddie_queue.append(zombie1)
                self.baddie_queue.append(zombie2)

                self.incrementScore(1)
            elif type(baddy) is Bat:
                self.incrementScore(5)
            elif type(baddy) is Runner:
                self.incrementScore(10)

    def incrementScore(self, inc):
        self.score += inc

    def Render(self):
        self.screen.fill(colors.WHITE)

        scoreSurf = self.scoreText.render("Score: {0}".format(self.score), True, (0, 0, 0))
        scoreRect = scoreSurf.get_rect()
        scoreRect.center = 100, 50
        self.screen.blit(scoreSurf, scoreRect)

        for i, tup in enumerate(self.explosions):
            exp, pos = tup
            if exp:
                if exp.i < len(exp.images):
                    img = exp.next()
                    img = pygame.transform.scale(img, (50, 50))
                    x, y, w, h = img.get_rect()
                    pos = pos[0] - int(w/2), pos[1] - int(h/2)
                    self.screen.blit(img, pos)
                else:
                    self.explosions.pop(i)
            else:
                self.explosions.pop(i)

        for p in self.projectiles:
            p.draw(self.screen)

        self.tank.draw(self.screen)

        self.baddies.draw(self.screen)
        self.balloons.draw(self.screen)

        self.drawCrossHairs()

        pygame.display.flip()

    def drawCrossHairs(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        offset = 5
        length = 10
        if pressed[0]:
            pygame.draw.line(self.screen, colors.RED, (mouse[0], mouse[1] - offset), (mouse[0], mouse[1] - length))
            pygame.draw.line(self.screen, colors.RED, (mouse[0], mouse[1] + offset), (mouse[0], mouse[1] + length))
            pygame.draw.line(self.screen, colors.RED, (mouse[0] - offset, mouse[1]), (mouse[0] - length, mouse[1]))
            pygame.draw.line(self.screen, colors.RED, (mouse[0] + offset, mouse[1]), (mouse[0] + length, mouse[1]))
        else:
            pygame.draw.line(self.screen, colors.BLACK, (mouse[0], mouse[1] - offset), (mouse[0], mouse[1] - length))
            pygame.draw.line(self.screen, colors.BLACK, (mouse[0], mouse[1] + offset), (mouse[0], mouse[1] + length))
            pygame.draw.line(self.screen, colors.BLACK, (mouse[0] - offset, mouse[1]), (mouse[0] - length, mouse[1]))
            pygame.draw.line(self.screen, colors.BLACK, (mouse[0] + offset, mouse[1]), (mouse[0] + length, mouse[1]))

    def saveScore(self, filename):
        with open(filename, 'w') as f:
            f.write("High-score,{0}".format(self.score))

    def loadScore(self, filename):

        try:
            with open(filename, 'r') as f:
                scoreline = f.readline()
                score = scoreline.split(',')[1]
        except:
            score = 0
            print("No save data found.")

        return int(score)
