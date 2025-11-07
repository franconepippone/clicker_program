from typing import Optional, Literal
import logging
import multiprocessing

from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QCursor, QColor, QTextCharFormat, QIcon, QAction, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QPlainTextEdit, QFileDialog, QMessageBox,
    QSplitter, QMenu, QMenuBar, QCheckBox
)

from logging.handlers import QueueListener

from .gui_utils import make_icon, make_eye_icon, ScriptHighlighter, CodeEditor, show_offset_dialog
from .settings_dialog import SettingsDialog
from .settings import Settings
from utils.resource_resolver import resource_path

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
    """Logging handler that safely forwards log strings to the GUI thread."""

    new_log = pyqtSignal(str, int)  # emit both message and level number

    def __init__(self, terminal_widget: QPlainTextEdit) -> None:
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.terminal: QPlainTextEdit = terminal_widget
        self.new_log.connect(self._append_to_terminal)

    def _append_to_terminal(self, msg: str, level: int) -> None:
        
        # dont do anything if debug msg prints are disabled
        if level == logging.DEBUG and not Settings.print_debug_msg:
            return

        # Choose color based on log level
        color_map = {
            logging.DEBUG: "#7E7E7E",
            logging.INFO: "#FFFFFF",
            logging.WARNING: "#ffe30b",
            logging.ERROR: "#cc0000",
            logging.CRITICAL: "#ff0000",
        }
        color = color_map.get(level, "#000000")

        # Set text color
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(msg + "\n", fmt)

        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.new_log.emit(msg, record.levelno)
        except Exception:
            pass


