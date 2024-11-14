from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from pathlib import Path
import os
import logging

logger = logging.getLogger("McSAS3")

class OptimizationRunTab(QWidget):
    def __init__(self, data_loading_tab, run_settings_tab, parent=None):
        super().__init__(parent)
        self.data_loading_tab = data_loading_tab
        self.run_settings_tab = run_settings_tab

        layout = QVBoxLayout()

        # File List Widget (loaded files)
        self.file_list_widget = QListWidget()
        layout.addWidget(QLabel("Loaded Files:"))
        layout.addWidget(self.file_list_widget)

        # Buttons for managing data files
        file_button_layout = QHBoxLayout()
        load_files_button = QPushButton("Load Datafile(s)")
        load_files_button.clicked.connect(self.load_data_files)
        clear_files_button = QPushButton("Clear Datafile(s)")
        clear_files_button.clicked.connect(self.clear_selected_files)
        file_button_layout.addWidget(load_files_button)
        file_button_layout.addWidget(clear_files_button)
        layout.addLayout(file_button_layout)

        # Horizontal line with "Data Configuration" label
        data_config_layout = QVBoxLayout()
        data_config_layout.addWidget(QLabel("Data Configuration"))

        # Data Configuration Section
        self.data_config_selector = QLineEdit()
        self.data_config_selector.setPlaceholderText("Select Data Configuration")
        select_data_config_button = QPushButton("Browse")
        select_data_config_button.clicked.connect(self.select_data_configuration)
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.data_config_selector)
        config_layout.addWidget(select_data_config_button)
        data_config_layout.addLayout(config_layout)

        layout.addLayout(data_config_layout)

        # # Horizontal line with "Data Configuration" label
        run_config_layout = QVBoxLayout()
        run_config_layout.addWidget(QLabel("Run Configuration"))

        # Run Settings Section
        self.run_config_selector = QLineEdit()
        self.run_config_selector.setPlaceholderText("Select Run Settings")
        select_run_config_button = QPushButton("Browse")
        select_run_config_button.clicked.connect(self.select_run_configuration)
        r_config_layout = QHBoxLayout()
        r_config_layout.addWidget(self.run_config_selector)
        r_config_layout.addWidget(select_run_config_button)
        run_config_layout.addLayout(r_config_layout)
        
        layout.addLayout(run_config_layout)

        # Run Button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.generate_cli_command)
        layout.addWidget(self.run_button)

        # CLI Command Display
        self.cli_command_display = QLineEdit()
        self.cli_command_display.setReadOnly(True)
        layout.addWidget(self.cli_command_display)

        # Placeholder for progress indicators
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def load_data_files(self):
        """Open a file dialog to load data files and add them to the file list widget."""
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Data Files", "", "All Files (*.*)")
        for file_name in file_names:
            if not self.is_file_in_list(file_name):
                item = QListWidgetItem(file_name)
                item.setData(Qt.ItemDataRole.UserRole, file_name)  # Store the original filename
                self.file_list_widget.addItem(item)
                logger.debug(f"Added file to list: {file_name}")

    def clear_selected_files(self):
        """Remove only the selected files from the file list."""
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Clear Files", "No files selected.")
            return

        for item in selected_items:
            self.file_list_widget.takeItem(self.file_list_widget.row(item))
            logger.debug(f"Removed file from list: {item.text()}")

    def is_file_in_list(self, file_path):
        """Check if a file is already in the list to avoid duplicates."""
        return any(self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole) == file_path
                   for i in range(self.file_list_widget.count()))

    def select_data_configuration(self):
        """Select a data configuration YAML file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Data Configuration File", "", "YAML Files (*.yaml)")
        if file_name:
            self.data_config_selector.setText(file_name)

    def select_run_configuration(self):
        """Select a run configuration YAML file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Run Settings File", "", "YAML Files (*.yaml)")
        if file_name:
            self.run_config_selector.setText(file_name)

    def generate_cli_command(self):
        """Generate and display the CLI command for running McSAS3."""
        selected_files = [
            self.file_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list_widget.count())
            if self.file_list_widget.item(i).isSelected()
        ]

        if not selected_files:
            QMessageBox.warning(self, "Run Command", "No data files selected.")
            return

        # CLI command format
        cli_command = "mcsas3_cli_runner.py"

        # Generate command for each selected file
        for file_path in selected_files:
            data_file = Path(file_path)
            result_file = data_file.stem + "_mcsas3.nxs"
            data_config = self.data_config_selector.text() or "data_config.yaml"
            run_config = self.run_config_selector.text() or "run_config.yaml"
            cli_command += f" -f {data_file} -F {data_config} -r {result_file} -R {run_config} -i 1 -d"

        # Display CLI command
        self.cli_command_display.setText(cli_command)
        print(cli_command)  # Debug output
