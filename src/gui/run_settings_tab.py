# src/gui/run_settings_tab.py

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file, save_yaml_file  # Import YAML load and save functions
import sasmodels.core  # For loading model parameters from sasmodels

logger = logging.getLogger("McSAS3")
class RunSettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Dropdown for default run configuration files
        self.config_dropdown = QComboBox()
        default_configs = get_default_config_files(directory="run_configurations")
        self.config_dropdown.addItems(default_configs)
        layout.addWidget(QLabel("Select Default Run Configuration:"))
        layout.addWidget(self.config_dropdown)

        # YAML Editor for run settings configuration
        self.yaml_editor_widget = YAMLEditorWidget("run_configurations", parent=self)
        layout.addWidget(QLabel("Run Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Info text field for model parameters
        self.info_field = QTextEdit()
        self.info_field.setReadOnly(True)
        layout.addWidget(QLabel("Model Parameters Info:"))
        layout.addWidget(self.info_field)

        # Connect dropdown to load selected configuration in YAML editor and populate info
        self.config_dropdown.currentTextChanged.connect(self.load_selected_default_config)
        self.yaml_editor_widget.yaml_editor.textChanged.connect(self.update_info_field)

        self.setLayout(layout)
        if default_configs:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def load_selected_default_config(self):
        """Load the selected run configuration YAML file and update the info field."""
        selected_file = self.config_dropdown.currentText()
        if selected_file:
            yaml_content = load_yaml_file(f"run_configurations/{selected_file}")
            self.yaml_editor_widget.set_yaml_content(yaml_content)
            self.update_info_field()

    def update_info_field(self):
        """Update the info field based on the YAML content in the editor."""
        yaml_content = self.yaml_editor_widget.get_yaml_content()
        # Populate the info field using sasmodels as per your previous instructions
