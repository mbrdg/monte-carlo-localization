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

    def get_position(self):
        return self.position

    def get_angle(self):
        return self.angle

    def rotate(self, angle=math.radians(15)):
        angle = angle + random.gauss(0, SIGMA_ROTATE)
        self.angle += angle

    def move(self, speed=10):
        speed = speed + random.gauss(0, SIGMA_MOVE)
        self.position[0] += speed * math.cos(self.angle)
        self.position[1] += speed * math.sin(self.angle)

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.position, ROBOT_RADIUS)
        pygame.draw.line(screen, (255, 0, 0), self.position, (self.position[0] + ROBOT_RADIUS * math.cos(
            self.angle), self.position[1] + ROBOT_RADIUS * math.sin(self.angle)), 3)
