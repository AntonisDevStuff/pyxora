from .assets import Assets

from typing import Tuple

import pygame

class Display:
    """Handles the main game display surface and rendering."""

    window = None
    """The main display window"""
    surface = None
    """The main display surface"""
    clock = None
    """The main display clock"""

    @classmethod
    def init(cls, title: str, resolution:Tuple[int, int], monitor=0, stretch=False,
             dynamic_zoom=False,fullscreen=False, resizable=False, vsync=False) -> None:
        """
        Initializes the main display window used by all scenes.

        Args:
            title (str): The title of the window.
            resolution (Tuple[int, int]): The resolution of the window (width, height).
            stretch (bool): Whether to stretch the internal surface to fit the screen. Defaults to False.
            dynamic_zoom (bool): Whether to dynamically zoom the internal surface. Defaults to False.
            fullscreen (bool): Start in fullscreen mode. Defaults to False.
            resizable (bool): Allows the window to be resizable. Defaults to False.
            vsync (bool): Enables vertical sync. Defaults to False.
        """
        cls._title = title
        cls._res = tuple(resolution)  # make sure it's tuple, no need to raise an error
        cls._width, cls._height = resolution

        cls._vsync = vsync
        cls._fullscreen = fullscreen
        cls._resizable = resizable

        cls._stretch = stretch
        cls._dynamic_zoom = dynamic_zoom

        cls._new_res = None
        cls._last_res = None
        cls._icon = None
        cls._index = monitor

        cls.clock = pygame.time.Clock()
        cls.surface = pygame.Surface(resolution)

        cls.set_title(title)

        cls.__set_mode()

    @classmethod
    def set_title(cls,title: str) -> None:
        """Class method to set the window title."""
        pygame.display.set_caption(title)

    @classmethod
    def set_icon(cls,icon: pygame.Surface) -> None:
        """Class method to set the window icon."""
        cls._icon = icon
        pygame.display.set_icon(icon)

    @classmethod
    def set_res(cls, res: Tuple[float, float]) -> None:
        """
        Set a new resolution (without re-sizing the window)
        If you want to re-size the window, use the `resize` method instead.

        Args:
            res (Tuple[float, float]): The new resolution.
        """
        cls._new_res = res

    @classmethod
    def get_res(cls) -> Tuple[float, float]:
        """
        Get the base resolution.

        Returns:
            Tuple[float, float]: The main (base) resolution of the window.
        """
        return cls._res

    @classmethod
    def get_center(cls) -> Tuple[float, float]:
        """
        Get the center point of the base resolution.

        Returns:
            Tuple[float, float]: The (x, y) center coordinates of the base resolution.
        """
        return (cls._res[0] / 2, cls._res[1] / 2)

    @classmethod
    def get_size(cls) -> Tuple[float, float]:
        """
        Get the possibly scaled resolution.

        If a new resolution is set, it returns that.
        Otherwise, it returns the base resolution.

        Returns:
            Tuple[float, float]: The size of the window.
        """
        return cls._res if not cls.is_resized() else cls._new_res

    @classmethod
    def is_resized(cls) -> bool:
        """
        Check if the display has been resized.

        Returns:
            bool: True if a new resolution has been set, otherwise False.
        """
        return bool(cls._new_res)

    @classmethod
    def is_fullscreen(cls) -> bool:
        """
        Check if the display has been resized.

        Returns:
            bool: True if a new resolution has been set, otherwise False.
        """
        return cls._fullscreen

    @classmethod
    def resize(cls, new_res) -> None:
        """
        Resize the display window.

        Args:
            new_res (tuple[int, int]): The new resolution.
        """
        cls.set_res(new_res)
        cls.__set_mode()

    @classmethod
    def get_stretch_surf(cls) -> pygame.Surface:
        """
        Get a stretched version of the internal surface to the new resolution.

        Returns:
            pygame.Surface: The scaled surface.
        """
        return pygame.transform.scale(cls.surface, cls._new_res)

    @classmethod
    def toggle_fullscreen(cls) -> None:
        """Toggle fullscreen mode on or off."""
        cls._fullscreen = not cls._fullscreen
        cls.set_icon(cls._icon)  # re-set icon for the new display mode
        # hack to keep the old resolution after toggling fullscreen
        if cls._fullscreen:
            cls._last_res = cls._new_res if cls._new_res is not None else cls._res
            cls._new_res = pygame.display.get_desktop_sizes()[cls._index]
        else:
            cls._new_res = cls._last_res
        cls.set_res(cls._new_res)
        # second hack to fix the toggle event problem
        pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE,w=cls._new_res[0], h=cls._new_res[1]))
        cls.__set_mode()

    @classmethod
    def draw_shape(cls, Shape, fill=0) -> None:
        """
        Draw a shape on the screen.

        Args:
            Shape: The shape object with a `.draw()` method.
            fill (int, optional): Fill mode or color. Defaults to 0.
        """

        # Just calls the abstracted shape.draw method, so we only need one method to draw any future shape :)
        Shape.draw(cls.surface, fill=fill, scale=1)

    @classmethod
    def draw_text(cls, Txt) -> None:
        """
        Draw text on the screen.

        Args:
            Txt: A text object with a `.draw()` method.
        """
        Txt.draw(cls.surface, scale=1)

    @classmethod
    def draw_image(cls, Image) -> None:
        """
        Draw an image on the screen.

        Args:
            Image: An image object with a `.draw()` method.
        """
        Image.draw(cls.surface, scale=1)

    @classmethod
    def draw_object(cls, Object: "Object") -> None:
        """
        Draw a object on the camera's surface if it is visible.

        Args:
            Object: The object
        """
        cls.draw_image(Object.image)

    # Note: I planned to use the new pygame.Window for more features,
    # but it caused issues with pybgag (web builds), so set_mode for now.
    @classmethod
    def __set_mode(cls) -> None:
        """Private method to set the display mode based on flags and resolution."""
        window_res = cls.get_size()
        vsync = int(cls._vsync)
        display = cls._index

        # apply the flags
        flags = 0

        if cls._fullscreen:
            flags |= pygame.FULLSCREEN
            flags |= pygame.HWSURFACE
            flags |= pygame.SCALED

        if cls._resizable and not cls._fullscreen:
            flags |= pygame.RESIZABLE

        cls.window = pygame.display.set_mode(window_res, flags=flags, vsync=vsync,display=display)
