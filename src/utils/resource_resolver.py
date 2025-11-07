import sys, os
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """Return absolute path to resource (handles PyInstaller and dev mode).
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) # type: ignore
    else:
        base_path = Path(__file__).resolve().parent.parent.parent   # points to the root project directory
    
    return base_path / relative_path