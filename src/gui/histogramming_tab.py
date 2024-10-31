import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

logger = logging.getLogger("McSAS3")

class HistogrammingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Histogramming Configuration YAML Editor
        self.histogram_editor = QTextEdit()
        layout.addWidget(QLabel("Histogramming Configuration (YAML):"))
        layout.addWidget(self.histogram_editor)

        self.setLayout(layout)
        logger.debug("HistogrammingTab initialized.")
