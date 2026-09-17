from src.config import Config




class Pacman:

    def __init__(self, config: Config):
        self.lives: int = config.lives
        self.pp_pacgum: int = config.points_per_pacgum
        self.pp_superpacgum: int = config.point_per_superpacgum
        self.pp_ghost: int = config.points_per_ghost
        self.total_pacgums: int = 0
        self.total_superpacgums: int = 0


    # We need the central coordinates to define where the pacman should spawn. -> return tuple[int, int]
#    def spawn_pacman() -> tuple[int, int]:

    # Function to define if the pacman is able to move to X direction. -> return bool
#    def able_to_move() -> bool:

    # Function to check if pacman coordinates is the same as ghosts.
#    def check_collision() -> bool:

    # Keep track of pacgums and superpacgums ingested by the pacman.
#    def ingested_gums() -> None:
