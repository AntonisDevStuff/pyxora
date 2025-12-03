from .explorer import ExplorerPanel
from .preview import PreviewPanel
from .controls import ControlsPanel
from .console import ConsolePanel
from .code_editor import CodeEditorPanel
from ..constants import COLORS

import tkinter as tk
from tkinter import ttk

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
        self.current_workspace = None

        # init file data
        self._open_file_path = None
        self._open_files_path = None

        self._create_workspace_tabs()
        self._create_workspace_container()

    def switch_workspace(self, workspace_name):
        """
        Switch to a different workspace layout.

        Args:
            workspace_name: Name of workspace to switch to
        """

        # Don't rebuild if already in this workspace
        if workspace_name == self.current_workspace:
            return

        # Skip if docs
        if workspace_name == "Docs":
            self._open_docs()
            return

        # Save the currently open file if switching away from Script workspace
        if self.current_workspace == "Script" and hasattr(self.editor, 'code_editor'):
            self._open_file_path = self.editor.code_editor.current_file
            self._open_files_path = self.editor.code_editor.open_files
            if workspace_name == "Scene":
                self.editor.code_editor.check_unsaved_changes()

        # Pause engine BEFORE destroying widgets if switching to Script workspace
        if workspace_name == "Script" and hasattr(self.editor, 'controls'):
            if self.editor.controls.engine.is_running() and not self.editor.controls.engine.is_paused():
                self.editor.controls.engine.toggle_pause()  # Use engine directly, not controls method

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

    def _create_workspace_tabs(self):
        """Create workspace selection tabs."""
        tab_frame = tk.Frame(self.parent, bg=COLORS["bg_main"], height=40)
        tab_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=(15, 0))
        tab_frame.pack_propagate(False)

        center_container = tk.Frame(tab_frame, bg=COLORS["bg_main"])
        center_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Workspace buttons
        workspaces = [
            ("🎮 Scene", "Scene"),
            ("📝 Script", "Script"),
            ("📚 Docs", "Docs")
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
                command=lambda w=workspace_name: self.switch_workspace(w)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[workspace_name] = btn

    def _create_workspace_container(self):
        """Create container for workspace content."""
        self.container = tk.Frame(self.parent, bg=COLORS["bg_main"])
        self.container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

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

    def _build_scene_workspace(self):
        """Build Scene workspace: Preview/Console + Controls (No Explorer, No Inspector)."""
        # Center column: Preview + Console
        center_column = tk.Frame(self.container, bg=COLORS["bg_main"])
        center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

        # Top frame: Preview + Controls
        top_frame = tk.Frame(center_column, bg=COLORS["bg_panel"], relief=tk.FLAT)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 8))
        top_frame.config(highlightbackground=COLORS["border"], highlightthickness=1)

        # Recreate preview and controls
        self.editor.preview = PreviewPanel(top_frame, self.editor.engine)
        self.editor.controls = ControlsPanel(top_frame, self.editor.engine, self.editor.preview)

        self.editor.input_forwarder.set_preview_label(self.editor.preview.label)

        # Bottom frame: Console
        console_frame = tk.Frame(center_column, bg=COLORS["bg_panel"], relief=tk.FLAT)
        console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, pady=(8, 0))
        console_frame.config(highlightbackground=COLORS["border"], highlightthickness=1)

        self.editor.console = ConsolePanel(console_frame)
        self.editor.engine.set_console(self.editor.console)

        # Connect inspector to preview (removed)
        # self.editor.preview.set_inspector(self.editor.inspector)

        # Start preview update loop
        self.editor.preview.start_update_loop()

    def _build_script_workspace(self):
        """Build Script workspace: Explorer (left) + Code Editor (center/right)."""
        # Left: Explorer Panel
        self.editor.explorer = ExplorerPanel(self.container, self.editor.project_path, self.editor)

        # Center/right: Code Editor Panel (expand to fill available space)
        self.editor.code_editor = CodeEditorPanel(self.container)
        self.editor.code_editor.container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))

        # Restore the previously open file if any
        if self._open_file_path:
            for item in self._open_files_path:
                self.editor.code_editor.open_file(item)
            self.editor.code_editor.open_file(self._open_file_path)

    def _build_docs_workspace(self):
        """Build Docs workspace: Documentation viewer."""
        self.editor.docs = DocsPanel(self.container)

    def _open_docs(self):
        """Open documentation server in browser (starts server if not running)."""
        import webbrowser
        import threading

        # init new vars
        if not hasattr(self, '_docs_server'):
            self._docs_server = None
            self._docs_url = None

        # just open browser, if already running
        if self._docs_server and self._docs_url:
            webbrowser.open(self._docs_url)
            return

        # Start server in background thread
        def start_server():
            import subprocess
            import sys
            from tkinter import messagebox
            try:
                self._docs_server = subprocess.Popen(
                    [sys.executable, "-m", "pyxora", "docs", "local"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self._docs_url = "localhost:8080"
            except Exception as e:
                # Show error in GUI message box
                def show_error():
                    messagebox.showerror(
                        "Documentation Server Error",
                        f"Failed to start documentation server"
                    )
                self.parent.after(0, show_error)

        # Start server thread
        thread = threading.Thread(target=start_server, daemon=True)
        thread.start()

    def _stop_docs(self):
        """Stop documentation server"""
        if not hasattr(self, '_docs_server'):
            return
        self._docs_server.kill()
