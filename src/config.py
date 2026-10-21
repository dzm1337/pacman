from dataclasses import dataclass


@dataclass
class Config:
    level: list[dict[str, int]]
    width: int
    height: int
    lives: int
    pacgum: int
    points_per_pacgum: int
    point_per_superpacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
