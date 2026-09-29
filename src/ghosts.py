import random
from abc import ABC

from src.config import Config
from src.entity import Entity
from src.maze import Maze


class Ghost(Entity, ABC):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        x: int,
        y: int,
        color: tuple[int, int, int],
        sprite_path: str,
    ) -> None:
        super().__init__(
            maze, config, x, y, color=color, sprite_path=sprite_path
        )

    # @abstractmethod 0, 0 just for tests
    def target(self):
        return 0, 0

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self): ...

    def random_move(self, dt):
        directions: list[str] = ["UP", "DOWN", "LEFT", "RIGHT"]
        choice: str = random.choice(directions)

        if choice == "UP":
            dx, dy = 0, -1

        if choice == "DOWN":
            dx, dy = 0, 1

        if choice == "LEFT":
            dx, dy = -1, 0

        if choice == "RIGHT":
            dx, dy = 1, 0

        if self.able_to_move(dx, dy) and (dx, dy) != (0, 0):
                self.x += dx
                self.y += dy
        else:
            self.random_move(dt)


class Inky(Ghost):
    pass


class Pinky(Ghost):
    pass


class Clyde(Ghost):
    pass


class Blinky(Ghost):
    pass
