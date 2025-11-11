from __future__ import annotations
from typing import Callable
from PyQt6.QtWidgets import (
    QDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QDialogButtonBox, QApplication, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence
import logging

from .settings import Settings
from utils.allowed_keys import ALLOWED_KEYS_QT


logger_editor = logging.getLogger("Editor")


class SettingsDialog(QDialog):
    """A standardized settings panel with sidebar categories."""
    def __init__(self, parent=None, update_fnc: Callable| None = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 350)

        Settings.load_from_file()
        self.update_fnc = update_fnc

        # --- Main layout structure ---
        outer_layout = QVBoxLayout(self)  # Top-level vertical layout
        main_layout = QHBoxLayout()       # Holds sidebar + stacked pages
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # --- Sidebar ---
        self.category_list = QListWidget()
        self.category_list.setFixedWidth(150)
        self.category_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        main_layout.addWidget(self.category_list)

        # --- Stacked widget for category pages ---
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # --- Buttons (bottom) ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Close
        )
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings) # type: ignore
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.reject) # type: ignore

        # --- Compose layouts ---
        outer_layout.addLayout(main_layout)
        outer_layout.addWidget(buttons)

        # --- Add pages ---
        self._add_terminal_page()
        self._add_appearance_page()
        self._add_execution_page()

        # --- Default selection ---
        self.category_list.setCurrentRow(0)
        self.category_list.currentRowChanged.connect(self.stack.setCurrentIndex)

    # --- Execution settings page ---
    def _add_execution_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Notify checkbox
        self.notify_on_end = QCheckBox(" Notify when program ends")
        self.notify_on_end.setChecked(Settings.notify_when_program_ends)
        layout.addWidget(self.notify_on_end)

        # Pause/Play key selector
        key_layout = QHBoxLayout()
        key_label = QLabel("Pause/Resume key:")
        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setPlaceholderText("No key set")

        key_name = QKeySequence(Settings.pause_resume_key).toString()
        self.key_display.setText(key_name)
        self.key_id = Settings.pause_resume_key

        set_key_button = QPushButton("Set Key")
        set_key_button.clicked.connect(self._capture_pause_play_key)

        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_display)
        key_layout.addWidget(set_key_button)
        layout.addLayout(key_layout)

        layout.addStretch()

        self.category_list.addItem(QListWidgetItem("Execution"))
        self.stack.addWidget(page)


    def _capture_pause_play_key(self):
        """Open a small dialog to capture a single key press."""

        class KeyCaptureDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Press a key")
                self.setModal(True)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
                self.resize(250, 100)

                layout = QVBoxLayout(self)
                label = QLabel("Press any key to assign as Pause/Resume key", self)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)

                self.captured_key = None

            def keyPressEvent(self, a0: QKeyEvent | None) -> None:
                # Capture the key name (add key filtering eventually)
                if a0 is not None:
                    if a0.key() in ALLOWED_KEYS_QT: # key filtering
                        self.captured_key = a0.key()
                        self.accept()

        # Show key capture dialog
        dlg = KeyCaptureDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.captured_key:
            # Convert Qt key to readable name
            key_name = QKeySequence(dlg.captured_key).toString()
            self.key_display.setText(key_name)
            self.key_id = dlg.captured_key
            # You can store it to Settings if desired:
            # Settings.pause_play_key = dlg.captured_key

            
    # --- Terminal settings page ---
    def _add_terminal_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.print_debug_checkbox = QCheckBox(" Print debug messages")
        self.print_debug_checkbox.setChecked(Settings.print_debug_msg)
        self.clear_on_run_checkbox = QCheckBox(" Automatically clear on run")
        self.clear_on_run_checkbox.setChecked(Settings.clear_terminal_on_run)

        layout.addWidget(self.print_debug_checkbox)
        layout.addWidget(self.clear_on_run_checkbox)
        layout.addStretch()

        self.category_list.addItem(QListWidgetItem("Terminal"))
        self.stack.addWidget(page)

    # --- Appearance settings page ---
    def _add_appearance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.dark_mode_checkbox = QCheckBox(" Dark mode")
        self.text_size_label = QLabel("Text size:")
        self.text_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_size_slider.setRange(5, 20)
        self.text_size_slider.setValue(Settings.text_size)
        self.text_size_slider.setTickInterval(1)
        self.text_size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        #layout.addWidget(self.dark_mode_checkbox)
        layout.addWidget(self.text_size_label)
        layout.addWidget(self.text_size_slider)
        layout.addStretch()

        self.category_list.addItem(QListWidgetItem("Appearance"))
        self.stack.addWidget(page)

    # --- Apply settings ---
    def apply_settings(self):
        Settings.print_debug_msg = self.print_debug_checkbox.isChecked()
        Settings.clear_terminal_on_run = self.clear_on_run_checkbox.isChecked()
        Settings.dark_mode = self.dark_mode_checkbox.isChecked()
        Settings.text_size = self.text_size_slider.value()
        Settings.notify_when_program_ends = self.notify_on_end.isChecked()
        Settings.pause_resume_key = self.key_id

        if self.update_fnc:
            self.update_fnc()

        Settings.store_to_file()
        logger_editor.info("Saved settings")
    
    def keyPressEvent(self, a0: QKeyEvent | None):
        """Handle keypresses from inside the dialog."""
        if (event := a0) is not None:
            if event.key() == Qt.Key.Key_Escape:
                self.accept()  # Close on Esc
            else:
                super().keyPressEvent(a0)

        



# --- Test only ---
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dlg = SettingsDialog()
    dlg.exec()
