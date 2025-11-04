from __future__ import annotations
from typing import Callable
from PyQt6.QtWidgets import (
    QDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QSlider, QDialogButtonBox, QApplication
)
from PyQt6.QtCore import Qt
import logging

from .settings import Settings


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
        main_layout.setContentsMargins(10, 10, 10, 10)
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
        buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.reject)

        # --- Compose layouts ---
        outer_layout.addLayout(main_layout)
        outer_layout.addWidget(buttons)

        # --- Add pages ---
        self._add_terminal_page()
        self._add_appearance_page()

        # --- Default selection ---
        self.category_list.setCurrentRow(0)
        self.category_list.currentRowChanged.connect(self.stack.setCurrentIndex)

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

        if self.update_fnc:
            self.update_fnc()

        Settings.store_to_file()
        logger_editor.info("Saved settings")

        



# --- Test only ---
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    dlg = SettingsDialog()
    dlg.exec()
