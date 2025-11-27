from .display import Display
from .assets import Assets
from .camera import Camera as SceneCamera
from .utils import engine,asyncio

from time import perf_counter as time
from typing import Dict,Tuple,Any,Type

import pygame

class classproperty(property):
    """@private class to create @classproperties"""
    def __get__(self, obj, cls):
        return self.fget(cls)

class SceneManager:
    """The Main Manager of the Scenes."""
    scenes: Dict[str, Tuple[str, "Scene", Any]] = {}
    """A mapping of scene keys to (name, Scene object, additional data) tuples."""

    selected: str
    """The currently selected scene"""

    @classproperty
    def scene(cls) -> Tuple[str, "Scene", Any]:
        """Class Property to get the active scene."""
        return cls.scenes.get(cls.selected,(None,None,None))

    # --- Scene Control ---
    @classmethod
    async def start(cls) -> None:
        """
        Start the main game loop.
        """
        engine.print_versions()
        while True:
            scene = cls.scene
            if not scene:
                engine.error(Exception("No scene selected"))
                engine.quit()
            scene_object = scene[1]
            await scene_object._Scene__run()

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> None:
        """
        Create a new scene instance.

        Args:
            scene_class (str): The class of the scene.
            kwargs: Additional arguments passed to the scene's constructor.
        """
        scene = Assets.get("data","scenes",name)
        if not scene:
            engine.error(RuntimeError(f"Scene: {name}, not found in data/scenes folder"))
            engine.quit()
        cls.scene = (name, scene(**kwargs), kwargs)
        cls.selected = name

    @classmethod
    def change(cls, name: str, **kwargs) -> None:
        """
        Exit and change to a different scene.

        Args:
            name (str): The name of the scene to switch to.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_change()
        scene_obj._Scene__running = False
        cls.create(name,**kwargs)

    @classmethod
    def pause(cls) -> None:
        """
        Pause the current scene.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_pause()
        scene_obj._Scene__paused = True
        scene_obj._Scene__pause_last_time = time()

    @classmethod
    def resume(cls) -> None:
        """Resumes the current scene."""
        scene_obj = cls.scene[1]
        scene_obj._on_resume()
        scene_obj._Scene__paused = False
        scene_obj._Scene__dt = 0

    @classmethod
    def restart(cls) -> None:
        """
        Restart the current scene.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_restart()
        scene_obj._Scene__running = False

    @classmethod
    def reset(cls) -> None:
        """
        Reset the current scene.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_reset()
        scene_obj._Scene__running = False

        # manual create a new scene
        name, obj, kwargs = cls.scene
        cls.create(name,**kwargs)

    @classmethod
    def exit(cls) -> None:
        """
        Exit the application through the current scene.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_exit()
        scene_obj._Scene__running = False
        cls.selected = None

    @classmethod
    def quit(cls) -> None:
        """
        Quit the application through the current scene.
        """
        scene_obj = cls.scene[1]
        scene_obj._on_quit()
        engine.quit()

class SceneEvent:
    """
    A helper class to create custom events for the Scenes.
    """
    def __init__(self,scene: "Scene") -> None:
        """
        @private
        (Not include in the docs as it should be call only inside scene itself)
        Updates all the custom events and it's properties at the scene state.

        Initializes a Scene Event.

        Args:
            scene (SceneManager): The reference to the current Scene.
        """
        self.__data = {}
        self.__scene = scene

    def create(self,name: str,state: int = 0,**kwargs: Any) -> int:
        """
        Create and store a new custom event.

        Args:
            name (str): The name of the event.
            state (int): The event state, where:
                - 1: Runtime
                - -1: Pause time
                - 0: Both (default = 0)
            **kwargs: Additional arguments passed to the event's info. Can be any extra data needed for the event.

        Returns:
            int: The ID of the new event.
        """
        event_id = pygame.event.custom_type()
        create_time = self._now(state)
        last_time = create_time
        basic_argv = {
            "name":name,"custom":True,
            "create_time":create_time,"calls":0,
            "last_time":last_time,"timer":None,
            "loops":None,"state":state
        }

        kwargs.update(basic_argv)
        event = pygame.event.Event(
            event_id,
            kwargs
        )

        self.__data[name] = event
        return event_id

    def get(self,name: str) -> pygame.event.Event:
        """
        Get a custom event by its name.

        Args:
            name (str): The name of the event.

        Returns:
            pygame.event.Event or None: The event with the specified name, or None if not found.
        """
        return self.__data.get(name,None)

    def remove(self,name: str) -> "SceneEvent":
        """
        Remove a custom event by its name.

        Args:
            name (str): The name of the event.

        Returns:
            SceneEvent: The event that was removed
        """
        return self.__data.pop(name)

    def post(self,name: str) -> bool:
        """
        Post a custom event by its name.

        Args:
            name (str): The name of the event.

        Returns:
            bool: returns a boolean on whether the event was posted or not
        """
        event = self.get(name)
        return pygame.event.post(event)

    def match(self,name: str,other_event: "SceneEvent") -> bool:
        """
        Check if a custom event matches by its name.

        Args:
            name (str): The name of the event.
            other_event (SceneEvent): The event to compare against.

        Returns:
            bool: True if the events match, False otherwise.
        """
        event = self.get(name)
        return event.type == other_event.type

    # Handling events manually seems more flexible and easier for this use case.
    def schedule(self,name: str,timer: int,loops: int = -1) -> None:
        """
        Shedule a custom event by it's name, for ms timer and loop times.

        Args:
            name (str): The name of the event.
            timer (int): The time of the shedule in ms.
            loops (int): The amount of loop times (default = -1, forever).
        """
        event = self.get(name)
        event.timer = timer
        event.loops = loops

    # Update all the scene events and it properties
    def update(self,state: int):
        """
        @private

        (Not include in the doc as it should be call only inside scene itself)
        Updates all the custom events and it's properties at the scene state.

        Args:
            state (int): The scene state. (default = -1, forever).
        """
        for event_name in self.__data:
            event = self.get(event_name)

            if not (self._is_state(state,event.state)):
                continue

            if not event.timer:
                continue

            if event.calls == event.loops:
                continue

            self._update_time(event)

    def _now(self, state: int) -> float:
        """Returns the current time based on the state.

        Args:
            state (int): Determines which time value to return.
                - If 0: Returns runtime + pausetime.
                - If >0: Returns runtime.
                - If <0: Returns pausetime.

        Returns:
            float: The calculated current time value.
        """
        runtime = self.__scene.runtime
        pausetime = self.__scene.pausetime
        if state == 0:
            return runtime + pausetime

        now = runtime if state > 0 else pausetime
        return now

    def _update_time(self, event:pygame.event.Event) -> None:
        """Checks if an event should be triggered based on elapsed time.

        If the time since the last event trigger exceeds the timer threshold,
        the event is posted and its last_time is updated.

        Args:
            event (object): An object with the following attributes:
                - state (int): State used to determine which time value to use.
                - last_time (float): Timestamp of the last event trigger.
                - timer (float): Timer threshold in milliseconds.
                - name (str): Name of the event to post.

        Side Effects:
            Posts the event via self.post() if the condition is met.
            Updates event.last_time.
        """
        now = self._now(event.state)
        diff = (now - event.last_time) * 1000
        is_time = diff >= event.timer
        if not is_time:
            return

        self.post(event.name)
        event.last_time = now
        event.calls += 1

    @staticmethod
    def _is_state(state: int, event_state: int) -> bool:
        """Checks if the event state matches the given state or is neutral (0).

        Args:
            state (int): Target state to compare against.
            event_state (int): Current state of the event.

        Returns:
            bool: True if the event_state equals the state or is 0, False otherwise.
        """
        same = event_state == state
        is_zero = event_state == 0
        return (same or is_zero)

class Scene:
    """Represents a scene in the game."""
    _global_runtime = _global_pausetime = 0
    __global_start_time = time()

    def __init__(self,**kwargs: Any) -> None:
        """
        Initializes a Scene object.

        Args:
            **kwargs: Additional arguments passed to the scene. Can be any extra data needed for the scene.

        Raises:
            RuntimeError: If the Display has not been initialized. Call Display.init() first.
        """
        if not self.display.window:
            engine.error(RuntimeError("Display has not been initialized! Call Display.init first."))
            self.quit()

        self.__initialize(kwargs)

    @classproperty
    def manager(cls) -> Type[SceneManager]:
        """Class Property to get the scene manager class"""
        return SceneManager

    @classproperty
    def display(cls) -> Type[Display]:
        """Class Property to get a direct reference to the engine Display class."""
        return Display

    @classproperty
    def assets(cls) -> Type[Assets]:
        """Class Property to get a direct reference to the engine Assets class."""
        return Assets

    @classproperty
    def global_runtime(cls) -> float:
        """Class Property to get the total run time across all scenes."""
        return cls._global_runtime

    @classproperty
    def global_pausetime(cls) -> float:
        """Class Property to get the total pause time across all scenes."""
        return cls._global_pausetime

    @property
    def camera(self) -> SceneCamera:
        """Property to get the event camera instance of the current scene."""
        return self._camera

    @property
    def event(self) -> SceneEvent:
        """Property to get the event handler instance of the current scene."""
        return self._event

    @property
    def events(self) -> set:
        """Property to get all the events of the current frame."""
        return self._events

    @property
    def custom_events(self) -> set:
        """Property to get all the custom events of the current frame."""
        return self._custom_events

    @property
    def keys_pressed(self) -> set:
        """Property to get the keys currently pressed of the current frame."""
        return self._keys_pressed

    @property
    def dt(self) -> float:
        """Property to get the time elapsed since the last frame."""
        return self._dt

    @property
    def fps(self) -> float:
        """Property to get the current frames per second."""
        return self._fps

    @property
    def max_fps(self) -> int:
        """Property to get the maximum frames per second limit."""
        return self._max_fps

    @max_fps.setter
    def max_fps(self, value: int):
        """Setter to set the maximum frames per second limit."""
        self._max_fps = value

    @property
    def background_color(self) -> str | Tuple[int, int, int]:
        """Property to get the background color"""
        return self._background_color

    @background_color.setter
    def background_color(self, value: str | Tuple[int, int, int]):
        """Setter to set the background color"""
        self._background_color = value

    @property
    def runtime(self) -> float:
        """Property to get the run time"""
        return self._runtime

    @property
    def pausetime(self) -> float:
        """Property to get the pause time"""
        return self._pausetime

    # Utils
    def is_time(self,ms):
        """Checks if a specified time interval has elapsed since the last frame."""
        multiplier = 1/ms*1000
        return int(self._runtime * multiplier) != int((self._runtime - self._dt) * multiplier)

    def is_event(self,event_id):
        """Checks if an event is happening during the frame. """
        return event_id in self._events

    def is_custom_event(self,event_name):
        """Checks if a custom event is happening during the frame. """
        return event_name in self._custom_events

    def is_paused(self):
        """Returns if the scene is paused."""
        return self.__paused

    # Lifecycle Methods
    def _start(self) -> None:
        """
        @public
        Called once at the start of the scene. You must Override this func in your subclass.

        Raises:
            NotImplementedError: If not overridden.
        """
        raise NotImplementedError("start() must be overridden in subclass.")

    def _update(self) -> None:
        """
        @public
        Called every frame to update scene logic. You must Override this func in your subclass.

        Raises:
            NotImplementedError: If not overridden.
        """
        raise NotImplementedError("update() must be overridden in subclass.")

    def _draw(self) -> None:
        """
        @public
        Called every frame to draw elements to the screen. You must Override this func in your subclass.

        Raises:
            NotImplementedError: If not overridden.
        """
        raise NotImplementedError("draw() must be overridden in subclass.")

    # Paused Lifecycle Methods
    def _paused_update(self) -> None:
        """@public Called every paused frame to update scene logic. Override this func in your subclass."""
        pass

    def _paused_draw(self) -> None:
        """@public Called every paused frame to draw elements to the screen. Override this func in your subclass."""
        pass

    # Scene State Change Methods
    def _on_create(self) -> None:
        """@public Called once at the scene creation "manager.create()". Override this func in your subclass to add code."""
        pass

    def _on_exit(self) -> None:
        """@public Called once at every scene exit "manager.exit()". Override this func in your subclass to add code."""
        pass

    def _on_quit(self) -> None:
        """@public Called once at every scene quit "manager.quit()". Override this func in your subclass to add code."""
        pass

    def _on_restart(self) -> None:
        """@public Called once at every scene restart "manager.restart()". Override this func in your subclass to add code."""
        pass

    def _on_reset(self) -> None:
        """@public Called once at the scene reset "manager.reset()". Override this func in your subclass to add code."""
        pass

    def _on_change(self) -> None:
        """@public Called once at the scene change "manager.change()". Override this func in your subclass to add code."""
        pass

    def _on_resume(self) -> None:
        """@public Called once at the scene resume "manager.resume()". Override this func in your subclass to add code."""
        pass

    def _on_pause(self) -> None:
        """@public Called once at the scene pause "manager.pause()". Override this func in your subclass to add code."""
        pass

    def _on_error(self,error: BaseException) -> None:
        """
        @public
        Called once at engine error "Scene.__handle_error()". Override this func in your subclass to add code.

        Args:
            error (BaseException): The engine error that occurred.
        """
        pass

    # Scene Event/Input Methods
    def _on_event(self, event: pygame.Event) -> None:
        """
        @public
        Called every pygame event. Override this func in your subclass to add code.

        Args:
            event (pygame.Event): The pygame event that occurred.
        """
        pass

    def _on_keydown(self,key: str) -> None:
        """
        @public
        Called every keyboard keydown. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """
        pass

    def _on_keyup(self,key: str) -> None:
        """
        @public
        Called every keyboard keyup. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """
        pass

    def _on_keypressed(self,key: str) -> None:
        """
        @public
        Called every keypressed. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """
        pass

    def _on_mousewheel(self,wheel: int) -> None:
        """
        @public
        Called every mousewheel change. Override this func in your subclass to add code.

        Args:
            wheel (int): The wheel position, wheel>0 = up, wheel<1 = down.
        """
        pass

    # Paused Event/Input Methods
    def _on_paused_event(self, event: pygame.event.Event) -> None:
        """
        @public
        Called every paused pygame event. Override this func in your subclass to add code.

        Args:
            event (pygame.Event): The pygame event that occurred.
        """
        pass

    def _on_paused_keydown(self,key: str) -> None:
        """
        @public
        Called every paused keyboard keydown. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """

    def _on_paused_keyup(self,key: str) -> None:
        """
        @public
        Called every paused keyboard keypressed. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """
        pass

    def _on_paused_keypressed(self,key: str) -> None:
        """
        @public
        Called every paused keypressed. Override this func in your subclass to add code.

        Args:
            key (str): The keyboard key.
        """
        pass

    def _on_paused_mousewheel(self,wheel: int) -> None:
        """
        @public
        Called every paused mousewheel change. Override this func in your subclass to add code.

        Args:
            wheel (int): The wheel position, wheel>0 = up, wheel<1 = down.
        """
        pass

    # Main Loop
    # Async to support pygbag export
    async def __run(self) -> None:
        """
        Starts the scene.

        Raises:
            Exception: If there is any error in the scene.
        """
        try:
            self.__initialize_runtime()
            self._start()
            while self.__running:
                self.__handle_events()
                self.__update()
                self.__render()
                self.__flip()

                await asyncio.sleep(0)
            if not self.manager.selected:
                engine.quit()
        except Exception as e:
            self.__handle_error(e)

    # All the methods below are used to handle the scene frames.
    def __initialize(self,kwargs):
        try:
            self._max_fps = 60
            self._background_color = (0, 0, 0)

            self.__running = True
            self.__paused = False

            # set it here because the assets are loaded after the scene is initialized
            Display.set_icon(
                Assets.get("engine","images","icon")
            )

            self.__event_handlers = {
                True: (self._on_paused_keydown, self._on_paused_keyup, self._on_paused_keypressed, self._on_paused_mousewheel, self._on_paused_event),
                False: (self._on_keydown, self._on_keyup, self._on_keypressed, self._on_mousewheel, self._on_event)
            }

            # set manual the scene kwargs to the scene
            for k, v in kwargs.items():
                setattr(self, k, v)
            self._on_create()
        except Exception as e:
            # expect on_create error as is not in the main loop
            self.__handle_error(e)

    def __initialize_runtime(self):
        """Sets up initial basic runtime values."""
        self._dt = self._fps = self._runtime = self._pausetime = 0
        self._keys_pressed = set()  # we manually keep track with the key_pressed every frame, set so no duplicates
        self._events = set()  # log events every frame
        self._custom_events = set()  # log custom events every frame

        # Create custom Scene events
        self._event = SceneEvent(self)
        self._camera = SceneCamera()

        self._start_time = time()
        self.__running = True

    def __handle_error(self,error):
        """ Handles every possible error with a nice message."""
        if error:
            self._on_error(error)
            engine.error(error)
        engine.quit()

    def __handle_events(self):
        """Handles events during runtime or when paused."""
        self._events.clear()
        self._custom_events.clear()
        self._event.update(-1 if self.__paused else 1)
        on_keydown, on_keyup, on_keypressed, on_wheel, on_event = self.__event_handlers[self.__paused]
        for event in pygame.event.get():
            self._events.add(event.type)

            if hasattr(event, "custom"):
                self._custom_events.add(event.name)
                continue

            if event.type == pygame.QUIT:
                self.manager.quit()

            elif event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                self._keys_pressed.add(key)
                on_keydown(key)

            elif event.type == pygame.KEYUP:
                key = pygame.key.name(event.key)
                self._keys_pressed.discard(key)
                on_keyup(key)

            elif event.type == pygame.MOUSEWHEEL:
                wheel = "up" if event.y >= 1 else "down"
                on_wheel(wheel)

            elif event.type == pygame.VIDEORESIZE:
                Display.set_res((event.w, event.h))
                Display._dynamic_zoom and self.camera._dynamic_zoom()
            on_event(event)

        if self._keys_pressed:
            on_keypressed(self._keys_pressed)

    def __update(self):
        """Update the scene and timers, depending on whether it's paused or active."""
        update = self._paused_update if self.__paused else self._update
        update_timers = self.__update_paused_timers if self.__paused else self.__update_timers
        update()
        update_timers()

    def __update_timers(self):
        """Updates global and local runtime timers."""
        delta = time() - self._start_time
        global_delta = time() - self.__global_start_time

        self._runtime = delta - self._pausetime
        self._global_runtime = global_delta - self._global_pausetime

    def __update_paused_timers(self):
        """Tracks time spent in pause mode."""

        # That was the easiest way to track the duration during the pause
        # but not the best :D
        delta = time() - self.__pause_last_time

        self._pausetime += delta
        self._global_pausetime += delta

        self.__pause_last_time = time()

    # no point to update the fps every frame as is hard to tell with the eye
    # maybe i should change it to average instead?
    def __update_fps(self):
        """Updates the current scene fps every 250ms."""
        if self.is_time(250):
            self._fps = Display.clock.get_fps()

    def __render(self):
        """Renders the scene."""
        if not self.__paused:  # skip background if paused to keep the last frame render
            self.__draw_background()
        (self._paused_draw if self.__paused else self._draw)()

    def __draw_background(self):
        """Clears the screen with the background color."""
        Display.surface.fill(self._background_color)

    def __draw_display(self):
        """Draws the display."""
        surf = Display.get_stretch_surf() if Display.is_resized() else Display.surface
        Display.window.blit(surf,(0,0))

    def __flip(self):
        """Updates the display with the latest frame."""
        self.__update_fps()  # I think updating the fps before the flip is the best place?
        self._dt = round(Display.clock.tick(self._max_fps) / 1000, 3)  # Also take the dt
        self.__draw_display()
        pygame.display.flip()
