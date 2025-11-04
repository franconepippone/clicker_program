from __future__ import annotations
import json
import os
from typing import Any, Dict

DEFAULT_SETTINGS_FILENAME = "settings.json"

class Settings:
    """
    Global static settings class.
    Stores app-wide configuration with simple JSON persistence.
    """

    # --- Default values ---
    clear_terminal_on_run: bool = False
    print_debug_msg: bool = False
    text_size: int = 12
    dark_mode: bool = False

    # --- File I/O ---

    @classmethod
    def _get_serializable_attrs(cls) -> Dict[str, Any]:
        """Return a dict of class attributes safe to save as JSON."""
        data: Dict[str, Any] = {}
        for key, val in cls.__dict__.items():
            if key.startswith("__") or callable(val):
                continue
            # ensure it's JSON-serializable
            try:
                json.dumps(val)
                data[key] = val
            except (TypeError, OverflowError):
                pass
        return data

    @classmethod
    def store_to_file(cls, filename: str = DEFAULT_SETTINGS_FILENAME) -> None:
        """Write current settings to a JSON file."""
        data = cls._get_serializable_attrs()
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filename: str = DEFAULT_SETTINGS_FILENAME) -> None:
        """
        Load settings from JSON file, creating it with defaults if missing.
        Invalid files are reset to defaults.
        """
        if not os.path.exists(filename):
            print(f"{filename} not found, creating it with defaults...")
            cls.store_to_file(filename)
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Failed to read {filename}, recreating with defaults...")
            cls.store_to_file(filename)
            return

        for key, value in data.items():
            if hasattr(cls, key):
                setattr(cls, key, value)

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return current settings as a dict."""
        return cls._get_serializable_attrs()
