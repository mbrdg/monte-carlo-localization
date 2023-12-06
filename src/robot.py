import math
import itertools
import random

import numpy as np
import pygame
from shapely.geometry import LineString

from settings import *

ROBOT_RADIUS = 10
SIGMA_MOVE = .5
SIGMA_ROTATE = math.radians(.3)
SIGMA_MEASURE = 1.0


class Robot:
    def __init__(self, position, angle, *,
                 max_sensor_range=50.0, aperture=math.pi/4.0, num_sensors=5):
        self.position = position
        self.angle = angle
        self.radius = ROBOT_RADIUS

        self.max_sensor_range = max_sensor_range
        self.aperture = aperture
        self.num_sensors = num_sensors

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

    def compute_sensor_points(self, distances=None):
        x, y = self.position
        start_angle = self.angle - self.aperture / 2.0
        stop_angle = self.angle + self.aperture / 2.0
        angles = np.linspace(start_angle, stop_angle, num=self.num_sensors)

        if distances is None:
            distances = itertools.repeat(self.max_sensor_range, self.num_sensors)

        return (
            (x + math.cos(angle) * distance, y + math.sin(angle) * distance)
            for angle, distance in zip(angles, distances)
        )

    @staticmethod
    def intersects(line1, line2):
        line1 = LineString(line1)
        line2 = LineString(line2)

        res = line1.intersection(line2)
        return (res.x, res.y) if res.geom_type == "Point" else None

    def measure(self, walls):
        measurements = []
        for sample in self.compute_sensor_points():
            intersections = (
                Robot.intersects(
                    (wall.pos1 * GRID_SIZE, wall.pos2 * GRID_SIZE), (self.position, sample)
                ) for wall in walls
            )
            distances = (
                math.dist(self.position, point)
                for point in intersections if point is not None
            )

            measure = min(min(distances, default=self.max_sensor_range), self.max_sensor_range)
            noise = random.gauss(0.0, SIGMA_MEASURE)
            measurements.append(measure + noise)

        return measurements

    def draw(self, screen, walls):
        x, y = self.position
        pygame.draw.circle(screen, (0, 0, 0), (x, y), ROBOT_RADIUS)

        xr, yr = x + self.radius * \
            math.cos(self.angle), y + self.radius * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (x, y), (xr, yr), 3)

        for sensor_point in self.compute_sensor_points():
            pygame.draw.line(screen, (0, 100, 100), (x, y), sensor_point, 3)

        distances = self.measure(walls)
        points = tuple(self.compute_sensor_points(distances))
        for point in points:
            pygame.draw.line(screen, (255, 0, 0), (x, y), point, 3)
