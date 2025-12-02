from .constants import TK_TO_PYGAME_KEY_MAP, TK_TO_PYGAME_MOUSE_MAP
from ..utils import platform

import tkinter as tk
import pygame


class InputForwarder:
    """
    Forwards input events from Tkinter to Pygame.
    """

    def __init__(self, root_window, engine):
        """
        Initialize input forwarder with the root window for global input capture.

        Args:
            root_window: The main Tkinter root window
            engine: The CustomPyxora engine instance
        """
        self.root = root_window
        self.engine = engine
        self._setup_bindings()

        self.preview_label = None
        self.prev_mouse_pos = None

    def set_preview_label(self, preview_label):
        """
        Update the preview label reference.

        Args:
            preview_label: The new preview label widget
        """
        self.preview_label = preview_label

    def _is_mouse_over_preview(self, event):
        """
        Check if mouse event is over the preview panel.

        Args:
            event: The mouse event

        Returns:
            bool: True if mouse is over preview, False otherwise
        """
        if not self.preview_label or not self.preview_label.winfo_exists():
            return False

        # Get preview widget bounds
        preview_x = self.preview_label.winfo_rootx()
        preview_y = self.preview_label.winfo_rooty()
        preview_w = self.preview_label.winfo_width()
        preview_h = self. preview_label.winfo_height()

        # Check if mouse is within bounds
        return (preview_x <= event.x_root < preview_x + preview_w and
                preview_y <= event. y_root < preview_y + preview_h)

    def _setup_bindings(self):
        """Bind events globally to the root window."""
        # Global keyboard events
        self.root.bind_all("<KeyPress>", self._forward_key)
        self.root.bind_all("<KeyRelease>", self._forward_key)

        # Global mouse events
        self.root.bind_all("<Button>", self._forward_mouse)
        self.root.bind_all("<ButtonRelease>", self._forward_mouse)
        self.root.bind_all("<Motion>", self._forward_motion)
        if not platform.is_linux():
            self.root.bind_all("<MouseWheel>", self._forward_wheel)
        else:
            self.root.bind_all("<Button-4>", self._forward_wheel)
            self.root.bind_all("<Button-5>", self._forward_wheel)

    def _forward_key(self, event):
        """
        Forward keyboard events to pygame.

        Args:
            event: The Tkinter keyboard event
        """
        key = TK_TO_PYGAME_KEY_MAP.get(event.keysym)

        event_type = pygame. KEYDOWN if event.type == tk.EventType.KeyPress else pygame.KEYUP
        pygame.event.post(pygame.event.Event(event_type, {"key": key}))

    def _forward_mouse(self, event):
        if not self._is_mouse_over_preview(event):
            return

        # Get actual game resolution
        surface = self.engine.get_surface()
        if not surface:
            return

        game_w, game_h = surface.get_size()

        # Get preview widget size
        preview_w = event.widget.winfo_width()
        preview_h = event.widget.winfo_height()

        # Scale mouse coordinates
        scaled_x = int(event.x * game_w / preview_w)
        scaled_y = int(event.y * game_h / preview_h)

        button = TK_TO_PYGAME_MOUSE_MAP.get(event.num, 0)
        if event.type == tk.EventType.ButtonPress:
            event_type = pygame.MOUSEBUTTONDOWN
        elif event.type == tk.EventType.ButtonRelease:
            event_type = pygame.MOUSEBUTTONUP
        else:
            return
        pygame. event.post(pygame.event.Event(event_type, {
            "pos": (scaled_x, scaled_y),
            "button": button
        }))


    def _forward_motion(self, event):
        """
        Forward mouse motion events to pygame.

        Args:
            event: The Tkinter mouse motion event
        """
        if not self._is_mouse_over_preview(event):
            return

        # Get actual game resolution
        surface = self.engine.get_surface()
        if not surface:
            return

        game_w, game_h = surface.get_size()

        # Get preview widget size
        preview_w = event.widget.winfo_width()
        preview_h = event.widget.winfo_height()

        # Scale mouse coordinates
        scaled_x = int(event.x * game_w / preview_w)
        scaled_y = int(event.y * game_h / preview_h)
        scaled_pos = (scaled_x, scaled_y)

        # Calculate rel
        if self.prev_mouse_pos is not None:
            rel_x = scaled_x - self.prev_mouse_pos[0]
            rel_y = scaled_y - self.prev_mouse_pos[1]
        else:
            rel_x, rel_y = 0, 0  # Or None, depending on your API expectations

        pygame.event.post(pygame.event.Event(
            pygame.MOUSEMOTION,
            {"pos": scaled_pos, "rel": (rel_x, rel_y)},
        ))

        # Update previous position
        self.prev_mouse_pos = scaled_pos

    def _forward_wheel(self, event):
        """
        Forward mouse wheel events to pygame.

        Args:
            event: The Tkinter mouse wheel event
        """

        if platform.is_windows() or platform.is_mac():
            y = 1 if event.delta > 0 else -1
        else:
            y = 1 if event.num == 4 else -1
        pygame.event.post(pygame.event.Event(pygame.MOUSEWHEEL, {"x": 0, "y": y}))
