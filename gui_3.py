import sys
import logging
import multiprocessing
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QCursor, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QPlainTextEdit, QFileDialog, QMessageBox,
    QSplitter
)

from logging.handlers import QueueListener

from gui_utils import make_icon, make_eye_icon, ScriptHighlighter


# ----------------------
# Logging setup
# ----------------------
logger_comp = logging.getLogger("Compiler")
logger_comp.setLevel(logging.DEBUG)
logger_exec = logging.getLogger("Runtime")
logger_exec.setLevel(logging.DEBUG)
logger_decompiler = logging.getLogger("Decompiler")
logger_decompiler.setLevel(logging.DEBUG)
logger_editor = logging.getLogger("Editor")
logger_editor.setLevel(logging.DEBUG)


# ----------------------
# Terminal logging handler
# ----------------------
class TerminalLogHandler(QObject, logging.Handler):
    """Logging handler that safely forwards log strings to the GUI thread.

    Emits a simple string via a Qt signal; the connected slot runs in the
    GUI thread (the QObject is created in the main thread), so we never
    pass QTextCursor or other widget objects across threads.
    """

    new_log = pyqtSignal(str)

    def __init__(self, terminal_widget: QPlainTextEdit) -> None:
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.terminal: QPlainTextEdit = terminal_widget
        # Connect the signal to the append routine in the GUI thread
        self.new_log.connect(self._append_to_terminal)

    def _append_to_terminal(self, msg: str) -> None:
        cursor = self.terminal.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(msg + "\n")
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()

    def emit(self, record: logging.LogRecord) -> None:
        # Format the message in whatever thread the logger runs, but emit
        # only a plain string via the signal. Qt will queue it to the GUI
        # thread and call _append_to_terminal there.
        try:
            msg = self.format(record)
            self.new_log.emit(msg)
        except Exception:
            # Avoid raising from the logging subsystem
            pass

