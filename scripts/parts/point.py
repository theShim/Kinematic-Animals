import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *

    ##############################################################################################

class Point(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.pos = vec(pos)
        self.distance_constraint = 50
        self.prev: Point = None
        self.next: Point = None

        self.held = False

        self.acc = vec(0, GRAV)
        self.vel = vec()

    def mouse_stuff(self):
        mouse = pygame.mouse.get_pressed()
        mousePos = pygame.mouse.get_pos()

        for point in self.groups()[0].sprites():
            if point.held and point != self:
                return
            
        if mouse[0]:
            if self.pos.distance_to(mousePos) < 8:
                if self.held == False:
                    self.held = True
        else:
            self.held = False

        if self.held:
            self.pos = vec(mousePos)
            self.vel = vec(0, GRAV)

    def constraint(self):
        if self.prev:
            if self.pos.distance_to(self.prev.pos) > self.distance_constraint:
                delta: vec = self.pos - self.prev.pos
                delta = delta.normalize() * self.prev.distance_constraint
                self.pos = delta + self.prev.pos

            elif self.pos.distance_to(self.prev.pos) < self.distance_constraint:
                delta: vec = self.pos - self.prev.pos
                delta = delta.normalize() * self.prev.distance_constraint
                self.pos = delta + self.prev.pos

    def update(self, mouse_flag=True):
        if mouse_flag:
            self.mouse_stuff()
        self.constraint()

        self.draw()

    def draw(self):
        if pygame.key.get_pressed()[pygame.K_d]:
            pygame.draw.circle(self.screen, (200, 200, 200, 128) if self.prev else (176, 15, 15), self.pos, 8, 4)

            parts = 36
            for i in range(0, parts, 2):
                t1 = math.radians(360 * (i / parts))
                t2 = math.radians(360 * ((i+1) / parts))

                pos1 = self.pos + vec(math.cos(t1), math.sin(t1)) * self.distance_constraint
                pos2 = self.pos + vec(math.cos(t2), math.sin(t2)) * self.distance_constraint

                pygame.draw.line(self.screen, (180, 180, 180), pos1, pos2)

        else:
            if not self.prev:
                pygame.draw.circle(self.screen, (176, 15, 15), self.pos, 8, 4)