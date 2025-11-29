from pyxora import debug,version,pygame_version,sdl_version,python_version

from traceback import extract_tb
import os
import sys

import pygame

__all__ = ["print_versions","error","warning","quit"]

def print_versions() -> None:
    """Print the versions for the engine library and its dependencies."""
    print("-"*50)
    print("pyxora:", version)
    print("Dependencies: ")
    print("\tRendering: pygame-ce", pygame_version, "| SDL", sdl_version)
    print("\tPhysics: pymunk", pymunk_version)
    print("Python:", python_version)
    print("-"*50)

def error(err: Exception) -> None:
    """
    Handles exceptions by showing a popup error box or printing if pyxora.debug is True.

    Args:
        err (Exception): The exception instance that was raised.
    """
    error_type = type(err).__name__
    error_message = str(err)
    traceback_list = extract_tb(err.__traceback__)

    error_details = [
        f"File: {os.path.basename(tb.filename)}, Line: {tb.lineno}"
        for tb in traceback_list
    ]
    formatted_traceback = (
        "\n".join(error_details) if len(error_details) <= 1
        else "\n" + "\n".join(error_details)
    )

    nice_error_message = (
        f"Type: {error_type}\n"
        f"Message: {error_message}\n"
        f"Traceback: {formatted_traceback}"
    )

    if debug:
        print(
            "-----------------------------------\n"
            "Error: An unexpected error occurred\n"
            f"{nice_error_message}\n"
            "-----------------------------------"
        )
    else:
        pygame.display.message_box(
            "An unexpected error occurred",
            nice_error_message,
            "error"
        )


def warning(message: str) -> None:
    """
    Prints a warning message to the console.

    Args:
        message (str): The warning message to display.
    """
    print(f"Warning: {message}")

# def log(): ...


def quit() -> None:
    """
    Exit the application cleanly.

    Calls `sys.exit()` to terminate the process.
    """
    sys.exit()
