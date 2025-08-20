# src/gui/file_line_selection_widget.py

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal  # , QDragEnterEvent, QDropEvent, Qt
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget

logger = logging.getLogger("McSAS3")


class FilePathLineEdit(QLineEdit):
    """A QLineEdit widget with drag-and-drop and manual editing support."""

    fileChanged = pyqtSignal(str)  # Signal emitted when the file path is changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Enable drag-and-drop

    def dragEnterEvent(self, event):
        """Handle drag event to check if the dropped file is valid."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.debug("Drag enter event accepted.")
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop event to process dropped file paths."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if Path(file_path).exists():
                self.setText(file_path)
                self.fileChanged.emit(file_path)  # Emit signal with new file path
                event.accept()
            else:
                logger.warning(f"Dropped file does not exist: {file_path}")
                event.ignore()

    def keyPressEvent(self, event):
        """Handle manual entry of file paths and emit signal on Enter."""
        if event.key() == Qt.Key.Key_Return:
            file_path = self.text()
            if Path(file_path).exists():
                self.fileChanged.emit(file_path)  # Emit signal with entered file path
            else:
                logger.warning(f"Entered file does not exist: {file_path}")
        else:
            super().keyPressEvent(event)


class FileLineSelectionWidget(QWidget):
    """A reusable file selection widget with drag-and-drop and a 'Browse' button."""

    fileSelected = pyqtSignal(str)  # Signal emitted when a file is selected

    def __init__(self, placeholder_text="Select a file", file_types="All Files (*.*)", parent=None):
        super().__init__(parent)

        self.file_types = file_types  # Accepted file types for the file dialog

        # Layout for the file selection widget
        layout = QHBoxLayout(self)

        # Drag-and-drop and editable QLineEdit
        self.file_path_line = FilePathLineEdit()
        self.file_path_line.setStyleSheet(
            """
                QLineEdit {
                    background-color: palette(base);
                    color: palette(text);
                    font-family: "Courier New", monospace;
                }
            """
        )
        self.file_path_line.setPlaceholderText(placeholder_text)
        self.file_path_line.fileChanged.connect(self._emit_file_selected)
        layout.addWidget(self.file_path_line)

        # Browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.select_file)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)

    def select_file(self):
        """Open a file dialog to select a file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.file_types)
        if file_name:
            self.file_path_line.setText(file_name)
            self._emit_file_selected(file_name)

    def _emit_file_selected(self, file_path):
        """Emit the fileSelected signal with the selected file path."""
        logger.debug(f"File selected: {file_path}")
        self.fileSelected.emit(file_path)

    def set_file_path(self, file_path):
        """Set the file path in the QLineEdit."""
        self.file_path_line.setText(file_path)

    def get_file_path(self):
        """Get the current file path from the QLineEdit."""
        return self.file_path_line.text()
