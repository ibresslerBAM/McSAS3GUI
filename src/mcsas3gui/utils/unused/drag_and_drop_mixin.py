import logging

# from PyQt6.QtCore import QDragEnterEvent, QDropEvent
from pathlib import Path

logger = logging.getLogger("McSAS3")


class DragAndDropMixin:
    def enable_drag_and_drop(self, widget, on_drop_callback):
        """
        Enable drag-and-drop behavior for a given widget.

        Args:
            widget: The widget to enable drag-and-drop for.
            on_drop_callback: A callback function to handle the dropped file paths.
        """
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = lambda event: self.dragEnterEvent(event)
        widget.dropEvent = lambda event: self.dropEvent(event, on_drop_callback)

    def dragEnterEvent(self, event):
        """
        Handle the drag event to check if the dropped item is acceptable.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.debug("Drag enter event accepted.")
        else:
            logger.debug("Drag enter event ignored.")
            event.ignore()

    def dropEvent(self, event, on_drop_callback):
        """
        Handle the drop event to retrieve and process file paths.

        Args:
            event: The drop event.
            on_drop_callback: Callback function to handle the file path.
        """
        urls = event.mimeData().urls()
        logger.debug(f"Drop event received: {urls}")

        for url in urls:
            # Convert URL to a local file path
            file_path = url.toLocalFile()
            logger.debug(f"Parsed file path: {file_path}")

            if file_path and Path(file_path).exists():
                logger.debug(f"Valid file dropped: {file_path}")
                on_drop_callback(file_path)
            else:
                logger.warning(f"Invalid file dropped: {file_path}")
