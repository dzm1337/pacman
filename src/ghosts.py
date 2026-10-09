import random
from abc import ABC

from src.config import Config

# from src.game import Game
from src.definitions import DOWN, LEFT, RIGHT, UP
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
        self.last_move = None

        super().__init__(
            maze, config, x, y, color=color, sprite_path=sprite_path
        )

    # @abstractmethod 0, 0 just for tests
    def target(self):
        return 0, 0

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self): ...

    def move(self) -> None:
        direction = self.get_dir()
        self.last_move = direction
        dx, dy = direction
        self.x += dx
        self.y += dy


# The Inky will have a random moviment behaviour.
class Inky(Ghost):
    def get_dir(self) -> str:
        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice


# This one will target 4 spaces ahead of where the pac-man is located.
class Pinky(Ghost):
    def get_dir(self) -> str:

        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice


# The Clyde will target 8 spaces ahead of the pac-man.
class Clyde(Ghost):
    def get_dir(self) -> str:
        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice


# This one will follow the pac-man directly where he is located.
class Blinky(Ghost):
    def get_dir(self) -> str:

        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice
