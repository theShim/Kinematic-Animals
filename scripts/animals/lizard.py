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

class Lizard(pygame.sprite.Sprite):
    def __init__(self, game, groups, anchor_pos = (100, HEIGHT/2), scale=0.5):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.points = pygame.sprite.Group()
        self.anchor = Point(game, [self.points], anchor_pos)
        self.constraints = [52, 58, 40, 60, 68, 71, 65, 50, 28, 16 + 7, 14 + 7, 12 + 7, 9 + 7, 9 + 7, 16, 14, 12, 9, 9]
        self.scale = scale
        if self.scale != 1:
            self.constraints = [r * self.scale for r in self.constraints]
        self.old_anchor_pos = self.anchor.pos.copy()

        self.point_number = len(self.constraints) - 1
        self.angle_threshold = 40

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


        self.points.update()

        self.legs = pygame.sprite.Group()
        for segment in [[3, 4], [7, 8]]:
            points = self.points.sprites()
            delta = points[segment[0]].pos - points[segment[1]].pos
            angle = math.atan2(delta.y, delta.x)
            Leg(self.game, 
                [self.legs], 
                points[segment[0]].pos + vec(math.cos(angle + math.pi/2), math.sin(angle + math.pi/2)) * points[segment[0]].distance_constraint, 
                points[segment[0]].pos + vec(math.cos(angle + math.pi/2), math.sin(angle + math.pi/2)) * (points[segment[0]].distance_constraint + 40),
                segment
            )
            Leg(self.game, 
                [self.legs], 
                points[segment[0]].pos + vec(math.cos(angle - math.pi/2), math.sin(angle - math.pi/2)) * points[segment[0]].distance_constraint, 
                points[segment[0]].pos + vec(math.cos(angle - math.pi/2), math.sin(angle - math.pi/2)) * (points[segment[0]].distance_constraint + 40),
                segment
            )

    def legs_update(self):
        flip = False
        points = self.points.sprites()
        for leg in self.legs.sprites():
            segment = leg.segment
            delta = points[segment[0]].pos - points[segment[1]].pos
            angle = math.atan2(delta.y, delta.x)
            leg.anchor = points[segment[0]].pos + vec(math.cos(angle + math.pi/2 * (-1 if flip else 1)), math.sin(angle + math.pi/2 * (-1 if flip else 1))) * points[segment[0]].distance_constraint
            # leg.points[1] = points[segment[0]].pos + vec(math.cos(angle + math.radians(70) * (-1 if flip else 1)), math.sin(angle + math.radians(70) * (-1 if flip else 1))) * (points[segment[0]].distance_constraint)
            leg.current_end_goal = points[segment[0]].pos + vec(math.cos(angle + math.radians(70) * (-1 if flip else 1)), math.sin(angle + math.radians(70) * (-1 if flip else 1))) * (points[segment[0]].distance_constraint + 40)
            flip = not flip

        self.legs.update()

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
            try:
                theta = math.acos(dotted / (a.normalize().magnitude() * b.normalize().magnitude()))
            except ValueError:
                continue

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

    def update(self):
        self.angle_constraint()
        self.old_anchor_pos = self.anchor.pos.copy()

        self.draw()
        self.points.update()
        self.legs_update()

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
        tail = points[-1].pos + vec(math.cos(tail_angle), math.sin(tail_angle)) * points[-1].distance_constraint
        first_half.append(tail)
        p = points[-1].pos + vec(math.cos(tail_angle + math.pi / 5), math.sin(tail_angle + math.pi / 5)) * points[-1].distance_constraint
        first_half.append(p)
        p = points[-1].pos + vec(math.cos(tail_angle - math.pi / 5), math.sin(tail_angle - math.pi / 5)) * points[-1].distance_constraint
        second_half.append(p)



        #actual drawing
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        side_points = first_half + second_half[::-1]
        pygame.draw.polygon(surf, (0, 255, 0, 128), side_points)

        for leg in self.legs.sprites():
            leg.draw_leg(surf)

        l_eye = self.anchor.pos + vec(math.cos(head_angle - math.radians(75)), math.sin(head_angle - math.radians(75))) * 16
        pygame.draw.circle(surf, (255, 255, 255, 255), l_eye, 6)
        r_eye = self.anchor.pos + vec(math.cos(head_angle + math.radians(75)), math.sin(head_angle + math.radians(75))) * 16
        pygame.draw.circle(surf, (255, 255, 255, 255), r_eye, 6)

        if pygame.key.get_pressed()[pygame.K_d]:
            for point in first_half:
                pygame.draw.circle(surf, (255, 0, 255, 200), point, 3)
            for point in second_half:
                pygame.draw.circle(surf, (0, 255, 255, 200), point, 3)

        self.screen.blit(surf, (0, 0))



