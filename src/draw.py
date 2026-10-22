import time
from math import ceil

import pygame
from pygame import Surface

from src.definitions import (
    BLINK_PERIOD,
    BLINKY_COLOR,
    CELL_SIZE,
    COLOR_42,
    DOWN,
    FRIGHTENED_BLINK_TIME,
    HUD_HEIGHT,
    MAX_LEVEL,
    MOUTH_FRAME_TIME,
    LEFT,
    PACMAN_COLOR,
    RIGHT,
    STILL,
    UP,
    WALL_COLOR,
    WHITE,
    E,
    GhostState,
    N,
    S,
    W,
)
from src.font import BitmapFont, load_fonts
from src.game import Game

# Sprite file suffix for each direction (e.g. pacman_up.png, eyes_up.png)
DIRECTION_NAMES = (
    (UP, "up"),
    (DOWN, "down"),
    (LEFT, "left"),
    (RIGHT, "right"),
)

# Every font size used by the screens, baked in assets/fonts
FONT_SIZES = (64, 48, 32, 24, 20, 16, 8)
OPTION_SPACING = 65
MENU_SPRITE_SIZE = 36
TABLE_MARGIN = 30
TABLE_GAP = 20
MENU_GHOSTS = ("blinky", "pinky", "inky", "clyde")
HUD_GAP = 8


