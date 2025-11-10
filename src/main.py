"""
Main entrypoint of the application. Launches the editor when ran.
"""

import sys
from view.gui_3 import QApplication, ScriptEditorApp
from PyQt6.QtWidgets import QApplication
import view.settings    # just to preload settings
import multiprocessing

def set_global_font_size(app: QApplication, size: int):
    font = app.font()          # get the current default font
    font.setPointSize(size)    # change the size
    app.setFont(font)          # apply globally


def main():
    app = QApplication(sys.argv)

    multiprocessing.freeze_support()

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


