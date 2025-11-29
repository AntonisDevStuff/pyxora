from .path import get_path,valid_project
import subprocess
from pyxora.utils import platform

def explore(args):
    """Open a project."""
    path = get_path(args.name)
    if not valid_project(args.name):
        print(f"No project found with name '{args.name}'")
        return

    command_name = "explorer" if platform.is_windows() else "xdg-open" if platform.is_linux() else "open"
    subprocess.run([command_name, path])

    return path
