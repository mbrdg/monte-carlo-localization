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

        surrounding_cells = my_wallmap.get_surrounding_cells(robot.get_position(), mode='aperture',
                                                             range_=SENSOR_RANGE, angle=robot.get_angle(), aperture=robot.aperture)
        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        robot.update(surrounding_edges)

        # Draw
        screen.fill(WHITE)

        my_wallmap.draw(screen, draw_tile_debug=True)

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
