import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox

logger = logging.getLogger("McSAS3")

class ModelSetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Model Selection Dropdown
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["Sphere", "Cylinder", "Ellipsoid"])  # Example models
        layout.addWidget(QLabel("Select Model Type:"))
        layout.addWidget(self.model_dropdown)
        self.model_dropdown.currentTextChanged.connect(self.on_model_selected)

        # Parameters YAML Editor
        self.parameters_editor = QTextEdit()
        layout.addWidget(QLabel("Model Parameters (YAML):"))
        layout.addWidget(self.parameters_editor)

        self.setLayout(layout)
        logger.debug("ModelSetupTab initialized.")

    def on_model_selected(self, model):
        logger.debug(f"Model selected: {model}")
        # Placeholder: Load model-specific parameter template in YAML format
        self.parameters_editor.setPlainText(f"# Parameters for {model} model\n")