from __future__ import annotations 
import sys
import os
import logging
from PyQt5 import QtWidgets, QtCore
from pynput import keyboard
from typing import Optional
from logging.handlers import QueueHandler, QueueListener
import multiprocessing
import time

from executor import Executor
from compiler import Compiler
import logger_config

from processes_utils import start_key_listener, setup_subprocess_logging, ProcessDialog

def _run_program_from_text(text: str, log_queue: Optional[multiprocessing.Queue] = None):
    """
    Runs in a subprocess. Shows a small PyQt5 dialog and executes program logic
    in a background thread so the GUI remains responsive.
    """

    setup_subprocess_logging(log_queue)

    class ScriptRunnerDialog(ProcessDialog):
        worker: ExecutionThread

        def __init__(self):
            super().__init__("Script runner", "Runnig script, press ESC to terminate.", logger_config.logger_editor, ExecutionThread(text))
            self.worker.compilation_failed.connect(
                lambda: self.label.setText("Script compilation failed. Check terminal for error messages.")
            )

    class ExecutionThread(QtCore.QThread):
        finished = QtCore.pyqtSignal()
        compilation_failed = QtCore.pyqtSignal()

        def __init__(self, text):
            super().__init__()
            self.text = text

        def run(self):
            program = Compiler().compile_from_src(self.text)
            if not program:
                self.compilation_failed.emit()
                logger_config.logger_editor.error("Compilation failed.")
                return

            Executor().load_instructions(program).execute()
            self.finished.emit()

    key_listener = start_key_listener()

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
    with open("program.txt", "r", encoding="utf-8") as f:
        text = f.read()

    proc = begin_compile_and_execute_process(text, log_queue)
    print("Press ESC or click Stop in the popup to terminate the running process.")

    try:
        proc.join()
    finally:
        listener.stop()
        print("Listener stopped. Exiting.")
