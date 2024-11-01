# src/gui/run_settings_tab.py

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file, save_yaml_file  # Import YAML load and save functions
from sasmodels.core import load_model_info  # Ensure sasmodels is installed and accessible
import re

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
        if not yaml_content:
            self.info_field.setPlainText("Invalid YAML or empty configuration.")
            return

        # Start by displaying general YAML configuration information
        info_text = "Configuration Details:\n"
        
        # Retrieve basic configuration settings from YAML
        model_name = yaml_content.get("modelName", "Unknown Model")
        info_text += f"Model Name: {model_name}\n"

        max_iter = yaml_content.get("maxIter", "Not specified")
        conv_crit = yaml_content.get("convCrit", "Not specified")
        n_cores = yaml_content.get("nCores", "Not specified")
        info_text += f"Max Iterations: {max_iter}\nConvergence Criterion: {conv_crit}\nCores: {n_cores}\n"

        # If the modelName starts with "mcsas_", skip sasmodels model loading
        if model_name.startswith("mcsas_"):
            info_text += "\nUsing internal McSAS model. No additional sasmodels parameters available.\n"
            self.info_field.setPlainText(info_text)
            return

        try:
            # Load model info from sasmodels for supported models
            model_info = load_model_info(model_name)
            model_parameters = model_info.parameters.defaults.copy()

            # Filter out parameters that match exclusion patterns
            exclude_patterns = [r'up_.*', r'.*_M0', r'.*_mtheta', r'.*_mphi']
            filtered_parameters = {
                param: default_value
                for param, default_value in model_parameters.items()
                if not any(re.match(pattern, param) for pattern in exclude_patterns)
            }

            # Append sasmodels parameters to info text
            info_text += "\nSasmodels Parameters:\n"
            for param, default_value in filtered_parameters.items():
                info_text += f"  - {param}: {default_value}\n"

            info_text += "\nTo configure parameters, add each to 'fitParameterLimits' or 'staticParameters' in the YAML editor.\n"
            info_text += "For 'fitParameterLimits', specify lower and upper limits as a list."

        except Exception as e:
            info_text += f"\nError loading model parameters from sasmodels: {e}"

        # Set the final text to info_field
        self.info_field.setPlainText(info_text)
