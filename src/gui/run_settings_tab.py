import logging
from pathlib import Path
import re
import h5py
from tempfile import NamedTemporaryFile
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton
from PyQt6.QtCore import QTimer
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file
from sasmodels.core import load_model_info
# from mcsas3.McSASOptimizer import McSASOptimizer
from mcsas3.McData1D import McData1D
from mcsas3.McHat import McHat
import numpy as np

logger = logging.getLogger("McSAS3")

class RunSettingsTab(QWidget):
    def __init__(self, parent=None, data_loading_tab=None):
        super().__init__(parent)
        self.data_loading_tab = data_loading_tab
        self.update_timer = QTimer(self)  # Timer for debouncing updates
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_info_field)

        layout = QVBoxLayout()

        # Dropdown for default run configuration files
        self.config_dropdown = QComboBox()
        self.refresh_config_dropdown()
        layout.addWidget(QLabel("Select Default Run Configuration:"))
        layout.addWidget(self.config_dropdown)
        self.config_dropdown.currentTextChanged.connect(self.handle_dropdown_change)

        # YAML Editor for run settings configuration
        self.yaml_editor_widget = YAMLEditorWidget("run_configurations", parent=self)
        layout.addWidget(QLabel("Run Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Monitor changes in the YAML editor to detect custom changes
        self.yaml_editor_widget.yaml_editor.textChanged.connect(self.on_yaml_editor_change)

        # Test Run Button
        test_run_button = QPushButton("Test single repetition on loaded Test Data")
        test_run_button.clicked.connect(self.run_test_optimization)
        layout.addWidget(test_run_button)

        # Info text field for model parameters
        self.info_field = QTextEdit()
        self.info_field.setReadOnly(True)
        layout.addWidget(QLabel("Model Parameters Info:"))
        layout.addWidget(self.info_field)

        self.setLayout(layout)
        if self.config_dropdown.count() > 0:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def refresh_config_dropdown(self):
        """Populate or refresh the configuration dropdown list."""
        self.config_dropdown.clear()
        default_configs = get_default_config_files(directory="run_configurations")
        self.config_dropdown.addItems(default_configs)
        self.config_dropdown.addItem("<custom...>")

    def handle_dropdown_change(self):
        """Handle dropdown changes and load the selected configuration."""
        selected_text = self.config_dropdown.currentText()
        if selected_text != "<custom...>":
            self.load_selected_default_config()
            self.config_dropdown.blockSignals(True)
            self.config_dropdown.setCurrentText(selected_text)
            self.config_dropdown.blockSignals(False)

    def load_selected_default_config(self):
        """Load the selected YAML configuration file into the YAML editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file and selected_file != "<custom...>":
            yaml_content = load_yaml_file(f"run_configurations/{selected_file}")
            self.yaml_editor_widget.set_yaml_content(yaml_content)
            self.update_info_field()

    def on_yaml_editor_change(self):
        """Mark the dropdown as <custom...> if the YAML content is modified and debounce updates."""
        if self.config_dropdown.currentText() != "<custom...>":
            self.config_dropdown.setCurrentText("<custom...>")
        self.update_timer.start(400)  # Debounce updates with a 400 ms delay

    def update_info_field(self):
        """Update the info field based on the YAML content in the editor."""
        yaml_content = self.yaml_editor_widget.get_yaml_content()
        if not yaml_content:
            self.info_field.setPlainText("Invalid YAML or empty configuration.")
            return

        info_text = "Configuration Details:\n"
        model_name = yaml_content.get("modelName", "Unknown Model")
        info_text += f"Model Name: {model_name}\n"

        max_iter = yaml_content.get("maxIter", "Not specified")
        conv_crit = yaml_content.get("convCrit", "Not specified")
        n_cores = yaml_content.get("nCores", "Not specified")
        info_text += f"Max Iterations: {max_iter}\nConvergence Criterion: {conv_crit}\nCores: {n_cores}\n"

        if model_name.startswith("mcsas_"):
            info_text += "\nUsing internal McSAS model. No additional sasmodels parameters available.\n"
            self.info_field.setPlainText(info_text)
            return

        try:
            model_info = load_model_info(model_name)
            model_parameters = model_info.parameters.defaults.copy()
            exclude_patterns = [r'up_.*', r'.*_M0', r'.*_mtheta', r'.*_mphi']
            filtered_parameters = {
                param: default_value
                for param, default_value in model_parameters.items()
                if not any(re.match(pattern, param) for pattern in exclude_patterns)
            }

            info_text += "\nSasmodels Parameters:\n"
            for param, default_value in filtered_parameters.items():
                info_text += f"  - {param}: {default_value}\n"

            info_text += "\nTo configure parameters, add each to 'fitParameterLimits' or 'staticParameters' in the YAML editor.\n"
            info_text += "For 'fitParameterLimits', specify lower and upper limits as a list."
        except Exception as e:
            info_text += f"\nError loading model parameters from sasmodels: {e}"
            logger.error(f"Error loading model parameters: {e}")

        self.info_field.setPlainText(info_text)

    def run_test_optimization(self):
        """Run a single optimization repetition on the loaded test data."""
        # try:
        # Retrieve data from the DataLoadingTab
        mds = self.data_loading_tab.mds
        if not mds:
            self.info_field.setPlainText("No data loaded in the Data Loading tab.")
            return

        # Parse the YAML configuration for the optimizer
        yaml_content = self.yaml_editor_widget.get_yaml_content()
        if not yaml_content:
            self.info_field.setPlainText("Invalid or missing run configuration.")
            return

        # Create a temporary file to save data for the optimizer
        with NamedTemporaryFile(delete=False, suffix=".hdf5") as temp_file:
            temp_file.close()
            self.tempFileName = Path(temp_file.name)
        
        mds.store(self.tempFileName)
        yaml_content.update({'nRep': 1})
        mh = McHat(
            **(yaml_content)
        )
        mh.run(mds.measData.copy(), self.tempFileName)

        self.info_field.setPlainText("Optimization completed successfully.")
        # TODO: Update the data plot with fit intensity

        # except Exception as e:
        #     logger.error(f"Error during test optimization: {e}")
        #     self.info_field.setPlainText(f"Error during test optimization: {e}")
