"""
Inspector panel for viewing scene variables and properties.
"""
import tkinter as tk
from tkinter import ttk
import inspect

from ..constants import COLORS


class InspectorPanel:
    """
    Inspector panel showing current scene variables and properties.
    """
    
    def __init__(self, parent, engine):
        """
        Initialize the inspector panel.  
        
        Args:
            parent: The parent widget
            engine: The CustomPyxora engine instance
        """
        self.engine = engine
        
        self.frame = tk.Frame(parent, bg=COLORS["bg_panel"], relief=tk.FLAT)
        self.frame.pack(side=tk.RIGHT, fill=tk. BOTH, padx=(8, 0), pady=0)
        self.frame.config(width=280, highlightbackground=COLORS["border"], highlightthickness=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create inspector widgets."""
        # Title
        title = tk.Label(
            self.frame,
            text="Inspector",
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
        
        # Table frame
        table_frame = tk.Frame(self.frame, bg=COLORS["bg_dark"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("InspectorTree.Treeview",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_dim"],
            fieldbackground=COLORS["bg_dark"],
            borderwidth=0,
            relief="flat",
            font=("Consolas", 9),
            rowheight=28
        )
        style.configure("InspectorTree.Treeview.Heading",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_dim"],
            borderwidth=0,
            font=("Segoe UI", 10, "bold")
        )
        style. map("InspectorTree.Treeview",
            background=[("selected", COLORS["border_light"])],
            foreground=[("selected", COLORS["text"])]
        )
        
        # Create treeview
        columns = ("name", "value")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            height=20,
            style="InspectorTree.Treeview"
        )
        
        self.tree.heading("name", text="Name")
        self.tree.heading("value", text="Value")
        
        self.tree.column("name", width=100, anchor=tk.CENTER)
        self. tree.column("value", width=140, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk. Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk. RIGHT, fill=tk.Y)
        
        self.tree.config(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)
    
    def update(self):
        """Update the inspector with current scene variables."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Only update if scene is running
            if not self.engine.is_running():
                self. tree.insert("", tk.END, values=("Status", "Not Running"))
                return
            
            scene = self.engine.get_current_scene()
            if not scene:
                self.tree.insert("", tk.END, values=("Status", "No Scene"))
                return
            
            # Blacklist of class names to filter out
            BLACKLIST = {
                "Objects", "Camera", "SceneEvent", 
                "PhysicsManager", "Space", "Body", "Shape"
            }
            
            # Get all attributes
            attrs = []
            
            # Get regular attributes (non-underscore)
            try:
                for k, v in vars(scene).items():
                    if not k.startswith("_"):
                        attrs.append((k, v))
            except:
                pass
            
            # Get properties
            try:
                for k in dir(type(scene)):
                    if k.startswith("_"):
                        continue
                    attr = getattr(type(scene), k, None)
                    if isinstance(attr, property):
                        try:
                            value = getattr(scene, k)
                            attrs.append((k, value))
                        except:
                            pass
            except:
                pass
            
            if not attrs:
                self.tree.insert("", tk.END, values=("Status", "No Variables"))
                return
            
            # Remove duplicates
            seen = set()
            unique_attrs = []
            for k, v in attrs:
                if k not in seen:
                    seen.add(k)
                    unique_attrs.append((k, v))
            
            # Filter and format values
            for k, v in sorted(unique_attrs):
                try:
                    # Skip classes
                    if inspect.isclass(v):
                        continue
                    
                    # Skip methods and functions
                    if inspect.ismethod(v) or inspect.isfunction(v):
                        continue
                    
                    # Skip blacklisted class instances
                    if hasattr(v, "__class__"):
                        class_name = v.__class__.__name__
                        if class_name in BLACKLIST:
                            continue
                    
                    # Format value based on type
                    if isinstance(v, float):
                        value_str = f"{v:.2f}"
                    elif isinstance(v, (str, int, bool)):
                        value_str = str(v)
                    elif isinstance(v, (list, tuple, set)):
                        value_str = f"{type(v).__name__}[{len(v)}]"
                    elif isinstance(v, dict):
                        value_str = f"dict[{len(v)}]"
                    else:
                        # Skip other complex objects
                        continue
                    
                    # Truncate long strings
                    if len(value_str) > 40:
                        value_str = value_str[:37] + "..."
                    
                    self.tree.insert("", tk.END, values=(k, value_str))
                except:
                    # Skip any attribute that causes an error
                    continue
                    
        except Exception as e:
            # If anything fails, just show the error
            try:
                self.tree.delete(*self.tree.get_children())
                self.tree.insert("", tk.END, values=("Error", str(e)))
            except:
                pass