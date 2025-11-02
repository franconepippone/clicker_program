from __future__ import annotations 
from typing import Optional
import sys
import logging
from PyQt5 import QtWidgets, QtCore
from logging.handlers import QueueListener
import multiprocessing
from pynput import keyboard

from .executor import Executor
from app_logic.compiler.compiler import Compiler
from app_logic.compiler.compiler_config import configure_compiler
import utils.logger_config as logger_config

from utils.processes_utils import start_key_quitter, setup_subprocess_logging, ProcessDialog

# text shown in the process dialog
DIALOG_TEXT = """
Runnig script, press ESC to terminate.
Press SPACE to pause/resume execution.
"""

def _run_program_from_text(text: str, log_queue: Optional[multiprocessing.Queue] = None):
    """
    Runs in a subprocess. Shows a small PyQt5 dialog and executes program logic
    in a background thread so the GUI remains responsive.
    """

    setup_subprocess_logging(log_queue)

    class ScriptRunnerDialog(ProcessDialog):
        worker: ExecutionThread

        def __init__(self):
            super().__init__("Script runner", DIALOG_TEXT, logger_config.logger_editor, ExecutionThread(text))
            self.worker.compilation_failed.connect(self._change_text_to_compilation_failed)
            self.stop_button.clicked.connect(self.terminate_process)
            self.pause_button.clicked.connect(self.worker.executor.pause)
            self.play_button.clicked.connect(self.worker.executor.resume)
            self.worker.executor.set_pause_callback(self._on_pause_instruction)
            self._start_pause_listener()
        
        def _on_pause_instruction(self):
            # if pause is requested from instruction, click pause button to update UI (does not affect execution state)
            if self.pause_button.isVisible():   # only clicks when visible to avoid infinite loop
                self.pause_button.click() # emulates click (note that at this point execution is already paused by internal call to pause)  

        def _change_text_to_compilation_failed(self):
            self.label.setText("Script compilation failed. Check terminal for error messages.")
            self.stop_button.setText("Close")
            self.pause_button.hide()
        
        def _start_pause_listener(self):
            """Starts a keyboard listener that pauses/resumes execution on SPACE key press."""
            def on_press(key):
                if key == keyboard.Key.space:
                    if not self.paused:
                        self.pause_button.click()
                    else:
                        self.play_button.click()

            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            return listener

    class ExecutionThread(QtCore.QThread):
        finished = QtCore.pyqtSignal()
        compilation_failed = QtCore.pyqtSignal()
        executor: Executor

        def __init__(self, text):
            super().__init__()
            self.text = text
            self.executor = Executor()

        def run(self):
            program = Compiler(configure_compiler).compile_from_src(self.text)
            if not program:
                self.compilation_failed.emit()
                logger_config.logger_editor.error("Compilation failed.")
                return
            
            self.executor.load_instructions(program).execute()
            self.finished.emit()

    key_listener = start_key_quitter()

    # --- Run Qt event loop in main thread ---
    app = QtWidgets.QApplication(sys.argv)
    dlg = ScriptRunnerDialog()
    dlg.show()
    app.exec_()

    key_listener.stop()


# ---------------------------
# Helper to start program in a process
# ---------------------------
def begin_compile_and_execute_process(
    text: str, log_queue: Optional[multiprocessing.Queue] = None
) -> multiprocessing.Process:
    """
    Start execution in a separate process from source text.
    Returns the Process object so caller can terminate it if needed.
    Logs are redirected to log_queue if provided.
    """

    proc = multiprocessing.Process(target=_run_program_from_text, args=(text, log_queue))
    proc.start()
    return proc


# ---------------------------
# Example usage (main process)
# ---------------------------
if __name__ == "__main__":
    log_queue = multiprocessing.Queue()

    class ProcessLogHandler(logging.Handler):
        def emit(self, record):
            msg = self.format(record)
            print(f"PROCESS: {msg}")

    console_handler = ProcessLogHandler()
    formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(formatter)

    listener = QueueListener(log_queue, console_handler)
    listener.start()

    # Load and run program from file
    with open("recording.txt", "r", encoding="utf-8") as f:
        text = f.read()

    proc = begin_compile_and_execute_process(text, log_queue)
    print("Press ESC or click Stop in the popup to terminate the running process.")

    try:
        proc.join()
    finally:
        listener.stop()
        print("Listener stopped. Exiting.")
