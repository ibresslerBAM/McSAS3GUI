from pathlib import Path

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QThread, pyqtSignal


class ParallelWorker(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(int, str)
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    command_signal = pyqtSignal(str)

    def __init__(self, files, command_template, extra_keywords=None, max_workers=1):
        super().__init__()
        self.files = files
        self.command_template = command_template
        self.extra_keywords = extra_keywords or {}
        self.max_workers = max_workers
        self.abort_requested = False
        self.processes = []  # To keep track of active processes

    def run(self):
        total_files = len(self.files)
        progress = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for i, file_path in enumerate(self.files):
                result_file = str(Path(file_path).with_suffix("").parent / (Path(file_path).stem + "_mcsas3.hdf5"))
                keywords = {
                    "input_file": file_path,
                    "result_file": result_file,
                    **self.extra_keywords,
                }
                command = self.command_template.format(**keywords)
                self.command_signal.emit(command)
                
                futures.append(
                    executor.submit(self.execute_command, command, i)
                )

            for future in as_completed(futures):
                if self.abort_requested:
                    break
                progress += 1
                self.progress_signal.emit(int(progress / total_files * 100))

        if self.abort_requested:
            for process in self.processes:
                process.terminate()  # Terminate any running processes
                self.output_signal.emit("Process terminated.")

        self.finished_signal.emit()

    def execute_command(self, command, row):
        try:
            self.status_signal.emit(row, "Running")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.processes.append(process)
            stdout, stderr = process.communicate()
            self.processes.remove(process)

            if process.returncode == 0:
                self.status_signal.emit(row, "Complete")
                self.output_signal.emit(stdout)
            else:
                self.status_signal.emit(row, "Failed")
                self.output_signal.emit(stderr)
        except Exception as e:
            self.status_signal.emit(row, "Failed")
            self.output_signal.emit(f"Error: {e}")

    def abort(self):
        """Request the thread to terminate all running processes."""
        self.abort_requested = True
        for process in self.processes:
            process.terminate()
