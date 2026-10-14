from collections.abc import Callable

import pygame
from pygame import K_BACKSPACE, K_ESCAPE, K_KP_ENTER, K_RETURN, Surface

from src.definitions import (
    BACKGROUND,
    CELL_SIZE,
    FPS,
    MAX_LEVEL,
    GameState,
    Screen,
)
from src.draw import Draw
from src.game import Game


class Render:
    def __init__(self, draw: Draw, game: Game) -> None:
        self.running = True
        self.game = game
        self.name = ""
        self.screen_state = Screen.MENU
        self.draw = draw

    def _select_menu_option(self, option: str) -> None:
        if option == "Start":
            self.screen_state = Screen.PLAYING
        if option == "Leaderboard":
            self.screen_state = Screen.LEADERBOARD
        elif option == "Quit":
            self.running = False

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
            if self.screen_state == Screen.MENU:
                self.game.menu_index = self._screen_handler(
                    event.key,
                    self.game.menu_index,
                    self.game.menu_options,
                    self._select_menu_option,
                )
            elif self.screen_state == Screen.PLAYING:
                self.game.move_pacman(event.key)
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
            if not self.game.valid_player_name(self.name):
                return
            self._save_score()
        elif event.key == K_BACKSPACE:
            self.name = self.name[:-1]
            return
        elif event.key != K_ESCAPE:
            if event.unicode.isalnum():
                self.name += event.unicode.upper()
            return
        self.name = ""
        self.screen_state = Screen.MENU

    def display(self) -> None:
        screen: Surface = pygame.display.set_mode(
            (
                self.game.width * CELL_SIZE,
                self.game.height * CELL_SIZE,
            ),
            pygame.SCALED,
        )
        pygame.font.init()
        self.draw.load_assets()

        pygame.display.set_caption("PACMAN")
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            dt: float = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self._key_handler(event)

            screen.fill(BACKGROUND)

            if self.screen_state == Screen.MENU:
                self.game.reset_game()
                self.draw.menu(screen)
            elif self.screen_state == Screen.PLAYING:
                if self.game.state == GameState.PLAYING:
                    self.game.update(dt)
                    self.game.move_ghost(dt)
                    self.draw.game_screen(screen)
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
                self.draw.save(screen, self.name)
            elif self.screen_state == Screen.GAME_OVER:
                self.draw.game_over(screen)

            pygame.display.flip()
        pygame.quit()
