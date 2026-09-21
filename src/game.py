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

    def update(self, dx: int, dy: int) -> None:
        self.pacman.move(dx, dy)