# ----------------------
# Main editor
# ----------------------
class ScriptEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Editor")
        self.resize(500,600)
        self.is_modified=False
        self.current_file=None
        self.preview_path_on=False
        self.proc: Optional[multiprocessing.Process] = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8,8,8,8)
        main_layout.setSpacing(6)

        # ---------------- File toolbar ----------------
        file_toolbar = QHBoxLayout()
        new_btn = QPushButton("New")
        open_btn = QPushButton("Open")
        save_btn = QPushButton("Save")
        for b in [new_btn, open_btn, save_btn]:
            b.setFixedHeight(32)
            b.setStyleSheet(self.button_style())
            file_toolbar.addWidget(b)
        file_toolbar.addStretch()

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #ccc;")

        # ---------------- Run / Record / Preview ----------------
        exec_toolbar = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.setIcon(make_icon(QColor("#00cc00"), "triangle"))
        self.run_btn.setToolTip("Run the current script")
        self.record_btn = QPushButton("Record")
        self.record_btn.setIcon(make_icon(QColor("#cc0000"), "circle"))
        self.record_btn.setToolTip("Record session")
        self.preview_btn = QPushButton("Preview Path")
        self.preview_btn.setCheckable(True)
        self.preview_btn.setChecked(self.preview_path_on)
        self.preview_btn.setIcon(make_eye_icon(self.preview_path_on))
        self.preview_btn.setToolTip("Toggle path preview")

        for b in [self.run_btn, self.record_btn, self.preview_btn]:
            b.setFixedHeight(32)
            b.setStyleSheet(self.button_style())
            exec_toolbar.addWidget(b)
        exec_toolbar.addStretch()

        # ---------------- Editor ----------------
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Type your script...")
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.editor.setStyleSheet("""
            QPlainTextEdit { font-family: Consolas, monospace; font-size:14px; border:1px solid #ccc; background-color:#fdfdfd; }
        """)
        self.highlighter = ScriptHighlighter(self.editor.document())
        self.editor.textChanged.connect(self.mark_modified)

        # ---------------- Terminal ----------------
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.terminal.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
        """)
        terminal_label = QLabel("> Terminal")
        terminal_label.setStyleSheet("padding:2px;")
        terminal_label.setFixedHeight(20)

        terminal_container = QVBoxLayout()
        terminal_container.setContentsMargins(0,0,0,0)
        terminal_container.setSpacing(1)
        terminal_container.addWidget(terminal_label)
        terminal_container.addWidget(self.terminal)

        terminal_widget = QFrame()
        terminal_widget.setLayout(terminal_container)

        # Attach log handlers for main process
        main_handler = TerminalLogHandler(self.terminal)
        formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
        main_handler.setFormatter(formatter)
        for logger in [logger_comp, logger_exec, logger_decompiler, logger_editor]:
            logger.addHandler(main_handler)

        # ---------------- Splitter ----------------
        splitter = QSplitter(Qt.Vertical)   # type: ignore[attr-defined]
        splitter.addWidget(self.editor)
        splitter.addWidget(terminal_widget)
        splitter.setSizes([400,150])

        # ---------------- Bottom status bar ----------------
        bottom_bar = QFrame()
        bottom_bar.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10,2,10,2)
        self.coord_label = QLabel("X:0, Y:0")
        bottom_layout.addWidget(self.coord_label)
        bottom_layout.addStretch()

        # ---------------- Assemble ----------------
        main_layout.addLayout(file_toolbar)
        main_layout.addWidget(separator)
        main_layout.addLayout(exec_toolbar)
        main_layout.addWidget(splitter)
        main_layout.addWidget(bottom_bar)
        self.setLayout(main_layout)

        # ---------------- Connections ----------------
        new_btn.clicked.connect(self.new_file)
        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_file)
        self.run_btn.clicked.connect(self.run_script)
        self.record_btn.clicked.connect(self.record_script)
        self.preview_btn.toggled.connect(self.toggle_preview)

        # subprocesses logging queue
        queue_handler = TerminalLogHandler(self.terminal)
        formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
        queue_handler.setFormatter(formatter)

        self.log_queue = multiprocessing.Queue()
        self.queue_listener = QueueListener(self.log_queue, queue_handler)

        # Mouse coordinates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(50)

        # Timer to monitor child process and re-enable UI when it exits
        self.proc_monitor_timer = QTimer(self)
        self.proc_monitor_timer.timeout.connect(self._check_process)

        logger_editor.info("Editor started")

    # ---------------- Utility Methods ----------------
    def button_style(self):
        return """
            QPushButton {
                font-weight: normal;
                padding: 4px 10px;
                border: 1px solid #aaa;
                border-radius: 6px;
                background-color: #f5f5f5;
            }
            QPushButton:hover {
                background-color: #eaeaea;
            }
        """

    def toggle_preview(self, checked):
        self.preview_path_on = checked
        self.preview_btn.setIcon(make_eye_icon(checked))
        logger_editor.info(f"Preview Path {'ON' if checked else 'OFF'}")

    # ==========================================================
    # script save / load methods
    # ==========================================================

    def mark_modified(self):
        self.is_modified=True

    def confirm_discard_changes(self):
        if self.is_modified:
            reply = QMessageBox.question(self,"Unsaved Changes",
                "You have unsaved changes. Discard?", QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
            if reply==QMessageBox.No: return False
        return True

    def new_file(self):
        if not self.confirm_discard_changes(): return
        self.editor.clear()
        self.is_modified=False
        self.current_file=None
        logger_editor.info("Created new empty script")

    def open_file(self):
        if not self.confirm_discard_changes(): return
        fname, _ = QFileDialog.getOpenFileName(self,"Open File","","Text Files (*.txt *.py *.md);;All Files (*)")
        if fname:
            with open(fname,'r',encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.is_modified=False
            self.current_file=fname
        logger_editor.info(f"Opened file: {self.current_file if self.current_file else 'New file'}")

    def save_file(self):
        if not self.current_file:
            fname,_=QFileDialog.getSaveFileName(self,"Save File","","Text Files (*.txt *.py *.md);;All Files (*)")
            if not fname: return
            self.current_file=fname

        with open(self.current_file,'w',encoding='utf-8') as f:
            f.write(self.editor.toPlainText())

        self.is_modified = False
        logger_editor.info(f"Saved file: {self.current_file}")


    # ==========================================================
    # run / record methods
    # ==========================================================

    def run_script(self):
        code_src = self.editor.toPlainText()
        logger_exec.info("Running script...")

        from executor_process import begin_compile_and_execute_process

        self.queue_listener.start()

        # Start the subprocess and disable the Run button until it finishes
        self.proc = begin_compile_and_execute_process(code_src, self.log_queue)
        self.subprocess_mark_as_started()
    
    def record_script(self):
        logger_editor.info("Starting recording session")
        
        from recorder_process import begin_recording_process

        self.queue_listener.start()

        self.subprocess_mark_as_started()
        # Start the subprocess and disable the Run button until it finishes
        self.proc = begin_recording_process(self.log_queue)
        self.subprocess_mark_as_started()
    
    def subprocess_mark_as_started(self):
        """Disables the Run and Record buttons and starts the process monitor timer.
        """
        self.run_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.proc_monitor_timer.start(500)

    def update_mouse_position(self):
        pos = QCursor.pos()
        self.coord_label.setText(f"X:{pos.x()}  Y:{pos.y()}")

    def _check_process(self):
        """Poll the subprocess; when it exits, stop the listener and re-enable UI."""
        if not isinstance(self.proc, multiprocessing.Process):
            alive = False
        else:
            alive = self.proc.is_alive()

        if not alive:
            logger_editor.debug("Child process has exited; cleaning up.")
            # stop queue listener
            try:
                self.queue_listener.stop()
            except Exception:
                logger_editor.exception("Failed to stop queue listener")

            # reset state
            self.proc = None

            # re-enable Run button 
            self.run_btn.setEnabled(True)
            self.record_btn.setEnabled(True)

            # stop the monitor timer
            self.proc_monitor_timer.stop()

# ----------------------
# Run the app
# ----------------------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = ScriptEditorApp()
    window.show()
    sys.exit(app.exec_())
