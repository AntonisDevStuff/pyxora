"""
Input forwarding from Tkinter to Pygame. 
Captures Tkinter events and forwards them to the pygame event queue.
"""
import tkinter as tk
import pygame
from . constants import TK_TO_PYGAME_KEY_MAP, TK_TO_PYGAME_MOUSE_MAP


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
    
    def _setup_bindings(self):
        """Bind events globally to the root window."""
        # Global keyboard events
        self.root.bind_all("<KeyPress>", self._forward_key)
        self.root.bind_all("<KeyRelease>", self._forward_key)
        
        # Global mouse events
        self.root.bind_all("<Button>", self._forward_mouse)
        self.root.bind_all("<ButtonRelease>", self._forward_mouse)
        self.root.bind_all("<Motion>", self._forward_motion)
        self.root.bind_all("<MouseWheel>", self._forward_wheel)
    
    def _forward_key(self, event):
        """
        Forward keyboard events to pygame.
        
        Args:
            event: The Tkinter keyboard event
        """
        key = TK_TO_PYGAME_KEY_MAP.get(event.keysym)
        
        if not key:
            return
        
        event_type = pygame. KEYDOWN if event.type == tk.EventType.KeyPress else pygame.KEYUP
        pygame.event.post(pygame.event.Event(event_type, {"key": key}))
    
    def _forward_mouse(self, event):
        """
        Forward mouse button events to pygame.
        
        Args:
            event: The Tkinter mouse button event
        """
        if not self.engine.is_running():
            return
        
        pg_button = TK_TO_PYGAME_MOUSE_MAP.get(event.num, 0)
        
        event_type = pygame.MOUSEBUTTONDOWN if "Button-" in str(event.type) else pygame.MOUSEBUTTONUP
        pygame.event.post(pygame.event.Event(event_type, {"pos": (event.x, event. y), "button": pg_button}))
    
    def _forward_motion(self, event):
        """
        Forward mouse motion events to pygame.
        
        Args:
            event: The Tkinter mouse motion event
        """
        if not self.engine. is_running():
            return
        pygame.event.post(pygame.event.Event(pygame. MOUSEMOTION, {"pos": (event.x, event.y), "rel": (0, 0)}))
    
    def _forward_wheel(self, event):
        """
        Forward mouse wheel events to pygame. 
        
        Args:
            event: The Tkinter mouse wheel event
        """
        if not self.engine.is_running():
            return
        y = 1 if event.delta > 0 else -1
        pygame. event.post(pygame.event. Event(pygame.MOUSEWHEEL, {"x": 0, "y": y}))