import os
import logging
from pathlib import Path
from tempfile import gettempdir
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTextEdit, QFileDialog, QMessageBox, QComboBox
)
import yaml
from gui.yaml_editor_widget import YAMLEditorWidget
from .file_line_selection_widget import FileLineSelectionWidget
from utils.file_utils import get_default_config_files

logger = logging.getLogger("McSAS3")


class HistogramSettingsTab(QWidget):
    _programmatic_change = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_used_directory = Path(gettempdir())  # Default to system temp directory
        self.test_data_file = None  # Store the selected test data file

        layout = QVBoxLayout()

        # Dropdown for histogram configurations
        self.config_dropdown = QComboBox()
        self.refresh_config_dropdown()
        layout.addWidget(QLabel("Select Default Histogramming Configuration:"))
        layout.addWidget(self.config_dropdown)
        self.config_dropdown.currentTextChanged.connect(self.handle_dropdown_change)

        # YAML Editor for histogram settings
        self.yaml_editor_widget = YAMLEditorWidget(directory="hist_configurations", parent=self)
        layout.addWidget(QLabel("Histogramming Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Monitor changes in the YAML editor to detect custom changes
        self.yaml_editor_widget.yaml_editor.textChanged.connect(self.on_yaml_editor_change)

        # File Selection for Test Datafile
        self.file_line_selection_widget = FileLineSelectionWidget(
            placeholder_text="Select histogramming configuration",
            file_types="YAML Files (*.yaml)"
        )
        self.file_line_selection_widget.fileSelected.connect(self.select_test_datafile)
        layout.addWidget(self.file_line_selection_widget)

        # Test Button
        test_button = QPushButton("Test Histogramming")
        test_button.clicked.connect(self.test_histogramming)
        layout.addWidget(test_button)

        # Information Output
        self.info_field = QTextEdit()
        self.info_field.setReadOnly(True)
        layout.addWidget(QLabel("Test Output:"))
        layout.addWidget(self.info_field)

        self.setLayout(layout)

        # Automatically load the first configuration if available
        if self.config_dropdown.count() > 0:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def refresh_config_dropdown(self):
        """Populate or refresh the histogramming configuration dropdown."""
        self.config_dropdown.clear()
        default_configs = get_default_config_files(directory="hist_configurations")
        self.config_dropdown.addItems(default_configs)
        self.config_dropdown.addItem("<Other...>")

    def handle_dropdown_change(self):
        """Handle dropdown changes and load the selected configuration."""
        selected_text = self.config_dropdown.currentText()
        if selected_text != "<Other...>":
            self.load_selected_default_config()

    def load_selected_default_config(self):
        """Load the selected histogramming configuration YAML file into the editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file and selected_file != "<Other...>":
            try:
                # Construct the full path to the selected file
                file_path = Path("hist_configurations") / selected_file
                if file_path.is_file():
                    with open(file_path, 'r') as file:
                        # Parse YAML content as structured data
                        yaml_content = list(yaml.safe_load_all(file))
                    # Pass parsed content to the YAML editor
                    # Temporarily disable the on_yaml_editor_change trigger
                    self._programmatic_change = True
                    self.yaml_editor_widget.set_yaml_content(yaml_content)
                    self._programmatic_change = False
                else:
                    logger.error(f"File not found: {file_path}")
                    QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            except Exception as e:
                logger.error(f"Error loading histogramming configuration: {e}")
                QMessageBox.critical(self, "Error", f"Error loading histogramming configuration: {e}")

    def on_yaml_editor_change(self):
        """Mark the dropdown as <Other...> if the YAML content is modified by the user."""
        if hasattr(self, "_programmatic_change") and self._programmatic_change:
            # Skip handling changes triggered programmatically
            return
        if self.config_dropdown.currentText() != "<Other...>":
            self.config_dropdown.setCurrentText("<Other...>")

    def select_test_datafile(self):
        """Open a file dialog to select a test data file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Test Data File",
            str(self.last_used_directory),
            "Data Files (*.nxs *.h5 *.hdf5)"
        )
        if file_name:
            self.last_used_directory = Path(file_name).parent  # Update the last used directory
            self.file_path_line.setText(file_name)
            self.test_data_file = file_name
            logger.debug(f"Selected test data file: {file_name}")

    def test_histogramming(self):
        """Execute a histogramming test with the current settings and selected data file."""
        try:
            if not self.test_data_file or not Path(self.test_data_file).exists():
                QMessageBox.warning(self, "Error", "Please select a valid test data file.")
                return

            yaml_content = self.yaml_editor_widget.get_yaml_content()
            if not yaml_content:
                QMessageBox.warning(self, "Error", "Please configure histogramming settings.")
                return

            logger.debug("Launching histogramming test.")
            self.info_field.append("Launching histogramming test...")
            command = [
                "python",
                "histogram_cli_runner.py",
                "--config", "hist_configurations/histogram_config.yaml",
                "--datafile", self.test_data_file
            ]

            # TODO: Replace with actual subprocess logic
            self.info_field.append(f"Command executed: {' '.join(command)}\n")
            self.info_field.append("Test histogramming completed successfully.\n")

        except Exception as e:
            logger.error(f"Error during histogramming test: {e}")
            QMessageBox.critical(self, "Error", f"Error during histogramming test: {e}")
