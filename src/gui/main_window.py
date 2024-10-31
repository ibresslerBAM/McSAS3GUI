from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .data_loading_tab import DataLoadingTab
from .model_setup_tab import ModelSetupTab
from .optimization_tab import OptimizationTab
from .histogramming_tab import HistogrammingTab
from .output_tab import OutputTab

class McSAS3MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("McSAS3 GUI Interface")
        self.setGeometry(100, 100, 800, 600)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Initialize tabs
        self.setup_tabs()

    def setup_tabs(self):
        self.tabs.addTab(DataLoadingTab(self), "Data Loading")
        self.tabs.addTab(ModelSetupTab(self), "Model Setup")
        self.tabs.addTab(OptimizationTab(self), "Optimization Settings")
        self.tabs.addTab(HistogrammingTab(self), "Histogramming")
        self.tabs.addTab(OutputTab(self), "Output")
