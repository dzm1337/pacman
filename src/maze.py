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
        """
        Return the shape of the maze.
        """
        return self.width, self.height

    @property
    def get_maze(self) -> list[list[int]]:
        """
        Return the generated maze.
        """
        return self.maze.maze

    def find_nearest_open_cell(self, center_x: int, center_y: int):
        maze: list[list[int]] = self.get_maze
        max_distance = max(self.width, self.height)

        for distance in range(0, max_distance):
            for dy in range(-distance, distance + 1):
                for dx in range(-distance, distance + 1):
                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x < self.width and 0 <= y < self.height:
                        if maze[y][x] != 15:
                            return x, y

        return center_x, center_y

    def find_center_position(self) -> tuple[int, int]:
        """
        Find the center position of the maze, if not pososible
        try to find the closest to it.
        """

        center_x: int = self.width // 2
        center_y: int = self.height // 2

        return self.find_nearest_open_cell(center_x, center_y)
