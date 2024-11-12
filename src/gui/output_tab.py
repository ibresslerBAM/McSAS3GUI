import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

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



class OutputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Placeholder for graphs
        self.layout.addWidget(QLabel("Output Graphs"))

        # Set up Matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        logger.debug("OutputTab initialized.")

    def plot_data(self, mds):
        """Plot data on a log-log scale in the output panel."""
        # Clear the plot to avoid overlaying multiple datasets
        self.ax.clear()

        # Plot data assuming mds provides Q and I arrays
        self.ax.loglog(mds.Q, mds.I, label="Loaded Data")
        self.ax.set_xlabel("Q")
        self.ax.set_ylabel("Intensity")
        self.ax.legend()

        # Refresh the canvas
        self.canvas.draw()
        logger.debug("Data plotted in OutputTab.")

