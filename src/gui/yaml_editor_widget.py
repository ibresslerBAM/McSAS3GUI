# src/gui/yaml_editor_widget.py

import logging
import yaml
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QHBoxLayout
from utils.yaml_syntax_highlighter import YAMLHighlighter

logger = logging.getLogger("McSAS3")

class YAMLEditorWidget(QWidget):
    def __init__(self, directory, parent=None):
        super().__init__(parent)
        self.directory = directory
        layout = QVBoxLayout()

        # YAML Editor with Syntax Highlighting
        self.yaml_editor = QTextEdit()
        self.yaml_editor.setAcceptDrops(False)  # Disable drag-and-drop
        self.yaml_highlighter = YAMLHighlighter(self.yaml_editor.document())
        layout.addWidget(self.yaml_editor)

        # Load and Save Buttons
        button_layout = QHBoxLayout()
        load_button = QPushButton("Load Configuration")
        load_button.clicked.connect(self.load_yaml)
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_yaml)
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_yaml(self):
        """Open a file dialog to load a YAML file and display it in the editor."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", self.directory, "YAML Files (*.yaml)")
        if file_name:
            logger.debug(f"Loading YAML configuration from file: {file_name}")
            with open(file_name, 'r') as file:
                try:
                    yaml_content = yaml.safe_load(file)
                    yaml_text = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
                    self.yaml_editor.setPlainText(yaml_text)
                except yaml.YAMLError as e:
                    logger.error(f"Error loading YAML file {file_name}: {e}")
                    self.yaml_editor.setPlainText("Error loading YAML file.")

    def save_yaml(self):
        """Save the content of the YAML editor to a file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", self.directory, "YAML Files (*.yaml)")
        if file_name:
            yaml_content = self.yaml_editor.toPlainText()
            try:
                parsed_content = yaml.safe_load(yaml_content)
                with open(file_name, 'w') as file:
                    yaml.dump(parsed_content, file, default_flow_style=False, sort_keys=False)
                    logger.debug(f"Saved YAML configuration to file: {file_name}")
            except yaml.YAMLError as e:
                logger.error(f"Error saving YAML to file {file_name}: {e}")

    def get_yaml_content(self):
        """Parse and return the YAML content from the editor as a dictionary."""
        try:
            return yaml.safe_load(self.yaml_editor.toPlainText())
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return {}

    def set_yaml_content(self, yaml_content):
        """Set YAML content in the editor, formatted as a string."""
        yaml_text = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)
        self.yaml_editor.setPlainText(yaml_text)
