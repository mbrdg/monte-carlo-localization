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
                 max_sensor_range=20.0, aperture=math.pi, num_sensors=10):
        self.position = position
        self.angle = angle
        self.radius = ROBOT_RADIUS

        self.max_sensor_range = max_sensor_range
        self.aperture = aperture
        self.num_sensors = num_sensors
        self.compute_sensor_points()

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

        self.compute_sensor_points()
        return target_angle

    def apply_rotation(self, angle):
        self.angle = angle

    def move(self, speed=10, *, position=None):
        if position is None:
            position = self.position

        speed = speed + random.gauss(0, SIGMA_MOVE)
        position[0] += speed * math.cos(self.angle)
        position[1] += speed * math.sin(self.angle)
        self.compute_sensor_points()

        return position

    def apply_move(self, position):
        self.position = position

    def compute_sensor_points(self):
        x, y = self.position
        min_angle, max_angle = self.angle - self.aperture / 2.0, self.angle + self.aperture / 2.0

        self.sensors = (
            (x + math.cos(angle) * self.max_sensor_range, y + math.sin(angle) * self.max_sensor_range)
            for angle in np.linspace(min_angle, max_angle, num=self.num_sensors)
        )

    def measure(self, walls):
        # TODO: This is not tested
        # Please, Colino be kind with me if you found any bug here!

        def line_line_intersection(p1, p2):
            (x1, y1), (x2, y2) = p1
            (x3, y3), (x4, y4) = p2

            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) 
            if denominator == 0:
                return None
            
            common_a, common_b = (x1 * y2 - y1 * x2), (x3 * y4 - y3 * x4)
            px = (common_a * (x3 - x4) - (x2 - x1) * common_b) / denominator
            py = (common_a * (y3 - y4) - (y2 - y1) * common_b) / denominator

            return (px, py)

        measurements = []
        for sample in self.sensors:
            intersections = [line_line_intersection((self.position, sample), wall) for wall in walls]
            sample_measurements = [self.max_sensor_range if point is None else math.dist(self.position, point) for point in intersections]
            measurements.append(min(sample_measurements) + random.gauss(0.0, SIGMA_MEASURE))

        return measurements

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.position, ROBOT_RADIUS)
        pygame.draw.line(screen, (255, 0, 0), self.position, (
            self.position[0] + ROBOT_RADIUS * math.cos(self.angle), self.position[1] + ROBOT_RADIUS * math.sin(self.angle)), 3)
