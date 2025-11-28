from ..utils import platform

import pygame

COLORS = {
    # Color scheme for the editor UI
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
    
    # Syntax highlighting colors
    "syntax_keyword": "#ff79c6",
    "syntax_builtin": "#8be9fd",
    "syntax_string": "#f1fa8c",
    "syntax_comment": "#6272a4",
    "syntax_number": "#bd93f9",
    "syntax_decorator": "#50fa7b",
    "syntax_function": "#ffb86c",
    "syntax_private_method": "#50fa7b",
    "syntax_main_module": "#ff5555",
    "syntax_module_attr": "#ff9999", 
    "syntax_class_name": "#8be9fd",
    "syntax_json_key": "#8be9fd",
    "syntax_json_string": "#f1fa8c",
    "syntax_json_number": "#bd93f9",
    "syntax_json_boolean": "#ff79c6",
    "syntax_json_null": "#ff79c6",
    
    # Search highlight colors
    "search_highlight": "#ffff00",
    "search_highlight_fg": "#000000",
    "search_current": "#ff9500",
    "search_current_fg": "#000000",
}


# Tkinter to Pygame key mappings
TK_TO_PYGAME_KEY_MAP = {
    # Letters (a-z)
    "a": pygame.K_a, "b": pygame.K_b, "c": pygame.K_c, "d": pygame.K_d,
    "e": pygame.K_e, "f": pygame. K_f, "g": pygame.K_g, "h": pygame.K_h,
    "i": pygame.K_i, "j": pygame.K_j, "k": pygame.K_k, "l": pygame. K_l,
    "m": pygame.K_m, "n": pygame.K_n, "o": pygame.K_o, "p": pygame.K_p,
    "q": pygame.K_q, "r": pygame.K_r, "s": pygame.K_s, "t": pygame.K_t,
    "u": pygame.K_u, "v": pygame. K_v, "w": pygame.K_w, "x": pygame.K_x,
    "y": pygame.K_y, "z": pygame.K_z,
    
    # Numbers (0-9) - top row
    "0": pygame. K_0, "1": pygame.K_1, "2": pygame.K_2, "3": pygame.K_3,
    "4": pygame.K_4, "5": pygame.K_5, "6": pygame. K_6, "7": pygame.K_7,
    "8": pygame.K_8, "9": pygame.K_9,
    
    # Numpad numbers
    "KP_0": pygame.K_KP0, "KP_1": pygame.K_KP1, "KP_2": pygame.K_KP2,
    "KP_3": pygame.K_KP3, "KP_4": pygame.K_KP4, "KP_5": pygame.K_KP5,
    "KP_6": pygame.K_KP6, "KP_7": pygame.K_KP7, "KP_8": pygame.K_KP8,
    "KP_9": pygame.K_KP9,
    
    # Numpad operators
    "KP_Period": pygame.K_KP_PERIOD,
    "KP_Divide": pygame.K_KP_DIVIDE,
    "KP_Multiply": pygame.K_KP_MULTIPLY,
    "KP_Subtract": pygame.K_KP_MINUS,
    "KP_Add": pygame.K_KP_PLUS,
    "KP_Enter": pygame.K_KP_ENTER,
    "KP_Equal": pygame.K_KP_EQUALS,
    
    # Arrow keys
    "Up": pygame. K_UP,
    "Down": pygame.K_DOWN,
    "Left": pygame.K_LEFT,
    "Right": pygame.K_RIGHT,
    
    # Special keys
    "BackSpace": pygame.K_BACKSPACE,
    "Tab": pygame.K_TAB,
    "Clear": pygame.K_CLEAR,
    "Return": pygame.K_RETURN,
    "Pause": pygame.K_PAUSE,
    "Escape": pygame.K_ESCAPE,
    "space": pygame.K_SPACE,
    "Delete": pygame.K_DELETE,
    
    # Navigation keys
    "Insert": pygame.K_INSERT,
    "Home": pygame.K_HOME,
    "End": pygame.K_END,
    "Prior": pygame.K_PAGEUP,      # Page Up
    "Next": pygame.K_PAGEDOWN,     # Page Down
    
    # Function keys
    "F1": pygame.K_F1, "F2": pygame.K_F2, "F3": pygame.K_F3,
    "F4": pygame.K_F4, "F5": pygame.K_F5, "F6": pygame.K_F6,
    "F7": pygame.K_F7, "F8": pygame.K_F8, "F9": pygame.K_F9,
    "F10": pygame.K_F10, "F11": pygame.K_F11, "F12": pygame.K_F12,
    "F13": pygame.K_F13, "F14": pygame. K_F14, "F15": pygame.K_F15,
    
    # Lock keys
    "Num_Lock": pygame.K_NUMLOCK,
    "Caps_Lock": pygame.K_CAPSLOCK,
    "Scroll_Lock": pygame.K_SCROLLOCK,
    
    # Modifiers - Right
    "Shift_R": pygame.K_RSHIFT,
    "Control_R": pygame.K_RCTRL,
    "Alt_R": pygame.K_RALT,
    "Meta_R": pygame.K_RMETA,
    "Super_R": pygame.K_RSUPER,
    
    # Modifiers - Left
    "Shift_L": pygame.K_LSHIFT,
    "Control_L": pygame.K_LCTRL,
    "Alt_L": pygame.K_LALT,
    "Meta_L": pygame.K_LMETA,
    "Super_L": pygame.K_LSUPER,
    
    # Special system keys
    "Mode_switch": pygame.K_MODE,
    "Help": pygame. K_HELP,
    "Print": pygame.K_PRINT,
    "Sys_Req": pygame.K_SYSREQ,
    "Break": pygame.K_BREAK,
    "Menu": pygame.K_MENU,
    "Power": pygame.K_POWER,
    
    # Punctuation and symbols
    "exclam": pygame.K_EXCLAIM,          # !
    "quotedbl": pygame.K_QUOTEDBL,       # "
    "numbersign": pygame. K_HASH,         # #
    "dollar": pygame.K_DOLLAR,           # $
    "ampersand": pygame. K_AMPERSAND,     # &
    "apostrophe": pygame.K_QUOTE,        # '
    "quoteright": pygame.K_QUOTE,        # '
    "parenleft": pygame.K_LEFTPAREN,     # (
    "parenright": pygame. K_RIGHTPAREN,   # )
    "asterisk": pygame.K_ASTERISK,       # *
    "plus": pygame.K_PLUS,               # +
    "comma": pygame.K_COMMA,             # ,
    "minus": pygame. K_MINUS,             # -
    "period": pygame.K_PERIOD,           # . 
    "slash": pygame.K_SLASH,             # /
    "colon": pygame.K_COLON,             # :
    "semicolon": pygame. K_SEMICOLON,     # ;
    "less": pygame.K_LESS,               # <
    "equal": pygame. K_EQUALS,            # =
    "greater": pygame.K_GREATER,         # >
    "question": pygame.K_QUESTION,       # ?
    "at": pygame.K_AT,                   # @
    "bracketleft": pygame.K_LEFTBRACKET, # [
    "backslash": pygame.K_BACKSLASH,     # \
    "bracketright": pygame.K_RIGHTBRACKET, # ]
    "asciicircum": pygame.K_CARET,       # ^
    "underscore": pygame. K_UNDERSCORE,  # _
    
    # International
    "Euro": pygame.K_EURO,
    
    # Android (if applicable)
    "AC_Back": pygame.K_AC_BACK,
}

# Mouse button mappings
TK_TO_PYGAME_MOUSE_MAP = {
    1: 1,  # Left click
    2: 2,  # Middle click
    3: 3,  # Right click
}

# File type icons
FILE_ICONS = {
    '.py': '📜',
    '. json': '📋',
    '.txt': '📄',
    '.md': '📝',
    '.png': '🖼️',
    '.jpg': '🖼️',
    '.jpeg': '🖼️',
    '.wav': '🔊',
    '.mp3': '🎵',
    '. ogg': '🎵',
    '.ttf': '🔤',
    '.otf': '🔤',
}