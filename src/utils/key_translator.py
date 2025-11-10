from PyQt6.QtCore import Qt
from pynput.keyboard import KeyCode, Key

def qt_to_pynput(key):
    """
    Convert PyQt normal key (letters/digits) to pynput KeyCode.
    Returns KeyCode or None if unmapped.
    """
    # Letters A-Z
    if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
        char = chr(key)  # Qt.Key_A = 65, corresponds to 'A'
        return KeyCode(char=char.lower())

    # Numbers 0-9
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        char = chr(key)  # Qt.Key_0 = 48
        return KeyCode(char=char)

    # Space
    if key == Qt.Key.Key_Space:
        return Key.space

    # Tab
    if key == Qt.Key.Key_Tab:
        return Key.tab

    # Enter / Return
    if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
        return Key.enter

    # Add more symbols manually if needed
    symbols_map = {
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

    if key in symbols_map:
        return KeyCode(char=symbols_map[key])

    return None  # unmapped
