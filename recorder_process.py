from __future__ import annotations
import sys
import logging
from PyQt5 import QtWidgets, QtCore
from typing import Optional
from logging.handlers import QueueListener
import multiprocessing

import pyautogui

from recorder import Recorder
from decompiler import Decompiler
import logger_config

from processes_utils import start_key_quitter, setup_subprocess_logging, ProcessDialog


def _start_recording(log_queue: Optional[multiprocessing.Queue] = None, result_queue: Optional[multiprocessing.Queue] = None):
    """
    Runs in a subprocess. Shows a small PyQt5 dialog and executes recording logic in 
    a background thread so the GUI remains responsive.
    """

    setup_subprocess_logging(log_queue)
    
    class MouseRecorderDialog(ProcessDialog):
        def __init__(self):
            super().__init__(
                "Recorder", 
                "Recording mouse actions, press ENTER to finish recording.\npress ESC to cancel (recording will be lost)", 
                logger_config.logger_editor, 
                ExecutionThread()
            )
            self.pause_button.hide()
            self.stop_button.setText("Stop Recording")
            self.stop_button.clicked.connect(lambda: pyautogui.press('enter'))

    class ExecutionThread(QtCore.QThread):
        finished = QtCore.pyqtSignal()

        def run(self):
            program = Recorder().start()
            src = None
            if program:
                src = Decompiler().decompile_to_src(program)
            # send recorded source back to parent via result_queue if provided
            try:
                if result_queue and src:
                    result_queue.put(src)
            except Exception:
                logger_config.logger_editor.exception("Failed to put src into result_queue")

            self.finished.emit()
    
    listener = start_key_quitter()

    # --- Run Qt event loop in main thread ---
    app = QtWidgets.QApplication(sys.argv)
    dlg = MouseRecorderDialog()
    dlg.show()
    app.exec_()
    
    listener.stop()
    

# ---------------------------
# Helper to start program in a process
# ---------------------------
def begin_recording_process(
    log_queue: Optional[multiprocessing.Queue] = None,
    result_queue: Optional[multiprocessing.Queue] = None,
) -> multiprocessing.Process:
    """
    Start execution in a separate process from source text.
    Returns the Process object so caller can terminate it if needed.
    Logs are redirected to log_queue if provided.
    """

    proc = multiprocessing.Process(target=_start_recording, args=(log_queue, result_queue))
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


    proc = begin_recording_process(log_queue)
    print("Press ESC or click Stop in the popup to terminate the running process.")

    try:
        proc.join()
    finally:
        listener.stop()
        print("Listener stopped. Exiting.")
