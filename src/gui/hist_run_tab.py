import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar, QHBoxLayout, QFileDialog
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from .file_selection_widget import FileSelectionWidget

logger = logging.getLogger("McSAS3")

class HistRunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # File Selection
        self.file_selector = FileSelectionWidget("YAML Files (*.yaml)")
        layout.addWidget(QLabel("Select Files for Histogramming:"))
        layout.addWidget(self.file_selector)

        # Configuration Selector
        self.config_selector = QLineEdit()
        self.config_selector.setPlaceholderText("Select Histogramming Configuration")
        config_button = QPushButton("Browse")
        config_button.clicked.connect(self.select_configuration)
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_selector)
        config_layout.addWidget(config_button)
        layout.addLayout(config_layout)

        # Run Button
        self.run_button = QPushButton("Run Histogramming")
        self.run_button.clicked.connect(self.run_histogramming)
        layout.addWidget(self.run_button)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def select_configuration(self):
        config_file, _ = QFileDialog.getOpenFileName(self, "Select Histogramming Configuration", "", "YAML Files (*.yaml)")
        if config_file:
            self.config_selector.setText(config_file)

    def run_histogramming(self):
        # Run histogramming logic, update progress bar
        pass
