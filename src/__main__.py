import argparse
import sys

from pyxora import version

from .docs import build_docs, local, online
from .projects import build_project, delete, format, info, ls, new, open, rename, run

# ASCII Art font: Avatar
show_art = lambda: print(
r""" ____ ___  ____  _ ____  ____  ____ 
/  __\\  \//\  \///  _ \/  __\/  _ \
|  \/| \  /  \  / | / \||  \/|| / \|
|  __/ / /   /  \ | \_/||    /| |-||
\_/   /_/   /__/\\\____/\_/\_\\_/ \|     
""")

def main():
    len(sys.argv) == 1 and show_art()

    parser = argparse.ArgumentParser(prog="pyxora", description="pyxora CLI")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"v{version}",
        help="Show the version of pyxora",
    )

    subparsers = parser.add_subparsers(
        dest="Action", required=True, help="Action to run"
    )

    # new
    parser_new = subparsers.add_parser(
        "new", aliases=["create", "setup", "init"], help="Create a new project"
    )
    parser_new.add_argument("name", help="The name of the new project")
    parser_new.add_argument(
        "--description", "-d", default="", help="An optional description of the project"
    )
    parser_new.add_argument(
        "--author",
        "-a",
        default="",
        help="The name of the project author/studio (default: current system user)",
    )

    parser_new.add_argument(
        "--tags",
        "-t",
        nargs="*",
        default=[],
        help="Space-separated list of tags (e.g., --tags 2d prototype platformer)",
    )

    parser_new.add_argument(
        "--version", "-v", default="0.0.0", help="Initial project version (0.0.0)"
    )

    parser_new.add_argument(
        "--input",
        "-i",
        action="store_true",
        help="Use terminal input to parse the project data",
    )

    parser_new.set_defaults(func=new)

    # run
    parser_run = subparsers.add_parser(
        "run", aliases=["start", "play"], help="Run a project"
    )
    parser_run.add_argument("name", help="The name of the new project")
    parser_run.add_argument(
        "--web", "-w", action="store_true", help="Use the web to run"
    )
    parser_run.set_defaults(func=run)

    # open
    parser_open = subparsers.add_parser(
        "open",
        aliases=["browse", "explore"],
        help="Open the project folder in the file manager",
    )
    parser_open.add_argument("name", help="The name of the project to open")
    parser_open.set_defaults(func=open)

    # rename
    parser_rename = subparsers.add_parser("rename", help="Rename a project")
    parser_rename.add_argument("old_name", help="The current name of the project")
    parser_rename.add_argument("new_name", help="The new name of the project")
    parser_rename.set_defaults(func=rename)

    # delete
    parser_delete = subparsers.add_parser(
        "delete", aliases=["remove", "del", "rm"], help="Delete a project"
    )
    parser_delete.add_argument("name", help="The name of the project to delete")
    parser_delete.add_argument(
        "--force",
        action="store_true",
        help="Do not ask for confirmation before deleting the project",
    )
    parser_delete.set_defaults(func=delete)

    # format
    parser_format = subparsers.add_parser(
        "format", aliases=["reset"], help="Delete all projects "
    )
    parser_format.add_argument(
        "--force",
        action="store_true",
        help="Do not ask for confirmation before deleting all the projects",
    )
    parser_format.set_defaults(func=format)

    # build
    parser_build = subparsers.add_parser(
        "build", aliases=["make", "compile"], help="Build the project"
    )
    parser_build.add_argument("name", help="The name of the project to build")
    parser_build.add_argument(
        "--web", "-w", action="store_true", help="Use the web builder"
    )
    parser_build.set_defaults(func=build_project)

    # info
    parser_info = subparsers.add_parser("info", help="Show the project metadata")
    parser_info.add_argument("name", help="The name of the project")
    parser_info.set_defaults(func=info)

    # list
    parser_list = subparsers.add_parser(
        "list", aliases=["ls"], help="List all projects"
    )
    parser_list.set_defaults(func=ls)

    # docs with subcommands: run, build, online
    parser_docs = subparsers.add_parser(
        "docs", aliases=["api"], help="Project documentation"
    )
    docs_subparsers = parser_docs.add_subparsers(
        dest="doc options", required=True, help="Docs options"
    )

    # docs run
    parser_docs_run = docs_subparsers.add_parser(
        "local", help="Run docs server locally"
    )
    parser_docs_run.set_defaults(func=local)

    # docs build
    parser_docs_build = docs_subparsers.add_parser(
        "build", help="Build the documentation"
    )
    parser_docs_build.set_defaults(func=build_docs)

    # docs online
    parser_docs_online = docs_subparsers.add_parser(
        "online", help="Open online documentation"
    )
    parser_docs_online.set_defaults(func=online)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
