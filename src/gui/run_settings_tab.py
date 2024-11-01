import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QPushButton,
    QFileDialog, QHBoxLayout, QMessageBox
)
from utils.yaml_utils import load_yaml_file, save_yaml_file, check_yaml_syntax
from utils.file_utils import get_default_config_files
from utils.yaml_syntax_highlighter import YAMLHighlighter  # Import syntax highlighter
import yaml

import re
import sasmodels.core  # Make sure sasmodels is installed

logger = logging.getLogger("McSAS3")

class RunSettingsTab(QWidget):
    exclude_patterns = [r'up_.*', r'.*_M0', r'.*_mtheta', r'.*_mphi']

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Dropdown for default configuration files from the "run_configurations" directory
        self.config_dropdown = QComboBox()
        default_configs = get_default_config_files(directory="run_configurations")
        logger.debug(f"Found default run configuration files: {default_configs}")
        self.config_dropdown.addItems(default_configs)
        self.config_dropdown.currentTextChanged.connect(self.load_selected_default_config)
        layout.addWidget(QLabel("Select Default Run Configuration:"))
        layout.addWidget(self.config_dropdown)

        # YAML Editor with Syntax Highlighting
        self.yaml_editor = QTextEdit()
        self.yaml_editor.setAcceptDrops(False)  # Disable drag-and-drop in the editor
        self.yaml_highlighter = YAMLHighlighter(self.yaml_editor.document())
        self.yaml_editor.textChanged.connect(self.validate_yaml_syntax)
        self.yaml_editor.textChanged.connect(self.on_yaml_editor_change)
        layout.addWidget(QLabel("Run Configuration (YAML):"))
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

        # Info Text Field
        self.info_field = QTextEdit()
        self.info_field.setReadOnly(True)
        layout.addWidget(QLabel("Model Parameters Info:"))
        layout.addWidget(self.info_field)

        self.setLayout(layout)
        logger.debug("RunSettingsTab initialized with configuration options and info field.")

        # Auto-load the first configuration, if available
        if default_configs:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def load_selected_default_config(self):
        """Load YAML content of the selected run configuration file into the editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file:
            logger.debug(f"Loading selected run configuration file: {selected_file}")
            yaml_content = load_yaml_file(f"run_configurations/{selected_file}")
            
            # Convert dictionary to a more readable YAML string
            yaml_text = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
            
            self.yaml_editor.setPlainText(yaml_text)
            self.populate_info_field(yaml_content)

    def load_yaml(self):
        """Open a file dialog to load a run configuration file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "run_configurations", "YAML Files (*.yaml)")
        if file_name:
            logger.debug(f"Loading run configuration file: {file_name}")
            yaml_content = load_yaml_file(file_name)
            
            # Convert dictionary to a more readable YAML string
            yaml_text = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
            
            self.yaml_editor.setPlainText(yaml_text)
            self.populate_info_field(yaml_content)

    def save_yaml(self):
        """Save the content of the YAML editor to a file."""
        yaml_content = self.yaml_editor.toPlainText()
        logger.debug("Saving run configuration.")
        save_yaml_file(yaml_content)

    def validate_yaml_syntax(self):
        """Check the syntax of the YAML content in the editor."""
        check_yaml_syntax(self.yaml_editor)

    def on_yaml_editor_change(self):
        """Regenerate the info field whenever the YAML editor content changes."""
        yaml_content = self.yaml_editor.toPlainText()
        self.populate_info_field(yaml_content)

    def populate_info_field(self, yaml_content):
        """Populate the info field with model parameters from the configuration and sasmodels."""
        info_text = "Model Parameters Info:\n"

        try:
            # Parse YAML content if it is in string format
            if isinstance(yaml_content, str):
                yaml_content = yaml.safe_load(yaml_content)

            # Extract modelName and other configuration details
            model_name = yaml_content.get("modelName", "Unknown Model")
            info_text += f"Model Name: {model_name}\n\n"

            if model_name.startswith("mcsas_"):
                # Internal model handling (if necessary)
                info_text += "Using internal McSAS model (no sasmodels parameters available).\n"
            else:
                # Load model parameters from sasmodels
                model_info = sasmodels.core.load_model_info(model_name)
                model_parameters = model_info.parameters.defaults.copy()

                # Filter parameters based on exclude_patterns
                filtered_parameters = {
                    param: default_value
                    for param, default_value in model_parameters.items()
                    if not any(re.match(pattern, param) for pattern in self.exclude_patterns)
                }

                # Display parameters
                info_text += "Available Model Parameters:\n"
                for param, default_value in filtered_parameters.items():
                    info_text += f"  - {param}: {default_value}\n"

                # Optional configuration values
                info_text += "\nConfigure parameter limits:\n"
                info_text += "Add each parameter to 'fitParameterLimits' or 'staticParameters' in the YAML editor.\n"
                info_text += "For 'fitParameterLimits', specify lower and upper limits as a list.\n"

            # Additional fields in YAML (e.g., maxIter, convCrit, nCores)
            max_iter = yaml_content.get("maxIter", "Not specified")
            conv_crit = yaml_content.get("convCrit", "Not specified")
            n_cores = yaml_content.get("nCores", "Not specified")
            info_text += f"\nMax Iterations: {max_iter}\nConvergence Criterion: {conv_crit}\nCores: {n_cores}\n"

            self.info_field.setPlainText(info_text)
            logger.debug("Info field populated with model parameters.")
        except yaml.YAMLError as e:
            error_message = "Error parsing YAML content. Please correct the syntax."
            logger.error(f"{error_message}: {e}")
            self.info_field.setPlainText(error_message)
        except Exception as e:
            logger.error(f"Failed to populate info field: {e}")
            self.info_field.setPlainText("Error loading model parameters.")
