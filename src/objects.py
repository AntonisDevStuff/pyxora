from . import debug
from .scene import Scene
from .wrapper import Rect, Circle, vector, Image
from .assets import Assets
from .utils import engine

from inspect import stack as inspect_stack
from typing import Tuple, Iterator, Union, Optional, List, Any

import pygame
import pymunk

object_shapes = {
    1: "rect",
    2: "circle"
}
"""
Mapping of shape type indices to available shapes
"""

class PhysicsManager:
    """
    Manages the physics simulation of objects.

    Handles adding objects to the physics space, updating physics simulation steps,
    and configuring object shapes such as rectangles and circles.
    """
    def __init__(self) -> None:
        """
        Initializes a PhysicsManager
        """
        self.space: pymunk.Space = pymunk.Space()
        """The main space of the objects"""

    def add(self, Object: "Object") -> None:
        """
        Add an Object to the physics simulation.

        Args:
            Object (Object): The object to add to the physics space.
        """
        space = self.space
        physics = Object.physics
        static = Object.static
        shape_type = Object.shape_type
        if shape_type == 1:
            self.add_rect(Object, space, static, **physics)
        elif shape_type == 2:
            self.add_circle(Object, space, static, **physics)
        else:
            engine.error(RuntimeError("Unknown shape type"))

    def update(self, step: int) -> None:
        """
        Advance the physics simulation by a specified number of steps.

        Args:
            step (int): The amount of time steps to advance the simulation.
        """
        self.space.step(step)

    @staticmethod
    def add_rect(Object: "Object", space: pymunk.Space, static: bool, **rigidshape_kwargs) -> None:
        """
        Add a rectangular object to the physics space.

        Args:
            Object (Object): The object to add.
            static (bool): Whether the object is static (non-movable).
            space (pymunk.Space): The physics space to add the object to.
            **rigidshape_kwargs: Additional rigid shape properties to set on the pymunk shape.
        """
        body_type = pymunk.Body.STATIC if static else pymunk.Body.DYNAMIC
        rigidbody = pymunk.Body(body_type=body_type)
        rigidbody.position = (
            Object.spawn[0] + Object.size[0] / 2,
            Object.spawn[1] + Object.size[1] / 2
        )

        rigidshape = pymunk.Poly.create_box(rigidbody, Object.size)
        for key, value in rigidshape_kwargs.items():
            setattr(rigidshape, key, value)

        space.add(rigidbody, rigidshape)
        Object.rigidbody = rigidbody
        Object.rigidshape = rigidshape

    @staticmethod
    def add_circle(Object: "Object", space: pymunk.Space, static: bool, **rigidshape_kwargs) -> None:
        """
        Add a circular object to the physics space.

        Args:
            Object (Object): The object to add.
            static (bool): Whether the object is static (non-movable).
            space (pymunk.Space): The physics space to add the object to.
            **rigidshape_kwargs: Additional rigid shape properties to set on the pymunk shape.
        """
        body_type = pymunk.Body.STATIC if static else pymunk.Body.DYNAMIC
        rigidbody = pymunk.Body(body_type=body_type)
        rigidbody.position = Object.spawn

        rigidshape = pymunk.Circle(body=rigidbody, radius=Object.size)
        for key, value in rigidshape_kwargs.items():
            setattr(rigidshape, key, value)

        space.add(rigidbody, rigidshape)
        Object.rigidbody = rigidbody
        Object.rigidshape = rigidshape


