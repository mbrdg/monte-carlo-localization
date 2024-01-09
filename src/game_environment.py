import wallmap
from consts import *
from settings import *

class Environment:

    def __init__(self, env_id):
        self.env_id = env_id

        if env_id == 'environment_1':
            self.define_environment_1()
        elif env_id == 'environment_2':
            self.define_environment_2()
        else:
            raise Exception('Invalid environment id, {}'.format(env_id))
        
    def define_environment_1(self):

        self.width, self.height = 800, 600
        self.grid_size = 20
        self.wallmap = wallmap.Wallmap(grid_size=self.grid_size, width=self.width, height=self.height)

        x_cells_len = self.width // self.grid_size
        y_cells_len = self.height // self.grid_size

        # Add edges
        # random edges
        def top_wall_border():
            edge_0 = wallmap.Edge((0, 0), (0, 1))
            edge_1 = wallmap.Edge((0, 1), (x_cells_len, 1))
            edge_2 = wallmap.Edge((x_cells_len, 1), (x_cells_len, 0))
            edge_3 = wallmap.Edge((x_cells_len, 0), (0, 0))
            manual_edges = [edge_0, edge_1, edge_2, edge_3]
            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def bottom_wall_border():
            edge_0 = wallmap.Edge((0, y_cells_len),
                                (0, y_cells_len - 1))
            edge_1 = wallmap.Edge((0, y_cells_len - 1),
                                (x_cells_len, y_cells_len - 1))
            edge_2 = wallmap.Edge(
                (x_cells_len, y_cells_len - 1), (x_cells_len, y_cells_len))
            edge_3 = wallmap.Edge(
                (x_cells_len, y_cells_len), (0, y_cells_len))
            manual_edges = [edge_0, edge_1, edge_2, edge_3]
            # manual_edges = [edge_2]
            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def left_wall_border():
            edge_0 = wallmap.Edge((0, 0), (1, 0))
            edge_1 = wallmap.Edge((1, 0), (1, y_cells_len))
            edge_2 = wallmap.Edge((1, y_cells_len),
                                (0, y_cells_len))
            edge_3 = wallmap.Edge((0, y_cells_len), (0, 0))
            manual_edges = [edge_0, edge_1, edge_2, edge_3]
            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def right_wall_border():
            edge_0 = wallmap.Edge((x_cells_len, 0),
                                (x_cells_len - 1, 0))
            edge_1 = wallmap.Edge((x_cells_len - 1, 0),
                                (x_cells_len - 1, y_cells_len))
            edge_2 = wallmap.Edge(
                (x_cells_len - 1, y_cells_len), (x_cells_len, y_cells_len))
            edge_3 = wallmap.Edge(
                (x_cells_len, y_cells_len), (x_cells_len, 0))
            manual_edges = [edge_0, edge_1, edge_2, edge_3]
            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

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
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_2():
            manual_edges = [
                wallmap.Edge((13, 6), (20, 6)),
                wallmap.Edge((20, 6), (20, 9)),
                wallmap.Edge((20, 9), (13, 6)),
            ]
            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_3():
            manual_edges = [
                wallmap.Edge((13, 0), (13, 6)),
                wallmap.Edge((13, 6), (17, 6)),
                wallmap.Edge((17, 6), (14, 5)),
                wallmap.Edge((14, 5), (14, 0)),
                wallmap.Edge((14, 0), (13, 0)),
            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_4():
            manual_edges = [
                wallmap.Edge((6, 0), (6, 11)),
                wallmap.Edge((6, 11), (8, 11)),
                wallmap.Edge((8, 11), (8, 0)),
                wallmap.Edge((8, 0), (6, 0)),
            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_5():
            manual_edges = [
                wallmap.Edge((4, 5), (4, 6)),
                wallmap.Edge((4, 6), (6, 6)),
                wallmap.Edge((6, 6), (6, 5)),
                wallmap.Edge((6, 5), (4, 5)),
            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

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
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

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
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_8():
            manual_edges = [
                wallmap.Edge((4, 25), (8, 21)),
                wallmap.Edge((8, 21), (10, 23)),
                wallmap.Edge((10, 23), (6, 27)),
                wallmap.Edge((6, 27), (4, 25)),

            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

        def wall_9():
            manual_edges = [
                wallmap.Edge((30, 15), (33, 15)),
                wallmap.Edge((33, 15), (33, 35)),
                wallmap.Edge((33, 35), (30, 35)),
                wallmap.Edge((30, 35), (30, 15)),

            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_GREY))

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
                self.wallmap.add_edge(edge)

        def box_1():
            manual_edges = [
                wallmap.Edge((28, 4), (34, 4)),
                wallmap.Edge((34, 4), (34, 8)),
                wallmap.Edge((34, 8), (28, 8)),
                wallmap.Edge((28, 8), (28, 4)),
            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_BROWN))

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
        wall_9()
        box_1()
        #maze_1()

    def define_environment_2(self):
        self.width, self.height = 400, 400
        self.grid_size = 20
        self.wallmap = wallmap.Wallmap(grid_size=self.grid_size, width=self.width, height=self.height)

        x_cells_len = self.width // self.grid_size
        y_cells_len = self.height // self.grid_size

        # Add edges
        
        def borders():
            self.wallmap.add_edge(wallmap.Edge((0, 0), (x_cells_len, 0)))
            self.wallmap.add_edge(wallmap.Edge((x_cells_len, 0), (x_cells_len, y_cells_len)))
            self.wallmap.add_edge(wallmap.Edge((x_cells_len, y_cells_len), (0, y_cells_len)))
            self.wallmap.add_edge(wallmap.Edge((0, y_cells_len), (0, 0)))

        def box_1():
            manual_edges = [
                wallmap.Edge((5, 4), (8, 4)),
                wallmap.Edge((8, 4), (8, 8)),
                wallmap.Edge((8, 8), (5, 8)),
                wallmap.Edge((5, 8), (5, 4)),
            ]

            for edge in manual_edges:
                self.wallmap.add_edge(edge)

            self.wallmap.add_obstacle(wallmap.Obstacle(manual_edges, LIGHT_BROWN))

        borders()
        box_1()