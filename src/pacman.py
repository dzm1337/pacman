from src.config import Config
from src.definitions import WALLS
from src.maze import Maze


class Pacman:
    def __init__(self, maze: Maze, config: Config) -> None:
        self.maze = Maze(config)
        self.lives: int = config.lives
        self.pp_pacgum: int = config.points_per_pacgum
        self.vel = 1
        self.x, self.y = maze.find_center_position()
        self.pp_superpacgum: int = config.point_per_superpacgum
        self.pp_ghost: int = config.points_per_ghost
        self.total_pacgums: int = 0
        self.total_superpacgums: int = 0
        self.height = maze.height
        self.width = maze.width

    def able_to_move(self, dx: int, dy: int) -> bool:
        """
        Takes the cell position and compare with the
        moviment to verify if the entity is able to move
        """
        wall = WALLS[(dx, dy)]
        return not (self.maze.get_maze[self.y][self.x] & wall)


# Function to check if pacman coordinates is the same as ghosts.
#    def check_collision() -> bool:

# Keep track of pacgums and superpacgums ingested by the pacman.
#    def ingested_gums() -> None:
