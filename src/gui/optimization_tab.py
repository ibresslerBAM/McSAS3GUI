from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
from pathlib import Path
import logging

from .file_selection_widget import FileSelectionWidget
from .task_runner_mixin import TaskRunnerMixin

logger = logging.getLogger("McSAS3")

class OptimizationRunTab(QWidget, TaskRunnerMixin):
    last_used_directory = Path("~").expanduser()
    def __init__(self, data_loading_tab, run_settings_tab, parent=None):
        super().__init__(parent)
        self.data_loading_tab = data_loading_tab
        self.run_settings_tab = run_settings_tab

        self.file_selection_widget = FileSelectionWidget(
            title="Loaded Files:",
            acceptable_file_types="*",
            last_used_directory = self.last_used_directory
        )

        layout = QVBoxLayout()
        layout.addWidget(self.file_selection_widget)

        # Data Configuration Section
        self.data_config_selector = QLineEdit()
        self.data_config_selector.setPlaceholderText("Select Data Configuration")
        select_data_config_button = QPushButton("Browse")
        select_data_config_button.clicked.connect(self.select_data_configuration)
        data_config_layout = QHBoxLayout()
        data_config_layout.addWidget(self.data_config_selector)
        data_config_layout.addWidget(select_data_config_button)
        layout.addWidget(QLabel("Data Configuration:"))
        layout.addLayout(data_config_layout)

        # Run Configuration Section
        self.run_config_selector = QLineEdit()
        self.run_config_selector.setPlaceholderText("Select Run Settings")
        select_run_config_button = QPushButton("Browse")
        select_run_config_button.clicked.connect(self.select_run_configuration)
        run_config_layout = QHBoxLayout()
        run_config_layout.addWidget(self.run_config_selector)
        run_config_layout.addWidget(select_run_config_button)
        layout.addWidget(QLabel("Run Configuration:"))
        layout.addLayout(run_config_layout)

        # Progress and Run Controls
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.run_button = QPushButton("Run McSAS3 Optimization ...")
        self.run_button.clicked.connect(self.start_optimizations)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def select_data_configuration(self):
        """Select a data configuration YAML file."""
        # Set the initial directory to 'read_configurations'
        initial_dir = str(Path('read_configurations').resolve())
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Data Configuration File", initial_dir, "YAML Files (*.yaml)")
        if file_name:
            self.data_config_selector.setText(file_name)

    def select_run_configuration(self):
        """Select a run configuration YAML file."""
        # Set the initial directory to 'run_configurations'
        initial_dir = str(Path('run_configurations').resolve())
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Run Settings File", initial_dir, "YAML Files (*.yaml)")
        if file_name:
            self.run_config_selector.setText(file_name)

    def start_optimizations(self):
        files = self.file_selection_widget.get_selected_files()
        data_config = self.data_config_selector.text() or "data_config.yaml"
        run_config = self.run_config_selector.text() or "run_config.yaml"

        command_template = (
            "python mcsas3_cli_runner.py -f {input_file} -F {data_config} "
            "-r {result_file} -R {run_config} -i 1 -d"
        )

        extra_keywords = {"data_config": data_config, "run_config": run_config}
        self.run_tasks(files, command_template, extra_keywords)

    # def run_optimizations(self):
    #     """Run optimizations sequentially on the selected files."""
        
        # selected_files = self.file_selection_widget.get_selected_files()
        # if not selected_files:
        #     QMessageBox.warning(self, "Run Optimization", "No files selected.")
        #     return

        # # Prepare configurations
        # data_config = self.data_config_selector.text() or "data_config.yaml"
        # run_config = self.run_config_selector.text() or "run_config.yaml"

        # # Launch the worker thread for running optimizations
        # self.worker = OptimizationWorker(selected_files, data_config, run_config)
        # self.worker.progress_signal.connect(self.update_progress)
        # self.worker.status_signal.connect(self.update_file_status)
        # self.worker.finished_signal.connect(self.tasks_finished)

        # self.run_button.setEnabled(False)
        # self.progress_bar.setValue(0)
        # self.worker.start()

    # def update_progress(self, progress):
    #     """Update the progress bar."""
    #     self.progress_bar.setValue(progress)

    # def update_file_status(self, row, status):
    #     """Update the status of a file in the table."""
    #     self.file_selection_widget.set_status_by_row(row, status)
    #     # self.file_table.item(row, 1).setText(status)

    # def optimizations_finished(self):
    #     """Enable the run button after optimizations are complete."""
    #     self.run_button.setEnabled(True)
    #     QMessageBox.information(self, "Run Optimization", "All optimizations are complete.")

# class OptimizationWorker(QThread):
#     progress_signal = pyqtSignal(int)
#     status_signal = pyqtSignal(int, str)
#     finished_signal = pyqtSignal()

#     def __init__(self, selected_files, data_config, run_config):
#         super().__init__()
#         self.selected_files = selected_files
#         self.data_config = data_config
#         self.run_config = run_config

#     def run(self):
#         """Run optimizations sequentially."""
#         total_files = len(self.selected_files)
#         for row in range(total_files):
#             file_name = self.selected_files[row]
#             # make sure it lands in the original place. 
#             result_file = Path(file_name).parent / (Path(file_name).stem + "_mcsas3.nxs")
#             if result_file.is_file(): # not sure we can handle updates yet. 
#                 result_file.unlink()
#             command = [
#                 "python", "mcsas3_cli_runner.py",
#                 "-f", file_name,
#                 "-F", self.data_config,
#                 "-r", str(result_file),
#                 "-R", self.run_config,
#                 "-i", "1", "-d"
#             ]

#             try:
#                 self.status_signal.emit(row, "Running")
#                 subprocess.run(command, check=True)
#                 self.status_signal.emit(row, "Complete")
#             except subprocess.CalledProcessError:
#                 self.status_signal.emit(row, "Failed")

#             # Update progress
#             progress = int((row + 1) / total_files * 100)
#             self.progress_signal.emit(progress)

#         self.finished_signal.emit()
