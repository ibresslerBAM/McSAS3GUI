from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThreadPool

from utils.parallel_worker import ParallelWorker


class TaskRunnerMixin:
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.running_tasks = []  # Track running tasks for potential abortion

    def run_tasks(self, files, command_template, extra_keywords=None, max_workers=1):
        """
        Run tasks with the provided command template and files.

        Args:
            files (list): List of file paths to process.
            command_template (str): Command template with placeholders for replacement.
            extra_keywords (dict): Additional keywords for replacing in the command template.
            max_workers (int): Number of concurrent workers (1 for sequential execution).
        """
        if not files:
            QMessageBox.warning(self, "Run Tasks", "No files selected.")
            return

        # Always use ParallelWorker, adjust concurrency via max_workers
        worker = ParallelWorker(files, command_template, extra_keywords, max_workers=max_workers)

        worker.progress_signal.connect(self.update_progress)
        worker.status_signal.connect(self.update_file_status)
        worker.finished_signal.connect(self.tasks_finished)
        worker.output_signal.connect(self.append_output)  # Display task output
        worker.command_signal.connect(self.append_command)  # Append command to UI

        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.worker = worker
        self.worker.start()

    def append_command(self, command):
        """Append the resolved command to the output field."""
        if hasattr(self, "output_field"):
            self.output_field.append(f"Command: {command}")
        
    def update_progress(self, progress):
        """Update the progress bar."""
        self.progress_bar.setValue(progress)

    def update_file_status(self, row, status):
        """Update the status of a file in the table."""
        self.file_selection_widget.set_status_by_row(row, status)

    def display_output(self, row, output):
        """Display output from the subprocess."""
        self.info_field.append(f"Output for file {row}:\n{output}")

    def task_finished(self):
        """Check if all tasks are complete."""
        if all(worker.isFinished() for worker in self.running_tasks):
            self.tasks_finished()

    def tasks_finished(self):
        """Re-enable the run button after tasks are complete."""
        self.run_button.setEnabled(True)
        QMessageBox.information(self, "Run Tasks", "All tasks are complete.")

    def abort_running_tasks(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.abort()
        """Abort all running tasks."""
        for worker in self.running_tasks:
            worker.terminate()
        self.running_tasks.clear()
        self.run_button.setEnabled(True)
        QMessageBox.warning(self, "Run Tasks", "Tasks have been aborted.")
