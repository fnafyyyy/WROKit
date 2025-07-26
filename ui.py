# ui.py – interfejs użytkownika i logika GUI

import sys
import os
import json
import tempfile
import shutil
import zipfile
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QPushButton, QTextEdit, QLabel, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QPoint
from installer_engine import InstallerEngine
from utils import resource_path


class InstallWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    step = QtCore.pyqtSignal(int, int)

    def __init__(self, selected_programs):
        super().__init__()
        self.selected_programs = selected_programs
        self.engine = InstallerEngine(self.emit_log)

    def emit_log(self, msg):
        self.progress.emit(msg)

    def run(self):
        total = len(self.selected_programs)
        for idx, prog in enumerate(self.selected_programs, 1):
            self.engine.install(prog)
            self.step.emit(idx, total)
        self.finished.emit()


class InstallerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WROKit")
        self.setWindowIcon(QtGui.QIcon(resource_path("WROKit.ico")))
        self.setStyleSheet("background-color: #121212; color: #ffffff; border-radius: 12px;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.programs = self.load_programs()
        self.checkboxes = []
        self.all_selected = False

        header_label = QLabel("Wybierz programy do zainstalowania:")
        header_label.setStyleSheet("color: #ffffff;")
        self.layout.addWidget(header_label)

        self.select_all_btn = QPushButton("Zaznacz wszystkie")
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        self.select_all_btn.setStyleSheet("background-color: #2e2e2e; color: white; border: 1px solid #444;")
        self.layout.addWidget(self.select_all_btn)

        self.checkbox_container = QVBoxLayout()
        for prog in self.programs:
            cb = QCheckBox(prog['name'])
            cb.setStyleSheet("color: white;")
            self.checkboxes.append((cb, prog))
            self.checkbox_container.addWidget(cb)

        self.layout.addLayout(self.checkbox_container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
            }
        """)
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #333;")
        self.layout.addWidget(self.log)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        self.layout.addWidget(self.status_label)

        self.install_btn = QPushButton("Zainstaluj")
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 14px;
                margin-bottom: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.install_btn.clicked.connect(self.install_selected)
        self.layout.addWidget(self.install_btn)

        self.footer = QLabel("WROKit v1.0 – Instalator środowiska roboczego WRO-LOT")
        self.footer.setAlignment(QtCore.Qt.AlignCenter)
        self.footer.setStyleSheet("font-size: 10px; color: gray;")
        self.layout.addWidget(self.footer)

        self.setMinimumWidth(360)

    def load_programs(self):
        config_path = resource_path('config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def log_message(self, msg):
        self.log.append(msg)
        QtWidgets.QApplication.processEvents()

    def toggle_select_all(self):
        new_state = not self.all_selected
        for cb, _ in self.checkboxes:
            cb.setChecked(new_state)
        self.all_selected = new_state
        self.select_all_btn.setText("Odznacz wszystkie" if new_state else "Zaznacz wszystkie")

    def install_selected(self):
        selected = [prog for cb, prog in self.checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Brak wyboru", "Zaznacz przynajmniej jeden program.")
            return

        self.install_btn.setEnabled(False)
        self.worker = InstallWorker(selected)
        self.worker.progress.connect(self.log_message)
        self.worker.step.connect(self.update_progress)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Postęp: {current}/{total}")

    def on_install_finished(self):
        self.install_btn.setEnabled(True)
        self.status_label.setText("✅ Instalacja zakończona.")
        QMessageBox.information(self, "Zakończono", "Instalacja zakończona.")
