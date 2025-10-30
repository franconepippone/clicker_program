import re
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QColor, QPixmap, QPainter, QFont, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QFont
from PyQt5.QtCore import Qt, QRect, QSize

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
    return make_icon(QColor("#0070cc") if on else QColor("#999999"), "circle", size)


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


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setPlaceholderText("Type your script...")
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid #ccc;
                background-color: #fdfdfd;
            }
        """)

        self.line_number_area = LineNumberArea(self)

        # Signals for updating line numbers when needed
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    # --- Line number area logic ---

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = 30 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.gray)
                painter.drawText(
                    0, top, self.line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # --- Highlight current line ---

    def highlight_current_line(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#e8f2ff")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)



def show_offset_dialog(self):
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton

    dialog = QDialog(self)
    dialog.setWindowTitle("Offset All Positions")
    dialog.setModal(True)
    dialog.setFixedSize(250, 150)

    layout = QVBoxLayout(dialog)

    # X coordinate
    x_layout = QHBoxLayout()
    x_label = QLabel("X Offset:")
    x_spin = QSpinBox()
    x_spin.setRange(-10000, 10000)
    x_layout.addWidget(x_label)
    x_layout.addWidget(x_spin)
    layout.addLayout(x_layout)

    # Y coordinate
    y_layout = QHBoxLayout()
    y_label = QLabel("Y Offset:")
    y_spin = QSpinBox()
    y_spin.setRange(-10000, 10000)
    y_layout.addWidget(y_label)
    y_layout.addWidget(y_spin)
    layout.addLayout(y_layout)

    # Confirm / Cancel buttons
    buttons_layout = QHBoxLayout()
    confirm_btn = QPushButton("Confirm")
    cancel_btn = QPushButton("Cancel")
    buttons_layout.addStretch()
    buttons_layout.addWidget(confirm_btn)
    buttons_layout.addWidget(cancel_btn)
    layout.addLayout(buttons_layout)

    # --- Connections ---
    confirm_btn.clicked.connect(lambda: self.offset_positions(x_spin.value(), y_spin.value(), dialog))
    cancel_btn.clicked.connect(dialog.reject)

    dialog.exec_()