import math
import random

import pygame

ROBOT_RADIUS = 10
SIGMA_MOVE = .5
SIGMA_ROTATE = math.radians(.3)


class Robot():

    def __init__(self, position, angle) -> None:
        self.position = position
        self.angle = angle
        self.radius = ROBOT_RADIUS

    def get_position(self):
        return self.position

    def get_angle(self):
        return self.angle

    def rotate(self, angle=math.radians(15), *, target_angle=None):

        angle = angle + random.gauss(0, SIGMA_ROTATE)

        if target_angle is None:
            self.angle += angle
            target_angle = self.angle
        else:
            target_angle += self.angle

        return target_angle

    def apply_rotation(self, angle):
        self.angle = angle

    def move(self, speed=10, *, position=None):

        if position is None:
            position = self.position

        speed = speed + random.gauss(0, SIGMA_MOVE)
        position[0] += speed * math.cos(self.angle)
        position[1] += speed * math.sin(self.angle)

        return position

    def apply_move(self, position):
        self.position = position

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.position, ROBOT_RADIUS)
        pygame.draw.line(screen, (255, 0, 0), self.position, (self.position[0] + ROBOT_RADIUS * math.cos(
            self.angle), self.position[1] + ROBOT_RADIUS * math.sin(self.angle)), 3)
