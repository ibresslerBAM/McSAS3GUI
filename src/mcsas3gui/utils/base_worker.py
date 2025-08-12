import logging
import shlex
import subprocess
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger("McSAS3")


class BaseWorker(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal()

    def __init__(self, selected_files, command_template, extra_keywords=None):
        """
        Args:
            selected_files (list): List of file paths to process.
            command_template (str): Command template with placeholders for replacement.
            extra_keywords (dict): Additional keywords for replacing in the command template.
        """
        super().__init__()
        self.selected_files = selected_files
        self.command_template = command_template
        self.extra_keywords = extra_keywords or {}

    def quote_path(self, path):
        """Ensure the path is properly quoted for safe command-line usage."""
        if isinstance(path, Path):
            path = str(path.as_posix())
        return f'"{path}"' if " " in path else path

    def run(self):
        """Run commands sequentially."""
        total_files = len(self.selected_files)
        for row, file_name in enumerate(self.selected_files):
            result_file = Path(file_name).parent / (Path(file_name).stem + "_output.hdf5")
            if result_file.is_file():
                result_file.unlink()

            # Add file-specific keywords, quoting paths
            keywords = {
                "input_file": self.quote_path(Path(file_name)),
                "result_file": self.quote_path(Path(result_file)),
                **{key: self.quote_path(value) for key, value in self.extra_keywords.items()},
            }

            # Replace placeholders in the command template
            command = shlex.split(self.command_template.format(**keywords))

            logger.info(f"Running command: {command}")

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
