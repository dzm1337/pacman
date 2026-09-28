from abc import ABC
<<<<<<< HEAD
from enum import Enum
import random
=======
>>>>>>> 8bfb217b029fc21a82f514d32a864741aa66eb04

from src.definitions import GhostState
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
        super().__init__(maze, config, x, y, color=color, sprite_path=sprite_path)

    # @abstractmethod 0, 0 just for tests
    def target(self):
        return 0, 0

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self): ...


    def random_move(self):
        directions: list[str] = ["UP", "DOWN", "LEFT", "RIGHT"]
        choice: str = random.choice(directions)
        return choice


class Inky(Ghost):
    pass


class Pinky(Ghost):
    pass


class Clyde(Ghost):
    pass


class Blinky(Ghost):
    pass
