from __future__ import annotations 
from typing import Optional
import sys
import os
import logging
from PyQt6.QtCore import Qt
from PyQt6 import QtCore, QtWidgets
import multiprocessing
from PyQt6.QtGui import QKeyEvent
from pynput import keyboard
import time
from dataclasses import dataclass

from .executor import Executor
from app_logic.compiler.compiler import Compiler
from app_logic.compiler.compiler_config import get_compiler_cfg
import utils.logger_config as logger_config
from utils.processes_utils import setup_subprocess_logging, ProcessDialog


# text shown in the process dialog
DIALOG_TEXT = """
Runnig script, press ESC to terminate.
Press SPACE to pause/resume execution.
"""

@dataclass
class RunParams:
    """Stores all the run parameters to pass to the "run" process"""
    text: str
    safemode: bool
    pause_key: Qt.Key
    log_queue: Optional[multiprocessing.Queue] = None


def _run_program_from_text(params: RunParams):
    """
    Runs in a subprocess. Shows a small PyQt5 dialog and executes program logic
    in a background thread so the GUI remains responsive.
    """

    setup_subprocess_logging(params.log_queue)

    class ScriptRunnerDialog(ProcessDialog):
        worker: ExecutionThread

        def __init__(self):
            super().__init__("Script runner", DIALOG_TEXT, logger_config.logger_editor, ExecutionThread(params.text))
            self.worker.compilation_failed.connect(self._change_text_to_compilation_failed)
            self.stop_button.clicked.connect(self.terminate_process)
            self.pause_button.clicked.connect(self.worker.executor.pause)
            self.play_button.clicked.connect(self.worker.executor.resume)
            self.worker.executor.set_pause_callback(self._on_pause_instruction)
        
        def _on_pause_instruction(self):
            # if pause is requested from instruction, click pause button to update UI (does not affect execution state)
            if self.pause_button.isVisible():   # only clicks when visible to avoid infinite loop
                self.pause_button.click() # emulates click (note that at this point execution is already paused by internal call to pause)  

        def _change_text_to_compilation_failed(self):
            self.label.setText("Script compilation failed. Check terminal for error messages.")
            self.stop_button.setText("Close")
            self.pause_button.hide()

        def keyPressEvent(self, a0: QKeyEvent | None) -> None:
            super().keyPressEvent(a0)
            if a0 and (a0.key() == params.pause_key):
                if not self.paused:
                    self.pause_button.click()
                else:
                    self.play_button.click()

    class ExecutionThread(QtCore.QThread):
        finished = QtCore.pyqtSignal()
        compilation_failed = QtCore.pyqtSignal()
        executor: Executor

        def __init__(self, text):
            super().__init__()
            self.text = text
            self.executor = Executor()

        def run(self):
            cfg_fn = get_compiler_cfg(safemode = params.safemode)
            program = Compiler(cfg_fn).compile_from_src(self.text)
            if not program:
                self.compilation_failed.emit()
                logger_config.logger_editor.error("Compilation failed.")
                return
            
            self.executor.load_instructions(program).execute()
            time.sleep(.5)   # waits for all logs to arrive
            self.finished.emit()


    # --- Run Qt event loop in main thread ---
    app = QtWidgets.QApplication(sys.argv)
    dlg = ScriptRunnerDialog()
    dlg.show()
    app.exec()

# ---------------------------
# Helper to start program in a process
# ---------------------------
def begin_compile_and_execute_process(params: RunParams) -> multiprocessing.Process:
    """
    Start execution in a separate process from source text.
    Returns the Process object so caller can terminate it if needed.
    Logs are redirected to log_queue if provided.
    """

    proc = multiprocessing.Process(target=_run_program_from_text, args=(params,))
    proc.start()
    return proc


# ---------------------------
# Example usage (main process)
# ---------------------------
if __name__ == "__main__":
    from logging.handlers import QueueListener
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

    params = RunParams(
        text,
        False,
        Qt.Key.Key_Space
    )

    proc = begin_compile_and_execute_process(params)
    print("Press ESC or click Stop in the popup to terminate the running process.")

    try:
        proc.join()
    finally:
        listener.stop()
        print("Listener stopped. Exiting.")
