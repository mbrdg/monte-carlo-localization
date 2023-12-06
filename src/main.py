# main.py
import copy
import math
import random
import sys
from itertools import chain

import numpy as np
import pygame

import map_gen
import wallmap
from consts import *
from robot import Robot
from settings import *

FPS = 60


def get_surrounding_cells(pos, my_wallmap, grid_size, sensor_range, sensor_angle, sensor_aperature=math.pi):
    surrounding_cells = []

    grid_pos = [math.floor(pos[0] / grid_size), math.floor(pos[1] / grid_size)]
    grid_range = math.ceil(sensor_range / grid_size)

    def sign(a): return 1 if a > 0 else -1 if a < 0 else 0

    most_dist = [
        round(math.cos(sensor_angle) * grid_range),
        round(math.sin(sensor_angle) * grid_range)
    ]

    most_dist_aperture_min = [
        round(math.cos(sensor_angle - sensor_aperature/2)
              * grid_range),
        round(math.sin(sensor_angle - sensor_aperature/2)
              * grid_range)
    ]

    most_dist_aperture_max = [
        round(math.cos(sensor_angle + sensor_aperature/2)
              * grid_range),
        round(math.sin(sensor_angle + sensor_aperature/2)
              * grid_range)
    ]

    x_aperture_min = (0-sign(most_dist[0]),
                      most_dist[0] + most_dist_aperture_min[0])
    y_aperture_min = (0-sign(most_dist[1]),
                      most_dist[1] + most_dist_aperture_min[1])

    x_aperture_max = (0-sign(most_dist[0]),
                      most_dist[0] + most_dist_aperture_max[0])
    y_aperture_max = (0-sign(most_dist[1]),
                      most_dist[1] + most_dist_aperture_max[1])

    x_range = (0-sign(most_dist[0]), most_dist[0] +
               sign(most_dist[0]))
    y_range = (0-sign(most_dist[1]), most_dist[1] +
               sign(most_dist[1]))

    min_x = min((min(x_aperture_min), min(x_aperture_max), min(x_range)))
    max_x = max((max(x_aperture_min), max(x_aperture_max), max(x_range)))

    min_y = min((min(y_aperture_min), min(y_aperture_max), min(y_range)))
    max_y = max((max(y_aperture_min), max(y_aperture_max), max(y_range)))

    for x_offset in range(min_x, max_x+1):
        for y_offset in range(min_y, max_y+1):
            # check if x, y is inside borders

            x = grid_pos[0] + x_offset
            y = grid_pos[1] + y_offset

            if x < 0 or x >= WIDTH // grid_size or y < 0 or y >= HEIGHT // grid_size:
                continue

            if f'{x};{y}' in my_wallmap.tilemap:
                surrounding_cells.append((
                    f'{x};{y}', my_wallmap.tilemap[f'{x};{y}']))

    return surrounding_cells


def get_simple_surrounding_cells(pos, my_wallmap, grid_size, sensor_range):

    surrounding_cells = []

    grid_pos = [math.floor(pos[0] / grid_size), math.floor(pos[1] / grid_size)]
    grid_range = math.ceil(sensor_range / grid_size)

    for x_offset in range(-grid_range, grid_range+1):
        for y_offset in range(-grid_range, grid_range+1):
            # check if x, y is inside borders

            x = grid_pos[0] + x_offset
            y = grid_pos[1] + y_offset

            if x < 0 or x >= WIDTH // grid_size or y < 0 or y >= HEIGHT // grid_size:
                continue

            if f'{x};{y}' in my_wallmap.tilemap:
                surrounding_cells.append((
                    f'{x};{y}', my_wallmap.tilemap[f'{x};{y}']))

    return surrounding_cells


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wall Map")

    grid_size = GRID_SIZE

    my_wallmap = wallmap.Wallmap(None, grid_size)

    # Add edges
    # random edges

    map_gen.define_environment_1(my_wallmap, grid_size)

    clock = pygame.time.Clock()

    robot = Robot([WIDTH//2, HEIGHT//2], 0, aperture=math.pi/2, num_sensors=20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()
        new_position = copy.deepcopy(robot.get_position())

        if pressed_keys[pygame.K_w]:
            new_position = robot.move(1, position=new_position)
        if pressed_keys[pygame.K_a]:
            robot.rotate(math.radians(-1.5))
        if pressed_keys[pygame.K_d]:
            robot.rotate(math.radians(1.5))

        if not my_wallmap.robot_has_collision(new_position, robot.radius):
            robot.apply_move(new_position)

        # Update

        surrounding_cells = get_surrounding_cells(
            robot.get_position(), my_wallmap, grid_size, SENSOR_RANGE, robot.get_angle())

        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        robot.update(surrounding_edges)

        # Draw
        screen.fill(WHITE)

        my_wallmap.draw_tile_debug(screen)
        my_wallmap.draw(screen)
        my_wallmap.draw_obstacles(screen)

        robot.draw(screen, draw_sensor_ranges=False, draw_measurements=True)

        for key, _ in surrounding_cells:
            cell_x, cell_y = key.split(';')
            cell_x = int(cell_x) * grid_size
            cell_y = int(cell_y) * grid_size
            s = pygame.Surface((20, 20), pygame.SRCALPHA)
            # notice the alpha value in the color
            s.fill((0, 255, 0, 50))

            screen.blit(s, (cell_x, cell_y))

        # Refresh the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
