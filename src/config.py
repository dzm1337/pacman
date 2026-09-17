from dataclasses import dataclass



@dataclass
class Config:
    highscore_filename: str
    level: list
    width: int
    height: int
    lives: int
    pacgum: 42
    points_per_pacgum: int
    point_per_superpacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
