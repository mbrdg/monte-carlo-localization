# main.py
import argparse
import configparser
import math
import random
import sys
import threading
from itertools import chain
from threading import Thread
from time import sleep

import numpy as np
import pygame

import game_environment as game_environment
import wallmap
from consts import *
from robot import Particle
from settings import *

FPS = 24
SAMPLES = 400
SPEED = 3
ROT_SPEED = 5
GEN_VARIANCE = 1000


class Game:

    def __init__(self, config_data):
        self.width, self.height = config_data['width'], config_data['height']
        self.grid_size = config_data['grid_size']
        self.sensor_range = config_data['sensor_range']
        self.sensor_aperture = config_data['sensor_aperture']
        self.num_sensors = config_data['num_sensors']

        pygame.init()

        

        self.enviroment = game_environment.Environment('enviroment_2')
        self.wallmap = self.enviroment.wallmap
        self.width, self.height = self.enviroment.width, self.enviroment.height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Montecarlo Localization")

        self.clock = pygame.time.Clock()

        Particle.ROBOT_SIZE = config_data['robot_size']
        Particle.PARTICLE_SIZE = config_data['particle_size']

        self.particles = [
            Particle(
                (random.uniform(0, self.width), random.uniform(0, self.height)),
                random.uniform(0, 2 * math.pi),
                range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors,
                type='particle'
            ) for _ in range(SAMPLES)
        ]

        self.robot_start_positions = [
            (self.width / 2.0, self.height / 2.0),
            (200, 300)
        ]

        self.robot = Particle(
            self.robot_start_positions[0], 0,
            range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors,
            type='robot'
        )

        self.gen_variance_max = 5000
        self.gen_variance_min = 1

        print(f"Variance limits {self.gen_variance_min},{self.gen_variance_max} ; Samples {SAMPLES}")

    def get_surrounding_cells_edges(self, particle):
        surrounding_cells = self.wallmap.get_surrounding_cells(
            particle.get_position(),
            mode='aperture',
            range_=particle.range_,
            angle=particle.get_angle(),
            aperture=particle.aperture*1.2
        )
        surrounding_edges = [cell for _, cell in surrounding_cells]
        surrounding_edges = set(chain(*surrounding_edges))

        return surrounding_cells, surrounding_edges

    def gaussian_distribution(self, x, y, mean, variance):
        return np.exp(-((x - mean[0])**2 + (y - mean[1])**2) / (2 * variance)) / (2 * np.pi * variance)
    
    def generate_particle_positions(self, positions, weights, num_particles):
        particle_indices = np.random.choice(
            len(positions), size=num_particles, p=weights/np.sum(weights))
        particles = positions[particle_indices]
        return particles
    
    def fit_normal(self, values, weights):
            
            # prepare
            values = np.array(values)
            weights = np.array(weights)
                
            # estimate mean
            weights_sum =  weights.sum()
            mean = (values*weights).sum() / weights_sum
        
            # estimate variance
            errors = (values-mean)**2
            variance = (errors*weights).sum() / weights_sum
                
            return (mean, variance)
    
    def generate_particles(self, particles, ground_thruth):

        MIN_PARTICLES = 15
            
        width, height = self.width, self.height

        for p in particles:
            _, p_surrounding_edges = self.get_surrounding_cells_edges(p)
            p.update(p_surrounding_edges, grid_size=self.grid_size)

        scores = [(i, p.likelihood(ground_thruth))
                for i, p in enumerate(particles)]
        #scores_avg = np.mean([score for _, score in scores])
        #scores = [(i, score/scores_avg) for i, score in scores]
        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:max((len(particles) // 10), round(.5 *MIN_PARTICLES ))]

        x, y = np.meshgrid(np.arange(width), np.arange(height))
        density_map = np.zeros((height, width))

        top_scores_avg = np.mean([score for _, score in top_scores])
    
        gen_variance = self.gen_variance_max * (1-(top_scores_avg)) 

        for i, weight in top_scores:
            density_map += weight * \
                self.gaussian_distribution(
                    x, y, particles[i].get_position(), gen_variance)

        density_map /= np.sum(density_map)

        # if density map has Nan values, skip

        

        if not np.isnan(density_map).any():

            num_generated_particles = (len(particles) - len(top_scores))

            if (len(particles) >    MIN_PARTICLES):
                deductive = (len(particles) - len(top_scores)) * 0.9
                if deductive <= 0:
                    deductive = 1
                num_generated_particles = round(deductive)

            
            generated_particle_positions = self.generate_particle_positions(np.array(
                [x.flatten(), y.flatten()]).T, density_map.flatten(), num_generated_particles)

            top_rotations = [particles[i].get_angle() for i, _ in top_scores]

            (rot_mean, rot_variance) = self.fit_normal(top_rotations, [score for _, score in top_scores])
            rot_mean = rot_mean % (math.pi*2)
            rot_variance = rot_variance * (1 / top_scores_avg)

            new_particles = [particles[i] for i, _ in top_scores]
            new_particles.extend([Particle(position, (np.random.normal(loc=rot_mean, scale=rot_variance))%(math.pi*2),
                                        range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors) for position in generated_particle_positions])
        else:
            new_particles = particles

        print(f"Total particles {len(particles)} ; Scores svg {top_scores_avg} ; Variance {gen_variance}")

        return new_particles
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
            pressed_keys = pygame.key.get_pressed()
    
            robot_next_position = self.robot.get_position()
            next_positions = [p.get_position() for p in self.particles]
    
            speed = SPEED
            rot_speed = ROT_SPEED
    
            if pressed_keys[pygame.K_w]:
    
                if pressed_keys[pygame.K_LSHIFT]:
                    speed *= 2
                    rot_speed *= 3
    
                robot_next_position, mnoise = self.robot.move(
                    speed, position=robot_next_position)
                next_positions = [p.move(speed, noise=mnoise)[0]
                                for p in self.particles]
    
            if pressed_keys[pygame.K_a]:
                _, lnoise = self.robot.rotate(math.radians(-rot_speed))
                for p in self.particles:
                    p.rotate(math.radians(-rot_speed), noise=lnoise)
            if pressed_keys[pygame.K_d]:
                _, rnoise = self.robot.rotate(math.radians(rot_speed))
                for p in self.particles:
                    p.rotate(math.radians(rot_speed), noise=rnoise)
    
            if not self.wallmap.particle_has_collision(robot_next_position, self.robot.get_radius()):
                self.robot.apply_move(robot_next_position)
                for p, position in zip(self.particles, next_positions):
                    p.apply_move(position)
    
            # Clear
    
            self.screen.fill(WHITE)
    
            # Update
    
            surrounding_cells, surrounding_edges = self.get_surrounding_cells_edges(
                self.robot)
            self.robot.update(surrounding_edges, grid_size=self.grid_size)
    
            robot_measure = self.robot.measure(surrounding_edges)
    
            self.particles = self.generate_particles(self.particles, robot_measure)

            self.wallmap.draw(self.screen, draw_tile_debug=True)

            # particle_measurements = particle.measure(surrounding_edges)
            # print(Particle.likelihood(ground_thruth, particle_measurements))

            Particle.draw_robot(self.screen, self.robot, color=(148, 0, 211))

            for p in self.particles:
                Particle.draw_particle(self.screen, p)

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
    robot_size = config.getint('EnvironmentSettings', 'robot_size')
    particle_size = config.getint('EnvironmentSettings', 'particle_size')

    sensor_range = config.getint(sim_settings_name, 'sensor_range')
    sensor_aperture = math.radians(config.getint(
        sim_settings_name, 'sensor_aperture'))
    num_sensors = config.getint(sim_settings_name, 'num_sensors')

    return {
        'width': width,
        'height': height,
        'grid_size': grid_size,
        'robot_size': robot_size,
        'particle_size': particle_size,
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
