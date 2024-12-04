# McSAS3GUI

McSAS3GUI is a graphical user interface for the McSAS3 software. This guide will walk you through the steps necessary to clone, set up, and run the McSAS3GUI application.

## Prerequisites

Ensure you have the following software installed on your system:
- [Git](https://git-scm.com/)
- [Python 3.12](https://www.python.org/downloads/)

## Installation and Setup

1. **Clone the Repositories**

   First, clone the repositories for McSAS3GUI and McSAS3:

   ```bash
   git clone https://github.com/toqduj/McSAS3GUI.git
   git clone https://github.com/BAMresearch/McSAS3.git
   ```

2. **Switch to the `refactoring` Branch in McSAS3**

   Change to the McSAS3 directory and switch to the `refactoring` branch:

   ```bash
   cd McSAS3
   git switch refactoring
   ```
   Navigate back to the McSAS3GUI directory:

   ```bash
   cd ../McSAS3GUI
   ```

3. **(Optional) Deactivate Conda Environment**

   If you're using conda, make sure to deactivate any active environment:

   ```bash
   conda deactivate
   ```

4. **Create a Virtual Environment**

   Set up a Python virtual environment:

   ```bash
   python3.12 -m venv .venv
   ```

5. **Activate the Virtual Environment**

   Activate the newly created virtual environment:

   ```bash
   source .venv/bin/activate
   ```

6. **Install Dependencies**

   Upgrade pip and install required McSAS3GUI dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. **Install McSAS3 in Editable Mode**

   Install the McSAS3 package in editable mode:

   ```bash
   pip install -e ../McSAS3/
   ```

## Running the Application

Once all dependencies are installed, you can run the McSAS3GUI application with the following command (from the McSAS3GUI directory):

```bash
python src/main.py
```

## Contributing

We welcome contributions! Please ensure your code follows the project's coding style and includes relevant tests and documentation.

## License

This project is licensed under the MIT license
