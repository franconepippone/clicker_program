from PyQt6.QtCore import Qt
import string

ALLOWED_KEYS_QT = {
    # Basic control keys
    #Qt.Key.Key_Return,
    Qt.Key.Key_Enter,
    Qt.Key.Key_Space,
    #Qt.Key.Key_Backspace,
    Qt.Key.Key_Tab,
    #Qt.Key.Key_Delete,

    # Arrow keys
    Qt.Key.Key_Up,
    Qt.Key.Key_Down,
    Qt.Key.Key_Left,
    Qt.Key.Key_Right,

    # Function keys
    Qt.Key.Key_F1,
    Qt.Key.Key_F2,
    Qt.Key.Key_F3,
    Qt.Key.Key_F4,
    Qt.Key.Key_F5,
    Qt.Key.Key_F6,
    Qt.Key.Key_F7,
    Qt.Key.Key_F8,
    Qt.Key.Key_F9,
    Qt.Key.Key_F10,
    Qt.Key.Key_F11,
    Qt.Key.Key_F12,
}

# Letters A-Z
ALLOWED_KEYS_QT |= {getattr(Qt.Key, f"Key_{ch}") for ch in string.ascii_uppercase}

# Numbers 0-9
ALLOWED_KEYS_QT |= {getattr(Qt.Key, f"Key_{ch}") for ch in string.digits}

# Common symbols
ALLOWED_KEYS_QT |= {
    #Qt.Key.Key_Comma,
    #Qt.Key.Key_Period,
    #Qt.Key.Key_Slash,
    #Qt.Key.Key_Semicolon,
    #Qt.Key.Key_QuoteLeft,
    Qt.Key.Key_Minus,
    #Qt.Key.Key_Equal,
    #Qt.Key.Key_BracketLeft,
    #Qt.Key.Key_BracketRight,
    #Qt.Key.Key_Backslash,
    #Qt.Key.Key_Apostrophe,
}


if __name__ == "__main__":
    print(ALLOWED_KEYS_QT)