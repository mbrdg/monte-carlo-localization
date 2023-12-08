# main.py
import argparse
import configparser
import math
import random
import sys
from itertools import chain

import numpy as np
import pygame
from shapely import STRtree
from shapely.geometry import Point

import map_gen
import wallmap
from consts import *
from robot import Particle
from settings import *

FPS = 24
UPDATE_INTERVAL_MILLIS = 400
SAMPLES = 200
SPEED = 3
ROT_SPEED = 5
GEN_VARIANCE = 10


class Game:

    def __init__(self, config_data):
        self.width, self.height = config_data['width'], config_data['height']
        self.grid_size = config_data['grid_size']
        self.sensor_range = config_data['sensor_range']
        self.sensor_aperture = config_data['sensor_aperture']
        self.num_sensors = config_data['num_sensors']

        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Wall Map")

        self.my_wallmap = wallmap.Wallmap(None, self.grid_size)

        map_gen.define_environment_1(self.my_wallmap, self.grid_size)

        self.clock = pygame.time.Clock()

        # Read-only, should only be constructed after building the wallmap
        tree = STRtree([obs.get_polygon() for obs in self.my_wallmap.get_obstacles()])

        self.xx, self.yy = np.meshgrid(np.arange(self.width), np.arange(self.height))
        self.candidates = np.array([self.xx.flatten(), self.yy.flatten()]).T

        self.my_wallmap_mask = np.array([
            float(tree.query(Point(c[0], c[1]).buffer(Particle.RADIUS)).size == 0)
            for c in self.candidates
        ]).reshape((self.height, self.width))

        self.particles = self.reset_particles()
        self.robot_start_positions = [
            (self.width / 2.0, self.height / 2.0),
            (200, 300)
        ]

        self.robot = Particle(
            self.robot_start_positions[0], 0,
            range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors
        )

    def get_surrounding_cells_edges(self, particle):
        surrounding_cells = self.my_wallmap.get_surrounding_cells(
            particle.get_position(),
            mode='aperture',
            range_=particle.range_,
            angle=particle.get_angle(),
            aperture=particle.aperture*1.2
        )
        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        return surrounding_cells, surrounding_edges

    def reset_particles(self):
        density_map = self.my_wallmap_mask / np.sum(self.my_wallmap_mask)
        positions = self.generate_particle_positions(
            self.candidates, density_map.flatten(), SAMPLES
        )

        return [
            Particle(position, random.uniform(0, 2.0 * math.pi),
                     range_=self.sensor_range,
                     aperture=self.sensor_aperture,
                     num_sensors=self.num_sensors) for position in positions
        ]

    def gaussian_distribution(self, x, y, mean, variance):
        return np.exp(-((x - mean[0])**2 + (y - mean[1])**2) / (2 * variance)) / (2 * np.pi * variance)
    
    def generate_particle_positions(self, positions, weights, num_particles):
        particle_indices = np.random.choice(
            len(positions), size=num_particles, p=weights/np.sum(weights))
        particles = positions[particle_indices]
        return particles
    
    def fit_normal(self, values, weights):
        # estimate mean
        weights_sum = weights.sum()
        mean = (values * weights).sum() / weights_sum
    
        # estimate variance
        errors = (values - mean) ** 2
        variance = (errors * weights).sum() / weights_sum
            
        return (mean, variance)
    
    def generate_particles(self, particles, ground_thruth):
        for p in particles:
            _, p_surrounding_edges = self.get_surrounding_cells_edges(p)
            p.update(p_surrounding_edges, grid_size=self.grid_size)

        scores = [(i, p.likelihood(ground_thruth)) for i, p in enumerate(particles)]
        scores_avg = np.mean([score for _, score in scores])
        indexed_scores = [(i, score / scores_avg) for i, score in scores]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        indexed_top_scores = scores[:int(len(particles) * 0.1)]

        density_map = np.zeros((self.height, self.width))

        for i, weight in indexed_top_scores:
            density_map += weight * self.gaussian_distribution(
                self.xx, self.yy, particles[i].get_position(), GEN_VARIANCE
            )

        # multiplying by the mask makes impossible to gen particles in the walls
        # density_map /= np.sum(density_map)
        density_map *= self.my_wallmap_mask

        # if density map has Nan values, skip
        if np.isnan(density_map).any():
            return particles

        num_generated_particles = (len(particles) - len(indexed_top_scores))
        if (len(particles) > 20):
            deductive = max(num_generated_particles * 0.95, 1.0)
            num_generated_particles = round(deductive)

        # print("Total particles: ", len(particles))
        generated_particle_positions = self.generate_particle_positions(
            self.candidates, density_map.flatten(), num_generated_particles
        )

        top_rotations = np.array([particles[i].get_angle() for i, _ in indexed_top_scores])
        top_scores = np.array([score for _, score in indexed_top_scores])
        rot_mean, rot_variance = self.fit_normal(top_rotations, top_scores)
        rot_mean = rot_mean % (2.0 * math.pi)

        new_particles = [particles[i] for i, _ in indexed_top_scores]
        new_particles.extend([
            Particle(position, (np.random.normal(loc=rot_mean, scale=rot_variance)) % (2.0 * math.pi),
                     range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors) 
            for position in generated_particle_positions
        ])

        return new_particles
    
    def run(self):
        running = True
        update_particles = False
        pygame.time.set_timer(pygame.USEREVENT, UPDATE_INTERVAL_MILLIS)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    update_particles = True
    
            pressed_keys = pygame.key.get_pressed()
    
            robot_next_position = self.robot.get_position()
            next_positions = [p.get_position() for p in self.particles]
    
            speed = SPEED * (pressed_keys[pygame.K_LSHIFT] + 1)
            rot_speed = ROT_SPEED * ((2 * pressed_keys[pygame.K_LSHIFT]) + 1)
    
            if pressed_keys[pygame.K_w]:
                robot_next_position, mnoise = self.robot.move(
                    speed, position=robot_next_position
                )
                next_positions = [
                    p.move(speed, noise=mnoise)[0] for p in self.particles
                ]
    
            if pressed_keys[pygame.K_a]:
                _, lnoise = self.robot.rotate(math.radians(-rot_speed))
                for p in self.particles:
                    p.rotate(math.radians(-rot_speed), noise=lnoise)
            if pressed_keys[pygame.K_d]:
                _, rnoise = self.robot.rotate(math.radians(rot_speed))
                for p in self.particles:
                    p.rotate(math.radians(rot_speed), noise=rnoise)

            if pressed_keys[pygame.K_r]:
                self.particles.clear()
                self.particles = self.reset_particles()
    
            if not self.my_wallmap.particle_has_collision(robot_next_position, self.robot.get_radius()):
                self.robot.apply_move(robot_next_position)

            for particle, position in zip(self.particles, next_positions):
                if not self.my_wallmap.particle_has_collision(position, particle.get_radius()):
                    particle.apply_move(position)
    
            # Clear
            self.screen.fill(WHITE)
    
            # Update
            surrounding_cells, surrounding_edges = self.get_surrounding_cells_edges(self.robot)
            self.robot.update(surrounding_edges, grid_size=self.grid_size)

            if pressed_keys[pygame.K_u] or update_particles:
                robot_measure = self.robot.measure(surrounding_edges)
                self.particles = self.generate_particles(self.particles, robot_measure)
                update_particles = False

            self.my_wallmap.draw(self.screen, draw_tile_debug=True)

            for p in self.particles:
                Particle.draw_particle(self.screen, p)
            Particle.draw_robot(self.screen, self.robot, color=(148, 0, 211))

            for key, _ in surrounding_cells:
                cell_x, cell_y = key.split(';')
                cell_x = int(cell_x) * self.grid_size
                cell_y = int(cell_y) * self.grid_size
                s = pygame.Surface((20, 20), pygame.SRCALPHA)
                # notice the alpha value in the color
                s.fill((0, 255, 0, 50))

                self.screen.blit(s, (cell_x, cell_y))

            # Refresh the display
            pygame.display.flip()

            # Cap the frame rate
            self.clock.tick(FPS)
            print(f'FPS {self.clock.get_fps()}')

        pygame.quit()
        sys.exit()




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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the robot simulation')
    parser.add_argument('--config', type=str, default='config.ini',
                        help='Path to the config file')
    parser.add_argument('--sim_settings', type=str, default='SimulationSettings',
                        help='Name of the simulation settings in the config file')
    args = parser.parse_args()

    config_data = read_config(args.config, args.sim_settings)

    game = Game(config_data)
    game.run()
