from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class ColumnSetting(QDialog):
    def __init__(self, parent=None, config_handler=None, config=None):
        super().__init__(parent)
        self.config_handler = config_handler
        self.config = config

        # Set up the dialog window
        self.setWindowTitle("Toggle Columns")
        self.setGeometry(100, 100, 500, 400)
        self.setMinimumSize(500, 400)

        # Create and configure the layout with a placeholder label
        layout = QVBoxLayout()
        label = QLabel("Work in progress")
        label.setAlignment(Qt.AlignCenter)  # Center-align the text
        layout.addWidget(label)

        # Set the layout to the dialog
        self.setLayout(layout)
