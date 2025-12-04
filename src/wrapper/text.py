from .functions import vector
from ..assets import Assets
from ..utils import engine

from typing import Union,Tuple
from collections import OrderedDict

import pygame

text_sizes = {
    1, 2, 4, 8, 10, 12,
    14, 16, 18, 24, 32,
    48, 64, 72, 96, 128,
    144, 192, 256
}
"""The available text sizes"""

class Text:
    """
    A class for rendering text

    Supports caching of fonts and rendered surfaces for performance,
    alignment options, scaling (zoom), and limiting cache size.
    """

    surfaces: dict = OrderedDict()
    """The surfaces cache"""
    _cache_limit = 10000  # default surface cache limit is 10000

    def __init__(self,text: str,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3,color: str | tuple, font_name: str = pygame.font.get_default_font().split(".")[0],size: int = 24,align: str = "left") -> None:
        """
        Initialize a Text object.

        Args:
            pos (pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3): The position of the text.
            text (str): The string to render.
            color (str or tuple): The color of the text.
            font_name (str): The text font name.
            size (int): Font size.
            align (str): Alignment of the text: "left", "center", or "right".
        """
        size = self.__fix_size(size)
        font = self.__get_font(font_name,size)

        self._text = text
        self._pos = vector(*pos)
        self._color = color
        self._font_name = font_name

        self._font = font
        self._size = size

        self._zoom = 1
        self._zoom_surface = None  # cache the zoom_surface for performance

        # Initialize the surface cache
        self._cache_surface() if (font,text) not in self.surfaces else setattr(self,"_surface",self.surfaces[(font,text)])

        # change the position of the text based on the alignment
        self._align_pos(align)

    @classmethod
    def set_cache(cls,new_limit: int) -> None:
        """
        Set the maximum number of cached surfaces.
        Note: Default is 10000, but can be increased or decreased as needed.

        Args:
            new_limit (int): New cache size limit.
        """
        cls._cache_limit = new_limit

    @classmethod
    def get_cache(cls) -> int:
        """
        Get the number of cached surfaces.

        Returns:
            int: The number of cached surfaces.
        """
        return len(cls.surfaces)

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear all cached text surfaces.
        """
        cls.surfaces.clear()

    @classmethod
    def font_size_for(cls,text: str, size: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3, font_name: str) -> int:
        """
        Calculates the largest font size that fits the text inside a given area.

        Args:
            text (str): Text to render.
            size (size: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3): The size of the text.
            font_name (str): Name of the cache font.

        Returns:
            int: Maximum font size that fits.
        """
        width,height = size[0],size[1]
        font_type = "sys" if font_name.lower() in pygame.font.get_fonts() else "local"
        for font_size in text_sizes:
            font = cls.__get_font(font_name, font_size)
            text_surface = font.render(text, True, (0, 0, 0))
            text_width, text_height = text_surface.get_size()

            if text_width > width or text_height > height:
                return font_size - 1

        return font_size

    @property
    def position(self) -> pygame.math.Vector2 | pygame.math.Vector3:
        """
        Get a copy of the position of the text.

        Returns:
            pygame.math.Vector2 or pygame.math.Vector3: The position of the text.
        """
        return self._pos.copy()

    @property
    def value(self) -> str:
        """
        Get the value of the text.

        Returns:
            str: The value of the text.
        """
        return self._text

    @property
    def color(self) -> str | tuple:
        """
        Get the color of the text.

        Returns:
            (str or tuple): The color of the text.
        """
        return self._color

    @property
    def font(self) -> str:
        """
        Get the color of the text.

        Returns:
            (str): The font name
        """
        return self._font_name

    @property
    def font_size(self) -> int:
        """
        Get the size of the text font.

        Returns:
            int: The size of the text font.
        """
        return self._size

    @property
    def size(self) -> int:
        """
        Get the surface size of the text font.

        Returns:
            int: The size of the text font.
        """
        return self._surface.get_size()

    @property
    def rect(self) -> pygame.Rect:
        """
        Get the rectangle bounds of the text surface.

        Returns:
            pygame.Rect: The rectangle with position applied.
        """
        _rect = self._surface.get_rect()
        _rect.x = self._pos[0]
        _rect.y = self._pos[1]
        return _rect

    @property
    def memory(self) -> int:
        """
        Returns the memory size of the text in bytes.

        Returns:
            int: The memory size of the text surface.
        """
        bytes_per_pixel = self._surface.get_bytesize()
        width,height = self._surface.get_size()
        return width * height * bytes_per_pixel

    def move(self,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3) -> None:
        """
        Moves the text by the given offset.

        Args:
            pos (Tuple[int | float, int | float] | Vector2 | Vector3):
                The amount to move the text by, relative to its current position.
        """
        self._pos.x += pos[0]
        self._pos.y += pos[1]

    def move_at(self,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3) -> None:
        """
        Moves the text to a position.

        Args:
            pos (Tuple[int | float, int | float] | Vector2 | Vector3):
                The new position for the text.
        """
        self._pos.x = pos[0]
        self._pos.y = pos[1]

    def draw(self,surf: pygame.Surface,scale: float) -> None:
        """
        Draws the text on the given surface.

        Args:
            surf (pygame.Surface):
                The surface to draw the text on.
            scale (float):
                The scale factor to apply to the text.
        """
        zoom = scale
        if zoom == 1:
            surf.blit(self._surface, self._pos)
            return
        if not self._zoom == zoom:
            self._zoom_surface = pygame.transform.scale_by(self._surface, zoom)
            self._zoom = zoom
        surf.blit(self._zoom_surface, self._pos)

    def _cache_surface(self) -> None:
        """
        Caches the rendered text surface for future use.

        This method ensures that the text surface is only rendered once and stored in a cache.
        If the cache limit is reached, the oldest cached surface is removed to make room for the new one.
        """
        self._surface = self._font.render(self._text, False, self._color)

        if len(self.surfaces) >= self._cache_limit:
            self.surfaces and self.surfaces.popitem(last=True)

        self.surfaces[(self._font,self._text)] = self._surface

    def _align_pos(self,align: str) -> None:
        """
        Adjust the text position based on the specified alignment.

        Args:
            align (str): "left", "center", or "right".
        """
        # the text is left aligned by default
        if align == "left":
            return

        rect = self.rect
        if align == "center":
            self._pos.x -= rect.width / 2
            self._pos.y -= rect.height / 2
        elif align == "right":
            self._pos.x += rect.width / 2
        else:
            raise ValueError(f"Invalid alignment: {align}")

    @staticmethod
    def __get_font(font_name: str, size: int) -> pygame.font.Font:
        """
        Retrieves the font from the assets.

        Args:
            font_name (str): The name of the font.

        Returns:
            pygame.font.Font: The font object.
        """
        font = Assets.get("engine","fonts",font_name) or Assets.get("data","fonts",font_name)
        if not font:
            raise ValueError(f"Font '{font_name}' not found.")
        return font.get(size)

    @staticmethod
    def __fix_size(size: int) -> int:
        """
        Returns the closest supported font size from the default set.

        Args:
            size (int): The requested font size.

        Returns:
            int: The closest allowed font size.
        """
        closest = min(text_sizes, key=lambda s: abs(s - size))

        if closest != size:
            engine.warning(f"Font size {size} not available. Using closest: {closest}")
            return closest
        return size
