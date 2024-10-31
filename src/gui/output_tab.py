import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger("McSAS3")

class OutputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Placeholder for graphs
        layout.addWidget(QLabel("Output Graphs"))

        # Matplotlib Canvas for Graph Display
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        logger.debug("OutputTab initialized.")

    def plot_data(self, mds):
        # Clear and plot new data
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(mds.Q, mds.I, label="Intensity")
        ax.set_xlabel("Q")
        ax.set_ylabel("I")
        ax.legend()
        self.canvas.draw()
        logger.debug("Data plotted in OutputTab.")
