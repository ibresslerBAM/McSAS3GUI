import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
from pathlib import Path
import logging

from .file_selection_widget import FileSelectionWidget
from .file_line_selection_widget import FileLineSelectionWidget
from ..utils.task_runner_mixin import TaskRunnerMixin
from ..utils.file_utils import get_main_path

logger = logging.getLogger("McSAS3")

class OptimizationRunTab(QWidget, TaskRunnerMixin):
    last_used_directory = Path("~").expanduser()
    def __init__(self, data_loading_tab, run_settings_tab, parent=None):
        super().__init__(parent)
        self.data_loading_tab = data_loading_tab
        self.main_path = get_main_path()  # Get the main path of the application
        self.run_settings_tab = run_settings_tab

        self.file_selection_widget = FileSelectionWidget(
            title="Loaded Files:",
            acceptable_file_types="*",
            last_used_directory = self.last_used_directory
        )

        layout = QVBoxLayout()
        layout.addWidget(self.file_selection_widget)

        # Data Configuration Section
        self.data_config_selector = FileLineSelectionWidget(
            placeholder_text="Select data load configuration file",
            file_types="YAML data config Files (*.yaml)"
        )
        self.data_config_selector.fileSelected.connect(self.load_data_config_file)  # Handle file selection
        # self.data_loading_tab.yaml_editor_widget.yaml_editor.fileSaved.connect(self.data_config_selector.set_file_path)  # Handle file save

        layout.addWidget(self.data_config_selector)

        # Run Configuration Section
        self.run_config_selector = FileLineSelectionWidget(
            placeholder_text="Select run configuration file",
            file_types="YAML run config Files (*.yaml)"
        )
        self.run_config_selector.fileSelected.connect(self.load_run_config_file)  # Handle file selection
        # self.run_settings_tab.yaml_editor_widget.yaml_editor.fileSaved.connect(self.run_config_selector.set_file_path)  # Handle file save

        layout.addWidget(self.run_config_selector)

        # Progress and Run Controls
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.run_button = QPushButton("Run McSAS3 Optimization ...")
        self.run_button.clicked.connect(self.start_optimizations)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def load_data_config_file(self, file_path:str):
        """Process the file after selection or drop."""
        if Path(file_path).exists():
            self.pdi = []   # clear any previous information
            logger.debug(f"File loaded: {file_path}")
            self.selected_file = file_path
            self.data_config_selector.set_file_path(self.selected_file)
        else:
            logger.warning(f"File does not exist: {file_path}")
            QMessageBox.warning(self, "File Error", f"Cannot access file: {file_path}")

    def load_run_config_file(self, file_path:str):
        """Process the file after selection or drop."""
        if Path(file_path).exists():
            self.pdi = []   # clear any previous information
            logger.debug(f"File loaded: {file_path}")
            self.selected_file = file_path
            self.run_config_selector.set_file_path(self.selected_file)
        else:
            logger.warning(f"File does not exist: {file_path}")
            QMessageBox.warning(self, "File Error", f"Cannot access file: {file_path}")

    def start_optimizations(self):
        files = self.file_selection_widget.get_selected_files()
        data_config = self.data_config_selector.get_file_path()
        run_config = self.run_config_selector.get_file_path()

        command_template = (
            str(Path(sys.executable).as_posix()) + " "
            "-m mcsas3.mcsas3_cli_runner -f {input_file} -F {data_config} "
            "-r {result_file} -R {run_config} -i 1 -d"
        )

        extra_keywords = {"data_config": data_config, "run_config": run_config}
        self.run_tasks(files, command_template, extra_keywords)
