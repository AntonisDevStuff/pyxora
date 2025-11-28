"""
UI components for the Pyxora editor.
"""
from .window import EditorWindow
from .workspace import WorkspaceManager
from .explorer import ExplorerPanel
from . preview import PreviewPanel
from .controls import ControlsPanel
from . console import ConsolePanel
from .inspector import InspectorPanel
from . code_editor import CodeEditorPanel

__all__ = [
    'EditorWindow',
    'WorkspaceManager',
    'ExplorerPanel',
    'PreviewPanel',
    'ControlsPanel',
    'ConsolePanel',
    'InspectorPanel',
    'CodeEditorPanel'
]