# main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from .getting_started_tab import GettingStartedTab
from .data_loading_tab import DataLoadingTab
from .run_settings_tab import RunSettingsTab  # Import the new RunSettingsTab
from .optimization_tab import OptimizationRunTab
from .hist_settings_tab import HistogramSettingsTab
from .hist_run_tab import HistRunTab

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
        self.tabs.addTab(GettingStartedTab(self), "Getting Started")
        DLTab = DataLoadingTab(self)
        self.tabs.addTab(DLTab, "Data Settings")
        RSTab = RunSettingsTab(self, DLTab)
        self.tabs.addTab(RSTab, "Run Settings")
        self.tabs.addTab(OptimizationRunTab(self, DLTab, RSTab), "McSAS3 Optimization ...")
        self.tabs.addTab(HistogramSettingsTab(self), "Histogram Settings")
        self.tabs.addTab(HistRunTab(self), "(Re-)Histogramming ...")