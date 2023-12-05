# main.py
import random
import sys

import pygame

import wallmap
from consts import *
from settings import *

FPS = 60


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wall Map")

    grid_size = 20

    my_wallmap = wallmap.Wallmap(None, grid_size)

    # Add edges
    # random edges

    edge_0 = wallmap.Edge((2, 2), (2, 4))
    edge_1 = wallmap.Edge((2, 4), (16, 4))
    edge_2 = wallmap.Edge((16, 4), (16, 2))
    edge_3 = wallmap.Edge((16, 2), (2, 2))
    manual_edges = [edge_0, edge_1, edge_2, edge_3]

    # manual_edges = [edge_2]
    for edge in manual_edges:
        my_wallmap.add_edge(edge)

    my_wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

    for _ in range(2):
        pos1 = (random.randint(0, WIDTH // grid_size),
                random.randint(0, HEIGHT // grid_size))
        pos2 = (random.randint(0, WIDTH // grid_size),
                random.randint(0, HEIGHT // grid_size))
        edge = wallmap.Edge(pos1, pos2)
        my_wallmap.add_edge(edge)
        print(f'Added edge from {pos1} to {pos2}')

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update

        # Draw
        screen.fill(WHITE)

        my_wallmap.draw_tile_debug(screen)
        my_wallmap.draw(screen)
        # my_wallmap.draw_obstacles(screen)

        # Refresh the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
