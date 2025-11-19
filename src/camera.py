from .display import Display
from .wrapper.functions import vector
from .wrapper import Text,Image,Shape

from math import log2
from typing import Tuple

import pygame

class Camera:
    """
    Camera class for the pyxora display environment.
    Handles position, zoom, and rendering of shapes, text, and images with camera-relative coordinates.

    Note: Every Scene has a camera instance by default. You can create multiple instances but it's not recommended.
    """

    def __init__(self) -> None:
        """Initialize the camera position, offset, zoom, and set initial zoom."""
        self._pos = vector(0, 0)
        self._offset = vector(0, 0)
        self._zoom_scale = 1
        self._zoom_factor = 0
        self._zoom_direction = 0
        self.__max_zoom_factor = 3
        self.zoom(1)

    @property
    def surface(self) -> pygame.Surface:
        """Property to the current drawing surface."""
        return Display.surface

    @property
    def position(self) -> pygame.math.Vector2:
        """Property to get a copy of the position of the camera."""
        return self._pos.copy()

    @property
    def rect(self) -> pygame.Rect:
        """Property to get the camera's rectangle area as a pygame.Rect."""
        rect = pygame.Rect(self._pos + self._offset, Display._res)
        rect.width = int(rect.width / self.zoom_scale)
        rect.height = int(rect.height / self.zoom_scale)
        return rect

    @property
    def zoom_scale(self) -> float:
        """Property to get the current zoom scale factor"""
        return self._zoom_scale

    @property
    def zoom_factor(self) -> float:
        """Property to get the current log2 zoom factor"""
        return self._zoom_factor

    @property
    def zoom_direction(self) -> float:
        """Property to get the current zoom direction."""
        return self._zoom_direction

    @property
    def zoom_level(self) -> float:
        """Property to get the current zoom level."""
        if self.zoom_direction == 0 and self.zoom_factor == 0:
            return 1
        elif self.zoom_factor == 0:
            return 1
        elif self.zoom_factor >= 1:
            return self.zoom_factor + 1
        else:
            return self.zoom_factor - 1

    def set_max_zoom(self, factor: float) -> None:
        """
        Set the maximum zoom factor for the camera.

        Args:
            factor: The maximum zoom factor to set.
        """
        self.__max_zoom_factor = factor

    def get_max_zoom(self) -> float:
        """
        Get the maximum zoom factor for the camera.

        Returns:
            The maximum zoom factor.
        """
        return self.__max_zoom_factor

    def is_visible(self, obj) -> bool:
        """
        Check if an object is at least partially visible on the screen (Requires object to have a rect attribute).

        Args:
            obj: The object to check visibility for.

        Returns:
            True if the object is visible, False otherwise.
        """
        return self.rect.colliderect(obj.rect)

    def move(self, offset: Tuple[int | float, int | float] | pygame.math.Vector2) -> None:
        """
        Move the camera by a given offset (tuple or vector).

        Args:
            offset: The offset to move the camera by.
        """
        self._pos.x += offset[0]
        self._pos.y += offset[1]

    def move_at(self, new_pos: Tuple[int | float, int | float] | pygame.math.Vector2) -> None:
        """
        Move the camera to a specific position (centered).

        Args:
            new_pos: The new position to move the camera to.
        """
        self._pos.x = new_pos[0] + Display._res[0] / 2
        self._pos.y = new_pos[1] + Display._res[1] / 2

    def zoom(self, factor: int) -> None:
        """
        Zoom the camera by a given step, adjusting its scale.

        Args:
            factor: The zoom factor to apply.
        """
        if factor == 0:
            return
        factor = (factor + 1) if factor < 0 else (factor - 1)
        scale = 2 ** (self.zoom_factor + factor)
        self.zoom_at(scale)

    def zoom_at(self, scale: float) -> None:
        """
        Set the camera zoom to a specific scale, centering the view.

        Args:
            scale: The scale to set the camera zoom to.
        """
        if not scale:
            return
        min_scale = 2 ** -self.__max_zoom_factor
        max_scale = 2 ** self.__max_zoom_factor
        scale = max(min_scale, min(max_scale, scale))
        factor = log2(scale)
        direction = factor - self._zoom_factor

        # Center the camera based on the new zoom scale
        sign = 1 if scale < 0 else -1
        self._offset.x = 1 / scale * Display._res[0] / 2 * sign + Display._res[0] / 2
        self._offset.y = 1 / scale * Display._res[1] / 2 * sign + Display._res[1] / 2

        self._zoom_scale = scale
        self._zoom_factor = factor
        self._zoom_direction = direction

    def draw_shape(self, Shape: Shape, fill: int = 0) -> None:
        """Draw a shape on the camera's surface if it is visible."""
        if not self.is_visible(Shape):
            return

        Shape._pos -= self._pos + self._offset
        Shape._pos *= self._zoom_scale
        Shape.draw(self.surface, fill, self._zoom_scale)
        Shape._pos /= self._zoom_scale
        Shape._pos += self._offset + self._pos

    def draw_text(self, Txt: Text) -> None:
        """Draw text on the camera's surface if it is visible."""
        if not self.is_visible(Txt):
            return

        Txt._pos -= self._pos + self._offset
        Txt._pos *= self._zoom_scale
        Txt.draw(self.surface, self._zoom_scale)
        Txt._pos /= self._zoom_scale
        Txt._pos += self._offset + self._pos

    def draw_image(self, Image: Image) -> None:
        """Draw an image on the camera's surface if it is visible."""
        if not self.is_visible(Image):
            return
        Image._pos -= self._pos + self._offset
        Image._pos *= self._zoom_scale
        Image.draw(self.surface, self._zoom_scale)
        Image._pos /= self._zoom_scale
        Image._pos += self._offset + self._pos

    def draw_object(self, Object: "Object") -> None:
        """Draw a object on the camera's surface if it is visible."""
        self.draw_image(Object.image)

    def _dynamic_zoom(self) -> None:
        """Dynamically adjust the zoom based on the display's resolution."""
        scale = min((Display._res[0] / Display._new_res[0]),(Display._res[1] / Display._new_res[1]))
        self.zoom_at(scale)
