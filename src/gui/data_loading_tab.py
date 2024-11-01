import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QPushButton,
    QFileDialog, QListWidget, QHBoxLayout, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.yaml_utils import load_yaml_file, save_yaml_file, check_yaml_syntax
from utils.file_utils import get_default_config_files
from utils.yaml_syntax_highlighter import YAMLHighlighter  # Import syntax highlighter
import yaml
from pathlib import Path
from mcsas3.McData1D import McData1D  # Ensure McSAS3 is installed and available

logger = logging.getLogger("McSAS3")

class DataLoadingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Dropdown for default configuration files from the root "read_configurations" directory
        self.config_dropdown = QComboBox()
        default_configs = get_default_config_files(directory="read_configurations")
        logger.debug(f"Found default configuration files: {default_configs}")
        self.config_dropdown.addItems(default_configs)
        self.config_dropdown.currentTextChanged.connect(self.load_selected_default_config)
        layout.addWidget(QLabel("Select Default Configuration:"))
        layout.addWidget(self.config_dropdown)

        # YAML Editor with Syntax Highlighting (Drag-and-drop disabled)
        self.yaml_editor = QTextEdit()
        self.yaml_editor.setAcceptDrops(False)  # Disable drag-and-drop in the editor
        self.yaml_highlighter = YAMLHighlighter(self.yaml_editor.document())
        self.yaml_editor.textChanged.connect(self.validate_yaml_syntax)
        layout.addWidget(QLabel("Data Loading Configuration (YAML):"))
        layout.addWidget(self.yaml_editor)

        # Save and Load Configuration Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_yaml)
        load_button = QPushButton("Load Configuration")
        load_button.clicked.connect(self.load_yaml)
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

        # File List for Drag-and-Drop
        self.file_list_widget = QListWidget()
        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.dragEnterEvent = self.file_list_drag_enter_event
        self.file_list_widget.dropEvent = self.file_list_drop_event
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
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

        # Load the first configuration automatically, if available
        if default_configs:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

        logger.debug("DataLoadingTab initialized with file list and configuration options.")

    def load_selected_default_config(self):
        """Load YAML content of the selected configuration file into the editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file:
            logger.debug(f"Loading selected configuration file: {selected_file}")
            yaml_content = load_yaml_file(f"read_configurations/{selected_file}")
            yaml_text = yaml.dump(yaml_content)
            self.yaml_editor.setPlainText(yaml_text)

    def load_yaml(self):
        """Open a file dialog to load a configuration file outside the dropdown list."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "read_configurations", "YAML Files (*.yaml)")
        if file_name:
            logger.debug(f"Loading configuration file: {file_name}")
            yaml_content = load_yaml_file(file_name)
            yaml_text = yaml.dump(yaml_content)
            self.yaml_editor.setPlainText(yaml_text)

    def save_yaml(self):
        """Save the content of the YAML editor to a file."""
        yaml_content = self.yaml_editor.toPlainText()
        logger.debug("Saving YAML configuration.")
        save_yaml_file(yaml_content)

    def validate_yaml_syntax(self):
        """Check the syntax of the YAML content in the editor."""
        check_yaml_syntax(self.yaml_editor)

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
        selected_files = [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count()) if self.file_list_widget.item(i).isSelected()]
        
        if not selected_files:
            QMessageBox.information(self, "Show Files", "No files selected.")
            return

        # Parse the YAML configuration from the editor
        try:
            yaml_config = yaml.safe_load(self.yaml_editor.toPlainText())
        except yaml.YAMLError as e:
            QMessageBox.critical(self, "YAML Error", f"Error parsing YAML configuration:\n{e}")
            return

        # Load and display data for each selected file
        for file_path in selected_files:
            try:
                # Load the file with McData1D, passing configuration options
                mds = McData1D(
                    filename=Path(file_path),
                    nbins=yaml_config.get("nbins", 100),
                    csvargs=yaml_config.get("csvargs", {}),
                    resultIndex=yaml_config.get("resultIndex", 1)
                )
                logger.debug(f"Loaded data file: {file_path}")
                # Display loaded data (e.g., print summary or plot data)
                QMessageBox.information(self, "Data Loaded", f"File {file_path} loaded successfully.\nData Summary: {mds}")
            except Exception as e:
                logger.error(f"Error loading file {file_path}: {e}")
                QMessageBox.critical(self, "Loading Error", f"Failed to load file {file_path}:\n{e}")

            QMessageBox.warning(self, "Selected Files", "No files selected.")
