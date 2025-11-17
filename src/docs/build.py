import os
from pathlib import Path
from time import perf_counter as time

import pdoc

FAVICON = "https://raw.githubusercontent.com/pyxora/pyxora-docs/refs/heads/main/images/favicon.png"

def build_docs(*args, **kwargs):
    """
    Build static HTML documentation for all modules except excluded ones.
    Output is placed in a 'build' subfolder of the current working directory.
    """
    x1 = time()
    pdoc.render.configure(favicon=FAVICON, docformat="google")
    # This will always give you the correct absolute path to a build folder inside the current working directory
    output_path = Path(os.getcwd()) / "docs"
    output_path.mkdir(parents=True, exist_ok=True)
    pdoc.pdoc(
        "pyxora",
        "!pyxora.examples",
        "!pyxora.docs",
        "!pyxora.project",
        "!pyxora.templates",
        output_directory=output_path,
    )
    x2 = time()
    print("output path:", output_path)
    print(f"build time: {x2 - x1:.2f} seconds")
