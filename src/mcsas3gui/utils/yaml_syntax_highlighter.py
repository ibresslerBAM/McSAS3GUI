from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class YAMLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # Define formatting styles
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("blue"))
        self.key_format.setFontWeight(QFont.Weight.Bold)

        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("darkgreen"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("darkgray"))
        self.comment_format.setFontItalic(True)

        # Define regular expressions for YAML elements
        self.rules = [
            (QRegularExpression(r"^\s*[^#]*:"), self.key_format),  # Keys
            (QRegularExpression(r":\s*[^#]*"), self.value_format),  # Values
            (QRegularExpression(r"#.*$"), self.comment_format),  # Comments
        ]

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
