"""
Code editor panel - Coming Soon placeholder.  
"""
import tkinter as tk
from pathlib import Path

from ..constants import COLORS


class CodeEditorPanel:
    """
    Code editor panel - Coming Soon placeholder. 
    """
    
    def __init__(self, parent):
        """
        Initialize the code editor panel.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self._create_placeholder()
    
    def _create_placeholder(self):
        """Create Coming Soon placeholder."""
        # Main frame
        self.frame = tk.Frame(self.parent, bg=COLORS["bg_dark"])
        self.frame. pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk. Label(
            self.frame,
            text="📝",
            font=("Segoe UI", 80),
            bg=COLORS["bg_dark"],
            fg=COLORS["text"]
        )
        icon_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        
        # Title
        title_label = tk. Label(
            self.frame,
            text="Coming Soon...",
            font=("Segoe UI", 32, "bold"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text"]
        )
        title_label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)