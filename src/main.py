# main.py
import argparse
import configparser
import copy
import math
import sys
from itertools import chain

import pygame

import map_gen
import wallmap
from consts import *
from robot import Robot
from settings import *

FPS = 60


def read_config(file_path, sim_settings_name):
    config = configparser.ConfigParser()
    config.read(file_path)

    width, height = config.getint('EnvironmentSettings', 'window_width'), config.getint(
        'EnvironmentSettings', 'window_height')
    grid_size = config.getint('EnvironmentSettings', 'grid_size')

    sensor_range = config.getint(sim_settings_name, 'sensor_range')
    sensor_aperture = math.radians(config.getint(
        sim_settings_name, 'sensor_aperture'))
    num_sensors = config.getint(sim_settings_name, 'num_sensors')

    return {
        'width': width,
        'height': height,
        'grid_size': grid_size,
        'sensor_range': sensor_range,
        'sensor_aperture': sensor_aperture,
        'num_sensors': num_sensors
    }


def main() -> None:

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Robot Simulation Program')

    # Add a command-line argument for the config file
    parser.add_argument('--sim_settings', type=str, default='SimSettingsDefault',
                        help='Name for the simulation settings')

    # Parse the command-line arguments
    args = parser.parse_args()

    config_data = read_config('config.ini', args.sim_settings)

    width, height = config_data['width'], config_data['height']
    grid_size = config_data['grid_size']
    sensor_range = config_data['sensor_range']
    sensor_aperture = config_data['sensor_aperture']
    num_sensors = config_data['num_sensors']

    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Wall Map")

    my_wallmap = wallmap.Wallmap(None, grid_size)

    map_gen.define_environment_1(my_wallmap, grid_size)

    clock = pygame.time.Clock()

    robot = Robot([width//2, height//2], 0, range_=sensor_range,
                  aperture=sensor_aperture, num_sensors=num_sensors)

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
                                                             range_=robot.range_, angle=robot.get_angle(), aperture=robot.aperture*1.2)
        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        robot.update(surrounding_edges, grid_size=grid_size)

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
