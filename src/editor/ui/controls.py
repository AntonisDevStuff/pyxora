import tkinter as tk

from ..constants import COLORS


class ControlsPanel:
    """
    Control panel for managing game execution.
    """
    
    def __init__(self, parent, engine, preview_panel):
        """
        Initialize the controls panel.
        
        Args:
            parent: The parent widget
            engine: The CustomPyxora engine instance
            preview_panel: The PreviewPanel instance
        """
        self.engine = engine
        self.preview_panel = preview_panel
        
        self.frame = tk.Frame(parent, bg=COLORS["bg_panel"])
        self.frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self._create_buttons()
        self._start_update_loop()
    
    def _create_buttons(self):
        """Create control buttons."""
        btn_frame = tk.Frame(self.frame, bg=COLORS["bg_panel"])
        btn_frame.pack()
        
        # Base button style
        btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": COLORS["button_bg"],
            "fg": "#ffffff",
            "activebackground": COLORS["button_hover"],
            "activeforeground": "#ffffff",
            "relief": tk.FLAT,
            "padx": 18,
            "pady": 8,
            "cursor": "hand2",
            "bd": 0
        }
        
        self.btn_start = tk.Button(
            btn_frame, 
            text="▶ Start", 
            command=self._on_start, 
            **btn_style
        )
        self.btn_start.pack(side=tk. LEFT, padx=4)
        
        pause_style = btn_style.copy()
        pause_style["bg"] = "#1f6feb"
        pause_style["activebackground"] = "#388bfd"
        
        self.btn_pause = tk.Button(
            btn_frame, 
            text="⏸ Pause", 
            command=self._on_pause,
            state=tk.DISABLED, 
            **pause_style
        )
        self.btn_pause.pack(side=tk. LEFT, padx=4)
        
        stop_style = btn_style.copy()
        stop_style["bg"] = "#da3633"
        stop_style["activebackground"] = "#f85149"
        
        self. btn_stop = tk.Button(
            btn_frame, 
            text="⏹ Stop", 
            command=self._on_stop,
            state=tk.DISABLED, 
            **stop_style
        )
        self.btn_stop.pack(side=tk.LEFT, padx=4)
    
    def _on_start(self):
        """Handle start button click."""
        self.engine.start()
        self.preview_panel.label.focus_set()
    
    def _on_pause(self):
        """Handle pause button click."""
        self.engine.toggle_pause()
        if not self.engine.is_paused():
            self.preview_panel.label.focus_set()
    
    def _on_stop(self):
        """Handle stop button click."""
        self.engine.stop()
        self.engine._console.clear()
    
    def _start_update_loop(self):
        """Start the button state update loop."""
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states based on engine status."""
        if self.engine. is_running():
            self.btn_start.config(state=tk.DISABLED, bg=COLORS["button_disabled"])
            self.btn_pause.config(state=tk.NORMAL, bg="#1f6feb")
            self.btn_stop.config(state=tk.NORMAL, bg="#da3633")
            
            if self.engine.is_paused():
                self.btn_pause.config(text="▶ Resume")
            else:
                self. btn_pause.config(text="⏸ Pause")
        else:
            self.btn_start.config(state=tk.NORMAL, bg=COLORS["button_bg"])
            self.btn_pause.config(state=tk.DISABLED, bg=COLORS["button_disabled"])
            self.btn_stop.config(state=tk.DISABLED, bg=COLORS["button_disabled"])
            self.btn_pause.config(text="⏸ Pause")
        
        # Schedule next update
        self.frame.after(100, self._update_button_states)