"""
Custom Pyxora runtime engine for the editor.
Manages the game execution in a separate thread.
"""
from .. display import Display
from ..scene import Scene
from ..projects.run import local_run

import threading
import traceback
import pygame


class CustomPyxora:
    """
    Custom runtime engine that runs the game in a separate thread
    and allows control from the editor UI.
    """

    def __init__(self, args):
        """
        Initialize the custom runtime engine.

        Args:
            args: Command-line arguments for the project.
        """
        self.args = args

        self._thread = None
        self._running = False
        self._paused = False
        self._console = None

        Display.hidden = True

    def set_console(self, console):
        """
        Set the console widget for logging output.

        Args:
            console: The console widget instance.
        """
        self._console = console

    def is_running(self):
        """
        Check if the engine is currently running.

        Returns:
            bool: True if running, False otherwise.
        """
        return self._running

    def is_paused(self):
        """
        Check if the engine is currently paused.

        Returns:
            bool: True if paused, False otherwise.
        """
        return self._paused

    def get_surface(self):
        """
        Get the current pygame surface for rendering.

        Returns:
            pygame.Surface or None: The display surface if running, None otherwise.
        """
        if not self._running:
            return None
        return Display.surface

    def get_current_scene(self):
        """
        Get the currently active scene.

        Returns:
            Scene or None: The current scene object if available.
        """
        try:
            if not self._running:
                return None
            scene_tuple = Scene.manager.scene
            return scene_tuple[1]
        except:
            return None

    def start(self):
        """Start the game runtime in a separate thread."""
        if self._running:
            return

        if self._console:
            self._console.clear()

        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the game runtime and cleanup resources."""
        if not self._running:
            return

        self._running = False
        self._thread = None
        self._paused = False

        Scene.manager.exit()

    def toggle_pause(self):
        """Toggle between paused and running states."""
        if not self._running:
            return
        try:
            if self._paused:
                Scene.manager.resume()
                self._paused = False
            else:
                Scene.manager. pause()
                self._paused = True
        except Exception as e:
            print(f"Pause error: {e}")

    def _run(self):
        """Internal method to run the game loop."""
        try:
            local_run(self.args)
        except Exception as e:
            print(f"Scene error: {e}")
            traceback.print_exc()
        finally:
            self._running = False
