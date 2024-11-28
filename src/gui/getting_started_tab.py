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
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Don't Panic</title>
                <style>
                    .friendly-text {
                        font-size: 48px;
                        color: #4CAF50; /* A friendly green color */
                        text-align: center;
                        margin-top: 20%;
                        font-family: 'Comic Sans MS', 'Arial', sans-serif; /* A playful font */
                    }
                </style>
            </head>
            <body>
                <div class="friendly-text">Don't Panic</div>

                <h1>Welcome to McSAS3 GUI</h1>
                
                <p>It's been a long time coming, but now it's here: the graphical user interface to help you use McSAS3. </p>

                <h2> McWho? </h2>
                <p> McSAS3 (and its older sibling, McSAS) is a program to analyse small-angle scattering patterns using a Monte Carlo approach. If used right, with the appropriate model, it will fit your data perfectly, that is to say, to within the uncertainty of your datapoints. 
                Underneath, it superimposes a set (300 or so) of identical model instances. 
                The Monte Carlo optimization algorithm then uses an acceptance-rejection method to optimize one parameter on these model instances. In the end, it arrives at a set of parameter values that works best within the constraints given for your data. This can be histogrammed to give parameter distributions. </p>
                <p> Usually, McSAS is used to extract form-free <b><i>size</i></b> distributions and volume fractions assuming, say, spherical scatterers. But it's good that you now understand it's not limited to that. Choose well, and it will make you happy. </p>

                <h2>Getting Started</h2>
                <p>This McSAS3GUI interface guides you through setting up and running McSAS3 optimizations and histogramming. It is not required to run McSAS3, that can run headlessly in any data pipeline. This is just here to help you set that up, or help you deal with fitting small batches</p>
                <h3>Oh my god, it's full of tabs!</h3>
                <p>The UI has a handful of tabs, you nominally run through them from left to right. </p>
                <p>You are now here, in the "Getting Started"-tab.</p>
                <p>The tabs with "Settings" in the titles allow you to interactively configure and test the yaml configurations for data loading, McSAS optimization and (re)histogramming. </p>
                <p>The "McSAS3 Optimization ..." tab let you run full McSAS3 optimizations on (batches of) measurement files. </p>
                <p>Lastly, the "(Re)Histogramming ..." tab lets you (re-)histogram previously optimized results. </p>
                <p>Let's go through these tabs one by one...</p>

                <h3> The "Data Settings"-tab </h3>
                <p>In this tab, you can configure how your data should be read. McSAS3 has a very flexible data ingestor, which can read text-based formats (e.g. csv or pdh), as well as HDF5-based formats (such as NeXus or NXCanSAS) very flexibly. Several templates are available to show how this can be done. You can choose one of these templates from the pulldown menu at the top. This will load the template into the YAML editor widget. The YAML editor widget does syntax highlighting and validation for you, and you can load and save YAML files with the two buttons underneath the YAML editor field. Remember to save the configuration once you have tuned it to your wishes, as you'll need the saved data read configuration file later. </p>
                <p>Before you start editing the YAML, however, I would recommend also loading a test datafile of the type you want to read. This can be done by either dragging and dropping into the text line field below the "Load Configuration" and "Save configuration" buttons. You can also use the "Browse" button to browse to a particular test datafile. </p>
                <p>Now that you have a test file and a YAML, the interface will try to read your file. If it can, it will show (graphically) the resulting raw, clipped and binned data in a separate window. Keep this window open, it'll be useful. </p>
                <p>For NeXus files, you'll need to indicate the paths to Q, I and ISigma, the uncertainty estimate on I (the better this uncertainty estimate, the better it'll work). If the NeXus file cannot be read, the information window at the bottom will show the paths to all the datasets in your test file; hopefully you can find there the data you are looking for. </p>
                <p>For ascii/csv files, you can use the "csvargs" section to specify the keyword-value combinations that pandas.read_csv needs to work. For example, you can tell it how many lines to skip, what the separator is, and so on. </p>
                <p>Data units and unit conversions will be implemented before the v1 release (maybe, if I can free up the time). </p>
                <p>You can change the data limits you want to fit by adjusting the "dataRange" in the YAML, and you can use the "omitRanges" list of ranges to skip over data segments you don't want to fit, such as peaks.</p>
                <p>You can set the minimum possible inter-datapoint uncertainty limit for your data using "IEmin", which is a fraction of the intensity, default set to 1%. nBins sets the number of (log-spaced) bins to rebin your data into. 100 bins per decade or two is usually more than sufficient, and ensures proper speed. </p> 
                
                <h3> The "Run Settings"-tab </h3>

                <h3> The "Optimization..."-tab </h3>

                <h3> The "Hist Settings"-tab </h3>

                <h3> The "(Re-)Histogramming..."-tab </h3>
            </body>
        </html>
        """
        self.info_viewer.setHtml(html_content)

        layout.addWidget(self.info_viewer)
        self.setLayout(layout)
