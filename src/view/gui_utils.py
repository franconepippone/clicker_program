import re
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import (
    QIcon,
    QColor,
    QPixmap,
    QPainter,
    QFont,
    QTextCharFormat,
    QSyntaxHighlighter,
    QTextFormat,
    QPaintEvent
)
from PyQt6.QtWidgets import (
    QWidget,
    QPlainTextEdit,
    QVBoxLayout,
    QTextEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
)

# ----------------------
# Icon helpers
# ----------------------
def make_icon(color: QColor, shape: str, size: int = 14):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)         
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)            
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

KEYWORDS_BLUE = [
    "move", "moverel", "click", "wait", "doubleclick",
    "print", "centermouse", "goback",
    "setoffset", "clearoffset", "pause"
]

KEYWORDS_ORANGE = [
    "call", "return", "jump", "label"
]

KEYWORDS_PURPLE = [
    "var", "printvar"
]

class ScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)

        # Define color schemes for each keyword group
        self.keyword_formats = {
            "blue": self._make_format("#005cc5", bold=True),
            "purple": self._make_format("#6f42c1", bold=True),
            "orange": self._make_format("#d73a49", bold=True),
        }

        # Build keyword lists with their colors
        self.keyword_groups = [
            (KEYWORDS_BLUE, self.keyword_formats["blue"]),
            (KEYWORDS_PURPLE, self.keyword_formats["purple"]),
            (KEYWORDS_ORANGE, self.keyword_formats["orange"]),
        ]

        # Comment style
        self.comment_format = self._make_format("#999999", italic=True)

    def _make_format(self, color: str, bold=False, italic=False) -> QTextCharFormat:
        """Helper to create a consistent text format."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def highlightBlock(self, text: str | None) -> None:
        if not text:
            return

        # Highlight keywords (case-insensitive)
        for keywords, fmt in self.keyword_groups:
            for word in keywords:
                pattern = r'\b{}\b'.format(re.escape(word))
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    start, end = match.span()
                    self.setFormat(start, end - start, fmt)

        # Highlight comments starting with ';'
        comment_index = text.find(";")
        if comment_index >= 0:
            self.setFormat(comment_index, len(text) - comment_index, self.comment_format)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        self.code_editor.line_number_area_paint_event(a0)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setPlaceholderText("Type your script...")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid #ccc;
                background-color: #fdfdfd;
            }
        """)

        self.line_number_area = LineNumberArea(self)

        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 5)

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

    def resizeEvent(self, e):
        super().resizeEvent(e)
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
                painter.setPen(Qt.GlobalColor.gray)
                painter.drawText(
                    0, top, self.line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
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
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)


def show_offset_dialog(parent: QWidget):

    dialog = QDialog(parent)
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
    #confirm_btn.clicked.connect(lambda: parent.offset_positions(x_spin.value(), y_spin.value(), dialog))
    cancel_btn.clicked.connect(dialog.reject)

    dialog.exec()
