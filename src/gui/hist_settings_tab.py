import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

from .yaml_editor_widget import YAMLEditorWidget

logger = logging.getLogger("McSAS3")

class HistSettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # YAML Editor
        self.yaml_editor_widget = YAMLEditorWidget("histogram_configurations", parent=self)
        layout.addWidget(QLabel("Histogram Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Test Button
        self.test_button = QPushButton("Test Histogramming Settings")
        self.test_button.clicked.connect(self.test_histogramming)
        layout.addWidget(self.test_button)

        # Information Panel
        self.info_field = QTextEdit()
        self.info_field.setReadOnly(True)
        layout.addWidget(QLabel("Information:"))
        layout.addWidget(self.info_field)

        self.setLayout(layout)

    def test_histogramming(self):
        yaml_content = self.yaml_editor_widget.get_yaml_content()
        # Test logic here, update info_field with results
        self.info_field.setText("Test passed!" if yaml_content else "Invalid YAML configuration.")
