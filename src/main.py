# main.py
import copy
import math
import random
import sys
from itertools import chain

import numpy as np
import pygame

import wallmap
from consts import *
from robot import Robot
from settings import *

FPS = 60


def define_environment_1(my_wallmap, grid_size):

    # Add edges
    # random edges
    def top_wall_border():
        edge_0 = wallmap.Edge((0, 0), (0, 1))
        edge_1 = wallmap.Edge((0, 1), (WIDTH//grid_size, 1))
        edge_2 = wallmap.Edge((WIDTH//grid_size, 1), (WIDTH//grid_size, 0))
        edge_3 = wallmap.Edge((WIDTH//grid_size, 0), (0, 0))
        manual_edges = [edge_0, edge_1, edge_2, edge_3]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def bottom_wall_border():
        edge_0 = wallmap.Edge((0, HEIGHT//grid_size),
                              (0, HEIGHT//grid_size - 1))
        edge_1 = wallmap.Edge((0, HEIGHT//grid_size - 1),
                              (WIDTH//grid_size, HEIGHT//grid_size - 1))
        edge_2 = wallmap.Edge(
            (WIDTH//grid_size, HEIGHT//grid_size - 1), (WIDTH//grid_size, HEIGHT//grid_size))
        edge_3 = wallmap.Edge(
            (WIDTH//grid_size, HEIGHT//grid_size), (0, HEIGHT//grid_size))
        manual_edges = [edge_0, edge_1, edge_2, edge_3]
        # manual_edges = [edge_2]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def left_wall_border():
        edge_0 = wallmap.Edge((0, 0), (1, 0))
        edge_1 = wallmap.Edge((1, 0), (1, HEIGHT//grid_size))
        edge_2 = wallmap.Edge((1, HEIGHT//grid_size),
                              (0, HEIGHT//grid_size))
        edge_3 = wallmap.Edge((0, HEIGHT//grid_size), (0, 0))
        manual_edges = [edge_0, edge_1, edge_2, edge_3]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def right_wall_border():
        edge_0 = wallmap.Edge((WIDTH//grid_size, 0),
                              (WIDTH//grid_size - 1, 0))
        edge_1 = wallmap.Edge((WIDTH//grid_size - 1, 0),
                              (WIDTH//grid_size - 1, HEIGHT//grid_size))
        edge_2 = wallmap.Edge(
            (WIDTH//grid_size - 1, HEIGHT//grid_size), (WIDTH//grid_size, HEIGHT//grid_size))
        edge_3 = wallmap.Edge(
            (WIDTH//grid_size, HEIGHT//grid_size), (WIDTH//grid_size, 0))
        manual_edges = [edge_0, edge_1, edge_2, edge_3]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_1():
        manual_edges = [
            wallmap.Edge((1, 16), (10, 16)),
            wallmap.Edge((10, 16), (15, 19)),
            wallmap.Edge((15, 19), (15, 24)),
            wallmap.Edge((15, 24), (14, 25)),
            wallmap.Edge((14, 25), (13, 24)),
            wallmap.Edge((13, 24), (13, 20)),
            wallmap.Edge((13, 20), (9, 18)),
            wallmap.Edge((9, 18), (1, 18)),
            wallmap.Edge((1, 18), (1, 16)),
        ]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_2():
        manual_edges = [
            wallmap.Edge((13, 6), (20, 6)),
            wallmap.Edge((20, 6), (20, 9)),
            wallmap.Edge((20, 9), (13, 6)),
        ]
        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_3():
        manual_edges = [
            wallmap.Edge((13, 0), (13, 6)),
            wallmap.Edge((13, 6), (17, 6)),
            wallmap.Edge((17, 6), (14, 5)),
            wallmap.Edge((14, 5), (14, 0)),
            wallmap.Edge((14, 0), (13, 0)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_4():
        manual_edges = [
            wallmap.Edge((6, 0), (6, 11)),
            wallmap.Edge((6, 11), (8, 11)),
            wallmap.Edge((8, 11), (8, 0)),
            wallmap.Edge((8, 0), (6, 0)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_5():
        manual_edges = [
            wallmap.Edge((4, 5), (4, 6)),
            wallmap.Edge((4, 6), (6, 6)),
            wallmap.Edge((6, 6), (6, 5)),
            wallmap.Edge((6, 5), (4, 5)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_6():
        manual_edges = [
            wallmap.Edge((14, 10), (16, 10)),
            wallmap.Edge((16, 10), (17, 11)),
            wallmap.Edge((17, 11), (17, 13)),
            wallmap.Edge((17, 13), (16, 14)),
            wallmap.Edge((16, 14), (14, 14)),
            wallmap.Edge((14, 14), (13, 13)),
            wallmap.Edge((13, 13), (13, 11)),
            wallmap.Edge((13, 11), (14, 10)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_7():
        manual_edges = [
            wallmap.Edge((19, 19), (23, 19)),
            wallmap.Edge((23, 19), (23, 27)),
            wallmap.Edge((23, 27), (21, 27)),
            wallmap.Edge((21, 27), (21, 21)),
            wallmap.Edge((21, 21), (19, 21)),
            wallmap.Edge((19, 21), (19, 19)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def wall_8():
        manual_edges = [
            wallmap.Edge((4, 25), (8, 21)),
            wallmap.Edge((8, 21), (10, 23)),
            wallmap.Edge((10, 23), (6, 27)),
            wallmap.Edge((6, 27), (4, 25)),

        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    def maze_1():
        manual_edges = [
            wallmap.Edge((25, 15), (37, 15)),
            wallmap.Edge((25, 15), (25, 17)),
            wallmap.Edge((25, 17), (27, 17)),
            wallmap.Edge((31, 15), (31, 21)),
            wallmap.Edge((31, 21), (29, 21)),
            wallmap.Edge((29, 21), (29, 23)),
            wallmap.Edge((25, 19), (25, 27)),
            wallmap.Edge((25, 27), (33, 27)),
            wallmap.Edge((35, 27), (37, 27)),
            wallmap.Edge((37, 27), (37, 15)),
            wallmap.Edge((37, 25), (33, 25)),
            wallmap.Edge((31, 27), (31, 23)),
            wallmap.Edge((31, 23), (35, 23)),
            wallmap.Edge((35, 23), (35, 17)),
            wallmap.Edge((35, 17), (33, 17)),
            wallmap.Edge((31, 19), (33, 19)),
            wallmap.Edge((35, 21), (33, 21)),
            wallmap.Edge((31, 25), (29, 25)),
            wallmap.Edge((25, 25), (27, 25)),
            wallmap.Edge((27, 25), (27, 21)),
            wallmap.Edge((25, 19), (29, 19)),
            wallmap.Edge((29, 19), (29, 17)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

    def box_1():
        manual_edges = [
            wallmap.Edge((28, 4), (34, 4)),
            wallmap.Edge((34, 4), (34, 8)),
            wallmap.Edge((34, 8), (28, 8)),
            wallmap.Edge((28, 8), (28, 4)),
        ]

        for edge in manual_edges:
            my_wallmap.add_edge(edge)

        my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_BROWN))

    top_wall_border()
    bottom_wall_border()
    left_wall_border()
    right_wall_border()
    wall_1()
    wall_2()
    wall_3()
    wall_4()
    wall_5()
    wall_6()
    wall_7()
    wall_8()
    box_1()
    maze_1()

    # for _ in range(2):
    #    pos1 = (random.randint(0, WIDTH // grid_size),
    #            random.randint(0, HEIGHT // grid_size))
    #    pos2 = (random.randint(0, WIDTH // grid_size),
    #            random.randint(0, HEIGHT // grid_size))
    #    edge = wallmap.Edge(pos1, pos2)
    #    my_wallmap.add_edge(edge)
    #    print(f'Added edge from {pos1} to {pos2}')

    return my_wallmap


def find_min_max_cosine(start_angle, end_angle):
    # Ensure the angles are within the valid range (0 to 360 degrees)
    start_angle = start_angle % math.pi*2
    end_angle = end_angle % math.pi*2

    # Calculate cosine values
    min_cosine = min(math.cos(start_angle), math.cos(end_angle))
    max_cosine = max(math.cos(start_angle), math.cos(end_angle))

    return min_cosine, max_cosine


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

    define_environment_1(my_wallmap, grid_size)

    clock = pygame.time.Clock()

    robot = Robot([WIDTH//2, HEIGHT//2], 0)

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

        # surrounding_cells = get_simple_surrounding_cells(
        #    robot.get_position(), my_wallmap, grid_size, SENSOR_RANGE)

        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        # Draw
        screen.fill(WHITE)

        my_wallmap.draw_tile_debug(screen)
        my_wallmap.draw(screen)
        my_wallmap.draw_obstacles(screen)

        robot.draw(screen, surrounding_edges)

        for key, cell in surrounding_cells:
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
