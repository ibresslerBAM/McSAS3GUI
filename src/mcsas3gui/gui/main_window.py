# main_window.py

# import inspect
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from .getting_started_tab import GettingStartedTab
from .data_loading_tab import DataLoadingTab
from .run_settings_tab import RunSettingsTab  # Import the new RunSettingsTab
from .optimization_tab import OptimizationRunTab
from .hist_settings_tab import HistogramSettingsTab
from .hist_run_tab import HistRunTab

class McSAS3MainWindow(QMainWindow):
    """Main window for the McSAS3 GUI application, containing all tabs."""
    # use inspect to find main path for this package

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
        ORTab = OptimizationRunTab(self, DLTab, RSTab)
        self.tabs.addTab(ORTab, "McSAS3 Optimization ...")
        HSTab = HistogramSettingsTab(self)
        self.tabs.addTab(HSTab, "Histogram Settings")
        HRTab = HistRunTab(self, HSTab)
        self.tabs.addTab(HRTab, "(Re-)Histogramming ...")
        # make some signal connections we can't seem to do anywhere else: 
        # when a histogram file is saved in the hist settings tab, set this to the current file in the hist run tab
        HSTab.yaml_editor_widget.fileSaved.connect(HRTab.histogram_config_selector.set_file_path)  
        # when a data load settigns file is saved in the data settings tab, set this to the current file in the optimization run tab
        DLTab.yaml_editor_widget.fileSaved.connect(ORTab.data_config_selector.set_file_path)  # Handle file save
        RSTab.yaml_editor_widget.fileSaved.connect(ORTab.run_config_selector.set_file_path)  # Handle file save
