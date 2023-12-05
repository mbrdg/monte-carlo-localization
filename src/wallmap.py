import sys

import numpy as np
import pygame

from consts import *
from settings import *


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


def lineLineIntersect(P0, P1, Q0, Q1):
    def orientation(P, Q, R):
        val = (Q[1] - P[1]) * (R[0] - Q[0]) - (Q[0] - P[0]) * (R[1] - Q[1])
        if val == 0:
            return 0  # Collinear points
        return 1 if val > 0 else 2  # Clockwise or counterclockwise

    def on_segment(P, Q, R):
        return (Q[0] <= max(P[0], R[0]) and Q[0] >= min(P[0], R[0]) and
                Q[1] <= max(P[1], R[1]) and Q[1] >= min(P[1], R[1]))

    o1 = orientation(P0, P1, Q0)
    o2 = orientation(P0, P1, Q1)
    o3 = orientation(Q0, Q1, P0)
    o4 = orientation(Q0, Q1, P1)

    # Check for special case of collinear and overlapping lines
    if o1 == o2 == o3 == o4 == 0:
        return on_segment(P0, Q0, P1) or on_segment(P0, Q1, P1) or on_segment(Q0, P0, Q1) or on_segment(Q0, P1, Q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(P0, Q0, P1):
        return True
    if o2 == 0 and on_segment(P0, Q1, P1):
        return True
    if o3 == 0 and on_segment(Q0, P0, Q1):
        return True
    if o4 == 0 and on_segment(Q0, P1, Q1):
        return True

    return False


class Wallmap:
    def __init__(self, game, grid_size=16):
        self.game = game
        self.grid_size = grid_size
        self.tilemap = {}
        self.gridmap = {}
        self.edges = []
        self.obstacles = []

    def add_edge(self, edge):
        pos1 = edge.pos1
        pos2 = edge.pos2
        loc_str = f'{pos1};{pos2}'
        self.gridmap[loc_str] = edge

        self.edges.append(edge)

        for x in range(min(pos1[0], pos2[0])-1, max(pos1[0], pos2[0])+1):
            for y in range(min(pos1[1], pos2[1])-1, max(pos1[1], pos2[1])+1):

                # check if x, y is inside borders

                if x < 0 or x >= WIDTH // self.grid_size or y < 0 or y >= HEIGHT // self.grid_size:
                    print(f'({x}, {y}) is outside borders')
                    continue

                tile_points = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
                for i in range(len(tile_points)):
                    tile_point0 = np.array(tile_points[i])
                    tile_point1 = np.array(
                        tile_points[(i+1) % len(tile_points)])
                    if lineLineIntersect(pos1, pos2, tile_point0, tile_point1):
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

    def draw(self, screen):
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
            tile_pos = np.array([int(x) for x in tile.split(';')])
            intensity = int(
                (len(self.edges)-len(self.tilemap[tile]))/len(self.edges) * 255)
            pygame.draw.rect(screen, (255, intensity, intensity), pygame.Rect(
                tile_pos * self.grid_size, (self.grid_size, self.grid_size)))
