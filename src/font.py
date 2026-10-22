import json
from pathlib import Path

import pygame
from pygame import Surface

FONT_DIR = Path("assets/fonts")
# Glyph positions in each sheet, and the line height of each size
FONT_META = FONT_DIR / "pacman.json"


class BitmapFont:
    """
    The pacman font baked into a PNG sheet of white glyphs, one per size.
    Text is drawn by copying glyph images onto the screen, like
    mlx_put_image_to_window: no TTF rendering while the game runs
    """

    def __init__(
        self,
        sheet: Surface,
        height: int,
        image_height: int,
        glyphs: dict[str, list[int]],
    ) -> None:
        self.sheet = sheet
        # Line height, used to lay out rows of text
        self.height = height
        # Glyph images go a few pixels below the line height
        self.image_height = image_height
        # char -> [x in the sheet, width]
        self.glyphs = glyphs
        # (char, color) -> glyph image in that color, made on first use
        self._cache: dict[tuple[str, tuple[int, int, int]], Surface] = {}

    def get_height(self) -> int:
        return self.height

    def _glyph_box(self, char: str) -> list[int]:
        # Characters missing from the sheet are drawn as '?'
        return self.glyphs.get(char, self.glyphs["?"])

    def size(self, text: str) -> tuple[int, int]:
        """
        Width and height in pixels of the text written with this font
        """
        width = sum(self._glyph_box(char)[1] for char in text)
        return width, self.height

    def image_size(self, text: str) -> tuple[int, int]:
        """
        Size of the drawn text, glyphs included (positions the text)
        """
        return self.size(text)[0], self.image_height

    def _glyph(self, char: str, color: tuple[int, int, int]) -> Surface:
        key = (char, color)
        if key not in self._cache:
            sheet_x, width = self._glyph_box(char)
            glyph = Surface((width, self.image_height), pygame.SRCALPHA)
            for y in range(self.image_height):
                for x in range(width):
                    if self.sheet.get_at((sheet_x + x, y)).a:
                        glyph.set_at((x, y), color)
            self._cache[key] = glyph
        return self._cache[key]

    def draw(
        self,
        screen: Surface,
        text: str,
        topleft: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        """
        Draw the text one glyph image after the other from topleft
        """
        x, y = topleft
        for char in text:
            screen.blit(self._glyph(char, color), (x, y))
            x += self._glyph_box(char)[1]


def load_fonts(sizes: tuple[int, ...]) -> dict[int, BitmapFont]:
    """
    Load the sheet of each size listed in FONT_META
    """
    meta = json.loads(FONT_META.read_text(encoding="utf-8"))
    return {
        size: BitmapFont(
            pygame.image.load(FONT_DIR / f"pacman_{size}.png"),
            meta[str(size)]["height"],
            meta[str(size)]["image_height"],
            meta[str(size)]["glyphs"],
        )
        for size in sizes
    }
