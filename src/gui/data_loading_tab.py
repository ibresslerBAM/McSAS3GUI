# src/gui/data_loading_tab.py

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QLineEdit, QHBoxLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import QTimer, Qt
import h5py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from gui.yaml_editor_widget import YAMLEditorWidget
from utils.file_utils import get_default_config_files
from utils.yaml_utils import load_yaml_file, save_yaml_file
from pathlib import Path
import yaml
from mcsas3.McData1D import McData1D
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextOption, QTextCursor  # Import QTextOption for word wrapping
 
logger = logging.getLogger("McSAS3")

class DataLoadingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_dialog = None  # Track the plot dialog
        self.update_timer = QTimer(self)  # Timer for debouncing updates
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_and_plot)  # Trigger plot after delay
        self.pdi=[]

        layout = QVBoxLayout()

        # Dropdown for default configuration files
        self.config_dropdown = QComboBox()
        self.refresh_config_dropdown()
        layout.addWidget(QLabel("Select Default Configuration:"))
        layout.addWidget(self.config_dropdown)
        self.config_dropdown.currentTextChanged.connect(self.handle_dropdown_change)

        # YAML Editor for data loading configuration
        self.yaml_editor_widget = YAMLEditorWidget("read_configurations", parent=self)
        layout.addWidget(QLabel("Data Loading Configuration (YAML):"))
        layout.addWidget(self.yaml_editor_widget)

        # Monitor changes in the YAML editor to detect custom changes
        self.yaml_editor_widget.yaml_editor.textChanged.connect(self.on_yaml_editor_change)

        # File Selection Line and Button in a Horizontal Layout
        file_selection_layout = QHBoxLayout()
        self.file_path_line = QLineEdit()
        self.file_path_line.setPlaceholderText("Selected test data file")
        file_selection_layout.addWidget(self.file_path_line)

        select_file_button = QPushButton("Select Test Datafile")
        select_file_button.clicked.connect(self.select_datafile)
        file_selection_layout.addWidget(select_file_button)

        layout.addLayout(file_selection_layout)

        # Error Message Display at the Bottom
        self.error_message_display = QTextEdit()
        self.error_message_display.setReadOnly(True)  # Make the display non-editable
        self.error_message_display.setWordWrapMode(QTextOption.WrapMode.WordWrap)  # Enable word wrap
        self.error_message_display.setPlaceholderText("Messages will be displayed here.")
        self.error_message_display.setStyleSheet("color: darkgreen;")  # Display messages in green
        layout.addWidget(self.error_message_display)

        self.setLayout(layout)
        logger.debug("DataLoadingTab initialized with auto-plotting and configuration management.")

        # Auto-load the first configuration if available
        if self.config_dropdown.count() > 0:
            self.config_dropdown.setCurrentIndex(0)
            self.load_selected_default_config()

    def display_error(self, message):
        """Display the error message in the logger and on the tab."""
        # Optionally truncate the message if needed
        truncated_message = message if len(message) <= 200 else message[:200] + "..."
        self.error_message_display.setText(truncated_message)
        logger.error(message)

    def refresh_config_dropdown(self):
        """Populate or refresh the configuration dropdown list."""
        self.config_dropdown.clear()
        default_configs = get_default_config_files(directory="read_configurations")
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
            yaml_content = load_yaml_file(f"read_configurations/{selected_file}")
            self.yaml_editor_widget.set_yaml_content(yaml_content)

    def on_yaml_editor_change(self):
        """Mark the dropdown as <custom...> if the YAML content is modified and debounce updates."""
        if self.config_dropdown.currentText() != "<custom...>":
            self.config_dropdown.setCurrentText("<custom...>")
        
        # Start/restart the debounce timer to delay plot update
        self.update_timer.start(400)  # Wait 400 ms before updating plot

    def select_datafile(self):
        """Open a file dialog to select a data file and display its path in the file path line."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Test Data File", "", "All Files (*.*)")
        if file_name:
            self.pdi = [] # clear any previous information
            self.file_path_line.setText(file_name)
            logger.debug(f"Selected data file: {file_name}")
            # Check for specific file types and list paths if applicable
            if file_name.lower().endswith(('.hdf5', '.h5', '.nxs')):
                self.list_hdf5_paths_and_dimensions(file_name)
            self.update_and_plot()

    def list_hdf5_paths_and_dimensions(self, file_name: str) -> None:
        """List paths and dimensions of datasets in an HDF5/Nexus file."""
        self.error_message_display.clear()
        try:
            self.pdi = []
            with h5py.File(file_name, 'r') as hdf:
                def _log_and_display_attrs(name: str, obj: h5py.HLObject) -> None:
                    if isinstance(obj, h5py.Dataset):
                        path_dim_info = f"Path: {name}, Shape: {obj.shape}"
                        self.pdi += [path_dim_info]
                        self.error_message_display.append(path_dim_info)
                        logger.debug(path_dim_info)
                hdf.visititems(_log_and_display_attrs)
            # self.error_message_display.setText(f"Available datasets in file: \n {self.pdi}")
            logger.debug(f"{self.pdi=}")
        except Exception as e:
            error_message = f"Error reading HDF5 file: {e}. Verify the file structure."
            logger.error(error_message)
            self.error_message_display.append(f"Error: {error_message}")


    def save_configuration(self):
        """Save the YAML configuration and refresh the dropdown to include new files."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "read_configurations/", "YAML Files (*.yaml)")
        if file_name:
            if not file_name.endswith(".yaml"):
                file_name += ".yaml"
            yaml_content = self.yaml_editor_widget.get_yaml_content()
            save_yaml_file(file_name, yaml_content)
            logger.debug(f"Configuration saved to {file_name}")
            self.refresh_config_dropdown()

    def update_and_plot(self):
        """Load and plot the data file using the current YAML configuration."""
        # Clear any previous error message
        if len(self.pdi) > 0:
            self.error_message_display.setText(
                f"Available datasets in file ({len(self.pdi)} found):\n" + "\n".join(self.pdi)
            )
        else:
            self.error_message_display.setText("")

        file_path = self.file_path_line.text()
        if not file_path:
            self.clear_plot()
            return

        # Parse the YAML configuration from the editor
        try:
            yaml_content = self.yaml_editor_widget.yaml_editor.toPlainText()
            yaml_config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            self.display_error(f"YAML Error: {e}")
            self.clear_plot()
            return

        # Load data and update the plot
        try:
            mds = McData1D(
                filename=Path(file_path),
                nbins=yaml_config.get("nbins", 100),
                csvargs=yaml_config.get("csvargs", None),
                pathDict=yaml_config.get("pathDict", None),
                dataRange=yaml_config.get("dataRange", [-np.inf, np.inf]),
                omitQRanges=yaml_config.get("omitQRanges", []),
                resultIndex=yaml_config.get("resultIndex", 1)
            )
            logger.debug(f"Loaded data file: {file_path}")
            self.show_plot_popup(mds)  # Display the plot in a popup window
        except Exception as e:
            self.display_error(f"Error loading file {file_path}: {e}")
            self.clear_plot()

    def clear_plot(self):
        """Clear the plot when no valid data is available."""
        if self.plot_dialog and self.plot_dialog.isVisible():
            self.ax.clear()
            self.ax.figure.canvas.draw()

    def display_error(self, message):
        """Display the error message in the logger and on the tab."""
        self.error_message_display.setText(message)
        if len(self.pdi)>0:
            self.error_message_display.append(
                f"Available datasets in file ({len(self.pdi)} found):\n" + "\n".join(self.pdi)
            )
        self.error_message_display.moveCursor(QTextCursor.MoveOperation.Start)
        logger.error(message)

    def show_plot_popup(self, mds):
        """Display a popup window with the loaded data plot."""
        # If a plot window is already open, update it
        if self.plot_dialog is None or not self.plot_dialog.isVisible():
            self.plot_dialog = QDialog(self)
            self.plot_dialog.setWindowTitle("Data Plot")
            self.plot_dialog.setMinimumSize(700, 500)
            layout = QVBoxLayout(self.plot_dialog)

            # Create the matplotlib figure and axes
            self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
            canvas = FigureCanvas(self.fig)
            layout.addWidget(canvas)

            # Embed the canvas in the dialog layout
            self.plot_dialog.setLayout(layout)

        # Clear the previous plot and redraw
        self.ax.clear()
        mds.rawData.plot('Q', 'I', yerr='ISigma', ax=self.ax, label='As provided data')
        mds.clippedData.plot('Q', 'I', yerr='ISigma', ax=self.ax, label='Clipped data')
        mds.binnedData.plot('Q', 'I', yerr='ISigma', ax=self.ax, label='Binned data')
        self.ax.set_yscale('log')
        self.ax.set_xscale('log')
        self.ax.set_xlabel('Q (1/nm)')
        self.ax.set_ylabel('I (1/(m sr))')

        # Add vertical dashed lines for the clipped data boundaries
        if not mds.clippedData.empty:
            xmin = mds.clippedData['Q'].min()
            xmax = mds.clippedData['Q'].max()
            self.ax.axvline(x=xmin, color='red', linestyle='--', label='Clipped boundary min')
            self.ax.axvline(x=xmax, color='red', linestyle='--', label='Clipped boundary max')

        self.ax.legend()
        self.fig.canvas.draw()
        self.plot_dialog.show()
