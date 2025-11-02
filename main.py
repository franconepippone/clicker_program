import sys
from view.gui_3 import QApplication, ScriptEditorApp



# ----------------------
# Run the app
# ----------------------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = ScriptEditorApp()
    window.show()
    sys.exit(app.exec_())
