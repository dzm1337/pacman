from src.config import Config
from src.maze import Maze


class Pacman:
    def __init__(self, maze: Maze, config: Config) -> None:
        self.maze = Maze(config)
        self.lives: int = config.lives
        self.pp_pacgum: int = config.points_per_pacgum
        self.pp_superpacgum: int = config.point_per_superpacgum
        self.pp_ghost: int = config.points_per_ghost
        self.total_pacgums: int = 0
        self.total_superpacgums: int = 0
        self.height = maze.height
        self.width = maze.width


#    def able_to_move() -> bool:

# Function to check if pacman coordinates is the same as ghosts.
#    def check_collision() -> bool:

# Keep track of pacgums and superpacgums ingested by the pacman.
#    def ingested_gums() -> None:
