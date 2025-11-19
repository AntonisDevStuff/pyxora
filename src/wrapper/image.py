from .functions import vector

from typing import Union,Tuple

import pygame

class Image:
    """The Image class that includes methods for drawing, moving, and scaling images on a Pygame surface."""
    def __init__(self,image: pygame.Surface,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3, shape_type:int = "rect",align: str = "topleft",custom_size=None) -> None:
        """Initializes an Image object with the given position, image, shape type, and custom size.

        Args:
            image (pygame.Surface): The image surface.
            pos (pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3): The position of the image.
            shape_type (int): The shape type of the image. Default = rect
            align (str): The alignment of the image. Default = topleft
            custom_size (tuple): The custom size of the image. Optional

        Note:
            Available Shape Types: rect,circle (more will be added in the future, along with shapes.py)
            Available Alignments: topleft, topright, midtop, midleft, center, midright, bottomleft, midbottom, bottomright
        """
        self._surface = image
        self._pos = vector(*pos)
        self._size = self.rect.size

        # custom_size = scale
        if custom_size:
            self._surface = pygame.transform.smoothscale(image, custom_size)

        if custom_size:
            self._size = custom_size

        self._scale = 1.0
        self._scale_surface = None

        shape_type == 2 and self.__apply_circular_mask()

        # change the position of the text based on the alignment
        self.__apply_alignment(align)

    @property
    def position(self) -> pygame.math.Vector2 | pygame.math.Vector3:
        """
        Get a copy of the position of the text.

        Returns:
            pygame.math.Vector2 or pygame.math.Vector3: The position of the text.
        """
        return self._pos.copy()

    @property
    def size(self) -> tuple:
        """
        Get a the size of the image.

        Returns:
            tuple: the image size
        """
        return tuple(self._size)

    @property
    def shape(self) -> str:
        """
        Get a the shape of the image.

        Returns:
            str: the image shape
        """
        return self._shape

    @property
    def value(self) -> pygame.Surface:
        """
        Get a copy of the surface image.

        Returns:
            pygame.Surface: the image copy surface
        """
        return self._surface.copy()

    @property
    def rect(self) -> pygame.Rect:
        """
        Returns the rectangle of the image.

        Returns:
            pygame.Rect: The rectangle of the image.
        """
        _rect = self._surface.get_rect()
        _rect.x = self._pos[0]
        _rect.y = self._pos[1]
        return _rect

    @property
    def memory(self) -> int:
        """
        Returns the memory size of the image in bytes.

        Returns:
            int: The memory size of the image surface.
        """
        bytes_per_pixel = self._surface.get_bytesize()
        width,height = self._surface.get_size()
        return width * height * bytes_per_pixel

    def move(self,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3) -> None:
        """
        Moves the image by the given offset.

        Args:
            pos (Tuple[int | float, int | float] | Vector2 | Vector3):
                The amount to move the image by, relative to its current position.
        """
        self._pos.x += pos[0]
        self._pos.y += pos[1]

    def move_at(self,pos: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3) -> None:
        """
        Moves the image to a position.

        Args:
            pos (Tuple[int | float, int | float] | Vector2 | Vector3):
                The new position for the image.
        """
        self._pos.x = pos[0]
        self._pos.y = pos[1]

    def draw(self,surf: pygame.Surface,scale: float) -> None:
        """
        Draws the image on the given surface.

        Args:
            surf (pygame.Surface):
                The surface to draw the image on.
            scale (float):
                The scale factor to apply to the image.
        """
        if scale == 1:
            surf.blit(self._surface, self._pos)
            return

        if not self._scale == scale:
            self._scale_surface = pygame.transform.smoothscale_by(self._surface, scale)
            self._scale = scale

        surf.blit(self._scale_surface, self._pos)

    def __apply_circular_mask(self) -> None:
        """Applies a circular alpha mask to the surface."""
        mask = pygame.Surface(self._size, pygame.SRCALPHA)
        radius = self._size[0] // 2
        center = (radius, radius)
        pygame.draw.circle(mask, (255, 255, 255), center, radius)
        self._surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def __apply_alignment(self, align: str):
        """
        Adjusts position based on alignment keywords.

        Supported alignments:
        'topleft', 'topright', 'midtop', 'midleft', 'center', 'midright',
        'bottomleft', 'midbottom', 'bottomright'
        """
        align = align.lower().strip()
        rect = self.rect

        # Horizontal adjustment
        if "left" in align:
            self._pos.x -= 0
        elif "center" in align or "mid" in align:
            self._pos.x -= rect.width / 2
        elif "right" in align:
            self._pos.x -= rect.width
        else:
            raise ValueError(f"Invalid horizontal alignment in: {align}")

        # Vertical adjustment
        if "top" in align:
            self._pos.y -= 0
        elif "center" in align or "mid" in align:
            self._pos.y -= rect.height / 2
        elif "bottom" in align:
            self._pos.y -= rect.height
        else:
            raise ValueError(f"Invalid vertical alignment in: {align}")
