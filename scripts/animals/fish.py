import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import math

from scripts.parts.point import Point

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *

    ##############################################################################################

def generate_ellipsis(point_num, rotation, minor_radius, major_radius, pos=(0, 0)):
    points = []
    for i in range(point_num):
        a = math.radians(360 * (i / point_num))
        x = pos[0] + math.cos(rotation) * minor_radius * math.cos(a) - math.sin(rotation) * major_radius * math.sin(a)
        y = pos[1] + math.sin(rotation) * minor_radius * math.cos(a) + math.cos(rotation) * major_radius * math.sin(a)
        points.append(vec(x, y))
    return points

    ##############################################################################################

class Fish(pygame.sprite.Sprite):
    def __init__(self, game, groups, anchor_pos=(200, HEIGHT/2), ai=False):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.points = pygame.sprite.Group()
        self.anchor = Point(game, [self.points], anchor_pos)
        self.point_number = 10
        self.constraints = [22, 30, 36, 36, 30, 24, 18, 14, 12, 10, 6]
        self.angle_threshold = 40

        points = [self.anchor]
        for i in range(self.point_number):
            points.append(Point(game, [self.points], (anchor_pos[0] + (i + 1) * 80, HEIGHT/2)))

        for i in range(len(points)):
            if i == 0:
                points[i].next = points[i + 1]
            elif i == len(self.points) - 1:
                points[i].prev = points[i - 1]
            else:
                points[i].prev = points[i - 1]
                points[i].next = points[i + 1]

            points[i].distance_constraint = self.constraints[i]

        self.ai = ai
        self.ai_t = 0

    def ai_move(self):
        self.ai_t += math.radians(3)
        self.anchor.pos = vec(WIDTH - 200, HEIGHT - 200) + vec(math.cos(self.ai_t), math.sin(self.ai_t)) * 150

    def update(self):
        if self.ai:
            self.ai_move()

        self.draw()

    def draw(self):
        first_half = []
        second_half = []

        for i, p in enumerate(self.points.sprites()):
            p: Point

            if p.next:
                delta = p.pos - p.next.pos
                angle = math.atan2(delta.y, delta.x)
                
                side_1 = p.pos + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * p.distance_constraint
                side_2 = p.pos + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * p.distance_constraint
                first_half.append(side_1)
                second_half.append(side_2)

            else:
                side_1 = p.pos + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * p.distance_constraint
                side_2 = p.pos + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * p.distance_constraint
                first_half.append(side_1)
                second_half.append(side_2)


            p.update()

        side_points = first_half + second_half[::-1]
        if pygame.key.get_pressed()[pygame.K_d]:
            for i in range(0, len(side_points) - 1):
                pygame.draw.circle(self.screen, (255, 0, 0), side_points[i], 3)

                p1 = side_points[i]
                p2 = side_points[i + 1]
                pygame.draw.line(self.screen, (200, 200, 200), p1, p2)

            pygame.draw.circle(self.screen, (255, 0, 0), side_points[-1], 3)
            pygame.draw.line(self.screen, (200, 200, 200), side_points[-1], side_points[0])

        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        for i, side_fin_point in enumerate([self.points.sprites()[2], self.points.sprites()[5]]):
            delta = side_fin_point.pos - side_fin_point.next.pos
            angle = math.atan2(delta.y, delta.x)
            side_fin_point: Point

            side_fins = [
                side_fin_point.pos + vec(math.cos(angle + math.pi / 2 + math.pi / 8), math.sin(angle + math.pi / 2 + math.pi / 8)) * side_fin_point.distance_constraint,
                side_fin_point.pos + vec(math.cos(angle - math.pi / 2 - math.pi / 8), math.sin(angle - math.pi / 2 - math.pi / 8)) * side_fin_point.distance_constraint
            ]
            flag = True
            for point in side_fins:
                ellipse = generate_ellipsis(10, angle + (math.pi/4 if flag else -math.pi/4), 16 / (i+1), 30 / (i+1), point)
                pygame.draw.polygon(surf, (10, 200, 168, 150), ellipse)
                flag = not flag

        pygame.draw.polygon(surf, (238, 197, 36, 150), side_points)
        pygame.draw.circle(surf, (238, 197, 36, 150), self.points.sprites()[0].pos, self.points.sprites()[0].distance_constraint)
        pygame.draw.circle(surf, (238, 197, 36, 150), self.points.sprites()[-1].pos, self.points.sprites()[-1].distance_constraint)
        self.screen.blit(surf, (0, 0))