class Leg(pygame.sprite.Sprite):
    def __init__(self, game, groups, anchor_pos: vec, end_pos: vec, segment):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen

        self.anchor = vec(anchor_pos)
        self.lengths = [20, 30]
        self.points = [self.anchor.copy()]
        self.end_goal = end_pos
        self.current_end_goal = end_pos.copy()
        self.segment = segment
        self.distance_constraint = [12, 8, 6]

        for length in self.lengths:
            last_point = self.points[-1]
            delta = self.end_goal - last_point
            new_point = last_point + delta * length
            self.points.append(new_point)

        self.fabrik_step = self.fabrik()
        self.walk_distance = sum(self.lengths) * 1.8
        self.new_step = False

    def fabrik(self):
        while True:
            #backward
            previous_copy = self.end_goal
            new_points = [self.end_goal]

            for i in range(1, len(self.points)):
                next_copy = previous_copy + (self.points[-(i+1)] - previous_copy).normalize() * self.lengths[-i]
                new_points.append(next_copy)
                previous_copy = next_copy

            new_points.reverse()
            self.points = new_points


            #forward
            previous_copy = self.anchor
            new_points = [self.anchor]

            for i in range(1, len(self.points)):
                direction = (self.points[i] - previous_copy).normalize()
                next_copy = previous_copy + direction * self.lengths[i - 1]
                new_points.append(next_copy)
                previous_copy = next_copy

            self.points = new_points
            yield

    def walk(self):
        if self.new_step == False:
            if self.end_goal.distance_to(self.current_end_goal) >= self.walk_distance:
                self.new_step = True
                
        else:
            self.end_goal += (self.current_end_goal - self.end_goal) / (self.current_end_goal - self.end_goal).magnitude() * 50
            if self.end_goal.distance_to(self.current_end_goal) < self.walk_distance / 4:
                self.end_goal = self.current_end_goal.copy()
                self.new_step = False

    def update(self):
        self.walk()
        next(self.fabrik_step)

        if pygame.key.get_pressed()[pygame.K_d]:
            self.draw()

    def draw(self):
        for i, p in enumerate(self.points):
            pygame.draw.line(self.screen, (200, 200, 200), p, self.points[i+1], 2) if i+1 < len(self.points) else ...
            pygame.draw.circle(self.screen, (255, 255, 255), p, 8, 3)

        pygame.draw.circle(self.screen, (220, 30, 20), self.anchor, 8, 1)
        pygame.draw.circle(self.screen, (220, 110, 30), self.current_end_goal, 8, 1)
        pygame.draw.circle(self.screen, (20, 30, 220), self.end_goal, 8, 1)

        # pygame.draw.circle(self.screen, (220, 220, 30), self.end_goal, self.walk_distance, 1)

    def draw_leg(self, surf):
        first_half = []
        second_half = []

        #tip
        delta = self.points[-1] - self.points[-2]
        angle = math.atan2(delta.y, delta.x)
        tip = self.points[-1] + vec(math.cos(angle), math.sin(angle)) * self.distance_constraint[0]
        first_half.append(tip)
        p = self.points[-1] + vec(math.cos(angle - math.pi / 5), math.sin(angle - math.pi / 5)) * self.distance_constraint[0]
        first_half.append(p)
        p = self.points[-1] + vec(math.cos(angle + math.pi / 5), math.sin(angle + math.pi / 5)) * self.distance_constraint[0]
        second_half.append(p)
        p = self.points[-1] + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * self.distance_constraint[0]
        first_half.append(p)
        p = self.points[-1] + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * self.distance_constraint[0]
        second_half.append(p)

        p = self.points[-2] + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * self.distance_constraint[1]
        first_half.append(p)
        p = self.points[-2] + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * self.distance_constraint[1]
        second_half.append(p)

        p = (self.points[-2] + self.points[-3]) / 2 + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * self.distance_constraint[1]
        first_half.append(p)
        p = (self.points[-2] + self.points[-3]) / 2 + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * self.distance_constraint[1]
        second_half.append(p)

        p = self.points[-3] + vec(math.cos(angle - math.pi / 2), math.sin(angle - math.pi / 2)) * self.distance_constraint[2]
        first_half.append(p)
        p = self.points[-3] + vec(math.cos(angle + math.pi / 2), math.sin(angle + math.pi / 2)) * self.distance_constraint[2]
        second_half.append(p)

        p = self.points[-3] + vec(math.cos(angle - math.pi * 0.75), math.sin(angle - math.pi * 0.75)) * self.distance_constraint[2]
        first_half.append(p)
        p = self.points[-3] + vec(math.cos(angle + math.pi * 0.75), math.sin(angle + math.pi * 0.75)) * self.distance_constraint[2]
        second_half.append(p)

        if pygame.key.get_pressed()[pygame.K_d]:
            for point in first_half:
                pygame.draw.circle(surf, (255, 0, 100, 255), point, 3)
            for point in second_half:
                pygame.draw.circle(surf, (255, 255, 0, 255), point, 3)
            
        side_points = first_half + second_half[::-1]
        pygame.draw.polygon(surf, (0, 255, 0, 128), side_points)