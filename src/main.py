"""
Main entrypoint of the application. Launches the editor when ran.

executable version

"""

import sys
import multiprocessing

from view.gui_3 import QApplication, ScriptEditorApp
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
import view.settings    # just to preload settings
from utils.resource_resolver import resource_path

def set_global_font_size(app: QApplication, size: int):
    font = app.font()          # get the current default font
    font.setPointSize(size)    # change the size
    app.setFont(font)          # apply globally


def main():
    multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    icon = QIcon(str(resource_path("assets/app_icon.ico")))
    app.setWindowIcon(icon)

    #app.setStyle("Fusion")
    window = ScriptEditorApp()
    window.update_all_widget_fonts(app, 10)
    window.show()
    sys.exit(app.exec())

# ----------------------
# Run the app
# ----------------------
if __name__=="__main__":
    main()    


