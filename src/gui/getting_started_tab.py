from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser

class GettingStartedTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.info_viewer = QTextBrowser()
        self.info_viewer.setOpenExternalLinks(True)

        # Load HTML content
        html_content = """
        <html>
            <body>
                <h1>Welcome to McSAS3 GUI</h1>
                <p>This interface guides you through setting up and running McSAS3 optimizations and histogramming.</p>
                <h2>Getting Started</h2>
                <p><b>Step 1:</b> Use the "Data Settings" tab to configure and load your data files.</p>
                <p><b>Step 2:</b> Configure your run settings in the "Run Settings" tab.</p>
                <p><b>Step 3:</b> Run McSAS3 optimizations in the "McSAS3 Optimization..." tab.</p>
                <p><b>Step 4:</b> Re-histogram results using the "Histogram Settings" and "(Re-)Histogramming..." tabs.</p>
            </body>
        </html>
        """
        self.info_viewer.setHtml(html_content)

        layout.addWidget(self.info_viewer)
        self.setLayout(layout)