class Objects:
    """
    Manages a collection of Object instances in a Scene.

    Responsible for adding/removing objects, updating physics and scripts,
    drawing objects, and toggling debug hitboxes.
    """
    show_hitbox = debug
    """Debug Feature"""

    def __init__(self, render: bool = None) -> None:
        """
        Initialize an Objects manager.

        Args:
            render (bool, optional): Renderer to use. Defaults to the Scene's camera if not provided.
        """
        self.Physics:PhysicsManager  = PhysicsManager()

        self.__data: List["Object"] = []
        self.__counter: int = 0

        scene = self.__get_scene()
        render = render if render is not None else scene.camera

        self.__scene = scene
        self.__render = render

    def __iter__(self) -> Iterator["Object"]:
        """Iterate over all managed objects."""
        return iter(self.__data)

    @property
    def total(self) -> int:
        """Get the total objects"""
        return self.__counter

    def add(self, Object: "Object") -> None:
        """
        Add an Object to the manager and physics simulation.

        Args:
            Object (Object): The object to add.
        """
        self.__counter += 1

        Object.id = self.__counter
        Object.Manager = self

        self.Physics.add(Object)
        self.__data.append(Object)

    def remove(self, Object) -> None:
        """
        Remove an object from the manager.

        Args:
            Object (Object): The object to remove.

        Returns:
            The removed object.
        """
        return self.__data.remove(Object)

    def pop(self, index: int) -> "Object":
        """
        Remove and return an object at a specified index.

        Args:
            index (int): Index of the object to remove.

        Returns:
            Object: The removed object.
        """
        return self.__data.pop(index)

    def clear(self) -> None:
        """Remove all objects and reset the physics manager."""
        self.Physics = PhysicsManager()

        self.__counter = 0
        self.__data.clear()

    def set_gravity(self, gravity: Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3) -> None:
        """
        Set the gravity for the physics simulation.

        Args:
            gravity (Tuple[int | float, int | float] | pygame.math.Vector2 | pygame.math.Vector3)): Gravity vector (x, y).
        """
        self.Physics.space.gravity = gravity

    def toggle_hitbox(self) -> None:
        """Toggle rendering of debug hitboxes."""
        self.show_hitbox = not self.show_hitbox

    def update(self) -> None:
        """Update physics and object scripts each frame."""
        dt = self.__scene.dt
        self.Physics.update(dt)
        for obj in self:
            obj.update()

    def draw(self) -> None:
        """Draw all visible objects and their hitboxes (if enabled)."""
        for obj in self:
            obj.draw(self.__render)


    @staticmethod
    def __get_scene() -> Scene:
        """
        Get the Scene instance from the call stack.

        Returns:
            Scene: The scene in which this Objects manager is created.

        Raises:
            RuntimeError: If called outside of a Scene.
        """

        # hack to get the scene without having it as arguemnt
        # we need the scene for dt and default renderer
        for frame_info in inspect_stack():
            local_self = frame_info.frame.f_locals.get('self')
            if isinstance(local_self, Scene):
                return local_self
        engine.error(RuntimeError("Objects can only be created inside a Scene"))


