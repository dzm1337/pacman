from src.entity import Entity


class Pacman(Entity):
    def __init__(self, maze, config, color, sprite_path, vel) -> None:
        super().__init__(
            maze,
            config,
            *maze.find_center_position(),
            color=color,
            sprite_path=sprite_path,
            vel=vel,
        )
        self.pp_pacgum: int = config.points_per_pacgum
        self.pp_superpacgum: int = config.point_per_superpacgum
        self.pp_ghost: int = config.points_per_ghost
        self.total_pacgums: int = 0
        self.total_superpacgums: int = 0
