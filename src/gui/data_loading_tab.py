# src/gui/data_loading_tab.py

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog,
    QListWidget, QHBoxLayout, QListWidgetItem, QMessageBox
)
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file
from pathlib import Path
import yaml
from mcsas3.McData1D import McData1D
from PyQt6.QtCore import Qt

logger = logging.getLogger("McSAS3")

class DataLoadingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Dropdown for default configuration files from "read_configurations" directory
        self.config_dropdown = QComboBox()
        default_configs = get_default_config_files(directory="read_configurations")
        self.config_dropdown.addItems(default_configs)
        layout.addWidget(QLabel("Select Default Configuration:"))
        layout.addWidget(self.config_dropdown)

        # YAML Editor for data loading configuration
        self.yaml_editor_widget = YAMLEditorWidget("read_configurations", parent=self)
        layout.addWidget(QLabel("Data Loading Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Connect dropdown to load selected configuration in YAML editor
        self.config_dropdown.currentTextChanged.connect(self.load_selected_default_config)

        # File List for Drag-and-Drop
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.dragEnterEvent = self.file_list_drag_enter_event
        self.file_list_widget.dropEvent = self.file_list_drop_event
        layout.addWidget(QLabel("Loaded Files:"))
        layout.addWidget(self.file_list_widget)

        # Buttons for managing data files
        file_button_layout = QHBoxLayout()
        load_files_button = QPushButton("Load Datafile(s)")
        load_files_button.clicked.connect(self.load_selected_files)
        clear_files_button = QPushButton("Clear Datafile(s)")
        clear_files_button.clicked.connect(self.clear_files)
        show_selected_button = QPushButton("Show Selected")
        show_selected_button.clicked.connect(self.show_selected_files)
        file_button_layout.addWidget(load_files_button)
        file_button_layout.addWidget(clear_files_button)
        file_button_layout.addWidget(show_selected_button)
        layout.addLayout(file_button_layout)

        self.setLayout(layout)
        logger.debug("DataLoadingTab initialized with file list and configuration options.")

        # Auto-load the first configuration if available
        if default_configs:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def load_selected_default_config(self):
        """Load the selected YAML configuration file into the YAML editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file:
            yaml_content = load_yaml_file(f"read_configurations/{selected_file}")
            self.yaml_editor_widget.set_yaml_content(yaml_content)

    def file_list_drag_enter_event(self, event):
        """Allow drag-and-drop of files into the file list widget."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def file_list_drop_event(self, event):
        """Handle files dropped into the file list widget."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.add_file_to_list(file_path)

    def add_file_to_list(self, file_path):
        """Add a file to the file list if it’s not already present."""
        if file_path not in [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())]:
            QListWidgetItem(file_path, self.file_list_widget)
            logger.debug(f"Added file to list: {file_path}")

    def load_selected_files(self):
        """Open a file dialog to load data files and add them to the file list widget."""
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Data Files", "", "All Files (*.*)")
        if file_names:
            for file_name in file_names:
                self.add_file_to_list(file_name)
            logger.debug(f"Loaded data files: {file_names}")

    def clear_files(self):
        """Remove only the selected files from the file list."""
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Clear Files", "No files selected.")
            return

        for item in selected_items:
            self.file_list_widget.takeItem(self.file_list_widget.row(item))
            logger.debug(f"Removed file from list: {item.text()}")

    def show_selected_files(self):
        """Load and display data from the selected files using McSAS3."""
        selected_files = [
            self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list_widget.count())
            if self.file_list_widget.item(i).isSelected()
        ]

        if not selected_files:
            QMessageBox.information(self, "Show Files", "No files selected.")
            return

        # Parse the YAML configuration from the editor
        try:
            yaml_content = self.yaml_editor_widget.yaml_editor.toPlainText()
            yaml_config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            QMessageBox.critical(self, "YAML Error", f"Error parsing YAML configuration:\n{e}")
            return

        # Load and display data for each selected file
        for file_path in selected_files:
            try:
                mds = McData1D(
                    filename=Path(file_path),
                    nbins=yaml_config.get("nbins", 100),
                    csvargs=yaml_config.get("csvargs", {}),
                    resultIndex=yaml_config.get("resultIndex", 1)
                )
                logger.debug(f"Loaded data file: {file_path}")

                # Update the display text with a checkmark but keep original filename in UserRole
                for i in range(self.file_list_widget.count()):
                    item = self.file_list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == file_path:
                        item.setText(f"✅ {file_path}")
                        break

                # Plot data in the output panel
                self.parent().output_tab.plot_data(mds)

            except Exception as e:
                logger.error(f"Error loading file {file_path}: {e}")
                QMessageBox.critical(self, "Loading Error", f"Failed to load file {file_path}:\n{e}")

    # def show_selected_files(self):
    #     """Load and display data from the selected files using McSAS3."""
    #     selected_files = [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count()) if self.file_list_widget.item(i).isSelected()]
        
    #     if not selected_files:
    #         QMessageBox.information(self, "Show Files", "No files selected.")
    #         return

    #     # Parse the YAML configuration from the editor
    #     try:
    #         yaml_content = self.yaml_editor_widget.yaml_editor.toPlainText()  # Corrected attribute access
    #         yaml_config = yaml.safe_load(yaml_content)
    #     except yaml.YAMLError as e:
    #         QMessageBox.critical(self, "YAML Error", f"Error parsing YAML configuration:\n{e}")
    #         return

    #     # Load and display data for each selected file
    #     for file_path in selected_files:
    #         try:
    #             mds = McData1D(
    #                 filename=Path(file_path),
    #                 nbins=yaml_config.get("nbins", 100),
    #                 csvargs=yaml_config.get("csvargs", {}),
    #                 resultIndex=yaml_config.get("resultIndex", 1)
    #             )
    #             logger.debug(f"Loaded data file: {file_path}")
    #             QMessageBox.information(self, "Data Loaded", f"File {file_path} loaded successfully.\nData Summary: {mds}")
    #         except Exception as e:
    #             logger.error(f"Error loading file {file_path}: {e}")
    #             QMessageBox.critical(self, "Loading Error", f"Failed to load file {file_path}:\n{e}")
