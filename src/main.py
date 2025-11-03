import sys
from view.gui_3 import QApplication, ScriptEditorApp
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = ScriptEditorApp()
    window.show()
    sys.exit(app.exec())

# ----------------------
# Run the app
# ----------------------
if __name__=="__main__":
    main()    