class Object:
    """
    Represents a single game object with optional physics and scripts.

    Supports rectangle or circle shapes, images, physics properties, and custom scripts.
    """

    def __init__(self, pos, size, image: Optional[Image]=None, shape_type: int=1) -> None:
        """
        Initialize a game object.

        Args:
            pos (tuple): The object position (x, y). The code will internally adjust it so objects are positioned in the center of the cords.
            size (tuple or int): Size of the object.
            image (Image, optional): Image to render. Defaults to engine icon.
            shape_type (int, optional): The object shape type
        """
        pos = (pos[0] - size, pos[1] - size) if shape_type == 2 else (pos[0] - size[0]/2, pos[1] - size[1]/2)
        img_size = (size*2, size*2) if shape_type == 2 else size
        if image:
            img = Image(image,pos,
                custom_size=img_size,
                shape_type=shape_type
            )
        else:
            img = Image(
                Assets.get("engine", "images", "icon"),
                pos,
                custom_size=img_size,
                shape_type=shape_type
            )

        self.Manager: Optional[Objects] = None
        self.id: Optional[int] = None

        self.__rigidbody: Optional[pymunk.Body] = None
        self.__rigidshape: Optional[pymunk.Shape] = None

        self.__image: Image = img
        self.__spawn = pos
        self.__size = size
        self.__shape_type = shape_type
        self.__invisible = False
        self.__scripts: List[Any] = []

        # Every object need to have phyiscs properties
        # add to init the default static values
        self.add_physics(static=True)


    @property
    def rigidbody(self) -> Optional[pymunk.Body]:
        """Get the object physics rigidbody."""
        return self.__rigidbody

    @rigidbody.setter
    def rigidbody(self, value: pymunk.Body) -> None:
        """Set the object physics rigidbody."""
        self.__rigidbody = value

    @property
    def rigidshape(self) -> Optional[pymunk.Shape]:
        """Get the object physics collision shape."""
        return self.__rigidshape

    @rigidshape.setter
    def rigidshape(self, value: pymunk.Shape) -> None:
        """Set the object physics collision shape."""
        self.__rigidshape = value

    @property
    def image(self) -> Image:
        """Get the object render image."""
        return self.__image

    @property
    def spawn(self) -> Tuple[float, float]:
        """Get the object starting position."""
        return self.__spawn

    @property
    def size(self) -> Union[Tuple[int, int], int]:
        """Get the object size."""
        return self.__size

    @property
    def shape(self) -> str:
        """Get the object shape."""
        return object_shapes[self.__shape_type]

    @property
    def shape_type(self) -> int:
        """Get the object shape type."""
        return self.__shape_type

    @property
    def invisible(self) -> bool:
        """Get whether the object is invisible."""
        return self.__invisible

    @property
    def scripts(self) -> List[Any]:
        """Get the list of scripts attached to the object."""
        return self.__scripts

    @property
    def hitbox(self) -> Union[Rect, Circle]:
        """Return a visual representation of the object's hitbox."""
        if self.shape_type == 1:
            return Rect(self.position, self.size, "red")

        elif self.shape_type ==2:
            return Circle(self.position, self.size, "red")

        else:
            engine.error(RuntimeError("Unknown shape type"))

    @property
    def position(self) -> pygame.math.Vector2:
        """Return the object position."""
        pos = vector(self.rigidbody.position[0], self.rigidbody.position[1])
        if self.shape_type == 1:
            pos.x -= self.size[0]/2
            pos.y -= self.size[1]/2
        return pos

    def move(self, new_pos: Tuple[float, float]) -> None:
        """
        Move the object relative to its current position.

        Args:
            new_pos (tuple): Delta position (dx, dy) to move.
        """
        pos = self.rigidbody.position
        self.move_at((pos[0] + new_pos[0], pos[1] + new_pos[1]))

    def move_at(self, new_pos: Tuple[float, float]) -> None:
        """
        Move the object to an absolute position.

        Args:
            new_pos (tuple): Absolute position (x, y).
        """
        self.rigidbody.position = new_pos
        self.Manager.Physics.space.reindex_shapes_for_body(self.rigidbody)
        self.static and self.Manager.Physics.space.reindex_static()

    def add_physics(self, mass: float=1, friction: float=0, elasticity: float=0, static: bool=False) -> None:
        """
        Add the physics properties for the object
        Note: This properties can't change after the Object is added in Objects.

        Args:
            mass (float, optional): Mass of the object. Defaults to 1.
            friction (float, optional): Friction coefficient. Defaults to 0.
            elasticity (float, optional): Elasticity coefficient. Defaults to 0.
            static (bool, optional): Whether the object is static. Defaults to False.
        """
        shape_type = self.__shape_type
        self.physics = {
            "mass": mass,
            "friction": friction,
            "elasticity": elasticity,
            "collision_type": shape_type,
        }
        self.static = static

    def update(self) -> None:
        """
        @private
        Update the object image position.
        """
        if self.image:
            self.image.move_at(self.rigidbody.position)
            if self.shape_type == 1:
                self.image.move((-self.size[0]/2, -self.size[1]/2))
            elif self.shape_type == 2:
                self.image.move((-self.size, -self.size))

    def draw(self,render):
        """
        @private
        Draw the Object
        """
        if self.invisible:
            return
        render.draw_image(self.__image)
        Objects.show_hitbox and render.draw_shape(self.hitbox, 1)
