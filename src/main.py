# main.py
import argparse
import configparser
import math
import random
import sys
from itertools import chain

import pygame

import map_gen
import wallmap
from consts import *
from robot import Particle
from settings import *

FPS = 24
SAMPLES = 300
SPEED = 3


def read_config(file_path, sim_settings_name):
    config = configparser.ConfigParser()
    config.read(file_path)

    width = config.getint('EnvironmentSettings', 'window_width')
    height = config.getint('EnvironmentSettings', 'window_height')
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


def get_surrounding_cells_edges(particle, my_wallmap):
    surrounding_cells = my_wallmap.get_surrounding_cells(
        particle.get_position(),
        mode='aperture',
        range_=particle.range_,
        angle=particle.get_angle(),
        aperture=particle.aperture*1.2
    )
    surrounding_edges = [cell for _, cell in surrounding_cells]
    surrounding_edges = set(chain(*surrounding_edges))

    return surrounding_cells, surrounding_edges


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

    particles = [
        Particle(
            (random.uniform(0, width), random.uniform(0, height)),
            random.uniform(0, 2 * math.pi),
            range_=sensor_range, aperture=sensor_aperture, num_sensors=num_sensors
        ) for _ in range(SAMPLES)
    ]
    robot = Particle(
        (width / 2.0, height / 2.0), 0,
        range_=sensor_range, aperture=sensor_aperture, num_sensors=num_sensors
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()

        robot_next_position = robot.get_position()
        next_positions = [p.get_position() for p in particles]

        if pressed_keys[pygame.K_w]:
            robot_next_position, mnoise = robot.move(
                SPEED, position=robot_next_position)
            next_positions = [p.move(SPEED, noise=mnoise)[0]
                              for p in particles]

        if pressed_keys[pygame.K_a]:
            _, lnoise = robot.rotate(math.radians(-1.5))
            for p in particles:
                p.rotate(math.radians(-1.5), noise=lnoise)
        if pressed_keys[pygame.K_d]:
            _, rnoise = robot.rotate(math.radians(1.5))
            for p in particles:
                p.rotate(math.radians(-1.5), noise=rnoise)

        if not my_wallmap.robot_has_collision(robot_next_position, robot.get_radius()):
            robot.apply_move(robot_next_position)
            for p, position in zip(particles, next_positions):
                p.apply_move(position)

        # Update

        surrounding_cells, surrounding_edges = get_surrounding_cells_edges(robot, my_wallmap)
        robot.update(surrounding_edges, grid_size=grid_size)

        for p in particles:
            _, p_surrounding_edges = get_surrounding_cells_edges(p, my_wallmap)
            p.update(p_surrounding_edges, grid_size=grid_size)

        # Draw
        screen.fill(WHITE)

        my_wallmap.draw(screen, draw_tile_debug=True)

        ground_thruth = robot.measure(surrounding_edges)
        scores = [i, p.likelihood(ground_thruth) for i, p in enumrate(particles)].sort()
        top_scores = scores[:SAMPLES // 10]

        # particle_measurements = particle.measure(surrounding_edges)
        # print(Particle.likelihood(ground_thruth, particle_measurements))

        Particle.draw_robot(screen, robot, color=(148, 0, 211))
        for p in particles:
            Particle.draw_particle(screen, p)

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
