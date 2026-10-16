import pygame
from pygame import Surface

from src.definitions import (
    BLINKY_COLOR,
    CELL_SIZE,
    COLOR_42,
    GUM_COLOR,
    PACMAN_COLOR,
    WALL_COLOR,
    WALL_WIDTH,
    WHITE,
    E,
    N,
    S,
    W,
)
from src.game import Game

FONT_PATH = "assets/fonts/pacman.ttf"
OPTION_SPACING = 65
MENU_SPRITE_SIZE = 36
TABLE_MARGIN = 30
TABLE_GAP = 20
MENU_GHOSTS = ("blinky", "pinky", "inky", "clyde")


class Draw:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.font: pygame.font.Font
        self.small_font: pygame.font.Font

    def load_assets(self) -> None:
        self.title_font = pygame.font.Font(FONT_PATH, 64)
        self.font = pygame.font.Font(FONT_PATH, 48)
        self.medium_font = pygame.font.Font(FONT_PATH, 32)
        self.small_font = pygame.font.Font(FONT_PATH, 24)
        # From biggest to smallest, the leaderboard uses the first that fits
        self.table_fonts = [
            pygame.font.Font(FONT_PATH, size) for size in (24, 20, 16)
        ]
        self.menu_pacman = self._load_sprite(
            "assets/pacman.png", MENU_SPRITE_SIZE
        )
        self.menu_ghosts = [
            self._load_sprite(f"assets/{name}.png", MENU_SPRITE_SIZE)
            for name in MENU_GHOSTS
        ]

    def _load_sprite(self, path: str, size: int = CELL_SIZE // 1.5) -> Surface:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (size, size))
        return image

    def ghosts(self, screen: Surface) -> None:
        for ghost in self.game.ghosts:
            gx, gy = ghost.render_pos()
            px: int = int(gx * CELL_SIZE + CELL_SIZE // 2)
            py: int = int(gy * CELL_SIZE + CELL_SIZE // 2)

            sprite = self._load_sprite(ghost.sprite_path)
            rect = sprite.get_rect(center=(px, py))
            screen.blit(sprite, rect)

    def pacman(self, screen: Surface, dx: int, dy: int) -> None:
        px: int = dx * CELL_SIZE + CELL_SIZE // 2
        py: int = dy * CELL_SIZE + CELL_SIZE // 2

        sprite = self._load_sprite(self.game.pacman.sprite_path)
        rect = sprite.get_rect(center=(px, py))
        screen.blit(sprite, rect)

    def gums(self, screen: Surface) -> None:
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

    def maze(self, screen: Surface) -> None:
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

    def text(
        self,
        screen: Surface,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int],
        font: pygame.font.Font | None = None,
        anchor: str = "center",
    ) -> None:
        font = font or self.font
        surface = font.render(text, True, color)
        rect = surface.get_rect(**{anchor: pos})
        screen.blit(surface, rect)

    def _options(
        self,
        screen: Surface,
        options: list[str],
        selected: int,
        center_y: int,
        font: pygame.font.Font | None = None,
        spacing: int = OPTION_SPACING,
    ) -> int:
        """
        Draw a vertical list of options centered on center_y,
        highlighting the selected one. Return the y of the first option.
        """
        center_x = screen.get_width() // 2
        font = font or self.font
        top_y = center_y - (len(options) - 1) * spacing // 2
        for i, option in enumerate(options):
            color = WHITE if i == selected else PACMAN_COLOR
            y = top_y + i * spacing
            self.text(screen, option, (center_x, y), color, font)
            if i == selected:
                text_w = font.size(option)[0]
                icon = self.menu_pacman.get_rect(
                    midright=(center_x - text_w // 2 - 15, y)
                )
                screen.blit(self.menu_pacman, icon)
        return top_y

    def _title(
        self,
        screen: Surface,
        text: str,
        center: tuple[int, int],
        color: tuple[int, int, int] = PACMAN_COLOR,
    ) -> None:
        """
        Draw a big title with a blue shadow, arcade style
        """
        x, y = center
        self.text(screen, text, (x + 4, y + 4), WALL_COLOR, self.title_font)
        self.text(screen, text, (x, y), color, self.title_font)

    def _footer(self, screen: Surface) -> None:
        self.text(
            screen,
            "Press ENTER to select",
            (screen.get_width() // 2, screen.get_height() - 30),
            COLOR_42,
            self.small_font,
        )

    def option_screen(self, screen: Surface) -> None:
        center_x = screen.get_width() // 2
        top_y = self._options(
            screen,
            self.game.options,
            self.game.options_index,
            screen.get_height() // 2 + 70,
            self.medium_font,
            45,
        )
        self._title(screen, "YOU WON!", (center_x, top_y - 190))
        self.text(
            screen,
            "SCORE",
            (center_x, top_y - 120),
            COLOR_42,
            self.small_font,
        )
        self.text(
            screen,
            str(self.game.score),
            (center_x, top_y - 85),
            WHITE,
            self.medium_font,
        )
        self._footer(screen)

    def victory(self, screen: Surface) -> None:
        """
        Draw the end screen telling the player they won
        """
        self._end_screen(screen, "YOU WON!", PACMAN_COLOR)

    def game_over(self, screen: Surface) -> None:
        """
        Draw the end screen telling the player they lost
        """
        self._end_screen(screen, "GAME OVER", BLINKY_COLOR)

    def _end_screen(
        self, screen: Surface, title: str, color: tuple[int, int, int]
    ) -> None:
        """
        Draw an end of game screen with a title and the final score
        """
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2

        self._title(screen, title, (center_x, center_y - 110), color)
        self._ghost_row(screen, center_x, center_y - 40)
        self.text(
            screen,
            "FINAL SCORE",
            (center_x, center_y + 30),
            COLOR_42,
            self.small_font,
        )
        self.text(
            screen,
            str(self.game.score),
            (center_x, center_y + 75),
            WHITE,
            self.font,
        )
        self.text(
            screen,
            "Press ENTER to continue",
            (center_x, screen.get_height() - 30),
            COLOR_42,
            self.small_font,
        )

    def game_screen(self, screen: Surface) -> None:
        self.gums(screen)
        self.maze(screen)
        self.ghosts(screen)
        self.pacman(screen, self.game.pacman.x, self.game.pacman.y)

    def save(self, screen: Surface, name: str) -> None:
        center_x = screen.get_width() // 2
        center_y = screen.get_width() // 2 + 100

        self.text(
            screen,
            "Type your name...",
            (center_x, center_y),
            PACMAN_COLOR,
            self.small_font,
        )
        self.text(
            screen,
            f"{name}",
            (center_x, center_y - 50),
            PACMAN_COLOR,
            self.small_font,
        )

    def _table_font(
        self, scores: list[tuple], max_width: int
    ) -> pygame.font.Font:
        """
        Pick the biggest font where rank, name and score fit in max_width
        """
        for font in self.table_fonts:
            rank_w = font.size(f"{len(scores)}.")[0]
            name_w = max(font.size(name)[0] for name, _ in scores)
            score_w = max(font.size(str(score))[0] for _, score in scores)
            if rank_w + name_w + score_w + 2 * TABLE_GAP <= max_width:
                return font
        return self.table_fonts[-1]

    def leaderboard(self, screen: Surface) -> None:
        width = screen.get_width()
        center_x = width // 2
        title_y = 50
        scores = self.game.db.top_scores()

        self.text(
            screen,
            "LEADERBOARD",
            (center_x, title_y),
            PACMAN_COLOR,
            self.medium_font,
        )

        if scores:
            font = self._table_font(scores, width - 2 * TABLE_MARGIN)
            rank_x = TABLE_MARGIN + font.size(f"{len(scores)}.")[0]
            name_x = rank_x + TABLE_GAP
            score_x = width - TABLE_MARGIN
            row_h = font.get_height() + 12
            top_y = title_y + 70

            for i, (name, score) in enumerate(scores):
                y = top_y + i * row_h
                color = WHITE if i == 0 else PACMAN_COLOR
                self.text(screen, f"{i + 1}.", (rank_x, y), COLOR_42,
                          font, anchor="midright")
                self.text(screen, name, (name_x, y), color,
                          font, anchor="midleft")
                self.text(screen, str(score), (score_x, y), WHITE,
                          font, anchor="midright")
        else:
            center_y = screen.get_height() // 2
            self.text(
                screen,
                "There is no score",
                (center_x, center_y - 20),
                PACMAN_COLOR,
                self.small_font,
            )
            self.text(
                screen,
                "registered!",
                (center_x, center_y + 15),
                PACMAN_COLOR,
                self.small_font,
            )

        self.text(
            screen,
            "ESC to leave",
            (center_x, screen.get_height() - 30),
            COLOR_42,
            self.small_font,
        )

    def _ghost_row(self, screen: Surface, center_x: int, y: int) -> None:
        gap = MENU_SPRITE_SIZE + 14
        start_x = center_x - gap * (len(self.menu_ghosts) - 1) // 2
        for i, sprite in enumerate(self.menu_ghosts):
            rect = sprite.get_rect(center=(start_x + i * gap, y))
            screen.blit(sprite, rect)

    def menu(self, screen: Surface) -> None:
        center_x = screen.get_width() // 2
        top_y = self._options(
            screen,
            self.game.menu_options,
            self.game.menu_index,
            screen.get_height() // 2 + 40,
        )
        title_y = top_y - 160
        self._title(screen, "PAC-MAN", (center_x, title_y))
        self._ghost_row(screen, center_x, title_y + 70)
        self._footer(screen)
