"""
Constants for the editor module.
Contains color schemes, key mappings, and other configuration constants.
"""
import pygame

# Color scheme for the editor UI
COLORS = {
    "bg_main": "#1a1d24",
    "bg_panel": "#21242b",
    "bg_dark": "#16181e",
    "bg_preview": "#0d0e11",
    "border": "#2d3139",
    "border_light": "#363a45",
    "text": "#ffffff",
    "text_dim": "#c9d1d9",
    "text_gray": "#8b949e",
    "button_bg": "#238636",
    "button_hover": "#2ea043",
    "button_disabled": "#21262d",
}

# Tkinter to Pygame key mappings
TK_TO_PYGAME_KEY_MAP = {
    # Letters
    "a": pygame.K_a, "b": pygame.K_b, "c": pygame.K_c, "d": pygame.K_d,
    "e": pygame.K_e, "f": pygame.K_f, "g": pygame.K_g, "h": pygame.K_h,
    "i": pygame. K_i, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l,
    "m": pygame.K_m, "n": pygame.K_n, "o": pygame. K_o, "p": pygame.K_p,
    "q": pygame.K_q, "r": pygame.K_r, "s": pygame.K_s, "t": pygame.K_t,
    "u": pygame.K_u, "v": pygame.K_v, "w": pygame.K_w, "x": pygame.K_x,
    "y": pygame. K_y, "z": pygame.K_z,
    
    # Numbers
    "0": pygame.K_0, "1": pygame.K_1, "2": pygame.K_2, "3": pygame.K_3,
    "4": pygame. K_4, "5": pygame.K_5, "6": pygame.K_6, "7": pygame.K_7,
    "8": pygame.K_8, "9": pygame.K_9,
    
    # Arrow keys
    "Up": pygame.K_UP, "Down": pygame.K_DOWN,
    "Left": pygame.K_LEFT, "Right": pygame. K_RIGHT,
    
    # Special keys
    "space": pygame.K_SPACE,
    "Escape": pygame.K_ESCAPE,
    "Return": pygame.K_RETURN,
    "Shift_L": pygame.K_LSHIFT,
    "Tab": pygame.K_TAB,
    "BackSpace": pygame.K_BACKSPACE,
    "Delete": pygame.K_DELETE,
    
    # Modifiers
    "Shift_R": pygame.K_RSHIFT,
    "Control_L": pygame.K_LCTRL,
    "Control_R": pygame.K_RCTRL,
    "Alt_L": pygame.K_LALT,
    "Alt_R": pygame.K_RALT,
    
    # Function keys
    "F1": pygame.K_F1, "F2": pygame.K_F2, "F3": pygame.K_F3,
    "F4": pygame.K_F4, "F5": pygame.K_F5, "F6": pygame.K_F6,
    "F7": pygame.K_F7, "F8": pygame.K_F8, "F9": pygame.K_F9,
    "F10": pygame.K_F10, "F11": pygame.K_F11, "F12": pygame. K_F12,
}

# Mouse button mappings
TK_TO_PYGAME_MOUSE_MAP = {
    1: 1,  # Left click
    2: 2,  # Middle click
    3: 3,  # Right click
}

# File type icons
FILE_ICONS = {
    '. py': '🐍',
    '.json': '📋',
    '.txt': '📄',
    '. md': '📝',
    '.png': '🖼️',
    '.jpg': '🖼️',
    '.jpeg': '🖼️',
    '.wav': '🔊',
    '.mp3': '🎵',
    '. ogg': '🎵',
    '.ttf': '🔤',
    '.otf': '🔤',
}