import tkinter as tk
from PIL import Image, ImageTk
import pygame

from ..constants import COLORS


class PreviewPanel:
    """
    Game preview panel that displays the pygame surface.
    """
    
    def __init__(self, parent, engine):
        """
        Initialize the preview panel.
        
        Args:
            parent: The parent widget
            engine: The CustomPyxora engine instance
        """
        self.engine = engine
        self.inspector = None

        # no point having more to refresh faster
        self.refresh = int(1000 / (max(pygame.display.get_desktop_refresh_rates())+1))
        
        preview_container = tk.Frame(parent, bg=COLORS["bg_panel"])
        preview_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        header = tk.Label(
            preview_container,
            text="Preview",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_panel"],
            fg=COLORS["text"],
            anchor="center"
        )
        header.pack(fill=tk.X, pady=(0, 10))
        
        self.frame = tk.Frame(preview_container, bg=COLORS["bg_preview"], relief=tk.FLAT)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.frame.config(highlightbackground=COLORS["border_light"], highlightthickness=1)
        
        # Prevent frame from shrinking/expanding
        self.frame.pack_propagate(False)
        
        # Label for displaying game surface
        self.label = tk.Label(
            self.frame, 
            bg="#000000", 
            text="Press Start to Run",
            font=("Consolas", 18), 
            fg=COLORS["text_gray"],
            takefocus=False
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize event to update font size
        self.label.bind("<Configure>", self._on_label_resize)
    
    def set_inspector(self, inspector):
        """
        Set the inspector panel for updates.
        
        Args:
            inspector: The InspectorPanel instance
        """
        self.inspector = inspector
    
    def start_update_loop(self):
        """Start the preview update loop."""
        self._update()

    def _on_label_resize(self, event):
        """Update placeholder text size when label is resized."""
        if self.engine.is_running():
            return
        
        label_height = event.height
        font_size = max(12, int(label_height * 0.08))
        self.label.config(font=("Consolas", font_size))
    
    def _update(self):
        """Update the preview display and inspector."""
        self.label.config(image='', text="Press Start to Run") # pre-text
        if self.engine.is_running():
            surface = self.engine.get_surface()
            if surface:
                self._render_surface(surface)
        
        if self.inspector:
            self.inspector.update()
        
        # Schedule next update (~monitor hz)
        self.label.after(self.refresh, self._update)
    
    def _render_surface(self, surface):
        """
        Render pygame surface to tkinter label.
        
        Args:
            surface: The pygame surface to render
        """
        try:
            # Convert pygame surface to PIL Image
            raw_data = pygame.image.tobytes(surface, "RGB")
            image = Image.frombytes("RGB", surface.get_size(), raw_data)
            
            # Resize to fit frame
            frame_width = self.frame.winfo_width()
            frame_height = self.frame.winfo_height()
            
            if frame_width > 1 and frame_height > 1:
                image = image.resize(
                    (frame_width, frame_height), 
                    Image. Resampling.BILINEAR
                )
            
            # Convert to PhotoImage and display
            image_tk = ImageTk.PhotoImage(image)
            self.label.config(image=image_tk)
            self.label.image = image_tk  # Keep reference
            
        except Exception as e:
            print(f"Preview render error: {e}")