# ⚙️ pyxora

> Note: This project is no longer actively maintained and has been archived.<br>It is provided as-is for reference purposes only.<br>No further updates, bug fixes, or support will be provided.

pyxora is a lightweight, open-source 2D game engine built on pygame-ce and pymunk.  
It’s designed to keep game development simple and flexible.

Perfect for prototypes, game jams, and learning projects.  
Handles rendering, physics, scenes and more so you can focus on making your game.

If it looks interesting to you, feel free to give it a try!

## Quick Start

### Installation
~~To install from PyPI:~~
```bash
pip install pyxora
```

To install locally:  
```bash
git clone https://github.com/AntonisDevStuff/pyxora.git
cd pyxora
pip install . 
```

### Create a New Project
To create a new project:

```bash
pyxora new my_game
```

**Note:** You can add metadata with optional flags like `--author`, `--description`, `--tags`, or use `--input` for an interactive setup. 

### Run the Project
To run your project:
```bash
pyxora run my_game
```

### Open in Editor
To open your project in the GUI editor:
```bash
pyxora open my_game
```

## Managing Projects
The CLI provides several commands to manage your projects:

```bash
pyxora list              # List all projects
pyxora info my_game      # Show project details
pyxora explore my_game   # Open project folder
pyxora build my_game     # Freeze the game
```

To see all available commands:
```bash
pyxora --help
```

## Documentation
The documentation is built using pdoc, a docstring generator.  
It provides an overview of the engine API and how it works.

It is recommended to read the documentation at least once to understand the engine’s structure and usage.

Documentation: [here]()

## Examples
Examples are great for understanding how the engine works and getting familiar with its syntax.

List examples and run one with:
```python
pyxora examples list
pyxora examples run example
```

## Can I Contribute?
Absolutely! Contributions are always welcome.
You can:

- Submit pull requests
- Open issues
- Suggest improvements
- Fix typos or write examples

## License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE.txt) file for the full license text.
