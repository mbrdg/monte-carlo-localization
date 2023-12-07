import itertools
import math

import numpy as np
import pygame
from shapely.geometry import Polygon

import geometry_utils
from consts import *


class Edge:

    # positions are given in terms of grid size
    # pos1 and pos2 are tuples of (x, y) coordinates
    # 0 -> WIDTH / grid_size

    def __init__(self, pos1, pos2):
        self.pos1 = np.array(pos1)
        self.pos2 = np.array(pos2)
        self.obstacles = []

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)


class Obstacle:
    def __init__(self, edges, color):
        self.edges = edges
        self.color = color
        self.polygon = Polygon(itertools.chain.from_iterable((e.pos1, e.pos2) for e in edges))

    def get_polygon(self):
        return self.polygon


class Wallmap:
    def __init__(self, game, grid_size=16, *, width=800, height=600):
        self.game = game
        self.grid_size = grid_size
        self.tilemap = {}
        self.gridmap = {}
        self.edges = []
        self.obstacles = []
        self.width = width
        self.height = height

    def get_obstacles(self):
        return self.obstacles

    def add_edge(self, edge):
        pos1 = edge.pos1
        pos2 = edge.pos2
        loc_str = f'{pos1};{pos2}'
        self.gridmap[loc_str] = edge

        self.edges.append(edge)

        for x in range(min(pos1[0], pos2[0])-1, max(pos1[0], pos2[0])+1):
            for y in range(min(pos1[1], pos2[1])-1, max(pos1[1], pos2[1])+1):

                # check if x, y is inside borders

                if x < 0 or x >= self.width // self.grid_size or y < 0 or y >= self.height // self.grid_size:
                    continue

                tile_points = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
                for i in range(len(tile_points)):
                    tile_point0 = np.array(tile_points[i])
                    tile_point1 = np.array(
                        tile_points[(i+1) % len(tile_points)])
                    if geometry_utils.line_line_intersection((pos1, pos2), (tile_point0, tile_point1)):
                        edge_loc_str = f'{x};{y}'
                        if edge_loc_str in self.tilemap:
                            self.tilemap[edge_loc_str].append(edge)
                        else:
                            self.tilemap[edge_loc_str] = [edge]
                        break

    def add_obstacle(self, obstacle):
        for edge in obstacle.edges:
            edge.add_obstacle(obstacle)

        self.obstacles.append(obstacle)

    def draw_walls(self, screen):
        for edge in self.gridmap.values():
            draw_pos1 = edge.pos1 * self.grid_size
            draw_pos2 = edge.pos2 * self.grid_size
            pygame.draw.line(screen, BLACK, draw_pos1, draw_pos2, 1)

    def draw_obstacles(self, screen):

        for obstacle in self.obstacles:
            points = []
            for edge in obstacle.edges:
                points.append(edge.pos1 * self.grid_size)
                points.append(edge.pos2 * self.grid_size)

            # Use Pygame to draw the filled polygon representing the obstacle
            pygame.draw.polygon(screen, obstacle.color, points)

    def draw_tile_debug(self, screen):
        # represent tiles in tilemap as red rectangles, with increasing intensity for each edge
        for tile in self.tilemap:
            tx, yx = tuple(int(x) for x in tile.split(';'))[:2]
            intensity = (len(self.edges) - len(self.tilemap[tile])) / len(self.edges)
            intensity = intensity ** 4
            pygame.draw.rect(
                screen,
                (255, int(intensity * 255), int(intensity * 255)), 
                pygame.Rect(tx * self.grid_size, yx * self.grid_size, self.grid_size, self.grid_size)
            )

    def draw(self, screen, *, draw_tile_debug=False):
        if draw_tile_debug:
            self.draw_tile_debug(screen)
        self.draw_walls(screen)
        self.draw_obstacles(screen)

    def particle_has_collision(self, position, radius):
        grid_pos = [math.floor(position[0] / self.grid_size), math.floor(position[1] / self.grid_size)]
        grid_range = math.ceil(radius / self.grid_size)

        for x_offset in range(-grid_range, grid_range+1):
            for y_offset in range(-grid_range, grid_range+1):
                # check if x, y is inside borders

                x = grid_pos[0] + x_offset
                y = grid_pos[1] + y_offset

                if x < 0 or x >= self.width // self.grid_size or y < 0 or y >= self.height // self.grid_size:
                    continue

                if f'{x};{y}' in self.tilemap:
                    edges = self.tilemap[f'{x};{y}']
                    for edge in edges:
                        if geometry_utils.circle_line_collision(
                            edge.pos1 * self.grid_size, edge.pos2 * self.grid_size,
                            position, radius
                        ):
                            return True
        return False

    def get_surrounding_cells_range(self, pos, range_):

        surrounding_cells = []

        grid_pos = [math.floor(pos[0] / self.grid_size),
                    math.floor(pos[1] / self.grid_size)]
        grid_range = math.ceil(range_ / self.grid_size)

        for x_offset in range(-grid_range, grid_range+1):
            for y_offset in range(-grid_range, grid_range+1):
                # check if x, y is inside borders

                x = grid_pos[0] + x_offset
                y = grid_pos[1] + y_offset

                if x < 0 or x >= self.width // self.grid_size or y < 0 or y >= self.height // self.grid_size:
                    continue

                if f'{x};{y}' in self.tilemap:
                    surrounding_cells.append((
                        f'{x};{y}', self.tilemap[f'{x};{y}']))

        return surrounding_cells

    def get_surrounding_cells_aperture(self, pos, range_, angle, aperture=math.pi):

        def sign_0(a): return 1 if a > 0 else -1 if a < 0 else 0

        surrounding_cells = []

        grid_pos = [math.floor(pos[0] / self.grid_size),
                    math.floor(pos[1] / self.grid_size)]
        grid_range = math.ceil(range_ / self.grid_size)

        most_dist = [
            round(math.cos(angle) * grid_range),
            round(math.sin(angle) * grid_range)
        ]

        most_dist_aperture_min = [
            round(math.cos(angle - aperture/2)
                  * grid_range),
            round(math.sin(angle - aperture/2)
                  * grid_range)
        ]

        most_dist_aperture_max = [
            round(math.cos(angle + aperture/2)
                  * grid_range),
            round(math.sin(angle + aperture/2)
                  * grid_range)
        ]

        x_aperture_min = (0-sign_0(most_dist[0]),
                          most_dist[0] + most_dist_aperture_min[0])
        y_aperture_min = (0-sign_0(most_dist[1]),
                          most_dist[1] + most_dist_aperture_min[1])

        x_aperture_max = (0-sign_0(most_dist[0]),
                          most_dist[0] + most_dist_aperture_max[0])
        y_aperture_max = (0-sign_0(most_dist[1]),
                          most_dist[1] + most_dist_aperture_max[1])

        x_range = (0-sign_0(most_dist[0]), most_dist[0] +
                   sign_0(most_dist[0]))
        y_range = (0-sign_0(most_dist[1]), most_dist[1] +
                   sign_0(most_dist[1]))

        min_x = min((min(x_aperture_min), min(x_aperture_max), min(x_range)))
        max_x = max((max(x_aperture_min), max(x_aperture_max), max(x_range)))

        min_y = min((min(y_aperture_min), min(y_aperture_max), min(y_range)))
        max_y = max((max(y_aperture_min), max(y_aperture_max), max(y_range)))

        for x_offset in range(min_x, max_x+1):
            for y_offset in range(min_y, max_y+1):
                # check if x, y is inside borders

                x = grid_pos[0] + x_offset
                y = grid_pos[1] + y_offset

                if x < 0 or x >= self.width // self.grid_size or y < 0 or y >= self.height // self.grid_size:
                    continue

                if f'{x};{y}' in self.tilemap:
                    surrounding_cells.append((
                        f'{x};{y}', self.tilemap[f'{x};{y}']))

        return surrounding_cells

    def get_surrounding_cells(self, pos, *, mode='aperture', **kwargs):
        if mode == 'aperture':
            return self.get_surrounding_cells_aperture(pos, **kwargs)
        elif mode == 'range':
            return self.get_surrounding_cells_range(pos, **kwargs)
        else:
            raise ValueError(
                f'Invalid mode {mode} for get_surrounding_cells()')
