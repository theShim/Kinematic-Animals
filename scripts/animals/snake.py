import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import math
import numpy as np

from scripts.parts.point import Point

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *

    ##############################################################################################

class Snake(pygame.sprite.Sprite):
    def __init__(self, game, groups, anchor_pos = (100, HEIGHT/2), angle_constraint_flag = False):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.points = pygame.sprite.Group()
        self.anchor = Point(game, [self.points], anchor_pos)
        self.point_number = 24
        self.constraints = [40, 50, 35] + [35 - (1 * i) for i in range(self.point_number - 2)]
        self.angle_threshold = 35

        points = [self.anchor]
        for i in range(self.point_number):
            points.append(Point(game, [self.points], (100 + (i + 1) * 80, HEIGHT/2)))

        for i in range(len(points)):
            if i == 0:
                points[i].next = points[i + 1]
            elif i == len(self.points) - 1:
                points[i].prev = points[i - 1]
            else:
                points[i].prev = points[i - 1]
                points[i].next = points[i + 1]

            points[i].distance_constraint = self.constraints[i]

        self.angle_constraint_flag = angle_constraint_flag

    def angle_constraint(self):
        for i in range(1, len(self.points) - 1):
            p1: Point = self.points.sprites()[i - 1]
            p2: Point = self.points.sprites()[i]
            p3: Point = self.points.sprites()[i + 1]
            # pygame.draw.line(self.screen, (0, 0, 255), p1.pos, p2.pos, 3)
            # pygame.draw.line(self.screen, (0, 0, 255), p3.pos, p2.pos, 3)

            a = p1.pos - p2.pos
            b = p3.pos - p2.pos
            dotted = np.dot(a.normalize(), b.normalize())
            theta = math.acos(dotted / (a.normalize().magnitude() * b.normalize().magnitude()))

            if theta < math.radians(180 - self.angle_threshold):
                angle = math.atan2(b.y, b.x)
                new1 = p2.pos + vec(math.cos(angle + math.radians(180 + self.angle_threshold)), math.sin(angle + math.radians(180 + self.angle_threshold))) * a.magnitude()
                new2 = p2.pos + vec(math.cos(angle + math.radians(180 - self.angle_threshold)), math.sin(angle + math.radians(180 - self.angle_threshold))) * a.magnitude()
                # pygame.draw.line(self.screen, (0, 255, 255), p2.pos, new, 3)

                if p1.pos.distance_to(new1) < p1.pos.distance_to(new2):
                    new = new1
                else:
                    new = new2

                p1.pos = new
                self.points.update(False)
            # break

    def update(self):
        self.points.update()

        if self.angle_constraint_flag:
            self.angle_constraint()

        self.draw()

    def draw(self):
        first_half = []
        second_half = []

        points = self.points.sprites()

        #head stuff
        head_delta = self.anchor.pos - points[1].pos
        head_angle = math.atan2(head_delta.y, head_delta.x)
        head = self.anchor.pos + vec(math.cos(head_angle), math.sin(head_angle)) * self.anchor.distance_constraint
        first_half.append(head)
        p = self.anchor.pos + vec(math.cos(head_angle - math.pi / 5), math.sin(head_angle - math.pi / 5)) * self.anchor.distance_constraint
        first_half.append(p)
        p = self.anchor.pos + vec(math.cos(head_angle + math.pi / 5), math.sin(head_angle + math.pi / 5)) * self.anchor.distance_constraint
        second_half.append(p)
        p = self.anchor.pos + vec(math.cos(head_angle - math.pi / 2), math.sin(head_angle - math.pi / 2)) * self.anchor.distance_constraint
        first_half.append(p)
        p = self.anchor.pos + vec(math.cos(head_angle + math.pi / 2), math.sin(head_angle + math.pi / 2)) * self.anchor.distance_constraint
        second_half.append(p)

        #body
        i = 1
        for point in points[1:]:
            try: delta = point.pos - points[i + 1].pos
            except: break
            angle = math.atan2(delta.y, delta.x)

            p = point.pos + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * point.distance_constraint
            first_half.append(p)
            p = point.pos + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * point.distance_constraint
            second_half.append(p)

            i += 1

        #tail stuff
        tail_delta = points[-1].pos - points[-2].pos
        tail_angle = math.atan2(tail_delta.y, tail_delta.x)
        p = points[-1].pos + vec(math.cos(tail_angle + math.pi / 5), math.sin(tail_angle + math.pi / 5)) * points[-1].distance_constraint
        first_half.append(p)
        tail = points[-1].pos + vec(math.cos(tail_angle), math.sin(tail_angle)) * points[-1].distance_constraint
        first_half.append(tail)
        p = points[-1].pos + vec(math.cos(tail_angle - math.pi / 5), math.sin(tail_angle - math.pi / 5)) * points[-1].distance_constraint
        second_half.append(p)



        #actual drawing
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        side_points = first_half + second_half[::-1]
        pygame.draw.polygon(surf, (255, 0, 0, 128), side_points)
        pygame.draw.polygon(surf, (100, 0, 0, 255), side_points, 5)

        l_eye = self.anchor.pos + vec(math.cos(head_angle - math.radians(75)), math.sin(head_angle - math.radians(75))) * 24
        pygame.draw.circle(surf, (255, 255, 255, 255), l_eye, 6)
        r_eye = self.anchor.pos + vec(math.cos(head_angle + math.radians(75)), math.sin(head_angle + math.radians(75))) * 24
        pygame.draw.circle(surf, (255, 255, 255, 255), r_eye, 6)

        if pygame.key.get_pressed()[pygame.K_d]:
            for point in first_half:
                pygame.draw.circle(surf, (255, 0, 255, 255), point, 3)
            for point in second_half:
                pygame.draw.circle(surf, (0, 255, 255, 255), point, 3)

        self.screen.blit(surf, (0, 0))