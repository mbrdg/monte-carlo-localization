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

GEN_INTERVAL = 8


class Game:

    def __init__(self, config_data):

        self.enviroment_id = config_data['environment_id']
        self.sensor_range = config_data['sensor_range']
        self.sensor_aperture = config_data['sensor_aperture']
        self.num_sensors = config_data['num_sensors']
        self.view_laser = config_data['view_laser']
        self.view_laser_outline = config_data['view_laser_outline']

        self.wall_density_viz = config_data['wall_density_viz']
        self.cell_range_viz = config_data['cell_range_viz']

        Particle.ROBOT_SIZE = config_data['robot_size']
        Particle.PARTICLE_SIZE = config_data['particle_size']

        self.enviroment = game_environment.Environment(self.enviroment_id)
        self.wallmap = self.enviroment.wallmap
        self.width, self.height = self.enviroment.width, self.enviroment.height
        self.grid_size = self.enviroment.grid_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Montecarlo Localization")
        self.clock = pygame.time.Clock()

    
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

        self.gen_variance_max = 1000
        self.gen_variance_min = 5

        self.rotation_variance_max = math.radians(360)
        self.rotation_variance_min = math.radians(1)

        self.current_variance = self.gen_variance_max
        self.last_scores = [0, 0, 0, 0, 0]
        self.num_last_scores = 5

        self.generation_split = 0.5
        self.max_generation_split = 0.9

        self.last_position_variance = 1000

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

        number_of_confidents = max(len(particles)//10, 10)

        scores = [(i, p.likelihood(ground_thruth))
                for i, p in enumerate(particles)]

        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:number_of_confidents]

        x, y = np.meshgrid(np.arange(width), np.arange(height))
        density_map = np.zeros((height, width))

        top_scores_avg = np.mean([score for _, score in top_scores])

        top_rotations = [particles[i].get_angle()% (math.pi*2) for i, _ in top_scores]
        (rot_mean, rot_variance) = self.fit_normal(top_rotations, [score for _, score in top_scores])
        rot_mean = rot_mean % (math.pi*2)

        num_generated_particles = (len(particles) - len(top_scores))

        gen_variance = self.current_variance

        gen_multiplier = 1

        print(f"Last score {self.last_scores} ; Top score {top_scores_avg}")
        if round(top_scores_avg,2) >= np.mean(self.last_scores) or top_scores_avg > 0.90:
            gen_multiplier = min(0.9, top_scores_avg)
            print(f"Gen multiplier {gen_multiplier}")
            gen_variance = self.current_variance * gen_multiplier * 0.9
            rot_variance *= gen_multiplier
        else:
            gen_multiplier = max(1.2, np.mean(self.last_scores)/top_scores_avg)
            print(f"Gen multiplier {gen_multiplier}")
            gen_variance = self.current_variance * gen_multiplier
            rot_variance *= gen_multiplier

        gen_variance = max(self.gen_variance_min, gen_variance) #* top_scores_avg   
        self.current_variance = gen_variance

        self.last_scores = self.last_scores[1:]
        self.last_scores.append(top_scores_avg)

        self.generation_split = self.generation_split * gen_multiplier # goes down with better scores
        self.generation_split = min(self.max_generation_split, self.generation_split)

        if (len(particles) > MIN_PARTICLES):
            deductive = (len(particles)-number_of_confidents) * gen_multiplier
            if deductive <= 0:
                deductive = 1
            num_generated_particles = round(deductive)
            num_generated_particles = min(SAMPLES, num_generated_particles)
            num_generated_particles = max(MIN_PARTICLES, num_generated_particles)
            print(f"Num generated particles {num_generated_particles}")
        else:
            num_generated_particles = MIN_PARTICLES

        for i, weight in top_scores:
            density_map += weight * \
                self.gaussian_distribution(
                    x, y, particles[i].get_position(), gen_variance)

        density_map /= np.sum(density_map)
        

        if not np.isnan(density_map).any():

            num_random_particles = round(num_generated_particles * self.generation_split)
            num_particles_from_gmm = num_generated_particles - num_random_particles

            print(f"Num random particles {num_random_particles} ; Num gmm particles {num_particles_from_gmm}")

            generated_particle_positions_gmm = self.generate_particle_positions(np.array(
                [x.flatten(), y.flatten()]).T, density_map.flatten(), num_particles_from_gmm)   
            
            generated_particle_positions_random = np.array(
                [[random.uniform(0, self.width), random.uniform(0, self.height)] for _ in range(num_random_particles)])
            
            new_particles = [particles[i] for i, _ in top_scores]

            if len(generated_particle_positions_gmm) > 0:

                new_particles.extend([Particle(position, (np.random.normal(loc=rot_mean, scale=rot_variance))%(math.pi*2),
                                        range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors) for position in generated_particle_positions_gmm])
            
            if len(generated_particle_positions_random) > 0:
                new_particles.extend([Particle(position, random.uniform(0, 2 * math.pi),
                                        range_=self.sensor_range, aperture=self.sensor_aperture, num_sensors=self.num_sensors) for position in generated_particle_positions_random])

        else:
            new_particles = particles

        print(f"Total particles {len(particles)} ; Scores svg {top_scores_avg} ; Variance {gen_variance}; Generation_split {self.generation_split}")

        return new_particles
    
    def run(self):
        running = True

        frame_count = 0

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

            if frame_count % GEN_INTERVAL == 0:
              self.particles = self.generate_particles(self.particles, robot_measure)

            Particle.draw_robot(self.screen, self.robot, color=(148, 0, 211), draw_lasers=self.view_laser, draw_laser_outlines=self.view_laser_outline)

            for p in self.particles:
                Particle.draw_particle(self.screen, p)

            self.wallmap.draw(self.screen)

            if self.cell_range_viz:
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

            frame_count += 1

        pygame.quit()
        sys.exit()




def read_config(file_path, sim_settings_name):
    config = configparser.ConfigParser()
    config.read(file_path)

    environment_id = config.get('EnvironmentSettings', 'environment_id')
    robot_size = config.getint('EnvironmentSettings', 'robot_size')
    particle_size = config.getint('EnvironmentSettings', 'particle_size')
    view_laser = config.getboolean('EnvironmentSettings', 'view_laser')
    view_laser_outline = config.getboolean(
        'EnvironmentSettings', 'view_laser_outline')

    wall_density_viz = config.getboolean(
        'DebugSettings', 'wall_density_viz')
    cell_range_viz = config.getboolean(
        'DebugSettings', 'cell_range_viz')

    sensor_range = config.getint(sim_settings_name, 'sensor_range')
    sensor_aperture = math.radians(config.getint(
        sim_settings_name, 'sensor_aperture'))
    num_sensors = config.getint(sim_settings_name, 'num_sensors')

    return {
        'environment_id': environment_id,
        'robot_size': robot_size,
        'particle_size': particle_size,
        'view_laser': view_laser,
        'view_laser_outline': view_laser_outline,
        'wall_density_viz': wall_density_viz,
        'cell_range_viz': cell_range_viz,
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
