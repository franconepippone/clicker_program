import re
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QFont, QTextCharFormat, QSyntaxHighlighter


# ----------------------
# Icon helpers
# ----------------------
def make_icon(color: QColor, shape: str, size: int = 14):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)         # type: ignore[attr-defined]
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(color)
    painter.setPen(Qt.NoPen)            # type: ignore[attr-defined]
    if shape == "circle":
        painter.drawEllipse(0,0,size,size)
    elif shape == "triangle":
        points = [QPoint(2,2), QPoint(size-2,size//2), QPoint(2,size-2)]
        painter.drawPolygon(*points)
    painter.end()
    return QIcon(pixmap)

def make_eye_icon(on: bool, size: int=14):
    return make_icon(QColor("#00cc00") if on else QColor("#999999"), "circle", size)


# ----------------------
# Syntax highlighter
# ----------------------

KEYWORDS = [
    "move", "moverel", "click", "wait", "doubleclick", "jump",
    "print", "centermouse", "waitinput", "goback",
    "setoffset", "clearoffset", "label"
]

class ScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#005cc5"))
        self.keyword_format.setFontWeight(QFont.Bold)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#999999"))
        self.comment_format.setFontItalic(True)

    def highlightBlock(self, text: str | None) -> None:
        if not text: return # should never happen

        for word in KEYWORDS:
            pattern = r'\b{}\b'.format(re.escape(word))
            for match in re.finditer(pattern, text, re.IGNORECASE):
                s, e = match.span()
                self.setFormat(s, e - s, self.keyword_format)
        comment_index = text.find(";")
        if comment_index >= 0:
            self.setFormat(comment_index, len(text) - comment_index, self.comment_format)
