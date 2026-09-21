from src.config import Config
from src.definitions import WALLS
from src.maze import Maze


class Entity:
    def __init__(self, maze: Maze, config: Config, x: int, y: int) -> None:
        self.maze = maze
        self.config = config
        self.x, self.y = x, y
        self.vel = 1

    def able_to_move(self, dx: int, dy: int) -> bool:
        """
        Takes the cell position and compare with the
        moviment to verify if the entity is able to move
        """
        wall = WALLS[(dx, dy)]
        return not (self.maze.get_maze[self.y][self.x] & wall)

    def move(self, dx: int, dy: int) -> None:
        if (dx, dy) != (0, 0) and self.able_to_move(dx, dy):
            self.x += dx
            self.y += dy
