# src/gui/hist_run_tab.py

import logging
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLineEdit, QPushButton, QProgressBar, QHBoxLayout, QFileDialog

from .file_line_selection_widget import FileLineSelectionWidget
from .file_selection_widget import FileSelectionWidget
from ..utils.task_runner_mixin import TaskRunnerMixin
from ..utils.file_utils import get_main_path


logger = logging.getLogger("McSAS3")


class HistRunTab(QWidget, TaskRunnerMixin):
    last_used_directory = Path("~").expanduser()
    def __init__(self, hist_settings_tab, parent=None):
        super().__init__(parent)
        self.main_path = get_main_path()
        self.file_selection_widget = FileSelectionWidget(
            title="Select McSAS3-optimized Files for Histogramming:",
            acceptable_file_types="*.nxs *.h5 *.hdf5",
            last_used_directory=self.last_used_directory
        )

        layout = QVBoxLayout()
        layout.addWidget(self.file_selection_widget)

        # Data Configuration Section
        self.histogram_config_selector = FileLineSelectionWidget(
            placeholder_text="Select histogramming configuration file",
            file_types="YAML hist config Files (*.yaml)"
        )
        self.histogram_config_selector.fileSelected.connect(self.load_hist_config_file)  # Handle file selection

        layout.addWidget(self.histogram_config_selector)

        # Run button
        self.run_button = QPushButton("Run Histogramming")
        self.run_button.clicked.connect(self.run_histogramming)
        layout.addWidget(self.run_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def load_hist_config_file(self, file_path:str):
        """Process the file after selection or drop."""
        if Path(file_path).exists():
            self.pdi = []   # clear any previous information
            logger.debug(f"File loaded: {file_path}")
            self.selected_file = file_path
            self.histogram_config_selector.set_file_path(self.selected_file)
        else:
            logger.warning(f"File does not exist: {file_path}")
            QMessageBox.warning(self, "File Error", f"Cannot access file: {file_path}")

    def run_histogramming(self):
        """Run histogramming on the selected files."""

        files = self.file_selection_widget.get_selected_files()
        hist_config = self.histogram_config_selector.get_file_path() or "data_config.yaml"

        command_template = (
            "python -m mcsas3.mcsas3_cli_histogrammer -r {input_file} -H {hist_config} "
            "-i 1"
        )

        extra_keywords = {"hist_config": hist_config}
        self.run_tasks(files, command_template, extra_keywords)

        # selected_files = self.file_selection_widget.get_selected_files()
        # if not selected_files:
        #     QMessageBox.warning(self, "Run Histogramming", "No files selected.")
        #     return

        # for idx, file in enumerate(selected_files):
        #     # Placeholder: Update status dynamically and handle subprocess calls
        #     self.file_selection_widget.set_status_by_file_name(file, "Processing")
        #     self.progress_bar.setValue(int((idx + 1) / len(selected_files) * 100))
        #     self.file_selection_widget.set_status_by_file_name(file, "Complete")
