import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

logger = logging.getLogger("McSAS3")

class OptimizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Optimization Parameters YAML Editor
        self.optimization_editor = QTextEdit()
        layout.addWidget(QLabel("Monte Carlo Optimization Parameters (YAML):"))
        layout.addWidget(self.optimization_editor)

        self.setLayout(layout)
        logger.debug("OptimizationTab initialized.")
