from src.config import Config
from src.definitions import (
    BLINKY_COLOR,
    CLYDE_COLOR,
    INKY_COLOR,
    PACMAN_COLOR,
    PINKY_COLOR,
)
from src.ghosts import Blinky, Clyde, Inky, Pinky
from src.maze import Maze
from src.pacman import Pacman


class Game:
    def __init__(self, maze: Maze, config: Config):
        self.maze = maze
        self.config = config
        self.maze_shape = self.maze.get_maze
        self.width, self.height = self.maze.get_shape
        self.score = 0
        # list of ghosts with their start positions
        # if not possible the exact position try to
        # find the nearest cell
        self.ghosts = [
            Inky(
                maze,
                config,
                *maze.find_nearest_open_cell(0, 0),
                color=INKY_COLOR,
            ),
            Pinky(
                maze,
                config,
                *maze.find_nearest_open_cell(self.width - 1, 0),
                color=PINKY_COLOR,
            ),
            Clyde(
                maze,
                config,
                *maze.find_nearest_open_cell(0, self.height - 1),
                color=CLYDE_COLOR,
            ),
            Blinky(
                maze,
                config,
                *maze.find_nearest_open_cell(self.width - 1, self.height - 1),
                color=BLINKY_COLOR,
            ),
        ]
        self.pacman = Pacman(maze, config, PACMAN_COLOR)
        # Create a set who has tuples who represent
        # each coordinate of the pacgums
        self.pacgums: set[tuple[int, int]] = {
            (y, x)
            for x in range(self.width)
            for y in range(self.height)
            if self.maze_shape[y][x] != 15
        }
        self.pacgums.discard((self.pacman.y, self.pacman.x))

    # We're going to use this method to move every type of
    # Entity regardless of being pacman of ghost

    def update(self, dx: int, dy: int, dt: float) -> None:
        if (dx, dy) != (0, 0):
            self.pacman.direction = (dx, dy)
        if self.pacman.tick(dt):
            self.pacman.move(*self.pacman.direction)
            self.eat_gum()

    def eat_gum(self) -> None:
        pos = (self.pacman.y, self.pacman.x)
        eaten = True if pos in self.pacgums else False
        if eaten:
            print(
                f"Amount of Pacgums left = {len(self.pacgums)}\nPos = {pos}\nEaten?: {eaten}\nCurrent score: {self.score}\n"
            )
        # if pacman it's in the same position as a pacgum
        # delete it from the set and eventually remove it from the maze
        if pos in self.pacgums:
            self.pacgums.remove(pos)
            self.score += self.config.points_per_pacgum
