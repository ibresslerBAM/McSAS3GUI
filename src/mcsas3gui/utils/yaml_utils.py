import yaml
from PyQt6.QtWidgets import QFileDialog


def load_yaml_file(file_path):
    with open(file_path, "r") as file:
        docs = list(yaml.safe_load_all(file))
        return docs if len(docs) > 1 else docs[0]
        # return yaml.safe_load(file)


def save_yaml_file(yaml_content, parent=None):
    file_name, _ = QFileDialog.getSaveFileName(parent, "Save YAML File", "", "YAML Files (*.yaml)")
    if file_name:
        with open(file_name, "w") as file:
            yaml.safe_dump(yaml_content, file)


def check_yaml_syntax(text_editor):
    try:
        yaml.safe_load(text_editor.toPlainText())
        text_editor.setStyleSheet("background-color: white;")
    except yaml.YAMLError:
        text_editor.setStyleSheet("background-color: lightcoral;")
