class Script:
    """
    Base class for all object scripts in Pyxora.

    Scripts are small behaviour classes that run on an Object. Override any of
    the methods to implement behaviour. The engine will call these methods at
    the appropriate times, always passing the owning Object as the first
    argument.
    """

    def __init__(self) -> None:
        """
        @private
        Initialize the Script.
        """
        ...

    def _start(self, object: "Object") -> None:
        """
        @public
        Called once when the script becomes active on an object.

        Args:
            object (Object): The pyxora Object this script is running on.

        """
        ...

    def _update(self, object: "Object", dt: float) -> None:
        """
        @public
        Called every update step (frame / tick) while the object is active.

        Args:
            object (Object): The pyxora Object this script is running on.
            dt (float): Delta time since the last update, in seconds.
        """
        ...

    def _draw(self, object: "Object") -> None:
        """
        @public
        Called every render pass after the object has been drawn by the engine.

        Args:
            object (Object): The pyxora Object this script is running on.
        """
        ...

    def _on_kill(self, object: "Object") -> None:
        """
        @public
        Called when the object is destroyed or removed from the scene.

        Args:
            object (Object): The pyxora Object this script is running on.
        """
        ...

    def _on_collision(self, object: "Object", other: "Object") -> None:
        """
        @public
        Called every physics step while this object is colliding with another.
        """
        pass


    def _on_collision_enter(self, object: "Object", other: "Object") -> None:
        """
        @public
        Called once when a collision with another object begins.
        """
        pass

    def _on_collision_exit(self, object: "Object", other: "Object") -> None:
        """
        @public
        Called once when a collision with another object ends.
        """
        pass
