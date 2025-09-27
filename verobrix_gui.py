#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
import sys, json, os

PROVENANCE_LOG = os.path.expanduser("~/verobrix_provenance.json")

class VeroBrixGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖥️ VeroBrix Cockpit")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.status = QLabel("🧠 Cognition loop clean.")
        layout.addWidget(self.status)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.refresh_btn = QPushButton("🔄 Refresh Provenance Log")
        self.refresh_btn.clicked.connect(self.load_log)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)
        self.load_log()

    def load_log(self):
        if os.path.exists(PROVENANCE_LOG):
            with open(PROVENANCE_LOG) as f:
                entries = json.load(f)
            self.log_view.clear()
            for entry in entries:
                line = f"[{entry['severity']}] {entry['timestamp']} :: {entry['module']} → {entry['message']}"
                self.log_view.append(line)
        else:
            self.log_view.setText("No provenance log found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = VeroBrixGUI()
    gui.show()
    sys.exit(app.exec_())
