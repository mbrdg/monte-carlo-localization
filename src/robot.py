import math
import random

import numpy as np
import pygame

ROBOT_RADIUS = 10
SIGMA_MOVE = .5
SIGMA_ROTATE = math.radians(.3)
SIGMA_MEASURE = 1.0


class Robot:
    def __init__(self, position, angle, *,
                 max_sensor_range=50.0, aperture=math.pi/4.0, num_sensors=10):
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
            (x + math.cos(angle) * self.max_sensor_range, y + math.sin(angle) * self.max_sensor_range)
            for angle in np.linspace(start_angle, stop_angle, num=self.num_sensors)
        )

    @staticmethod
    def line_line_intersection(a, b):
        (x1, y1), (x2, y2) = a
        (x3, y3), (x4, y4) = b

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) 
        if denominator == 0.0:
            return None
        
        det_a, det_b = (x1 * y2 - y1 * x2), (x3 * y4 - y3 * x4)
        px = (det_a * (x3 - x4) - (x2 - x1) * det_b) / denominator
        py = (det_a * (y3 - y4) - (y2 - y1) * det_b) / denominator

        return (px, py)

    def measure(self, walls):
        measurements = []
        for sample in self.compute_sensor_points():
            intersections = (Robot.line_line_intersection((wall.pos1, wall.pos2), (self.position, sample)) for wall in walls)
            distances = (math.dist(self.position, point) for point in intersections if point is not None)

            measure = min(distances, default=self.max_sensor_range)
            noise = random.gauss(0.0, SIGMA_MEASURE)
            measurements.append(measure + noise)

        return measurements

    def transform_measures_into_points(self, distances):
        x, y = self.position
        start_angle = self.angle + self.aperture / 2.0
        stop_angle = self.angle - self.aperture / 2.0
        angles = np.linspace(start_angle, stop_angle, num=self.num_sensors)

        return tuple(
            (x + math.cos(angle) * distance, y + math.sin(angle) * distance) 
            for angle, distance in zip(angles, distances)
        )

    def draw(self, screen, walls):
        x, y = self.position
        pygame.draw.circle(screen, (0, 0, 0), (x, y), ROBOT_RADIUS)

        xr, yr = x + self.radius * math.cos(self.angle), y + self.radius * math.sin(self.angle) 
        pygame.draw.line(screen, (255, 0, 0), (x, y), (xr, yr), 3)

        distances = self.measure(walls)
        points = self.transform_measures_into_points(distances)
        # points = tuple(self.compute_sensor_points())
        pygame.draw.lines(screen, (255, 0, 0, 128), False, points, 3)
