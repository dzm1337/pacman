from mazegenerator import MazeGenerator

from src.definitions import DOWN, LEFT, RIGHT, UP, E, N, S, W
from src.parser import fail


class Maze:
    """Maze from the A-Maze-ing package, with its paths."""

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Generate the maze, or exit if the generator fails."""
        self.width = width
        self.height = height
        self.seed = seed
        try:
            self.maze = MazeGenerator(
                size=(self.width, self.height),
                seed=self.seed,
                perfect=False,
            )
        except Exception as e:
            fail(f"maze Generator Failed: {e}")
        self.neighbours = self.find_neighbours()

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
        maze: list[list[int]] = self.maze.maze
        return maze

    def find_nearest_open_cell(
        self, center_x: int, center_y: int
    ) -> tuple[int, int]:
        """Return the open cell closest to the given cell."""
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

    def find_neighbours(
        self,
    ) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """Return the cells reachable from each cell."""
        neighbours: dict[tuple[int, int], list[tuple[int, int]]] = {
            (x, y): [] for y in range(self.height) for x in range(self.width)
        }
        maze = self.get_maze

        for y in range(len(maze)):
            for x in range(len(maze[y])):
                if not maze[y][x] & N:
                    dx, dy = UP
                    neighbours[(x, y)].append((x + dx, y + dy))

                if not maze[y][x] & S:
                    dx, dy = DOWN
                    neighbours[(x, y)].append((x + dx, y + dy))

                if not maze[y][x] & W:
                    dx, dy = LEFT
                    neighbours[(x, y)].append((x + dx, y + dy))

                if not maze[y][x] & E:
                    dx, dy = RIGHT
                    neighbours[(x, y)].append((x + dx, y + dy))
        return neighbours
