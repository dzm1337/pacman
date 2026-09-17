from mazegenerator import MazeGenerator

from src.config import Config


class Maze:
    def __init__(self, config: Config) -> None:
        self.width = config.width
        self.height = config.height
        self.seed = config.seed
        self.maze = MazeGenerator(
            size=(self.width, self.height), seed=self.seed
        )

    @property
    def get_shape(self) -> tuple[int, int]:
        return self.width, self.height

    @property
    def get_maze(self) -> list[list[int]]:
        return self.maze.maze

    def find_center_position(self) -> tuple[int, int]:
        center_x = self.width // 2
        center_y = self.height // 2

        maze = self.get_maze

        if maze[center_y][center_x] != 15:
            return center_x, center_y

        max_distance = max(self.width, self.height)

        for distance in range(1, max_distance):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x <= self.width and 0 <= y <= self.height:
                        if maze[y][x] != 15:
                            return x, y

        return center_x, center_y
