from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class SettingsDialog(QDialog):
    """A simple modal settings window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Example settings fields
        self.dark_mode_checkbox = QCheckBox("Enable dark mode")
        self.confirm_exit_checkbox = QCheckBox("Confirm before exit")

        layout.addWidget(QLabel("General"))
        layout.addWidget(self.dark_mode_checkbox)
        layout.addWidget(self.confirm_exit_checkbox)
        layout.addStretch()

        # OK / Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def get_settings(self) -> dict:
        """Return a dictionary with current settings."""
        return {
            "dark_mode": self.dark_mode_checkbox.isChecked(),
            "confirm_exit": self.confirm_exit_checkbox.isChecked(),
        }
