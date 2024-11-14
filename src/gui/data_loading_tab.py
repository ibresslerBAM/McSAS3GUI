# src/gui/data_loading_tab.py

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QLineEdit, QHBoxLayout, QMessageBox
)
import numpy as np
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file
from pathlib import Path
import yaml
from mcsas3.McData1D import McData1D

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QDialog


logger = logging.getLogger("McSAS3")

class DataLoadingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Dropdown for default configuration files from "read_configurations" directory
        self.config_dropdown = QComboBox()
        default_configs = get_default_config_files(directory="read_configurations")
        self.config_dropdown.addItems(default_configs)
        layout.addWidget(QLabel("Select Default Configuration:"))
        layout.addWidget(self.config_dropdown)

        # YAML Editor for data loading configuration
        self.yaml_editor_widget = YAMLEditorWidget("read_configurations", parent=self)
        layout.addWidget(QLabel("Data Loading Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Connect dropdown to load selected configuration in YAML editor
        self.config_dropdown.currentTextChanged.connect(self.load_selected_default_config)

        # File Selection Line and Button in a Horizontal Layout
        file_selection_layout = QHBoxLayout()
        self.file_path_line = QLineEdit()
        self.file_path_line.setPlaceholderText("Selected test data file")
        file_selection_layout.addWidget(self.file_path_line)

        select_file_button = QPushButton("Select Test Datafile")
        select_file_button.clicked.connect(self.select_datafile)
        file_selection_layout.addWidget(select_file_button)

        layout.addLayout(file_selection_layout)

        # Load and Plot Datafile Button
        plot_file_button = QPushButton("Load and Plot Datafile")
        plot_file_button.clicked.connect(self.load_and_plot_datafile)
        layout.addWidget(plot_file_button)

        self.setLayout(layout)
        logger.debug("DataLoadingTab initialized with single file selection and plotting functionality.")

        # Auto-load the first configuration if available
        if default_configs:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def load_selected_default_config(self):
        """Load the selected YAML configuration file into the YAML editor."""
        selected_file = self.config_dropdown.currentText()
        if selected_file:
            yaml_content = load_yaml_file(f"read_configurations/{selected_file}")
            self.yaml_editor_widget.set_yaml_content(yaml_content)

    def select_datafile(self):
        """Open a file dialog to select a data file and display its path in the file path line."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Test Data File", "", "All Files (*.*)")
        if file_name:
            self.file_path_line.setText(file_name)
            logger.debug(f"Selected data file: {file_name}")

    def load_and_plot_datafile(self):
        """Load and plot the data file specified in the file path line."""
        file_path = self.file_path_line.text()
        if not file_path:
            QMessageBox.warning(self, "Load Datafile", "No data file selected.")
            return

        # Parse the YAML configuration from the editor
        try:
            yaml_content = self.yaml_editor_widget.yaml_editor.toPlainText()
            yaml_config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            QMessageBox.critical(self, "YAML Error", f"Error parsing YAML configuration:\n{e}")
            return

        # Load data using McData1D and plot in a popup window
        try:
            mds = McData1D(
                filename=Path(file_path),
                nbins=yaml_config.get("nbins", 100),
                dataRange=yaml_config.get("dataRange", [-np.inf, np.inf]),
                csvargs=yaml_config.get("csvargs", {}),
                resultIndex=yaml_config.get("resultIndex", 1)
            )
            logger.debug(f"Loaded data file: {file_path}")

            # Display the plot in a popup window
            self.show_plot_popup(mds)

        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            QMessageBox.critical(self, "Loading Error", f"Failed to load file {file_path}:\n{e}")

    def show_plot_popup(self, mds):
        """Display a popup window with the loaded data plot."""
        # Create a dialog window for the plot
        plot_dialog = QDialog(self)
        plot_dialog.setWindowTitle("Data Plot")
        plot_dialog.setMinimumSize(700, 500)
        layout = QVBoxLayout(plot_dialog)

        # Create the matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        
        # Plot the different datasets with error bars
        mds.rawData.plot('Q', 'I', yerr='ISigma', ax=ax, label='As provided data')
        mds.clippedData.plot('Q', 'I', yerr='ISigma', ax=ax, label='Clipped data')
        mds.binnedData.plot('Q', 'I', yerr='ISigma', ax=ax, label='Binned data')

        # Set log scales and labels
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlabel('Q (1/nm)')
        ax.set_ylabel('I (1/(m sr))')

        # Add vertical dashed lines for the clipped data boundaries
        if not mds.clippedData.empty:
            xmin = mds.clippedData['Q'].min()
            xmax = mds.clippedData['Q'].max()
            ax.axvline(x=xmin, color='red', linestyle='--', label='Clipped boundary min')
            ax.axvline(x=xmax, color='red', linestyle='--', label='Clipped boundary max')

        ax.legend()

        # Embed the matplotlib canvas into the dialog
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        # Display the dialog window
        plot_dialog.exec()
    # def load_and_plot_datafile(self):
    #     """Load and plot the data file specified in the file path line."""
    #     file_path = self.file_path_line.text()
    #     if not file_path:
    #         QMessageBox.warning(self, "Load Datafile", "No data file selected.")
    #         return

    #     # Parse the YAML configuration from the editor
    #     try:
    #         yaml_content = self.yaml_editor_widget.yaml_editor.toPlainText()
    #         yaml_config = yaml.safe_load(yaml_content)
    #     except yaml.YAMLError as e:
    #         QMessageBox.critical(self, "YAML Error", f"Error parsing YAML configuration:\n{e}")
    #         return

    #     # Load data using McData1D and plot
    #     try:
    #         mds = McData1D(
    #             filename=Path(file_path),
    #             nbins=yaml_config.get("nbins", 100),
    #             csvargs=yaml_config.get("csvargs", {}),
    #             resultIndex=yaml_config.get("resultIndex", 1)
    #         )
    #         logger.debug(f"Loaded data file: {file_path}")

    #         # Plot data in the output panel
    #         self.parent().output_tab.plot_data(mds)

    #     except Exception as e:
    #         logger.error(f"Error loading file {file_path}: {e}")
    #         QMessageBox.critical(self, "Loading Error", f"Failed to load file {file_path}:\n{e}")
