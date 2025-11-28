import tkinter as tk
from tkinter import scrolledtext, font as tkfont, messagebox
from pathlib import Path
import re

from ..constants import COLORS

# Python keywords
keywords = {
    'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 
    'except', 'finally', 'with', 'as', 'import', 'from', 'return',
    'yield', 'break', 'continue', 'pass', 'raise', 'assert', 'del',
    'lambda', 'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False',
    'async', 'await', 'global', 'nonlocal'
}

# Python builtins
builtins = {
    'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list',
    'dict', 'set', 'tuple', 'type', 'isinstance', 'super', 'self',
    'open', 'input', 'map', 'filter', 'zip', 'enumerate', 'abs',
    'min', 'max', 'sum', 'all', 'any', 'sorted', 'reversed'
}


class CodeEditorPanel:
    """
    Simple multi-file code editor with syntax highlighting.      
    """
    
    def __init__(self, parent):
        """
        Initialize the code editor panel.   
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.open_files = {}  # {file_path: text_widget}
        self.current_file = None
        self.search_dialog = None
        self.modified_files = set()
        self.original_contents = {}  
        self.all_search_positions = [] 
        self.current_search_index = -1 
        
        # Main container
        self.container = tk. Frame(parent, bg=COLORS["bg_dark"])
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create UI
        self._create_tab_bar()
        self._create_editor_area()
    
    def check_unsaved_changes(self):
        """
        Check if there are any unsaved changes in open files. 
        Returns True if it's safe to proceed, False if user cancelled. 
        Use this before switching scenes. 
        """
        if not self.modified_files:
            return True
        
        # Get list of modified file names
        modified_names = [Path(fp). name for fp in self.modified_files]
        file_list = "\n".join(modified_names)
        
        response = messagebox.askyesno(
            "Unsaved Changes",
            f"You have unsaved changes in:\n\n{file_list}\n\nDo you want to save all changes before continuing? ",
            icon='warning'
        )
        
        if response:  # Yes, save all
            for file_path in list(self.modified_files):
                self._save_file(file_path)
            return True
        else:  # No, don't save - RESTORE ORIGINAL CONTENT
            for file_path in list(self.modified_files):
                if file_path in self.open_files and file_path in self.original_contents:
                    text_widget = self.open_files[file_path]
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", self.original_contents[file_path])
                    self.modified_files.discard(file_path)
                    self._update_tab_modified_indicator(file_path)
            return True

    def open_file(self, file_path):
        """
        Open a file in the editor.
        
        Args:
            file_path: Path to the file to open
        """
        file_path = str(file_path)
        
        # If file already open, just switch to it
        if file_path in self.open_files:
            self._switch_to_file(file_path)
            return
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            messagebox. showerror("Error", f"Error opening file: {e}")
            return
        
        # Store original content
        self.original_contents[file_path] = content
        
        # Hide placeholder
        self.placeholder.pack_forget()
        
        # Create text widget for this file
        text_widget = scrolledtext.ScrolledText(
            self.editor_frame,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_dim"],
            insertbackground=COLORS["text"],  # Cursor color
            font=("Consolas", 11),
            wrap=tk.NONE,
            undo=True,
            maxundo=-1,
            bd=0,
            padx=10,
            pady=10,
            selectbackground=COLORS["border_light"],
            selectforeground=COLORS["text"]
        )
        
        # Insert content
        text_widget.insert("1.0", content)
        
        # Bind events
        text_widget.bind("<KeyRelease>", lambda e: self._on_text_change(file_path))
        text_widget.bind("<MouseWheel>", lambda e: self._sync_scroll(e, file_path))
        text_widget.bind("<Button-4>", lambda e: self._sync_scroll(e, file_path))
        text_widget.bind("<Button-5>", lambda e: self._sync_scroll(e, file_path))
        text_widget.bind("<<Modified>>", lambda e: self._on_modified(file_path))
        text_widget.bind("<Button-1>", lambda e: self._clear_search_highlights())
        
        # Bind keyboard shortcuts
        self._bind_shortcuts(text_widget, file_path)
        
        # Apply syntax highlighting
        self._highlight_syntax(text_widget, file_path)
        
        # Store widget - DON'T PACK YET
        self.open_files[file_path] = text_widget
        
        # Create tab
        self._create_tab(file_path)
        
        # Switch to this file
        self._switch_to_file(file_path)
        
        # Update line numbers
        self._update_line_numbers(file_path)
    
    def _create_tab_bar(self):
        """Create tab bar for open files."""
        self.tab_bar = tk.Frame(self. container, bg=COLORS["bg_panel"], height=40)
        self.tab_bar.pack(side=tk.TOP, fill=tk.X)
        self.tab_bar.pack_propagate(False)
        
        # Tab container (scrollable)
        self.tab_container = tk.Frame(self.tab_bar, bg=COLORS["bg_panel"])
        self.tab_container.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)
        
        # Save button
        self.save_btn = tk.Button(
            self.tab_bar,
            text="💾 Save",
            font=("Segoe UI", 10),
            bg=COLORS["button_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._save_current_file
        )
        self.save_btn.pack(side=tk.RIGHT, padx=8)
        
        # Hover effects for save button
        self.save_btn.bind("<Enter>", lambda e: self. save_btn.config(bg=COLORS["button_hover"]))
        self.save_btn. bind("<Leave>", lambda e: self.save_btn.config(bg=COLORS["button_bg"]))
        
        self.tab_buttons = {}
    
    def _create_editor_area(self):
        """Create main editor area."""
        # Editor frame
        self.editor_frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        self.editor_frame.pack(fill=tk. BOTH, expand=True)
        
        # Line numbers frame
        self.line_numbers_frame = tk.Frame(self. editor_frame, bg=COLORS["bg_panel"], width=50)
        self.line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Line numbers text widget
        self.line_numbers = tk.Text(
            self.line_numbers_frame,
            width=4,
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            font=("Consolas", 11),
            state=tk.DISABLED,
            takefocus=False,
            bd=0,
            padx=8,
            pady=10,
            cursor="arrow"
        )
        self.line_numbers.pack(fill=tk. BOTH, expand=True)
        
        # Placeholder for when no file is open
        self.placeholder = tk.Frame(self.editor_frame, bg=COLORS["bg_dark"])
        self.placeholder.pack(fill=tk.BOTH, expand=True)
        
        placeholder_label = tk.Label(
            self.placeholder,
            text="📝\n\nNo File Open\n\nClick a file in Explorer to open it",
            font=("Segoe UI", 16),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_gray"],
            justify=tk.CENTER
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _is_file_modified(self, file_path):
        """Check if file has been modified."""
        if file_path not in self.open_files:
            return False
        
        current_content = self.open_files[file_path]. get("1.0", tk.END)
        # Remove trailing newline that Text widget adds
        if current_content.endswith('\n'):
            current_content = current_content[:-1]
        
        original_content = self.original_contents.get(file_path, "")
        return current_content != original_content
    
    def _update_tab_modified_indicator(self, file_path):
        """Update the modified indicator (~) in the tab."""
        if file_path not in self.tab_buttons:
            return
        
        file_name = Path(file_path).name
        tab_frame, tab_btn, close_btn = self.tab_buttons[file_path]
        
        is_modified = self._is_file_modified(file_path)
        
        if is_modified:
            tab_btn.config(text=f"  ~ {file_name}  ")
            self.modified_files.add(file_path)
        else:
            tab_btn. config(text=f"  {file_name}  ")
            self.modified_files.discard(file_path)
    
    def _bind_shortcuts(self, text_widget, file_path):
        """Bind keyboard shortcuts to text widget."""
        # Save: Ctrl+S
        text_widget.bind("<Control-s>", lambda e: self._save_file_shortcut(file_path))
        
        # Find: Ctrl+F
        text_widget.bind("<Control-f>", lambda e: self._show_search_dialog())
        
        # Select All: Ctrl+A
        text_widget.bind("<Control-a>", lambda e: self._select_all(text_widget))
        
        # Copy, Cut, Paste
        text_widget.bind("<Control-c>", lambda e: self._copy(text_widget))
        text_widget.bind("<Control-x>", lambda e: self._cut(text_widget))
        text_widget.bind("<Control-v>", lambda e: self._paste(text_widget, file_path))
        
        # Undo: Ctrl+Z (with safety check)
        text_widget. bind("<Control-z>", lambda e: self._undo(text_widget))
        
        # Redo: Ctrl+Y
        text_widget.bind("<Control-y>", lambda e: self._redo(text_widget))
        
        # Tab indentation
        text_widget.bind("<Tab>", lambda e: self._insert_tab(text_widget))
        text_widget.bind("<Shift-Tab>", lambda e: self._remove_indentation(text_widget))
        
        # Convert to string: Alt+S
        text_widget. bind("<Alt-s>", lambda e: self._convert_to_type(text_widget, "str"))
        
        # Convert to int: Alt+I
        text_widget.bind("<Alt-i>", lambda e: self._convert_to_type(text_widget, "int"))
        
        # Convert to float: Alt+F
        text_widget.bind("<Alt-f>", lambda e: self._convert_to_type(text_widget, "float"))
        
        # Convert to bool: Alt+B
        text_widget. bind("<Alt-b>", lambda e: self._convert_to_type(text_widget, "bool"))
    
    def _convert_to_type(self, text_widget, type_name):
        """Convert selected text to a specific type wrapper."""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            converted = f"{type_name}({selected_text})"
            text_widget.delete(tk. SEL_FIRST, tk. SEL_LAST)
            text_widget.insert(tk. INSERT, converted)
        except tk.TclError:
            pass  # No selection
        
        return "break"
    
    def _save_file_shortcut(self, file_path):
        """Handle Ctrl+S shortcut."""
        self._save_file(file_path)
        return "break"
    
    def _save_current_file(self):
        """Save the currently open file (called by save button)."""
        if self.current_file:
            self._save_file(self.current_file)
            messagebox.showinfo("Saved", f"File saved successfully!")
    
    def _select_all(self, text_widget):
        """Select all text in the widget."""
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)
        return "break"
    
    def _copy(self, text_widget):
        """Copy selected text to clipboard."""
        try:
            selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.container.clipboard_clear()
            self.container.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection
        return "break"
    
    def _cut(self, text_widget):
        """Cut selected text to clipboard."""
        try:
            selected_text = text_widget. get(tk.SEL_FIRST, tk.SEL_LAST)
            self.container. clipboard_clear()
            self.container.clipboard_append(selected_text)
            text_widget.delete(tk. SEL_FIRST, tk. SEL_LAST)
        except tk.TclError:
            pass  # No selection
        return "break"
    
    def _paste(self, text_widget, file_path):
        """Paste text from clipboard."""
        try:
            clipboard_text = self.container.clipboard_get()
            try:
                # Delete selected text first if any
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
            text_widget.insert(tk.INSERT, clipboard_text)
            self._highlight_syntax(text_widget, file_path)
        except tk.TclError:
            pass
        return "break"
    
    def _undo(self, text_widget):
        """Undo last action with safety check."""
        try:
            # Save current content
            current_content = text_widget.get("1.0", "end-1c")
            
            # Check if there's undo history by trying to peek at undo stack
            # We'll do a test: mark current position, try undo, then check
            if current_content. strip() == "":
                # If already empty, don't undo
                return "break"
            
            # Try undo
            text_widget.edit_undo()
            
            # Check what happened
            new_content = text_widget.get("1.0", "end-1c")
            
            # If undo resulted in empty content but we had content before, redo it
            if new_content.strip() == "" and current_content.strip() != "":
                text_widget.edit_redo()
        except tk.TclError:
            pass
        return "break"

    
    def _redo(self, text_widget):
        """Redo last undone action."""
        try:
            text_widget.edit_redo()
        except tk.TclError:
            pass
        return "break"
    
    def _insert_tab(self, text_widget):
        """Insert 4 spaces instead of tab."""
        text_widget.insert(tk.INSERT, "    ")
        return "break"
    
    def _remove_indentation(self, text_widget):
        """Remove indentation (4 spaces)."""
        try:
            # Get current line
            line_num = text_widget.index(tk. INSERT).split('.')[0]
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_text = text_widget.get(line_start, line_end)
            
            # Check if line starts with spaces
            if line_text.startswith("    "):
                text_widget.delete(line_start, f"{line_num}.4")
            elif line_text.startswith("   "):
                text_widget. delete(line_start, f"{line_num}.3")
            elif line_text.startswith("  "):
                text_widget.delete(line_start, f"{line_num}.2")
            elif line_text.startswith(" "):
                text_widget.delete(line_start, f"{line_num}.1")
        except:
            pass
        return "break"
    
    def _clear_search_highlights(self):
        """Clear all search highlights."""
        if not self.current_file or self.current_file not in self. open_files:
            return
        
        text_widget = self.open_files[self.current_file]
        text_widget.tag_remove("search_highlight", "1.0", tk. END)
        text_widget.tag_remove("search_current", "1.0", tk. END)
        self.all_search_positions = []
        self.current_search_index = -1
    
    def _show_search_dialog(self):
        """Show search dialog with Find All functionality."""
        if self.search_dialog and self.search_dialog.winfo_exists():
            self.search_dialog.focus()
            return "break"
        
        # Create search dialog
        self.search_dialog = tk.Toplevel(self.container)
        self.search_dialog.title("Find")
        self.search_dialog. geometry("450x200")
        self.search_dialog.configure(bg=COLORS["bg_panel"])
        self.search_dialog.resizable(False, False)
        
        # Search frame
        search_frame = tk. Frame(self.search_dialog, bg=COLORS["bg_panel"])
        search_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Search label
        search_label = tk. Label(
            search_frame,
            text="Find:",
            font=("Segoe UI", 11),
            bg=COLORS["bg_panel"],
            fg=COLORS["text"]
        )
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Search entry
        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 11),
            bg=COLORS["bg_dark"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(fill=tk. X, ipady=8, pady=(0, 10))
        self.search_entry.focus()
        
        # Bind Enter key to find next
        self.search_entry. bind("<Return>", lambda e: self._find_next())
        
        # Match count label
        self.match_count_label = tk.Label(
            search_frame,
            text="",
            font=("Segoe UI", 9),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"]
        )
        self.match_count_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = tk.Frame(search_frame, bg=COLORS["bg_panel"])
        button_frame.pack(fill=tk.X)
        
        # Find All button
        find_all_btn = tk.Button(
            button_frame,
            text="Find All",
            font=("Segoe UI", 10),
            bg=COLORS["button_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._find_all
        )
        find_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Find next button
        find_next_btn = tk.Button(
            button_frame,
            text="Find Next",
            font=("Segoe UI", 10),
            bg=COLORS["button_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._find_next
        )
        find_next_btn.pack(side=tk. LEFT, padx=(0, 10))
        
        # Find previous button
        find_prev_btn = tk.Button(
            button_frame,
            text="Find Previous",
            font=("Segoe UI", 10),
            bg=COLORS["button_bg"],
            fg=COLORS["text"],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self._find_previous
        )
        find_prev_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10),
            bg=COLORS["bg_dark"],
            fg="#ff5555",
            relief=tk. FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.search_dialog.destroy
        )
        close_btn.pack(side=tk.LEFT)
        
        return "break"
    
    def _find_all(self):
        """Find and highlight all occurrences of the search term."""
        if not self.current_file or self.current_file not in self.open_files:
            return
        
        search_term = self.search_entry.get()
        if not search_term:
            return
        
        text_widget = self.open_files[self.current_file]
        
        # Clear previous highlights
        text_widget.tag_remove("search_highlight", "1. 0", tk.END)
        text_widget.tag_remove("search_current", "1.0", tk.END)
        
        # Configure highlight tags
        text_widget.tag_config("search_highlight", 
                              background=COLORS["search_highlight"], 
                              foreground=COLORS["search_highlight_fg"])
        text_widget.tag_config("search_current", 
                              background=COLORS["search_current"], 
                              foreground=COLORS["search_current_fg"])
        
        # Find all occurrences
        self.all_search_positions = []
        pos = "1.0"
        
        while True:
            pos = text_widget.search(search_term, pos, tk.END)
            if not pos:
                break
            
            end_pos = f"{pos}+{len(search_term)}c"
            self.all_search_positions.append((pos, end_pos))
            text_widget.tag_add("search_highlight", pos, end_pos)
            pos = end_pos
        
        # Update match count
        match_count = len(self.all_search_positions)
        if match_count > 0:
            self.match_count_label.config(text=f"Found {match_count} match(es)")
            # Highlight first match
            self. current_search_index = 0
            first_pos, first_end = self.all_search_positions[0]
            text_widget.tag_remove("search_current", "1.0", tk.END)
            text_widget.tag_add("search_current", first_pos, first_end)
            text_widget.see(first_pos)
        else:
            self.match_count_label.config(text="No matches found")
            self.all_search_positions = []
            self.current_search_index = -1
    
    def _find_next(self):
        """Find next occurrence of search term."""
        if not self.current_file or self. current_file not in self.open_files:
            return
        
        search_term = self. search_entry.get()
        if not search_term:
            return
        
        text_widget = self.open_files[self.current_file]
        
        # If we have all positions from Find All, use them
        if self.all_search_positions:
            # Move to next match
            self.current_search_index = (self.current_search_index + 1) % len(self. all_search_positions)
            pos, end_pos = self. all_search_positions[self. current_search_index]
            
            # Update current highlight
            text_widget.tag_remove("search_current", "1.0", tk.END)
            text_widget.tag_add("search_current", pos, end_pos)
            text_widget.see(pos)
            
            # Update match count
            self.match_count_label.config(
                text=f"Match {self.current_search_index + 1} of {len(self.all_search_positions)}"
            )
        else:
            # No Find All performed, just do Find All first
            self._find_all()
        
        return "break"
    
    def _find_previous(self):
        """Find previous occurrence of search term."""
        if not self.current_file or self. current_file not in self.open_files:
            return
        
        search_term = self. search_entry.get()
        if not search_term:
            return
        
        text_widget = self.open_files[self.current_file]
        
        # If we have all positions from Find All, use them
        if self.all_search_positions:
            # Move to previous match
            self.current_search_index = (self.current_search_index - 1) % len(self.all_search_positions)
            pos, end_pos = self.all_search_positions[self.current_search_index]
            
            # Update current highlight
            text_widget.tag_remove("search_current", "1.0", tk.END)
            text_widget.tag_add("search_current", pos, end_pos)
            text_widget.see(pos)
            
            # Update match count
            self.match_count_label.config(
                text=f"Match {self.current_search_index + 1} of {len(self.all_search_positions)}"
            )
        else:
            # No Find All performed, just do Find All first
            self._find_all()
        
        return "break"
    
    def _create_tab(self, file_path):
        """Create a tab button for the file."""
        file_name = Path(file_path).name
        
        tab_frame = tk.Frame(self.tab_container, bg=COLORS["bg_panel"])
        tab_frame.pack(side=tk. LEFT, padx=2, anchor=tk.W)
        
        # Tab button
        tab_btn = tk. Button(
            tab_frame,
            text=f"  {file_name}  ",
            font=("Segoe UI", 10),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_dim"],
            relief=tk. FLAT,
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
            command=lambda: self._switch_to_file(file_path)
        )
        tab_btn.pack(side=tk.LEFT)
        
        # Close button
        close_btn = tk.Button(
            tab_frame,
            text="×",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["bg_dark"],
            fg=COLORS["text_gray"],
            relief=tk. FLAT,
            bd=0,
            padx=4,
            pady=4,
            cursor="hand2",
            command=lambda: self._close_file(file_path)
        )
        close_btn.pack(side=tk.LEFT)
        
        self.tab_buttons[file_path] = (tab_frame, tab_btn, close_btn)
        
        # Update tab styles
        self._update_tab_styles()
    
    def _switch_to_file(self, file_path):
        """Switch to display a different file WITHOUT flash."""
        # Hide current file FIRST
        if self.current_file and self.current_file in self. open_files:
            self. open_files[self.current_file].pack_forget()
        
        self.current_file = file_path
        
        self.open_files[file_path]. pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Force immediate update to prevent flash
        self. open_files[file_path].update_idletasks()
        
        self.open_files[file_path].focus_set()
        
        self._clear_search_highlights()
        
        self._update_line_numbers(file_path)
        
        self._update_tab_styles()
    
    def _close_file(self, file_path):
        """Close a file and remove its tab."""
        # Save before closing (auto-save)
        self._save_file(file_path)
        
        if file_path in self.open_files:
            text_widget = self.open_files[file_path]
            text_widget.pack_forget()
            text_widget.destroy()
            del self.open_files[file_path]
        
        self.modified_files.discard(file_path)
        if file_path in self.original_contents:
            del self.original_contents[file_path]
        
        # Remove tab
        if file_path in self.tab_buttons:
            tab_frame, tab_btn, close_btn = self.tab_buttons[file_path]
            tab_frame.pack_forget()
            tab_btn.destroy()
            close_btn.destroy()
            tab_frame.destroy()
            del self.tab_buttons[file_path]
        
        # Force redraw
        self.tab_container.update_idletasks()
        self.tab_bar.update_idletasks()
        
        # Switch to another file
        if file_path == self.current_file:
            self.current_file = None
            
            if self.open_files:
                # Switch to last opened file
                next_file = list(self.open_files.keys())[-1]
                self._switch_to_file(next_file)
            else:
                self.placeholder.pack(fill=tk.BOTH, expand=True)
        
        self.editor_frame.update_idletasks()
    
    def _save_file(self, file_path):
        """Save file content."""
        if file_path not in self.open_files:
            return
        
        try:
            content = self.open_files[file_path]. get("1.0", tk.END)
            # Remove trailing newline that Text widget adds
            if content.endswith('\n'):
                content = content[:-1]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update original content after saving
            self.original_contents[file_path] = content
            self.modified_files.discard(file_path)
            
            # Update tab to remove modified indicator
            self._update_tab_modified_indicator(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")
    
    def _update_tab_styles(self):
        """Update tab button styles based on active file."""
        for file_path, (_, tab_btn, close_btn) in self.tab_buttons.items():
            if file_path == self.current_file:
                tab_btn.config(bg=COLORS["button_bg"], fg=COLORS["text"])
                close_btn.config(bg=COLORS["button_bg"], fg="#ff5555")
            else:
                tab_btn.config(bg=COLORS["bg_dark"], fg=COLORS["text_dim"])
                close_btn.config(bg=COLORS["bg_dark"], fg="#ff5555") 
    
    def _on_text_change(self, file_path):
        """Handle text changes for syntax highlighting."""
        if file_path not in self.open_files:
            return
        
        text_widget = self.open_files[file_path]
        self._highlight_syntax(text_widget, file_path)
        self._update_line_numbers(file_path)
        self._update_tab_modified_indicator(file_path)
    
    def _on_modified(self, file_path):
        """Handle text modification."""
        if file_path not in self.open_files:
            return
        
        text_widget = self. open_files[file_path]
        if text_widget.edit_modified():
            self._update_tab_modified_indicator(file_path)
            text_widget.edit_modified(False)
    
    def _highlight_syntax(self, text_widget, file_path):
        """Apply syntax highlighting to the text widget."""
        # Determine file type and apply appropriate highlighting
        if file_path. endswith('.py'):
            self._highlight_python(text_widget)
        elif file_path.endswith('.json'):
            self._highlight_json(text_widget)
    
    def _highlight_python(self, text_widget):
        """Apply Python syntax highlighting with enhanced colors."""
        # Remove existing tags
        for tag in text_widget.tag_names():
            if tag. startswith('syntax_'):
                text_widget. tag_remove(tag, "1.0", tk.END)
        
        content = text_widget.get("1.0", tk.END)
        
        # Configure tags
        text_widget.tag_config('syntax_keyword', foreground=COLORS['syntax_keyword'])
        text_widget.tag_config('syntax_builtin', foreground=COLORS['syntax_builtin'])
        text_widget.tag_config('syntax_string', foreground=COLORS['syntax_string'])
        text_widget.tag_config('syntax_comment', foreground=COLORS['syntax_comment'])
        text_widget.tag_config('syntax_number', foreground=COLORS['syntax_number'])
        text_widget.tag_config('syntax_decorator', foreground=COLORS['syntax_decorator'])
        text_widget.tag_config('syntax_function', foreground=COLORS['syntax_function'])
        text_widget.tag_config('syntax_private_method', foreground=COLORS['syntax_private_method'])
        text_widget.tag_config('syntax_main_module', foreground=COLORS['syntax_main_module'])
        text_widget.tag_config('syntax_module_attr', foreground=COLORS['syntax_module_attr'])
        text_widget.tag_config('syntax_class_name', foreground=COLORS['syntax_class_name'])
        
        # Highlight comments (highest priority)
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_comment', start_idx, end_idx)
        
        # Highlight strings
        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1. 0+{match.end()}c"
            text_widget.tag_add('syntax_string', start_idx, end_idx)
        
        # Highlight numbers
        for match in re.finditer(r'\b\d+\. ?\d*\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_number', start_idx, end_idx)
        
        # Highlight decorators
        for match in re. finditer(r'@\w+', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget. tag_add('syntax_decorator', start_idx, end_idx)
        
        # Highlight class names (after 'class' keyword)
        for match in re.finditer(r'\bclass\s+(\w+)', content):
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match.end(1)}c"
            text_widget.tag_add('syntax_class_name', start_idx, end_idx)
        
        # Highlight private/special methods (functions starting with _)
        for match in re.finditer(r'\bdef\s+(_\w+)', content):
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match.end(1)}c"
            text_widget.tag_add('syntax_private_method', start_idx, end_idx)
        
        # Highlight regular function definitions (non-private)
        for match in re.finditer(r'\bdef\s+([a-zA-Z]\w*)', content):
            func_name = match.group(1)
            if not func_name.startswith('_'):
                start_idx = f"1.0+{match. start(1)}c"
                end_idx = f"1. 0+{match.end(1)}c"
                text_widget.tag_add('syntax_function', start_idx, end_idx)
        
        # Highlight pyxora attributes/methods (e. g., pyxora.Scene, pyxora.Object)
        for match in re.finditer(r'pyxora\.([A-Z_a-z]\w*)', content):
            # Get the line this match is on
            line_start_pos = content.rfind('\n', 0, match.start()) + 1
            line_end_pos = content.find('\n', match.start())
            if line_end_pos == -1:
                line_end_pos = len(content)
            
            line_content = content[line_start_pos:line_end_pos].strip()
            
            # Skip if this is in an import statement or comment
            if line_content.startswith('import ') or line_content.startswith('from ') or line_content.startswith('#'):
                continue
            
            # Highlight the attribute name (Scene, Object, etc.)
            start_idx = f"1.0+{match.start(1)}c"
            end_idx = f"1.0+{match. end(1)}c"
            text_widget.tag_add('syntax_module_attr', start_idx, end_idx)

        # Highlight main module usage (ONLY pyxora) - AFTER attributes so it doesn't override
        for match in re.finditer(r'\bpyxora\b', content):
            # Get the line this match is on
            line_start_pos = content. rfind('\n', 0, match.start()) + 1
            line_end_pos = content.find('\n', match.start())
            if line_end_pos == -1:
                line_end_pos = len(content)
            
            line_content = content[line_start_pos:line_end_pos].strip()
            
            # Skip if this is in an import statement or comment
            if line_content.startswith('import ') or line_content.startswith('from ') or line_content.startswith('#'):
                continue
            
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_main_module', start_idx, end_idx)


        # Highlight keywords
        for keyword in keywords:
            for match in re.finditer(rf'\b{keyword}\b', content):
                start_idx = f"1.0+{match. start()}c"
                end_idx = f"1.0+{match.end()}c"
                text_widget.tag_add('syntax_keyword', start_idx, end_idx)
        
        # Highlight builtins
        for builtin in builtins:
            for match in re.finditer(rf'\b{builtin}\b', content):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                text_widget.tag_add('syntax_builtin', start_idx, end_idx)
        
        # Set tag priority
        text_widget.tag_raise('syntax_main_module')
        text_widget.tag_raise('syntax_class_name')
        text_widget.tag_raise('syntax_private_method')
        text_widget.tag_raise('syntax_function')
    
    def _highlight_json(self, text_widget):
        """Apply JSON syntax highlighting with proper color priority."""
        # Remove existing tags
        for tag in text_widget. tag_names():
            if tag.startswith('syntax_'):
                text_widget.tag_remove(tag, "1.0", tk.END)
        
        content = text_widget.get("1.0", tk.END)
        
        # Configure tags with priority (lower priority first)
        text_widget.tag_config('syntax_json_null', foreground=COLORS['syntax_json_null'])
        text_widget.tag_config('syntax_json_boolean', foreground=COLORS['syntax_json_boolean'])
        text_widget.tag_config('syntax_json_number', foreground=COLORS['syntax_json_number'])
        text_widget.tag_config('syntax_json_string', foreground=COLORS['syntax_json_string'])
        text_widget.tag_config('syntax_json_key', foreground=COLORS['syntax_json_key'])
        
        # Highlight numbers FIRST (lowest priority)
        for match in re.finditer(r'-?\b\d+\.?\d*([eE][+-]?\d+)?\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_json_number', start_idx, end_idx)
        
        # Highlight booleans
        for match in re.finditer(r'\b(true|false)\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_json_boolean', start_idx, end_idx)
        
        # Highlight null
        for match in re.finditer(r'\bnull\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            text_widget.tag_add('syntax_json_null', start_idx, end_idx)
        
        # Highlight ALL strings (will override numbers inside strings)
        for match in re.finditer(r'"(?:[^"\\]|\\.)*"', content):
            start_idx = f"1. 0+{match.start()}c"
            end_idx = f"1.0+{match. end()}c"
            text_widget.tag_add('syntax_json_string', start_idx, end_idx)
        
        # Highlight JSON keys LAST (highest priority - will override string color for keys)
        for match in re.finditer(r'"(?:[^"\\]|\\.)*"\s*:', content):
            start_idx = f"1. 0+{match.start()}c"
            # Don't include the colon in the highlight
            end_idx = f"1.0+{match.end()-1}c"
            # Remove the string tag from this range first
            text_widget.tag_remove('syntax_json_string', start_idx, end_idx)
            # Then add the key tag
            text_widget.tag_add('syntax_json_key', start_idx, end_idx)
        
        # Set tag priority (higher priority tags override lower ones)
        text_widget.tag_raise('syntax_json_key')
        text_widget.tag_raise('syntax_json_string')
        text_widget.tag_raise('syntax_json_boolean')
        text_widget.tag_raise('syntax_json_null')
    
    def _update_line_numbers(self, file_path):
        """Update line numbers display."""
        if file_path not in self.open_files or file_path != self.current_file:
            return
        
        text_widget = self.open_files[file_path]
        
        # Get number of lines
        line_count = int(text_widget.index('end-1c').split('.')[0])
        
        # Generate line numbers
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        # Update line numbers widget
        self.line_numbers. config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers. insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)
        
        # Sync scroll position
        self.line_numbers.yview_moveto(text_widget.yview()[0])
    
    def _sync_scroll(self, event, file_path):
        """Sync line numbers scroll with text widget."""
        if file_path != self.current_file:
            return
        
        # Update line numbers after a short delay
        self.container.after(10, lambda: self._update_line_numbers(file_path))