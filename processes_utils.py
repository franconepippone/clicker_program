from typing import Optional
import multiprocessing
from PyQt5 import QtWidgets, QtCore
import logging
from logging.handlers import QueueHandler, QueueListener
import os
import time
from pynput import keyboard

import logger_config


def start_key_listener():
    """
    Start a keyboard listener that quits the program when ESC is pressed.
    """
    def on_press(key):
        if key == keyboard.Key.esc:
            logger_config.logger_editor.warning("ESC pressed — terminating.")
            time.sleep(.2)  # Give time for log to flush
            os._exit(0)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def setup_subprocess_logging(log_queue: Optional[multiprocessing.Queue] = None):
    """
    Setup logging via queue if provided.
    """
    if log_queue:
        queue_handler = QueueHandler(log_queue)
        for logger in [
            logger_config.logger_comp,
            logger_config.logger_exec,
            logger_config.logger_decompiler,
            logger_config.logger_editor,
            logger_config.logger_recorder
        ]:
            logger.handlers.clear()
            logger.addHandler(queue_handler)
            logger.setLevel(logging.DEBUG)



# --- Qt GUI ---
class ProcessDialog(QtWidgets.QDialog):
    def __init__(self, window_title: str, window_message: str, logger: logging.Logger, execution_thread: QtCore.QThread):
        super().__init__()
        self.setWindowTitle(window_title)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Dialog | QtCore.Qt.WindowCloseButtonHint)    # type: ignore
        self.setFixedSize(300, 150)

        self.logger = logger

        layout = QtWidgets.QVBoxLayout()
        # add small contents margins so the label wraps inside the dialog borders
        layout.setContentsMargins(8, 8, 8, 8)
        self.label = QtWidgets.QLabel(window_message, self)
        self.label.setStyleSheet("font-size: 10pt;")

        # allow the label to wrap long text within the dialog width
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)  # type: ignore
        layout.addWidget(self.label)

        self.stop_button = QtWidgets.QPushButton("Stop", self)
        # Do not let this button auto-become the default (Enter) when focused
        self.stop_button.setAutoDefault(False)
        self.stop_button.setDefault(False)
        # Option A (move initial focus to the dialog itself so the button isn't focused)
        self.setFocus(QtCore.Qt.OtherFocusReason)  # type: ignore

        layout.addWidget(self.stop_button)

        self.setLayout(layout)

        # Start execution in background thread
        self.worker = execution_thread
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def terminate_process(self):
        self.logger.warning("Stop button pressed — terminating.")
        os._exit(0)

    def on_finished(self):
        self.label.setText("Finished.")
        os._exit(0)