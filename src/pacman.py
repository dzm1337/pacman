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
        # Normal speed, so the F4 speed cheat can restore it exactly
        self.base_vel: float = vel
        self.pp_pacgum: int = config.points_per_pacgum
        self.pp_superpacgum: int = config.point_per_superpacgum
        self.pp_ghost: int = config.points_per_ghost
        self.total_pacgums: int = 0
        self.total_superpacgums: int = 0
        # Cheat (F1): ghosts can't touch pacman while this is on
        self.invincible: bool = False
