import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class GridOverlay(QtWidgets.QWidget):
    def __init__(self, cell_size=50):
        super().__init__()
        self.cell_size = cell_size

        # Make the window borderless, full screen, and always on top
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )

        # Transparent background
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(0, 255, 0, 128))  # green, semi-transparent
        pen.setWidth(1)
        painter.setPen(pen)

        width = self.width()
        height = self.height()

        # Draw vertical lines
        for x in range(0, width, self.cell_size):
            painter.drawLine(x, 0, x, height)

        # Draw horizontal lines
        for y in range(0, height, self.cell_size):
            painter.drawLine(0, y, width, y)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    overlay = GridOverlay(cell_size=50)
    sys.exit(app.exec_())
