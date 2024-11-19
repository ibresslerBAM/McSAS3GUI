import logging
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLineEdit, QPushButton, QProgressBar, QHBoxLayout, QFileDialog
from .file_selection_widget import FileSelectionWidget
from .task_runner_mixin import TaskRunnerMixin


logger = logging.getLogger("McSAS3")


class HistRunTab(QWidget, TaskRunnerMixin):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_selection_widget = FileSelectionWidget(
            title="Select Files for Histogramming:",
            acceptable_file_types="*.nxs *.h5 *.hdf5",
            last_used_directory=Path("~").expanduser()
        )

        layout = QVBoxLayout()
        layout.addWidget(self.file_selection_widget)

        # Configuration Selector
        self.hist_config_selector = QLineEdit()
        self.hist_config_selector.setPlaceholderText("Select Histogramming Configuration")
        select_config_button = QPushButton("Browse")
        select_config_button.clicked.connect(self.select_histogram_config)

        config_layout = QHBoxLayout()
        config_layout.addWidget(self.hist_config_selector)
        config_layout.addWidget(select_config_button)
        layout.addLayout(config_layout)

        # Progress Bar and Run Button
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.run_button = QPushButton("Run Histogramming")
        self.run_button.clicked.connect(self.start_histogramming)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

    def start_histogramming(self):
        files = self.file_selection_widget.get_selected_files()
        hist_config = self.hist_config_selector.text() or "histogram_config.yaml"

        command_template = (
            "python histogram_cli_runner.py --config {config_file} "
            "--datafile {input_file}"
        )

        extra_keywords = {"config_file": hist_config}
        self.run_tasks(files, command_template, extra_keywords)

class HistRunTab(QWidget):
    last_used_directory = Path("~").expanduser()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_selection_widget = FileSelectionWidget(
            title="Select McSAS3-optimized Files for Histogramming:",
            acceptable_file_types="*.nxs *.h5 *.hdf5",
            last_used_directory=self.last_used_directory
        )

        layout = QVBoxLayout()
        layout.addWidget(self.file_selection_widget)

        # Histogramming configuration section
        self.histogram_config_selector = QLineEdit()
        self.histogram_config_selector.setPlaceholderText("Select Histogramming Configuration")
        select_config_button = QPushButton("Browse...")
        select_config_button.clicked.connect(self.select_histogram_config)
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.histogram_config_selector)
        config_layout.addWidget(select_config_button)
        layout.addLayout(config_layout)

        # Run button
        self.run_button = QPushButton("Run Histogramming")
        self.run_button.clicked.connect(self.run_histogramming)
        layout.addWidget(self.run_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def select_histogram_config(self):
        """Select a histogramming configuration YAML file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Histogramming Configuration",
            str(self.file_selection_widget.last_used_directory),
            "YAML Files (*.yaml)"
        )
        if file_name:
            self.histogram_config_selector.setText(file_name)

    def run_histogramming(self):
        """Run histogramming on the selected files."""
        selected_files = self.file_selection_widget.get_selected_files()
        if not selected_files:
            QMessageBox.warning(self, "Run Histogramming", "No files selected.")
            return

        for idx, file in enumerate(selected_files):
            # Placeholder: Update status dynamically and handle subprocess calls
            self.file_selection_widget.set_status_by_file_name(file, "Processing")
            self.progress_bar.setValue(int((idx + 1) / len(selected_files) * 100))
            self.file_selection_widget.set_status_by_file_name(file, "Complete")
