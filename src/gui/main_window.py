# main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .data_loading_tab import DataLoadingTab
from .run_settings_tab import RunSettingsTab  # Import the new RunSettingsTab
from .optimization_tab import OptimizationRunTab
from .histogramming_tab import HistogrammingTab
from .output_tab import OutputTab

class McSAS3MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("McSAS3 Configuration Interface")
        self.setGeometry(100, 100, 800, 600)
        
        # Main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize and add tabs
        self.setup_tabs()

    def setup_tabs(self):
        DLTab = DataLoadingTab(self)
        self.tabs.addTab(DLTab, "Data Loading")
        RSTab = RunSettingsTab(self)
        self.tabs.addTab(RSTab, "Run Settings")  # Add renamed Run Settings tab
        self.tabs.addTab(OptimizationRunTab(self, DLTab, RSTab), "McSAS3 Optimization ...")
        self.tabs.addTab(HistogrammingTab(self), "Histogramming")
        self.tabs.addTab(OutputTab(self), "Output")
