from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLineEdit, QProgressBar, QMessageBox, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger("McSAS3")

class OptimizationRunTab(QWidget):
    def __init__(self, data_loading_tab, run_settings_tab, parent=None):
        super().__init__(parent)
        self.data_loading_tab = data_loading_tab
        self.run_settings_tab = run_settings_tab

        layout = QVBoxLayout()

        # File Table Widget
        self.file_table = QTableWidget(0, 2)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Status"])

        # Allow the first column to stretch and occupy available space.
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # Set the estimated pixel width for the second column (approx. 12 characters)
        # You might need to adjust 'font_metrics.averageCharWidth()' multiplier
        # depending on the actual font and size used in the application.
        font_metrics = self.file_table.fontMetrics()
        second_column_width = font_metrics.averageCharWidth() * 12
        self.file_table.setColumnWidth(1, second_column_width)

        layout.addWidget(QLabel("Loaded Files:"))
        layout.addWidget(self.file_table)

        # Buttons for managing data files
        file_button_layout = QHBoxLayout()
        load_files_button = QPushButton("Load Datafile(s)")
        load_files_button.clicked.connect(self.load_data_files)
        clear_files_button = QPushButton("Clear Selected File(s)")
        clear_files_button.clicked.connect(self.clear_selected_files)
        file_button_layout.addWidget(load_files_button)
        file_button_layout.addWidget(clear_files_button)
        layout.addLayout(file_button_layout)

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

        self.run_button = QPushButton("Run Optimization")
        self.run_button.clicked.connect(self.run_optimizations)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def load_data_files(self):
        """Open a file dialog to load data files and add them to the table."""
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Data Files", "", "All Files (*.*)")
        for file_name in file_names:
            if not self.is_file_in_table(file_name):
                row_position = self.file_table.rowCount()
                self.file_table.insertRow(row_position)
                self.file_table.setItem(row_position, 0, QTableWidgetItem(file_name))
                status_item = QTableWidgetItem("Pending")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.file_table.setItem(row_position, 1, status_item)
                logger.debug(f"Added file to table: {file_name}")

    def clear_selected_files(self):
        """Remove only the selected rows from the file table."""
        selected_rows = {index.row() for index in self.file_table.selectedIndexes()}
        for row in sorted(selected_rows, reverse=True):
            self.file_table.removeRow(row)

    def is_file_in_table(self, file_path):
        """Check if a file is already in the table to avoid duplicates."""
        for row in range(self.file_table.rowCount()):
            if self.file_table.item(row, 0).text() == file_path:
                return True
        return False

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

    def run_optimizations(self):
        """Run optimizations sequentially on the selected files."""
        if self.file_table.rowCount() == 0:
            QMessageBox.warning(self, "Run Optimization", "No files loaded.")
            return

        # Prepare configurations
        data_config = self.data_config_selector.text() or "data_config.yaml"
        run_config = self.run_config_selector.text() or "run_config.yaml"

        # Launch the worker thread for running optimizations
        self.worker = OptimizationWorker(self.file_table, data_config, run_config)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.status_signal.connect(self.update_file_status)
        self.worker.finished_signal.connect(self.optimizations_finished)

        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.worker.start()

    def update_progress(self, progress):
        """Update the progress bar."""
        self.progress_bar.setValue(progress)

    def update_file_status(self, row, status):
        """Update the status of a file in the table."""
        self.file_table.item(row, 1).setText(status)

    def optimizations_finished(self):
        """Enable the run button after optimizations are complete."""
        self.run_button.setEnabled(True)
        QMessageBox.information(self, "Run Optimization", "All optimizations are complete.")

class OptimizationWorker(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal()

    def __init__(self, file_table, data_config, run_config):
        super().__init__()
        self.file_table = file_table
        self.data_config = data_config
        self.run_config = run_config

    def run(self):
        """Run optimizations sequentially."""
        total_files = self.file_table.rowCount()
        for row in range(total_files):
            file_name = self.file_table.item(row, 0).text()
            # make sure it lands in the original place. 
            result_file = Path(file_name).parent / (Path(file_name).stem + "_mcsas3.nxs")
            if result_file.is_file(): # not sure we can handle updates yet. 
                result_file.unlink()
            command = [
                "python", "mcsas3_cli_runner.py",
                "-f", file_name,
                "-F", self.data_config,
                "-r", str(result_file),
                "-R", self.run_config,
                "-i", "1", "-d"
            ]

            try:
                self.status_signal.emit(row, "Running")
                subprocess.run(command, check=True)
                self.status_signal.emit(row, "Complete")
            except subprocess.CalledProcessError:
                self.status_signal.emit(row, "Failed")

            # Update progress
            progress = int((row + 1) / total_files * 100)
            self.progress_signal.emit(progress)

        self.finished_signal.emit()
