# main.py

import logging
import sys

from PyQt6.QtWidgets import QApplication

from mcsas3gui.gui.main_window import McSAS3MainWindow  # Main window with all tabs
from mcsas3gui.utils.logging_config import setup_logging  # Import the logging configuration


def main():
    # Initialize logging
    logger = setup_logging(
        log_level=logging.INFO, log_to_file=True
    )  # Enables file logging if needed
    logger.info("Starting McSAS3 GUI application...")
    # Start the PyQt application
    app = QApplication(sys.argv)

    main_window = McSAS3MainWindow()
    main_window.show()

    logger.debug("McSAS3 GUI is now visible.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