class Draw:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.font: BitmapFont
        self.small_font: BitmapFont

    def load_assets(self) -> None:
        fonts = load_fonts(FONT_SIZES)
        self.title_font = fonts[64]
        self.font = fonts[48]
        self.medium_font = fonts[32]
        self.small_font = fonts[24]
        # From biggest to smallest, the HUD uses the first that fits
        self.hud_fonts = [fonts[size] for size in (16, 8)]
        # From biggest to smallest, the leaderboard uses the first that fits
        self.table_fonts = [fonts[size] for size in (24, 16, 8)]
        # From biggest to smallest, the instructions use the first that fits
        self.instruction_fonts = [fonts[size] for size in (24, 20, 16, 8)]
        self.menu_pacman = self._load_sprite("assets/menu/pacman.png")
        self.menu_ghosts = [
            self._load_sprite(f"assets/menu/{name}.png")
            for name in MENU_GHOSTS
        ]
        self.playing_ghost = [
            self._load_sprite(ghost.sprite_path) for ghost in self.game.ghosts
        ]
        self.frightened_ghost = self._load_sprite("assets/game/frightened.png")
        self.frightened_white = self._load_sprite(
            "assets/game/frightened_white.png"
        )
        # Eyes of an eaten ghost, looking where it goes
        self.eyes = {
            direction: self._load_sprite(f"assets/game/eyes_{name}.png")
            for direction, name in DIRECTION_NAMES
        }
        # Waiting in its corner, the eaten ghost looks straight ahead
        self.eyes[STILL] = self._load_sprite("assets/game/eyes_still.png")
        self.pacman_directions = {
            direction: self._load_sprite(f"assets/game/pacman_{name}.png")
            for direction, name in DIRECTION_NAMES
        }
        # Mouth animation for each direction: open, half, closed, half
        self.pacman_frames = {
            direction: [
                self.pacman_directions[direction],
                self._load_sprite(f"assets/game/pacman_{name}_half.png"),
                self._load_sprite(f"assets/game/pacman_{name}_closed.png"),
                self._load_sprite(f"assets/game/pacman_{name}_half.png"),
            ]
            for direction, name in DIRECTION_NAMES
        }
        # Standing still (start or respawn), pacman looks right
        self.pacman_frames[STILL] = self.pacman_frames[RIGHT]
        # Last direction pacman moved to, kept while he is blocked
        self.pacman_facing = RIGHT
        self.super_pacgum_sprite = self._load_sprite(
            "assets/game/superpacgum.png"
        )
        self.pacgum_sprite = self._load_sprite("assets/game/pacgum.png")
        # Walls are images laid on the cell edges, centered on the edge
        self.wall_horizontal = self._load_sprite(
            "assets/game/wall_horizontal.png"
        )
        self.wall_vertical = self._load_sprite("assets/game/wall_vertical.png")
        # Top border of the maze, without the rows that would cover the HUD
        self.wall_top_edge = self._load_sprite(
            "assets/game/wall_horizontal_edge.png"
        )
        self.block_42 = self._load_sprite("assets/game/block_42.png")

    def _load_sprite(self, path: str) -> Surface:
        image = pygame.image.load(path).convert_alpha()
        return image

    @staticmethod
    def _cell_center(gx: float, gy: float) -> tuple[int, int]:
        """
        Screen position of the center of a maze cell, below the HUD
        """
        return (
            int(gx * CELL_SIZE + CELL_SIZE // 2),
            int(gy * CELL_SIZE + CELL_SIZE // 2) + HUD_HEIGHT,
        )

    def ghosts(self, screen: Surface) -> None:
        for i, ghost in enumerate(self.game.ghosts):
            px, py = self._cell_center(*ghost.render_pos())

            if ghost.state == GhostState.CHASE:
                rect = self.playing_ghost[i].get_rect(center=(px, py))
                screen.blit(self.playing_ghost[i], rect)
            elif ghost.state == GhostState.FRIGHTENED:
                sprite = self.frightened_ghost
                # Almost edible no more: blink white to warn the player
                ending = ghost.state_timer <= FRIGHTENED_BLINK_TIME
                if ending and int(ghost.state_timer / BLINK_PERIOD) % 2:
                    sprite = self.frightened_white
                rect = sprite.get_rect(center=(px, py))
                screen.blit(sprite, rect)
            elif ghost.state == GhostState.EATEN:
                eyes = self.eyes.get(ghost.direction, self.eyes[RIGHT])
                rect = eyes.get_rect(center=(px, py))
                screen.blit(eyes, rect)

    def super_pacgum(self, screen: Surface) -> None:
        for gum in self.game.super_pacgums_pos:
            px, py = self._cell_center(*gum)
            rect = self.super_pacgum_sprite.get_rect(center=(px, py))
            screen.blit(self.super_pacgum_sprite, rect)

    def pacman(self, screen: Surface, dx: int, dy: int) -> None:
        pacman = self.game.pacman
        if pacman.direction in self.pacman_frames:
            self.pacman_facing = pacman.direction
        frames = self.pacman_frames[self.pacman_facing]

        if pacman.prev == (pacman.x, pacman.y):
            # Not moving (blocked or still): keep the mouth open
            sprite = frames[0]
        else:
            # Chomp at a fixed pace, whatever pacman's speed
            seconds = time.monotonic()
            sprite = frames[int(seconds / MOUTH_FRAME_TIME) % len(frames)]

        px, py = self._cell_center(*pacman.render_pos())
        rect = sprite.get_rect(center=(px, py))
        screen.blit(sprite, rect)

    def gums(self, screen: Surface) -> None:
        for gy, gx in self.game.pacgums:
            rect = self.pacgum_sprite.get_rect(
                center=self._cell_center(gx, gy)
            )
            screen.blit(self.pacgum_sprite, rect)

    def maze(self, screen: Surface) -> None:
        maze = self.game.maze.get_maze
        # The wall images are thicker than one pixel: center them on the
        # cell edge, the extra pixel going up / left
        shift = (self.wall_horizontal.get_height() - 1) // 2
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = maze[y][x]
                left = x * CELL_SIZE
                top = y * CELL_SIZE + HUD_HEIGHT
                right = left + CELL_SIZE
                bottom = top + CELL_SIZE

                if cell == 15:
                    screen.blit(self.block_42, (left, top))
                    continue

                if cell & N:
                    if y == 0:
                        screen.blit(self.wall_top_edge, (left, top))
                    else:
                        screen.blit(self.wall_horizontal, (left, top - shift))
                if cell & E:
                    screen.blit(self.wall_vertical, (right - shift, top))
                if cell & S:
                    screen.blit(self.wall_horizontal, (left, bottom - shift))
                if cell & W:
                    screen.blit(self.wall_vertical, (left - shift, top))

    def text(
        self,
        screen: Surface,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int],
        font: BitmapFont | None = None,
        anchor: str = "center",
    ) -> None:
        font = font or self.font
        rect = pygame.Rect((0, 0), font.image_size(text))
        setattr(rect, anchor, pos)
        font.draw(screen, text, rect.topleft, color)

    def _options(
        self,
        screen: Surface,
        options: list[str],
        selected: int,
        center_y: int,
        font: BitmapFont | None = None,
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

    def _footer(
        self, screen: Surface, text: str = "Press ENTER to select"
    ) -> None:
        self.text(
            screen,
            text,
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
        self.hud(screen)
        # The maze is drawn below the HUD (see _cell_center)
        self.maze(screen)
        self.gums(screen)
        self.super_pacgum(screen)
        self.ghosts(screen)
        self.pacman(screen, self.game.pacman.x, self.game.pacman.y)

    def hud(self, screen: Surface) -> None:
        """
        Draw the bar above the maze with score, level, time and lives
        """
        y = HUD_HEIGHT // 2
        time_left = max(0, ceil(self.game.time_left))
        time_color = BLINKY_COLOR if time_left <= 10 else WHITE
        items = (
            ("SCORE", str(self.game.score), WHITE),
            ("LEVEL", str(self.game.level), WHITE),
            ("TIME", str(time_left), time_color),
        )
        lives = f"x{self.game.lives}"
        icon_w = self.pacman_directions[RIGHT].get_width()

        for font in self.hud_fonts:
            widths = [
                font.size(f"{label} {value}")[0] for label, value, _ in items
            ]
            lives_w = icon_w + HUD_GAP + font.size(lives)[0]
            free = screen.get_width() - 2 * HUD_GAP - sum(widths) - lives_w
            if free >= len(items) * HUD_GAP:
                break

        # Spread the items over the width, same space between each one
        space = max(HUD_GAP, free // len(items))
        left = HUD_GAP
        for (label, value, color), width in zip(items, widths):
            self.text(
                screen, label, (left, y), COLOR_42, font, anchor="midleft"
            )
            value_x = left + font.size(f"{label} ")[0]
            self.text(
                screen, value, (value_x, y), color, font, anchor="midleft"
            )
            left += width + space

        # Lives: pacman icon followed by the counter
        life_icon = self.pacman_directions[RIGHT]
        icon = life_icon.get_rect(midleft=(left, y))
        screen.blit(life_icon, icon)
        self.text(
            screen,
            lives,
            (left + icon_w + HUD_GAP, y),
            WHITE,
            font,
            anchor="midleft",
        )

    def save(
        self, screen: Surface, name: str, error: str | None = None
    ) -> None:
        center_x = screen.get_width() // 2
        center_y = screen.get_width() // 2 + 100

        if error:
            self.text(
                screen,
                "Invalid name",
                (center_x, center_y + 60),
                BLINKY_COLOR,
                self.small_font,
            )
            # Biggest font where the reason fits in the width
            max_width = screen.get_width() - 2 * TABLE_MARGIN
            font = next(
                (f for f in self.table_fonts if f.size(error)[0] <= max_width),
                self.table_fonts[-1],
            )
            self.text(
                screen, error, (center_x, center_y + 95), COLOR_42, font
            )

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
        self, scores: list[tuple[str, int]], max_width: int
    ) -> BitmapFont:
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
                self.text(
                    screen,
                    f"{i + 1}.",
                    (rank_x, y),
                    COLOR_42,
                    font,
                    anchor="midright",
                )
                self.text(
                    screen, name, (name_x, y), color, font, anchor="midleft"
                )
                self.text(
                    screen,
                    str(score),
                    (score_x, y),
                    WHITE,
                    font,
                    anchor="midright",
                )
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

    def pause(self, screen: Surface) -> None:
        """
        Draw the pause menu on a black screen
        """
        center_x = screen.get_width() // 2
        top_y = self._options(
            screen,
            self.game.pause_options,
            self.game.pause_index,
            screen.get_height() // 2 + 40,
            self.medium_font,
            50,
        )
        self._title(screen, "PAUSED", (center_x, top_y - 110))
        self._footer(screen, "P or ESC to resume")

    def _key_table(
        self,
        screen: Surface,
        header: str,
        rows: list[tuple[str, str]],
        y: int,
        font: BitmapFont,
        row_h: int,
    ) -> int:
        """
        Draw a centered header and its key / value rows, each value
        right after the key column so they read together.
        Return the y where the next section starts
        """
        center_x = screen.get_width() // 2
        self.text(screen, header, (center_x, y), COLOR_42, font)
        y += row_h
        gap = 2 * font.get_height()
        key_w = max(font.size(key)[0] for key, _ in rows)
        value_w = max(font.size(value)[0] for _, value in rows)
        left_x = center_x - (key_w + gap + value_w) // 2
        value_x = left_x + key_w + gap
        for key, value in rows:
            self.text(screen, key, (left_x, y), WHITE, font, anchor="midleft")
            self.text(
                screen,
                value,
                (value_x, y),
                PACMAN_COLOR,
                font,
                anchor="midleft",
            )
            y += row_h
        return y + row_h // 2

    def instructions(self, screen: Surface) -> None:
        """
        Draw the controls, the points of each item and the rules
        """
        config = self.game.config
        controls = [
            ("ARROWS OR WASD", "MOVE"),
            ("P OR ESC", "PAUSE"),
        ]
        points = [
            ("DOT", str(config.points_per_pacgum)),
            ("POWER PELLET", str(config.point_per_superpacgum)),
            ("GHOST", str(config.points_per_ghost)),
        ]
        rules = [
            "EAT ALL DOTS TO CLEAR A LEVEL",
            "POWER PELLETS MAKE GHOSTS EDIBLE",
            f"{config.lives} LIVES AND {config.level_max_time}S PER LEVEL",
            f"CLEAR {MAX_LEVEL} LEVELS TO WIN",
        ]
        cheats = [
            ("F1", "INVINCIBILITY"),
            ("F2", "GHOST FREEZE"),
            ("F3", "EXTRA LIFE"),
            ("F4", "EXTRA SPEED"),
            ("F5", "SKIP LEVEL"),
        ]

        width = screen.get_width()
        center_x = width // 2
        max_width = width - 2 * TABLE_MARGIN

        tables = controls + points + cheats
        row_count = len(tables) + len(rules) + 4  # one header per section
        max_height = screen.get_height() - 110 - 55  # title and footer

        # Biggest font (then the roomiest row spacing) where it all fits
        font, row_h = self.instruction_fonts[-1], 0
        for candidate in self.instruction_fonts:
            if any(candidate.size(rule)[0] > max_width for rule in rules):
                continue
            # Rows plus a half-row gap between each of the 4 sections
            for padding in (12, 8, 6):
                candidate_row_h = candidate.get_height() + padding
                total_h = row_count * candidate_row_h + 3 * (
                    candidate_row_h // 2
                )
                if total_h <= max_height:
                    font, row_h = candidate, candidate_row_h
                    break
            if row_h:
                break
        if not row_h:
            row_h = font.get_height() + 6

        y = 50
        self.text(
            screen,
            "HOW TO PLAY",
            (center_x, y),
            PACMAN_COLOR,
            self.medium_font,
        )
        y += 60

        y = self._key_table(screen, "CONTROLS", controls, y, font, row_h)
        y = self._key_table(screen, "POINTS", points, y, font, row_h)

        self.text(screen, "RULES", (center_x, y), COLOR_42, font)
        y += row_h
        for rule in rules:
            self.text(screen, rule, (center_x, y), WHITE, font)
            y += row_h
        y += row_h // 2

        self._key_table(screen, "CHEATS", cheats, y, font, row_h)

        self._footer(screen, "ESC to go back")

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
