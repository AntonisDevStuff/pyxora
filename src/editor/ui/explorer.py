"""
Explorer panel for browsing project files.  
"""
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import subprocess
import platform

from ..constants import COLORS, FILE_ICONS


class ExplorerPanel:
    """
    File explorer panel showing the project directory structure.
    """
    
    def __init__(self, parent, project_path, editor_window=None):
        """
        Initialize the explorer panel.  
        
        Args:
            parent: The parent widget
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self._editor_window = editor_window
        
        self.frame = tk.Frame(parent, bg=COLORS["bg_panel"], relief=tk.FLAT, bd=0)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 8), pady=0)
        self.frame.config(width=280, highlightbackground=COLORS["border"], highlightthickness=1)
        
        self._create_widgets()
        self._populate_tree()

        self.tree.bind("<Button-1>", self._on_left_click) 
        self.tree. bind("<Button-2>", self._on_middle_click) 
        self.tree.bind("<Button-3>", self._on_right_click)
    
    def _create_widgets(self):
        """Create explorer widgets."""
        # Title
        title = tk.Label(
            self.frame, 
            text="Explorer", 
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_panel"], 
            fg=COLORS["text"],
            anchor="center",
            padx=12,
            pady=12
        )
        title.pack(fill=tk.X, pady=(12, 0))
        
        # Separator
        separator = tk.Frame(self.frame, bg=COLORS["border"], height=1)
        separator.pack(fill=tk.X, padx=12, pady=8)
        
        # Tree frame
        tree_frame = tk.Frame(self.frame, bg=COLORS["bg_dark"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Configure treeview style
        style = ttk.Style()
        style. theme_use("clam")
        style.configure("ExplorerTree.Treeview",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_dim"],
            fieldbackground=COLORS["bg_dark"],
            borderwidth=0,
            relief="flat",
            font=("Consolas", 10),
            rowheight=24
        )
        style.configure("ExplorerTree.Treeview. Heading",
            background=COLORS["bg_dark"],
            foreground=COLORS["text"],
            borderwidth=0
        )
        style.map("ExplorerTree.Treeview",
            background=[("selected", COLORS["border_light"])],
            foreground=[("selected", COLORS["text"])]
        )
        
        # Scrollbar
        scrollbar = ttk. Scrollbar(tree_frame, orient=tk.VERTICAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame, 
            show="tree",
            yscrollcommand=scrollbar. set,
            selectmode="browse",
            style="ExplorerTree.Treeview"
        )
        
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side=tk. RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)

    
    def _populate_tree(self):
        """Populate the tree with project files."""
        self.tree.delete(*self.tree.get_children())
        
        if os.path.exists(self.project_path):
            self._add_directory("", self.project_path, is_root=True)
    
    def _add_directory(self, parent_id, path, is_root=False):
        """
        Recursively add directory contents to tree.
        
        Args:
            parent_id: Parent tree item ID
            path: Directory path
            is_root: Whether this is the root directory
        """
        try:
            items = sorted(os.listdir(path))
            for item in items:
                # Skip hidden files and cache
                if item.startswith('.') or item == '__pycache__':
                    continue
                
                full_path = os.path.join(path, item)
                
                if os.path.isdir(full_path):
                    icon = "📂"
                    display_text = f"{icon} {item}"
                    dir_id = self.tree.insert(parent_id, "end", text=display_text, open=is_root)
                    self._add_directory(dir_id, full_path)
                else:
                    icon = self._get_file_icon(item)
                    display_text = f"{icon} {item}"
                    self.tree.insert(parent_id, "end", text=display_text, values=[full_path])
        except PermissionError:
            pass
    
    def _get_file_icon(self, filename):
        """
        Get icon for file based on extension.
        
        Args:
            filename: The filename
            
        Returns:
            str: Icon emoji for the file type
        """
        ext = os.path.splitext(filename)[1].lower()
        return FILE_ICONS.get(ext, '📄')

    def _on_left_click(self, event):
        """Handle left-click on tree item."""        
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        # Get item path (values returns a tuple, get first element)
        item_values = self.tree.item(item_id, "values")
        if not item_values:
            return  # No values, exit
        
        item_path = item_values[0]
        
        # Convert to Path object
        full_path = Path(self.project_path) / item_path
        
        # Only open files in editor
        if not full_path.is_file():
            return
        
        # Only open . py and .json files in the editor
        if full_path. suffix not in ['.py', '.json']:
            return
        
        # Switch to Script workspace and open file
        if self._editor_window:
            self._editor_window. workspace_manager.switch_workspace("Script")
            self._editor_window.code_editor.open_file(str(full_path))

    def _on_middle_click(self, event):
        """Handle middle-click on tree item to open folder in explorer."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        # Get item path (values returns a tuple, get first element)
        item_values = self.tree.item(item_id, "values")
        if not item_values:
            return  # No values, exit
        
        item_path = item_values[0]
        
        # Convert to Path object
        full_path = Path(self.project_path) / item_path
        
        # If it's a file, get the parent folder
        if full_path.is_file():
            full_path = full_path.parent
        
        # Open folder in system explorer
        self._open_folder(str(full_path))

    def _on_right_click(self, event):
        """Handle right-click on tree item to show context menu."""
        # Get item at click position
        item_id = self. tree.identify_row(event. y)
        if not item_id:
            return  # Clicked on empty space, exit
        
        # Select the item
        self.tree. selection_set(item_id)
        
        # Get item path (values returns a tuple, get first element)
        item_values = self.tree.item(item_id, "values")
        if not item_values:
            return  # No values, exit
        
        item_path = item_values[0]
        full_path = Path(self.project_path) / item_path
        
        # Create context menu
        context_menu = tk.Menu(self.tree, tearoff=0, bg=COLORS["bg_panel"], fg=COLORS["text"])
        
        # Different menus for files vs folders
        if full_path.is_file():
            # File options
            if full_path.suffix in ['.py', '.json']:
                context_menu.add_command(
                    label="📝 Open in Editor",
                    command=lambda: self._on_left_click(event),
                    font=("Segoe UI", 9)
                )
                context_menu.add_separator()
            
            context_menu.add_command(
                label="🔗 Open with System App",
                command=lambda: self._open_folder(str(full_path)),
                font=("Segoe UI", 9, "bold")
            )
            
            context_menu.add_separator()
            
            context_menu.add_command(
                label="📂 Show in Explorer",
                command=lambda: self._open_folder(str(full_path. parent)),
                font=("Segoe UI", 9)
            )
            
            context_menu.add_command(
                label="📋 Copy Path",
                command=lambda: self._copy_path(str(full_path)),
                font=("Segoe UI", 9)
            )
        else:
            # Folder options
            context_menu.add_command(
                label="📂 Open in Explorer",
                command=lambda: self._open_folder(str(full_path)),
                font=("Segoe UI", 9, "bold")
            )
            
            context_menu.add_separator()
            
            context_menu.add_command(
                label="📋 Copy Path",
                command=lambda: self._copy_path(str(full_path)),
                font=("Segoe UI", 9)
            )
        
        # Bind to close menu on any click outside
        def close_menu(e=None):
            context_menu. unpost()
            self.tree. unbind("<Button-1>")
            self.tree.unbind("<Button-2>")
            self.tree.unbind("<Button-3>")
            # Re-bind the original events after a short delay
            self.tree.after(10, self._rebind_events)
        
        # Temporarily bind all clicks to close the menu
        self.tree.bind("<Button-1>", close_menu)
        self.tree. bind("<Button-2>", close_menu)
        self.tree.bind("<Button-3>", close_menu)
        
        # Also bind focus out
        context_menu.bind("<FocusOut>", close_menu)
        
        # Show menu at cursor position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _open_folder(self, file_path):
        """
        Open file with default system application.
        
        Args:
            file_path: Path to the file to open
        """
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":
                subprocess. Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            print(f"Failed to open file: {e}")

    def _copy_path(self, file_path):
        """
        Copy file path to clipboard.
        
        Args:
            file_path: Path to copy
        """
        self.tree.clipboard_clear()
        self.tree.clipboard_append(file_path)

    def _rebind_events(self):
        """Rebind tree events after context menu closes."""
        self.tree.bind("<Button-1>", self._on_left_click)
        self. tree.bind("<Button-2>", self._on_middle_click)
        self.tree.bind("<Button-3>", self._on_right_click)
    
    def refresh(self):
        """Refresh the explorer tree."""
        self._populate_tree()