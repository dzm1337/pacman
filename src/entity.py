from src.config import Config
from src.definitions import STILL, WALLS
from src.maze import Maze


class Entity:
    def __init__(
        self,
        maze: Maze,
        config: Config,
        x: int,
        y: int,
        color: tuple[int, int, int],
        sprite_path: str,
        vel: int,
    ) -> None:
        self.color = color
        self.maze = maze
        self.config = config
        self.move_timer: float = 0.0
        self.direction = 0, 0
        self.x, self.y = x, y
        self.spawn_pos = x, y
        self.vel = vel
        self.sprite_path = sprite_path
        self.wanted_direction = 0, 0
        self.prev = self.spawn_pos

    def able_to_move(self, direction: tuple[int, int]) -> bool:
        """
        Takes the cell position and compare with the
        moviment to verify if the entity is able to move
        """
        if direction == STILL:
            return False
        dx, dy = direction
        wall = WALLS[(dx, dy)]
        return not (self.maze.get_maze[self.y][self.x] & wall)

    def tick(self, dt: float) -> bool:
        """
        Count the elapsed time and return True if the
        entity is ready to move to the next step
        based on its speed (vel)
        """
        self.move_timer += dt
        # print(f"timer: {self.move_timer:.3f}  dt: {dt:.3f}")
        # 1 / vel is the time that one step takes (vel = 5 -> 0.2 per cell)
        # not enough time has built up yet, so don't move
        if self.move_timer < 1 / self.vel:
            return False
        # Subtract one step worth of time instead of resetting to 0,
        # so leftover time (ex: 0.21 - 0.2 -> 0.01) carries to the next step.
        self.move_timer -= 1 / self.vel
        # print("Walk")
        return True

    def reset(self) -> None:
        self.x, self.y = self.spawn_pos
        self.direction = STILL
        self.wanted_direction = STILL
        self.move_timer = 0
        self.prev = self.spawn_pos

    def render_pos(self) -> tuple[float, float]:
        t = min(self.move_timer * self.vel, 1.0)
        px, py = self.prev
        return px + (self.x - px) * t, py + (self.y - py) * t

    def move(self, direction: tuple[int, int]) -> None:
        dx, dy = direction
        self.prev = self.x, self.y
        if self.able_to_move(direction):
            self.x += dx
            self.y += dy
