from .path import get_projects_path
from random import randint as random
from shutil import rmtree as rm

def format_project(args):
    """Format the project directory by removing all projects."""
    path = get_projects_path()
    # deletion process is irreversible, so this is safe mechanism
    # the force is for bypassing the confirmation prompt, great for gui.
    force = args.force

    if not force:
        print("WARNING: This action will permanently delete ALL projects!")
        secure_number = str(random(1000, 9999))
        answer = input(f"To confirm, please type the number {secure_number}: ").strip()

        if answer != secure_number:
            print("!!!Wrong Answer!!!")
            print("No action taken")
            return

    rm(path)
    print("All projects deleted successfully!")
    return path
