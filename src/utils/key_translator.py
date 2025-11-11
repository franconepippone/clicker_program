from PyQt6.QtCore import Qt
from pynput.keyboard import KeyCode, Key

from pynput.keyboard import Key

# Tables to convert from qt to pynput
QT_KEY_TO_PYNPUT = {
    # Modifiers
    Qt.Key.Key_Shift: Key.shift,
    Qt.Key.Key_Control: Key.ctrl,
    Qt.Key.Key_Alt: Key.alt,
    Qt.Key.Key_AltGr: Key.alt_r,

    # Arrows
    Qt.Key.Key_Up: Key.up,
    Qt.Key.Key_Down: Key.down,
    Qt.Key.Key_Left: Key.left,
    Qt.Key.Key_Right: Key.right,

    # Navigation / editing
    Qt.Key.Key_Home: Key.home,
    Qt.Key.Key_End: Key.end,
    Qt.Key.Key_PageUp: Key.page_up,
    Qt.Key.Key_PageDown: Key.page_down,
    Qt.Key.Key_Insert: Key.insert,
    Qt.Key.Key_Delete: Key.delete,
    
    # Enter / Return
    Qt.Key.Key_Return: Key.enter,
    Qt.Key.Key_Enter: Key.enter,
    
    # Tab, Esc, Space
    Qt.Key.Key_Tab: Key.tab,
    Qt.Key.Key_Space: Key.space,
    Qt.Key.Key_Escape: Key.esc,
    
    # Function keys
    Qt.Key.Key_F1: Key.f1,
    Qt.Key.Key_F2: Key.f2,
    Qt.Key.Key_F3: Key.f3,
    Qt.Key.Key_F4: Key.f4,
    Qt.Key.Key_F5: Key.f5,
    Qt.Key.Key_F6: Key.f6,
    Qt.Key.Key_F7: Key.f7,
    Qt.Key.Key_F8: Key.f8,
    Qt.Key.Key_F9: Key.f9,
    Qt.Key.Key_F10: Key.f10,
    Qt.Key.Key_F11: Key.f11,
    Qt.Key.Key_F12: Key.f12,
}

SYMBOLS_MAP = {
    Qt.Key.Key_Comma: ',',
    Qt.Key.Key_Period: '.',
    Qt.Key.Key_Slash: '/',
    Qt.Key.Key_Semicolon: ';',
    Qt.Key.Key_QuoteLeft: '`',
    Qt.Key.Key_Minus: '-',
    Qt.Key.Key_Equal: '=',
    Qt.Key.Key_BracketLeft: '[',
    Qt.Key.Key_BracketRight: ']',
    Qt.Key.Key_Backslash: '\\',
    Qt.Key.Key_Apostrophe: "'",
}


def qt_to_pynput(key, filter: set[Key | KeyCode] | None = None) -> Key | KeyCode | None:
    """
    Convert PyQt keys to pynput Key or KeyCode.
    Returns Key/KeyCode or None if unmapped or filtered out.
    """

    # Apply filter if provided
    if filter and key not in filter:
        return None

    # Letters A-Z
    if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
        char = chr(key)  # Qt.Key_A = 65, corresponds to 'A'
        return KeyCode.from_char(char.lower())

    # Numbers 0-9
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        char = chr(key)  # Qt.Key_0 = 48
        return KeyCode.from_char(char)

    # Symbols
    if key in SYMBOLS_MAP:
        return KeyCode.from_char(SYMBOLS_MAP[key])

    # Map special keys from dictionary
    if key in QT_KEY_TO_PYNPUT:
        return QT_KEY_TO_PYNPUT[key]

    return None  # unmapped