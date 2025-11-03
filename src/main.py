import sys
from view.gui_3 import QApplication, ScriptEditorApp


def main():
    app = QApplication(sys.argv)
    window = ScriptEditorApp()
    window.show()
    sys.exit(app.exec_())

# ----------------------
# Run the app
# ----------------------
if __name__=="__main__":
    main()    


