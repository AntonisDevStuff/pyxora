"""
Main editor window class. 
Coordinates all UI panels and manages the overall editor layout.
"""
import tkinter as tk
from . workspace import WorkspaceManager

from .. runtime import CustomPyxora
from ..input import InputForwarder
from ..constants import COLORS

from ... projects. path import get_path
from ...assets import Assets

from PIL import Image, ImageTk
from sys import exit


class EditorWindow:
    """
    Main editor window that integrates all UI components.
    """
    
    def __init__(self, root, args):
        """
        Initialize the editor window. 
        
        Args:
            root: The Tkinter root window
            args: Command-line arguments for the project
        """
        self.root = root
        self.project_name = args.name
        self.project_path = get_path(args.name)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Setup window
        self._setup_window(screen_width, screen_height)
        
        # Initialize engine
        self.engine = CustomPyxora(args)
        
        # Setup global input forwarding
        self._setup_global_input()
        
        # Initialize workspace manager (replaces _init_ui)
        self.workspace_manager = WorkspaceManager(self.root, self)
        
        # Start with Game workspace
        self.workspace_manager.switch_workspace("Scene")
        
        # Setup cleanup
        self._setup_cleanup()
    
    def _setup_window(self, screen_width, screen_height):
        """Setup window properties and icon."""
        # Load icon
        Assets._load_engine_files()
        icon_path = Assets.engine. files["images"]["icon"]
        pil_image = Image.open(icon_path)
        photo = ImageTk.PhotoImage(pil_image)
        
        # Configure window
        self.root.title(f"Pyxora Editor — {self.project_name}")
        self.root.icon_photo = photo
        self.root.wm_iconphoto(False, photo)
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg=COLORS["bg_main"])
        self.root.minsize(1000, 600)
    
    def _setup_global_input(self):
        """Setup global input forwarding to pygame."""
        self.input_forwarder = InputForwarder(self.root, self.engine)
    
    def _setup_cleanup(self):
        """Setup cleanup handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_close(self):
        """Handle window close event."""
        self.engine.stop()
        if hasattr(self.workspace_manager.editor,"code_editor"):
            self.workspace_manager.editor.code_editor.check_unsaved_changes()
        self.workspace_manager._stop_docs()
        self.root.destroy()
        exit()