# ----------------------
# Main editor
# ----------------------
class ScriptEditorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mouse Emulator - Script Editor")
        self.resize(500, 600)
        self.is_modified = False
        self.current_file = None
        self.preview_path_on = False
        self.proc: Optional[multiprocessing.Process] = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- Native Menu Bar ----------------
        menubar = QMenuBar(self)

        # Add visual separation: light gray background and borders
        menubar.setStyleSheet("""
            /* Top-level menu bar */
            QMenuBar {
                background-color: palette(window);
                color: palette(window-text);
                border-bottom: 1px solid rgba(255, 255, 255, 30);
            }
            QMenuBar::item {
                spacing: 6px;
                padding: 4px 12px;
                background: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: rgba(150, 150, 150, 30);
            }

            /* Dropdown menus */
            QMenu {
                background-color: palette(window);
                color: palette(window-text);
                border: 1px solid rgba(0, 0, 0, 30);
                padding: 4px 0;
            }
            QMenu::item {
                padding: 4px 20px;         /* standard menu item padding */
                background: transparent;
            }
            QMenu::item:selected {
                background-color: rgba(150, 150, 150, 30);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0, 0, 0, 20);
                margin: 4px 0;
            }
        """)



        # File menu
        file_menu = menubar.addMenu("&File")
        assert isinstance(file_menu, QMenu)     # to get rid of pylance error

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        save_as_action = QAction("Save as", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        
        file_menu.addActions([new_action, open_action, save_action, save_as_action])

        # Preferences menu
        options_menu = menubar.addMenu("Preferences")
        assert isinstance(options_menu, QMenu)      # gets rid of pylance error

        settings_action = QAction("Settings...", self)
        options_menu.addAction(settings_action)
        settings_action.triggered.connect(self.open_settings_dialog)

        # Examples
        examples_menu = menubar.addMenu("Examples")
        self.setup_example_menu(examples_menu)
        main_layout.setMenuBar(menubar)

        # ---------------- Run / Record Toolbar ----------------
        exec_toolbar = QHBoxLayout()
        exec_toolbar.setContentsMargins(8, 6, 8, 6)  # add spacing from menu

        self.run_btn = QPushButton("Run")
        self.run_btn.setIcon(make_icon(QColor("#00cc00"), "triangle"))
        self.run_btn.setToolTip("Run the current script")

        self.record_btn = QPushButton("Record")
        self.record_btn.setIcon(make_icon(QColor("#cc0000"), "circle"))
        self.record_btn.setToolTip("Record session")

        # Create "Run in Safe Mode" checkbox
        self.safe_mode_checkbox = QCheckBox(" Run in safe mode")
        self.safe_mode_checkbox.setToolTip("Disables all mouse click commands, only do movement")
        self.safe_mode_checkbox.setChecked(False)

        # Style buttons and add to toolbar
        for b in [self.run_btn, self.record_btn]:
            b.setFixedHeight(32)
            b.setStyleSheet(self.button_style())
            exec_toolbar.addSpacing(4)
            exec_toolbar.addWidget(b)

        exec_toolbar.addSpacing(16)
        exec_toolbar.addWidget(self.safe_mode_checkbox)
        exec_toolbar.addStretch()

        # ---------------- Editor ----------------
        self.editor = CodeEditor()
        self.highlighter = ScriptHighlighter(self.editor.document())
        self.editor.textChanged.connect(self.mark_modified)

        # ---------------- Terminal ----------------

        # Terminal text area
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.terminal.setStyleSheet("""
            QPlainTextEdit {
                background-color: black;
                color: #f0f0f0;
                font-family: Consolas, monospace;
            }
        """)

        # Header (label + clear button)
        terminal_label = QLabel("> Terminal")
        terminal_label.setStyleSheet("padding:2px;")
        terminal_label.setFixedHeight(20)

        # Clear button
        clear_button = QPushButton("Clear")
        clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        clear_button.setToolTip("Clear terminal")
        clear_button.setFixedHeight(24)
        clear_button.setCursor(Qt.CursorShape.PointingHandCursor)

        clear_button.setStyleSheet(self.button_style())

        clear_button.clicked.connect(self.terminal.clear)



        # Horizontal header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 0, 4, 0)
        header_layout.setSpacing(4)
        header_layout.addWidget(terminal_label)
        header_layout.addStretch()  # pushes the button to the right
        header_layout.addWidget(clear_button)

        # Combine header and terminal in a vertical layout
        terminal_container = QVBoxLayout()
        terminal_container.setContentsMargins(0, 0, 0, 0)
        terminal_container.setSpacing(1)
        terminal_container.addLayout(header_layout)
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
        splitter = QSplitter(Qt.Orientation.Vertical)   
        splitter.addWidget(self.editor)
        splitter.addWidget(terminal_widget)
        splitter.setSizes([400, 150])

        # ---------------- Bottom status bar ----------------
        bottom_bar = QFrame()
        bottom_bar.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10, 2, 10, 2)
        self.coord_label = QLabel("X:0, Y:0")
        bottom_layout.addWidget(self.coord_label)
        bottom_layout.addStretch()

        # ---------------- Assemble ----------------
        main_layout.addLayout(exec_toolbar)
        main_layout.addWidget(splitter)
        main_layout.addWidget(bottom_bar)
        self.setLayout(main_layout)

        # ---------------- Connections ----------------
        self.run_btn.clicked.connect(self.run_script)
        self.record_btn.clicked.connect(self.record_script)
        #self.safe_mode_checkbox.cl

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

        Settings.load_from_file()
        self.update_settings()

        logger_editor.info("Editor started")
    
    def update_settings(self):
        self.update_all_widget_fonts(self, Settings.text_size)
    
    def open_settings_dialog(self):
        """Show the settings dialog"""
        logger_editor.debug("Opened settings dialog")
        dialog = SettingsDialog(self, self.update_settings)  # parent = main window
        if dialog.exec():               # exec() blocks until dialog is closed
            pass

        logger_editor.debug("Closed settings")
   
    
    def update_all_widget_fonts(self, widget, size):
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)

        for child in widget.findChildren(QWidget):
            self.update_all_widget_fonts(child, size)


    def setup_example_menu(self, examples_menu):
        from pathlib import Path

        def _find_examples_dir() -> Path | None:
            # Try PyInstaller-aware path first
            examples_dir = resource_path("example_programs")
            if examples_dir.exists() and examples_dir.is_dir():
                return examples_dir

            return None

        def _make_loader(path: Path):
            def _loader(*_args):
                print("Example file path:", path)
                if not self.confirm_discard_changes():
                    return
                try:
                    with path.open("r", encoding="utf-8") as fh:
                        self.editor.setPlainText(fh.read())
                    self.current_file = None
                    self.is_modified = False
                    logger_editor.info(f"Loaded example: {path.name}")
                except Exception:
                    logger_editor.exception(f"Failed to load example {path}")
            return _loader

        examples_dir = _find_examples_dir()
        print("Examples dir path:", examples_dir)
        if examples_dir:
            files = sorted(
                [p for p in examples_dir.iterdir() if p.is_file()],
                key=lambda p: p.name.lower(),
            )
            if files:
                for p in files:
                    action = QAction(p.name, self)
                    action.triggered.connect(_make_loader(p))
                    examples_menu.addAction(action)
            else:
                no_action = QAction("No examples found", self)
                no_action.setEnabled(False)
                examples_menu.addAction(no_action)
        else:
            no_dir_action = QAction("No examples directory", self)
            no_dir_action.setEnabled(False)
            examples_menu.addAction(no_dir_action)


    # ---------------- Utility Methods ----------------
    def button_style(self):
        return """
            QPushButton {
                font-weight: normal;
                padding: 4px 10px;
                border: 1px solid #aaa;
                border-radius: 6px;
                background-color: palette(button);
                color: palette(button-text);
            }
            QPushButton:hover {
                background-color: rgba(150, 150, 150, 30);  /* semi-transparent overlay */
            }
        """

    
    # ==========================================================
    # script save / load methods
    # ==========================================================

    def mark_modified(self):
        self.is_modified=True

    def confirm_discard_changes(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
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

    def save_file_as(self):
        fname,_=QFileDialog.getSaveFileName(self,"Save File As","","Text Files (*.txt *.py *.md);;All Files (*)")
        if not fname: return
        self.current_file=fname
        self.save_file()

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

    def _get_safe_mode_flag(self) -> bool:
        return self.safe_mode_checkbox.isChecked()

    def run_script(self):
        code_src = self.editor.toPlainText()
        if Settings.clear_terminal_on_run:
            self.terminal.clear()

        logger_exec.info("Running script...")

        from app_logic.virtual_machine.executor_process import begin_compile_and_execute_process, RunParams

        self.queue_listener.start()
        params = RunParams(
            code_src,
            self._get_safe_mode_flag(),
            Qt.Key(Settings.pause_resume_key),
            self.log_queue
        )
        # Start the subprocess and disable the Run button until it finishes
        self.proc = begin_compile_and_execute_process(params)
        self.subprocess_mark_as_started("run")
    
    def record_script(self):
        logger_editor.info("Starting recording session")
        
        from app_logic.recorder.recorder_process import begin_recording_process
        # ensure queue listener is running so process logs appear
        self.queue_listener.start()

        # create a small message queue for IPC (child -> parent)
        self.msg_queue = multiprocessing.Queue()

        # Start the subprocess and disable the Run/Record buttons until it finishes
        self.proc = begin_recording_process(self.log_queue, self.msg_queue)
        self.subprocess_mark_as_started("record")
    
    def subprocess_mark_as_started(self, process: Literal["run", "record"]):
        """Disables the Run and Record buttons and starts the process monitor timer.
        """
        self.run_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.proc_monitor_timer.start(500)
        self.process_type = process

    def update_mouse_position(self):
        pos = QCursor.pos()
        self.coord_label.setText(f"X:{pos.x()}  Y:{pos.y()}")
    
    def show_end_dialog(self):
        """Show an always-on-top info dialog saying 'Program ended.'"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Information")
        msg_box.setText("Script execution terminated.")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Make sure it's always on top
        msg_box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        msg_box.setWindowModality(Qt.WindowModality.ApplicationModal)

        msg_box.exec()

    def _check_process(self):
        """Poll the subprocess; when it exits, stop the listener and re-enable UI."""
        # First, check for any IPC messages from the child (e.g., recorded src)
        try:
            if getattr(self, 'msg_queue', None):
                # drain any messages - non-blocking
                while True:

                    try:
                        msg = self.msg_queue.get_nowait()
                    except Exception:
                        break
                    
                    else:
                        # Received recorded source; put into editor on main thread
                        try:
                            cursor = self.editor.textCursor()
                            cursor.beginEditBlock()
                            # Move to end of the current line, then try to move to the next block (next line)
                            cursor.movePosition(QTextCursor.MoveOperation.End)
                            cursor.insertText("\n" + msg + "\n")
                            cursor.endEditBlock()
                            # update editor cursor to reflect the insertion
                            self.editor.setTextCursor(cursor)
                            logger_editor.info("Inserted recorded source into editor.")
                        except Exception:
                            logger_editor.exception("Failed to insert recorded source into editor")
        except Exception:
            logger_editor.exception("Error while reading msg_queue")

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

            if Settings.notify_when_program_ends:
                if self.process_type == "run":
                    self.show_end_dialog()

            # reset state
            self.proc = None

            # re-enable Run/Record buttons
            self.run_btn.setEnabled(True)
            self.record_btn.setEnabled(True)

            # stop the monitor timer
            self.proc_monitor_timer.stop()

