from typing import Optional
import multiprocessing
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
import logging
from logging.handlers import QueueHandler, QueueListener
import os
import time

import utils.logger_config as logger_config


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
    paused: bool = False

    def __init__(self, window_title: str, window_message: str, logger: logging.Logger, execution_thread: QtCore.QThread):
        super().__init__()
        self.setWindowTitle(window_title)
        self.setWindowFlags(
            QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Dialog
            | QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        self.setFixedSize(300, 150)

        self.logger = logger
        self.execution_thread = execution_thread

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        # Message label
        self.label = QtWidgets.QLabel(window_message, self)
        #self.label.setStyleSheet("font-size: 10pt;")
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        layout.addWidget(self.label)

        # --- Buttons layout ---
        button_layout = QtWidgets.QHBoxLayout()

        # Pause button
        self.pause_button = QtWidgets.QPushButton("Pause", self)
        self.pause_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
        self.pause_button.setAutoDefault(False)
        self.pause_button.setDefault(False)
        self.pause_button.clicked.connect(self.toggle_pause)

        # Play button (initially hidden)
        self.play_button = QtWidgets.QPushButton("Play", self)
        self.play_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.setAutoDefault(False)
        self.play_button.setDefault(False)
        self.play_button.hide()
        self.play_button.clicked.connect(self.toggle_pause)

        # Stop button
        self.stop_button = QtWidgets.QPushButton("Stop", self)
        self.stop_button.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.setAutoDefault(False)
        self.stop_button.setDefault(False)

        # Equal stretch so both buttons share the width
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        button_layout.setStretch(0, 1)
        button_layout.setStretch(1, 1)
        button_layout.setStretch(2, 1)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Move focus away from buttons initially
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason) 

        # Start execution in background thread
        self.worker = execution_thread
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def toggle_pause(self):
        """Toggle between pause and play states."""
        if not self.paused:
            self.pause_button.hide()
            self.play_button.show()
            self.paused = True
        else:
            self.play_button.hide()
            self.pause_button.show()
            self.paused = False
    
    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        if a0:
            if a0.key() == Qt.Key.Key_Escape:
                logger_config.logger_editor.warning("ESC pressed — terminating.")
                time.sleep(.2)  # Give time for log to flush
                os._exit(0)


    def terminate_process(self):
        self.logger.warning("Stop button pressed — terminating.")
        time.sleep(.2)
        os._exit(0)

    def on_finished(self):
        self.label.setText("Finished.")
        os._exit(0)