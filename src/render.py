import pygame
from pygame import Surface

from src.definitions import (
    BACKGROUND,
    CELL_SIZE,
    COLOR_42,
    FPS,
    GUM_COLOR,
    PACMAN_COLOR,
    WALL_COLOR,
    WALL_WIDTH,
    E,
    GameState,
    N,
    S,
    Screen,
    W,
)
from src.game import Game


class Render:
    def __init__(self, game: Game) -> None:
        self.running = True
        self.game = game
        self.screen_state = Screen.MENU
        self.menu_options = ["Start", "Exit"]
        self.menu_index = 0
        self.font: pygame.font.Font

    def _load_sprite(self, path: str) -> Surface:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(
            image, (CELL_SIZE // 1.5, CELL_SIZE // 1.5)
        )
        return image

    def draw_ghosts(self, screen: Surface) -> None:
        for ghost in self.game.ghosts:
            px: int = ghost.x * CELL_SIZE + CELL_SIZE // 2
            py: int = ghost.y * CELL_SIZE + CELL_SIZE // 2

            sprite = self._load_sprite(ghost.sprite_path)
            rect = sprite.get_rect(center=(px, py))
            screen.blit(sprite, rect)

    def draw_pacman(self, screen: Surface, dx: int, dy: int):
        px: int = dx * CELL_SIZE + CELL_SIZE // 2
        py: int = dy * CELL_SIZE + CELL_SIZE // 2

        sprite = self._load_sprite(self.game.pacman.sprite_path)
        rect = sprite.get_rect(center=(px, py))
        screen.blit(sprite, rect)

    def draw_gums(self, screen: Surface) -> None:
        for gum in self.game.pacgums:
            left = gum[1] * CELL_SIZE
            top = gum[0] * CELL_SIZE
            pygame.draw.circle(
                screen,
                GUM_COLOR,
                (
                    left + CELL_SIZE // 2,
                    top + CELL_SIZE // 2,
                ),
                4,
            )

    def draw_maze(self, screen: Surface) -> None:
        maze = self.game.maze.get_maze
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = maze[y][x]
                left = x * CELL_SIZE
                top = y * CELL_SIZE
                right = left + CELL_SIZE
                bottom = top + CELL_SIZE

                if cell == 15:
                    pygame.draw.rect(
                        screen, COLOR_42, (left, top, CELL_SIZE, CELL_SIZE)
                    )
                    continue

                if cell & N:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, top),
                        (right, top),
                        WALL_WIDTH,
                    )

                # East
                if cell & E:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (right, top),
                        (right, bottom),
                        WALL_WIDTH,
                    )

                # South
                if cell & S:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, bottom),
                        (right, bottom),
                        WALL_WIDTH,
                    )

                # West
                if cell & W:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, top),
                        (left, bottom),
                        WALL_WIDTH,
                    )

    def draw_text(
        self,
        screen: Surface,
        text: str,
        center: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        surface = self.font.render(text, True, color)
        rect = surface.get_rect(center=center)
        screen.blit(surface, rect)

    def draw_menu(self, screen: Surface) -> None:
        center_x = screen.get_width() // 2
        center_y = screen.get_width() // 2 - 30

        self.draw_text(
            screen,
            "PAC-MAN",
            (center_x, center_y - 100),
            WALL_COLOR,
        )

        for i, option in enumerate(self.menu_options):
            if i != self.menu_index:
                color = PACMAN_COLOR
            else:
                color = (255, 255, 255)
            dist = center_y + i * 65
            print(dist)
            self.draw_text(screen, option, (center_x, dist), color)

    def _select_menu_option(self, option: str) -> None:
        if option == "Start":
            self.screen_state = Screen.PLAYING
        elif option == "Exit":
            self.running = False

    def _menu_handler(self, key: int) -> None:
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._select_menu_option(self.menu_options[self.menu_index])

    def _key_handler(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.screen_state == Screen.MENU:
                self._menu_handler(event.key)
            elif self.screen_state == Screen.PLAYING:
                self.game.change_direction(event.key)

    def draw_game(self, screen: Surface) -> None:
        self.draw_gums(screen)
        self.draw_maze(screen)
        self.draw_ghosts(screen)
        self.draw_pacman(screen, self.game.pacman.x, self.game.pacman.y)

    def display(self) -> None:
        screen: Surface = pygame.display.set_mode(
            (
                self.game.width * CELL_SIZE,
                self.game.height * CELL_SIZE,
            ),
            pygame.SCALED,
        )
        pygame.font.init()
        self.font = pygame.font.Font("assets/fonts/pacman.ttf", 48)

        pygame.display.set_caption("PACMAN")
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            dt: float = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self._key_handler(event)

            screen.fill(BACKGROUND)

            if self.screen_state == Screen.MENU:
                self.draw_menu(screen)
            elif self.screen_state == Screen.PLAYING:
                self.game.update(dt)
                self.draw_game(screen)
                if self.game.state != GameState.PLAYING:
                    self.running = False
            pygame.display.flip()

        pygame.quit()
