"""
Workspace management for switching between different editor layouts.
Similar to Godot's 2D/3D/Script/AssetLib tabs.
"""
import tkinter as tk
from tkinter import ttk

from .inspector import InspectorPanel
from .explorer import ExplorerPanel
from .preview import PreviewPanel
from .controls import ControlsPanel
from .console import ConsolePanel
from .inspector import InspectorPanel
from .explorer import ExplorerPanel
from .code_editor import CodeEditorPanel
from ..constants import COLORS


class WorkspaceManager:
    """
    Manages different workspace layouts (Scene, Script).  
    """
    
    def __init__(self, parent, editor_window):
        """
        Initialize workspace manager.
        
        Args:
            parent: Parent widget
            editor_window: Reference to EditorWindow instance
        """
        self.parent = parent
        self.editor = editor_window
        self.current_workspace = "Scene"
        
        self._create_workspace_tabs()
        self._create_workspace_container()
    
    def _create_workspace_tabs(self):
        """Create workspace selection tabs."""
        tab_frame = tk.Frame(self.parent, bg=COLORS["bg_main"], height=40)
        tab_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(15, 0))
        tab_frame.pack_propagate(False)
        
        # Center container for workspace buttons
        center_container = tk.Frame(tab_frame, bg=COLORS["bg_main"])
        center_container. place(relx=0.5, rely=0.5, anchor=tk. CENTER)
        
        # Workspace buttons
        workspaces = [
            ("🎮 Scene", "Scene"),
            ("📝 Script", "Script")
        ]
        
        self.tab_buttons = {}
        
        for label, workspace_name in workspaces:
            btn = tk.Button(
                center_container,
                text=label,
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["bg_panel"],
                fg=COLORS["text_gray"],
                activebackground=COLORS["border_light"],
                activeforeground=COLORS["text"],
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                bd=0,
                command=lambda w=workspace_name: self. switch_workspace(w)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[workspace_name] = btn
        
        # Highlight first tab
        self._update_tab_styles()
    
    def _create_workspace_container(self):
        """Create container for workspace content."""
        self.container = tk.Frame(self.parent, bg=COLORS["bg_main"])
        self.container. pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    def _update_tab_styles(self):
        """Update tab button styles based on active workspace."""
        for workspace_name, btn in self.tab_buttons.items():
            if workspace_name == self.current_workspace:
                btn.config(
                    bg=COLORS["button_bg"],
                    fg=COLORS["text"]
                )
            else:
                btn.config(
                    bg=COLORS["bg_panel"],
                    fg=COLORS["text_gray"]
                )
    
    def switch_workspace(self, workspace_name):
        """
        Switch to a different workspace layout.
        
        Args:
            workspace_name: Name of workspace to switch to
        """
        # Allow initial build even if it's the "current" workspace
        if workspace_name == self.current_workspace and self.container. winfo_children():
            return
        
        # Clear current workspace
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Load new workspace
        self.current_workspace = workspace_name
        self._update_tab_styles()
        
        if workspace_name == "Scene":
            self._build_scene_workspace()
        elif workspace_name == "Script":
            self._build_script_workspace()
    
    def _build_scene_workspace(self):
        """Build Scene workspace: Explorer + Preview/Console + Inspector."""
        # Left: Explorer
        self.editor.explorer = ExplorerPanel(self.container, self.editor. project_path, self.editor)
        
        # Center column: Preview + Console
        center_column = tk.Frame(self.container, bg=COLORS["bg_main"])
        center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
        
        # Top frame: Preview + Controls
        top_frame = tk. Frame(center_column, bg=COLORS["bg_panel"], relief=tk.FLAT)
        top_frame.pack(side=tk.TOP, fill=tk. BOTH, expand=True, pady=(0, 8))
        top_frame.config(highlightbackground=COLORS["border"], highlightthickness=1)
        
        # Recreate preview and controls
        
        self.editor. preview = PreviewPanel(top_frame, self.editor.engine)
        self.editor.controls = ControlsPanel(top_frame, self.editor.engine, self.editor. preview)
        
        # Bottom frame: Console
        console_frame = tk.Frame(center_column, bg=COLORS["bg_panel"], relief=tk.FLAT)
        console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=(8, 0))
        console_frame.config(highlightbackground=COLORS["border"], highlightthickness=1)
        
        self.editor.console = ConsolePanel(console_frame)
        self.editor.engine.set_console(self.editor.console)
        
        # Right: Inspector
        self.editor.inspector = InspectorPanel(self.container, self.editor.engine)
        
        # Connect inspector to preview
        self.editor.preview.set_inspector(self.editor.inspector)
        
        # Restart preview update loop
        self.editor.preview.start_update_loop()
    
    def _build_script_workspace(self):
        """Build Script workspace: Code Editor only (fullscreen)."""
        self.editor.code_editor = CodeEditorPanel(self.container)