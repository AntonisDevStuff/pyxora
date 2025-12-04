import tkinter as tk
import sys
from datetime import datetime

from ..constants import COLORS


class OutputRedirector:
    """Redirects stdout/stderr to the console widget."""

    def __init__(self, callback):
        """
        Initialize output redirector.

        Args:
            callback: Function to call with output text
        """
        self.callback = callback
        self.buffer = ""

    def write(self, msg):
        """Write message to buffer and callback."""
        self.buffer += msg
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self.callback(line + '\n')

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer:
            self.callback(self.buffer)
            self.buffer = ""


class ConsolePanel:
    """
    Console panel for displaying program output.
    """

    def __init__(self, parent):
        """
        Initialize the console panel.

        Args:
            parent: The parent widget
        """
        self.visible = True
        self._update_pending = False
        self._pending_lines = []

        # Main container - match preview padding
        self.container = tk. Frame(parent, bg=COLORS["bg_panel"])
        self.container.pack(fill=tk.BOTH, padx=12, pady=12)

        self._create_widgets()
        self._redirect_output()
        self._show_welcome_message()

    def append(self, text):
        """
        Append text to console.

        Args:
            text: Text to append
        """
        self._pending_lines.append(text)

        # Schedule batch update if not already pending
        if not self._update_pending:
            self._update_pending = True
            self.text.after(50, self._batch_update)

    def clear(self):
        """Clear all console output."""
        self._pending_lines.clear()
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
        self._show_welcome_message()

    def toggle(self):
        """Toggle console visibility."""
        if self.visible:
            # Hide console
            self.text_frame.pack_forget()
            self.container.pack_forget()
            self.container.pack(fill=tk.X, padx=12, pady=12)
            self.toggle_btn. config(text="▲")
            self.visible = False
        else:
            # Show console
            self.container.pack_forget()
            self.container.pack(fill=tk.BOTH, padx=12, pady=12)
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text="▼")
            self.visible = True

    def _create_widgets(self):
        """Create console widgets."""
        header_frame = tk. Frame(self.container, bg=COLORS["bg_panel"])
        header_frame.pack(fill=tk.X)

        left_spacer = tk.Frame(header_frame, bg=COLORS["bg_panel"], width=80)
        left_spacer. pack(side=tk.LEFT)

        header_label = tk.Label(
            header_frame,
            text="Console",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_panel"],
            fg=COLORS["text"],
            anchor="center"
        )
        header_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.toggle_btn = tk.Button(
            header_frame,
            text="▼",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            relief=tk.FLAT,
            command=self.toggle,
            cursor="hand2",
            padx=8,
            pady=2,
            bd=0,
            takefocus=False
        )
        self.toggle_btn.pack(side=tk.RIGHT)

        clear_btn = tk.Button(
            header_frame,
            text="🗑 Clear",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_gray"],
            relief=tk. FLAT,
            command=self.clear,
            cursor="hand2",
            padx=8,
            pady=2,
            bd=0,
            takefocus=False
        )
        clear_btn.pack(side=tk.RIGHT, padx=4)

        separator = tk.Frame(self.container, bg=COLORS["border"], height=1)
        separator.pack(fill=tk.X, pady=(8, 6))

        self.text_frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        self.text_frame. pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)

        self.text = tk. Text(
            self.text_frame,
            height=8,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_dim"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            state=tk.DISABLED,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bd=0,
            padx=16,
            pady=10,
            takefocus=False,
            spacing1=3,
            spacing3=3
        )

        scrollbar.config(command=self. text.yview)
        scrollbar.pack(side=tk. RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk. BOTH, expand=True)

    def _show_welcome_message(self):
        """Show welcome message in console."""
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"> Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.text.insert(tk.END, "> Ready to capture your game's output...\n\n")
        self.text.config(state=tk.DISABLED)

    def _redirect_output(self):
        """Redirect stdout and stderr to console."""
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # Redirect output to console (bad for debugging)
        sys.stdout = OutputRedirector(lambda text: self.append(text))
        sys.stderr = OutputRedirector(lambda text: self.append(text))

    def _batch_update(self):
        """Batch update multiple lines at once to prevent flickering."""
        if not self._pending_lines:
            self._update_pending = False
            return

        self.text. config(state=tk.NORMAL)

        # Process all pending lines
        lines_to_process = self._pending_lines[:]
        self._pending_lines. clear()

        for text in lines_to_process:
            # Split text into lines
            lines = text.split('\n')

            for i, line in enumerate(lines):
                # Skip empty last line from split
                if not line and i == len(lines) - 1:
                    continue

                # Add line with > prefix
                if line.strip():
                    self.text.insert(tk.END, f"> {line}\n")
                else:
                    self.text.insert(tk.END, "\n")

        # Auto-scroll to bottom
        self.text.see(tk. END)
        self.text.config(state=tk.DISABLED)

        self._update_pending = False
