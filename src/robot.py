import math
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

    def compute_sensor_points(self):
        x, y = self.position
        start_angle = self.angle - self.aperture / 2.0
        stop_angle = self.angle + self.aperture / 2.0

        return (
            (x + math.cos(angle) * self.max_sensor_range,
             y + math.sin(angle) * self.max_sensor_range)
            for angle in np.linspace(start_angle, stop_angle, num=self.num_sensors)
        )

    @staticmethod
    def line_line_intersection(line1, line2):

        line1 = LineString(line1)
        line2 = LineString(line2)

        res = line1.intersection(line2)

        if res.geom_type == 'Point':
            return res.x, res.y

        return None

        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def measure(self, walls):
        measurements = []
        for sample in self.compute_sensor_points():

            # wall_0 = list(walls)[0]
            # wall_p1, wall_p2 = wall_0.pos1 * GRID_SIZE, wall_0.pos2 * GRID_SIZE
            #
            # intersection = Robot.line_line_intersection(
            #    (wall_p1, wall_p2), (self.position, sample))
            #
            # print(
            #    f'Wall: {wall_p1}, {wall_p2}, Robot: {self.position}, {sample}')
            #
            # if intersection is not None:
            #    print('INTERSECTION ', intersection)
            #
            # measure = math.dist(self.position, intersection)
            #
            # return [measure]
            #
            # continue

            walls = list(walls)

            intersections = [Robot.line_line_intersection(
                (wall.pos1*GRID_SIZE, wall.pos2*GRID_SIZE), (self.position, sample)) for wall in walls]

            distances = [math.dist(self.position, point) if point is not None else self.max_sensor_range
                         for point in intersections]

            dist_i = np.argmin(distances)

            # print(
            #    f'Wall: {walls[dist_i].pos1*GRID_SIZE}, {walls[dist_i].pos2*GRID_SIZE}, Robot: {self.position}, {sample}')
            measure = distances[dist_i]

            # print('INTERSECTION ', intersections[dist_i])
            # print('MEASURE ', measure)

            if measure > self.max_sensor_range:
                measure = self.max_sensor_range
            noise = random.gauss(0.0, SIGMA_MEASURE)
            measurements.append(measure + noise)

        return measurements

    def transform_measures_into_points(self, distances):
        x, y = self.position
        start_angle = self.angle - self.aperture / 2.0
        stop_angle = self.angle + self.aperture / 2.0
        angles = np.linspace(start_angle, stop_angle, num=self.num_sensors)

        return tuple(
            (x + math.cos(angle) * distance, y + math.sin(angle) * distance)
            for angle, distance in zip(angles, distances)
        )

    def draw(self, screen, walls):
        x, y = self.position
        pygame.draw.circle(screen, (0, 0, 0), (x, y), ROBOT_RADIUS)

        xr, yr = x + self.radius * \
            math.cos(self.angle), y + self.radius * math.sin(self.angle)
        pygame.draw.line(screen, (255, 0, 0), (x, y), (xr, yr), 3)

        for sensor_point in self.compute_sensor_points():
            pygame.draw.line(screen, (0, 100, 100), (x, y), sensor_point, 3)

        distances = self.measure(walls)
        points = self.transform_measures_into_points(distances)
        # points = tuple(self.compute_sensor_points())
        for point in points:
            pygame.draw.line(screen, (255, 0, 0), (x, y), point, 3)
