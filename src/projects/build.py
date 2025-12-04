import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from importlib.metadata import requires
from time import perf_counter as time

from .info import info
from .path import get_path, valid_project


def local_build(args):
    x1 = time()
    name = args.name
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return

    project_path = get_path(name)
    main_script = os.path.join(project_path, "main.py")

    print("Build metadata: ")
    metadata = info(args)
    app_name = metadata["name"]
    app_version = metadata["version"]

    build_dir = os.path.abspath("build")  # everything goes here

    # remove previous build
    if os.path.exists(build_dir):
        print(f"Removing existing build directory at {build_dir} ...")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Error removing build directory: {e}")
            return

    os.makedirs(build_dir, exist_ok=True)

    includes = [
        dep.split("==")[0]
        .split(">=")[0]
        .split(">")[0]
        .split("<")[0]
        .split("[")[0]
        .replace("-", "_")
        for dep in requires("pyxora")
    ]

    # add the main engine
    includes.append("pyxora")

    # the pypi package name is 'pygame-ce', but the pacakge import is 'pygame'
    # so we include 'pygame' and remove 'pygame_ce'
    includes.append("pygame")
    includes.remove("pygame_ce")

    # these are not needed in the final build executable
    includes.remove("pygbag")  # web builds
    includes.remove("cx_Freeze")  # local builds
    includes.remove("pdoc")  # docs generator
    includes.remove("pillow")  # images

    # exec type base in platform
    if sys.platform == "win32":
        base = repr("Win32GUI")
        target_name = f"{app_name}.exe"
    else:
        base = None
        target_name = app_name

    # cx_Freeze setup script
    setup_code = textwrap.dedent(
        f"""\
        from cx_Freeze import setup, Executable

        includes = {includes!r}

        setup(
            name="{app_name}",
            version="1.0",
            description="{app_name} Build",
            executables=[Executable(r"{main_script}", target_name="{target_name}", base={base})],
            options={{
                "build_exe": {{
                    "build_exe": r"{build_dir}",
                    "includes": includes,
                    "include_files": [],
                }}
            }}
        )
    """
    )

    # create temp script file for the cx_freeze
    with tempfile.TemporaryDirectory() as temp_dir:
        setup_script_path = os.path.join(temp_dir, "setup_cxfreeze.py")
        with open(setup_script_path, "w") as f:
            f.write(setup_code)

        print("Running cx_Freeze...")
        try:
            subprocess.run(
                [sys.executable, setup_script_path, "build"],
                check=True,
                cwd=temp_dir,
                stdout=subprocess.DEVNULL,  # suppress output
                # stderr=subprocess.DEVNULL,  # suppress errors
            )
        except subprocess.CalledProcessError as e:
            print(f"Error during cx_Freeze build: {e}")
            return

    print("Copying project files into the build directory...")
    for item in os.listdir(project_path):
        src = os.path.join(project_path, item)
        dst = os.path.join(build_dir, item)
        if item in (
            "build",
            "__pycache__",
            "main.py",
            "metadata.json",
        ):  # skip this folders/files
            continue

        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            print(f"Error copying {src} to {dst}: {e}")
            return

    print(f"Build completed successfully. Executable and files are in: {build_dir}")

    x2 = time()

    print(f"Build time: {x2 - x1:.2f} seconds")


def web_build(args):
    x1 = time()
    name = args.name
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return

    project_path = get_path(name)
    build_dir = os.path.abspath("build")

    # remove previous build
    if os.path.exists(build_dir):
        print(f"Removing existing build directory at {build_dir} ...")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"Error removing build directory: {e}")
            return

    os.makedirs(build_dir, exist_ok=True)

    try:
        print("Running pygbag ...")
        subprocess.run(
            [sys.executable, "-m", "pygbag", "--archive", "main.py"],
            check=True,
            cwd=project_path,
            stdout=subprocess.DEVNULL,  # suppress output
            stderr=subprocess.DEVNULL,  # suppress errors
        )
    except subprocess.CalledProcessError as e:
        print(f"pygbag build failed with exit code {e.returncode}")
        return
    except FileNotFoundError:
        print(
            "pygbag command not found. Please ensure pygbag is installed and in your PATH."
        )
        return

    # move build from the project to current directory
    pygbag_output_dir = os.path.join(project_path, "build")
    try:
        shutil.rmtree(build_dir)
        shutil.move(pygbag_output_dir, build_dir)
    except Exception:
        print(f"Error moving {pygbag_output_dir} to {build_dir}")
        try:
            shutil.rmtree(
                pygbag_output_dir
            )  # try to remove the tmp pygbag build files if move fails
        except Exception:
            print("Error deleting pygbag tmp files")
        return

    print(f"Web build completed successfully. Files are in: {build_dir}")
    x2 = time()
    print(f"Build time: {x2 - x1:.2f} seconds")


def build_project(args):
    """Build a project"""
    if args.web:
        web_build(args)
    else:
        local_build(args)
