from src.config import Config
from src.ghosts import Blinky, Clyde, Inky, Pinky
from src.maze import Maze
from src.pacman import Pacman


class Game:
    def __init__(self, maze: Maze, config: Config):
        self.maze = maze
        self.config = config
        self.maze_shape = self.maze.get_maze
        self.width, self.height = self.maze.get_shape
        # list of ghosts with their start positions
        # if not possible the exact position try to
        # find the nearest cell
        self.ghosts = [
            Inky(maze, config, *maze.find_nearest_open_cell(0, 0)),
            Pinky(
                maze, config, *maze.find_nearest_open_cell(self.width - 1, 0)
            ),
            Clyde(
                maze, config, *maze.find_nearest_open_cell(0, self.height - 1)
            ),
            Blinky(
                maze,
                config,
                *maze.find_nearest_open_cell(self.width - 1, self.height - 1),
            ),
        ]
        self.pacman = Pacman(maze, config)

    # We're going to use this class to move every type of
    # Entity regardless of being pacman of ghost
    def update(self, dx: int, dy: int, dt: float) -> None:
        if (dx, dy) != (0, 0):
            self.pacman.direction = (dx, dy)
        if self.pacman.tick(dt):
            self.pacman.move(*self.pacman.direction)
