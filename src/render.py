from collections.abc import Callable

import pygame
from pygame import K_BACKSPACE, K_ESCAPE, K_KP_ENTER, K_RETURN, Surface

from src.definitions import (
    BACKGROUND,
    CELL_SIZE,
    FPS,
    HUD_HEIGHT,
    MAX_LEVEL,
    MAX_NAME_LENGTH,
    GameState,
    Screen,
)
from src.draw import Draw
from src.game import Game
from src.parser import fail

# Keys that pause the game, and resume it from the pause menu
PAUSE_KEYS = (pygame.K_p, K_ESCAPE)


class Render:
    def __init__(self, draw: Draw, game: Game) -> None:
        self.running = True
        self.game = game
        self.name = ""
        # Why the typed name can't be saved, shown on the save screen
        self.name_error: str | None = None
        self.screen_state = Screen.MENU
        self.draw = draw

    def _select_menu_option(self, option: str) -> None:
        if option == "Start":
            self.screen_state = Screen.PLAYING
        elif option == "Leaderboard":
            self.screen_state = Screen.LEADERBOARD
        elif option == "Instructions":
            self.screen_state = Screen.INSTRUCTIONS
        elif option == "Quit":
            self.running = False

    def _select_pause_option(self, option: str) -> None:
        if option == "Resume":
            self.screen_state = Screen.PLAYING
        elif option == "Main Menu":
            # The menu resets the game, so the current run is dropped
            self.screen_state = Screen.MENU

    def _screen_handler(
        self,
        key: int,
        index: int,
        option: list[str],
        select: Callable[[str], None],
    ) -> int:
        if key in (pygame.K_UP, pygame.K_w):
            index = (index - 1) % len(option)
        elif key in (pygame.K_DOWN, pygame.K_s):
            index = (index + 1) % len(option)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            select(option[index])
        return index

    def _key_handler(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_CAPSLOCK, pygame.K_ASTERISK):
                self.game.pacgums = []
                self.game.super_pacgums_pos = []
            if self.screen_state == Screen.MENU:
                self.game.menu_index = self._screen_handler(
                    event.key,
                    self.game.menu_index,
                    self.game.menu_options,
                    self._select_menu_option,
                )
            elif self.screen_state == Screen.PLAYING:
                if event.key in PAUSE_KEYS:
                    self.game.pause_index = 0
                    self.screen_state = Screen.PAUSED
                else:
                    self.game.move_pacman(event.key)
            elif self.screen_state == Screen.PAUSED:
                if event.key in PAUSE_KEYS:
                    self.screen_state = Screen.PLAYING
                else:
                    self.game.pause_index = self._screen_handler(
                        event.key,
                        self.game.pause_index,
                        self.game.pause_options,
                        self._select_pause_option,
                    )
            elif self.screen_state == Screen.INSTRUCTIONS:
                if event.key == K_ESCAPE:
                    self.screen_state = Screen.MENU
            elif self.screen_state == Screen.WON:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.screen_state = Screen.SAVE
            elif self.screen_state == Screen.GAME_OVER:
                if event.key in (K_KP_ENTER, K_RETURN):
                    self.screen_state = Screen.SAVE
            elif self.screen_state == Screen.LEADERBOARD:
                if event.key == K_ESCAPE:
                    self.screen_state = Screen.MENU
            elif self.screen_state == Screen.SAVE:
                self.handle_save(event)

    def _save_score(self) -> int | None:
        db = self.game.db
        rows = db.check_score_player(self.name)
        if not rows:
            db.insert_player(self.name, self.game.score)
        elif self.game.score > rows[0][0]:
            db.update_score(self.name, self.game.score)

    def handle_save(self, event) -> None:
        if event.key in (K_RETURN, K_KP_ENTER):
            self.name_error = self.game.name_error(self.name)
            if self.name_error:
                return
            self.name = self.name.strip()
            self._save_score()
        elif event.key == K_BACKSPACE:
            self.name = self.name[:-1]
            self.name_error = None
            return
        elif event.key != K_ESCAPE:
            char = event.unicode.upper()
            if not char:
                # Keys like shift or arrows don't type anything
                return
            if not self.game.valid_name_char(char):
                self.name_error = "Letters numbers and spaces only"
            elif len(self.name) >= MAX_NAME_LENGTH:
                self.name_error = f"Max {MAX_NAME_LENGTH} characters"
            else:
                self.name += char
                self.name_error = None
            return
        self.name = ""
        self.name_error = None
        self.screen_state = Screen.MENU

    def _window_size(self) -> tuple[int, int]:
        """
        Size of the window for the current level's maze, plus the HUD
        """
        return (
            self.game.width * CELL_SIZE,
            self.game.height * CELL_SIZE + HUD_HEIGHT,
        )

    def display(self) -> None:
        screen: Surface = pygame.display.set_mode(
            self._window_size(), pygame.SCALED
        )
        pygame.font.init()
        try:
            self.draw.load_assets()
        except Exception as e:
            fail(f"Error to load asset: {e}")

        pygame.display.set_caption("PACMAN")
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            dt: float = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self._key_handler(event)

            # Levels can have different sizes: follow the current one
            if screen.get_size() != self._window_size():
                screen = pygame.display.set_mode(
                    self._window_size(), pygame.SCALED
                )
            screen.fill(BACKGROUND)

            if self.screen_state == Screen.MENU:
                self.game.reset_game()
                self.draw.menu(screen)
            elif self.screen_state == Screen.PLAYING:
                if self.game.state == GameState.PLAYING:
                    self.game.update(dt)
                    self.draw.game_screen(screen)
                    self.game.move_ghost(dt)
                elif self.game.state == GameState.LOST:
                    self.screen_state = Screen.GAME_OVER
                elif self.game.state == GameState.WON:
                    if self.game.level == MAX_LEVEL:
                        self.screen_state = Screen.WON
                    else:
                        self.game.next_level()
            elif self.screen_state == Screen.WON:
                self.draw.victory(screen)
            elif self.screen_state == Screen.LEADERBOARD:
                self.draw.leaderboard(screen)
            elif self.screen_state == Screen.SAVE:
                self.draw.save(screen, self.name, self.name_error)
            elif self.screen_state == Screen.GAME_OVER:
                self.draw.game_over(screen)
            elif self.screen_state == Screen.PAUSED:
                self.draw.pause(screen)
            elif self.screen_state == Screen.INSTRUCTIONS:
                self.draw.instructions(screen)

            pygame.display.flip()
        pygame.quit()
