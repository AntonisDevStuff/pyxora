"""
Main entry point for the Pyxora editor.
"""
import tkinter as tk
from . ui.window import EditorWindow
from .. projects.path import valid_project


def run_editor(args):
    """
    Run the Pyxora editor for a given project.
    
    Args:
        args: Command-line arguments containing project name and other options. 
    """
    project_name = args.name
    if not valid_project(project_name):
        print(f"No project found with name '{project_name}'")
        return
    
    root = tk.Tk()
    app = EditorWindow(root, args)
    root.mainloop()