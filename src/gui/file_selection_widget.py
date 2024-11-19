from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QFileDialog, QListWidgetItem
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger("McSAS3")

class FileSelectionWidget(QWidget):
    def __init__(self, file_types="All Files (*.*)", parent=None):
        super().__init__(parent)
        self.file_types = file_types
        layout = QVBoxLayout()

        # File List
        self.file_list_widget = QListWidget()
        layout.addWidget(self.file_list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.load_files_button = QPushButton("Load Files")
        self.load_files_button.clicked.connect(self.load_files)
        self.clear_files_button = QPushButton("Clear Files")
        self.clear_files_button.clicked.connect(self.clear_files)
        button_layout.addWidget(self.load_files_button)
        button_layout.addWidget(self.clear_files_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", self.file_types)
        for file in files:
            if not self.is_file_in_list(file):
                item = QListWidgetItem(file)
                item.setData(Qt.ItemDataRole.UserRole, file)
                self.file_list_widget.addItem(item)

    def clear_files(self):
        for item in self.file_list_widget.selectedItems():
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

    def is_file_in_list(self, file):
        return any(self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole) == file
                   for i in range(self.file_list_widget.count()))
