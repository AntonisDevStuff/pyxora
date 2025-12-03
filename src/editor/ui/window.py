from .workspace import WorkspaceManager

from ..runtime import CustomPyxora
from ..input import InputForwarder
from ..constants import COLORS

from ...projects. path import get_path
from ...assets import Assets

import signal
import tkinter as tk
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

        self._setup_window()

        self.engine = CustomPyxora(args)

        self._setup_global_input()

        self.workspace_manager = WorkspaceManager(self.root, self)

        # Start with Game workspace
        self.workspace_manager.switch_workspace("Scene")

        self._setup_cleanup()

    def _setup_window(self):
        """Setup window properties and icon."""

        Assets._load_engine_files()
        icon_path = Assets.engine.files["images"]["icon"]
        pil_image = Image.open(icon_path)
        photo = ImageTk.PhotoImage(pil_image)

        self.root.title(f"Pyxora Editor — {self.project_name}")
        self.root.icon_photo = photo
        self.root.wm_iconphoto(False, photo)
        self.root.configure(bg=COLORS["bg_main"])
        self.root.minsize(1000, 900)

        # Desired window size
        win_w, win_h = 1000, 900

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Compute centered position
        x = (screen_width - win_w) // 2
        y = (screen_height - win_h) // 2

        # Apply geometry with position
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    def _setup_global_input(self):
        """Setup global input forwarding to pygame."""
        self.input_forwarder = InputForwarder(self.root, self.engine)

    def _setup_cleanup(self):
        """Setup cleanup handlers."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        signal.signal(signal.SIGINT, self._on_keyboard_interrupt)

    def _on_keyboard_interrupt(self, sig, frame):
        self._on_close()

    def _on_close(self):
        """Handle window close event."""
        self.engine.stop()
        if hasattr(self.workspace_manager.editor,"code_editor"):
            self.workspace_manager.editor.code_editor.check_unsaved_changes()
        self.workspace_manager._stop_docs()
        self.root.destroy()
        exit()
