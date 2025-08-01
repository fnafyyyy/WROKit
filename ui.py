from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QCheckBox, QProgressBar, QTextEdit, QMessageBox, QLineEdit, QTabWidget
)
from PyQt5 import QtGui, QtCore, QtWidgets
from install_worker import InstallWorker
from utils import resource_path
from domain_joiner import join_domain
import json


class InstallerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WROKit")
        self.setWindowIcon(QtGui.QIcon(resource_path("WROKit.ico")))
        self.setMinimumSize(720, 540)

        # Styl ogólny
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #1e1e1e;
                color: #ccc;
                padding: 8px 20px;
                border: 1px solid #333;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #121212;
                color: white;
                font-weight: bold;
            }
        """)

        self.tabs = QTabWidget()

        self.installer_tab = QWidget()
        self.setup_installer_tab()
        self.tabs.addTab(self.installer_tab, "Instalator")

        self.domain_tab = QWidget()
        self.setup_domain_tab()
        self.tabs.addTab(self.domain_tab, "Domena")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_installer_tab(self):
        layout = QVBoxLayout()
        self.installer_tab.setLayout(layout)

        self.programs = self.load_programs()
        self.checkboxes = []
        self.all_selected = False
        self.installing = False

        header_label = QLabel("Wybierz programy do zainstalowania:")
        layout.addWidget(header_label)

        self.select_all_btn = QPushButton("Zaznacz wszystkie")
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        self.select_all_btn.setStyleSheet("background-color: #2e2e2e; color: white; border: 1px solid #444;")
        layout.addWidget(self.select_all_btn)

        self.checkbox_container = QVBoxLayout()
        for prog in self.programs:
            cb = QCheckBox(prog['name'])
            self.checkboxes.append((cb, prog))
            self.checkbox_container.addWidget(cb)

        layout.addLayout(self.checkbox_container)

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
        layout.addWidget(self.progress_bar)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #333;")
        layout.addWidget(self.log)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        self.install_btn = QPushButton("Zainstaluj")
        self.install_btn.setStyleSheet(self.install_btn_style())
        self.install_btn.clicked.connect(self.toggle_install)
        layout.addWidget(self.install_btn)

        self.footer = QLabel("WROKit v1.0 – Instalator środowiska roboczego WRO-LOT")
        self.footer.setAlignment(QtCore.Qt.AlignCenter)
        self.footer.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.footer)

    def setup_domain_tab(self):
        layout = QVBoxLayout()
        self.domain_tab.setLayout(layout)

        label = QLabel("Podaj nazwę domeny:")
        label.setStyleSheet("padding-top: 12px;")
        layout.addWidget(label)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("np. wrolot.local")
        self.domain_input.setStyleSheet("padding: 8px; background-color: #1e1e1e; border: 1px solid #333; color: white;")
        layout.addWidget(self.domain_input)

        self.domain_button = QPushButton("Dołącz do domeny")
        self.domain_button.clicked.connect(self.join_domain_clicked)
        self.domain_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(self.domain_button)
        layout.addStretch()

    def join_domain_clicked(self):
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Błąd", "Wpisz nazwę domeny.")
            return
        success, output = join_domain(domain)
        if success:
            QMessageBox.information(self, "Sukces", "✅ Komputer został dodany do domeny.\nZrestartuj komputer.")
        else:
            QMessageBox.critical(self, "Błąd", f"❌ Nie udało się dołączyć do domeny:\n\n{output}")

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

    def toggle_install(self):
        if not self.installing:
            selected = [prog for cb, prog in self.checkboxes if cb.isChecked()]
            if not selected:
                QMessageBox.warning(self, "Brak wyboru", "Zaznacz przynajmniej jeden program.")
                return
            self.installing = True
            self.install_btn.setText("Anuluj")
            self.install_btn.setStyleSheet(self.cancel_btn_style())
            self.worker = InstallWorker(selected)
            self.worker.progress.connect(self.log_message)
            self.worker.step.connect(self.update_progress)
            self.worker.finished.connect(self.on_install_finished)
            self.worker.start()
        else:
            self.worker.abort()

    def install_btn_style(self):
        return """
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 14px;
                margin-top: 7px;
                margin-bottom: 7px;                       
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """

    def cancel_btn_style(self):
        return """
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 14px;
                margin-top: 7px;
                margin-bottom: 7px;                       
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Postęp: {current}/{total}")

    def on_install_finished(self):
        self.installing = False
        self.install_btn.setText("Zainstaluj")
        self.install_btn.setStyleSheet(self.install_btn_style())
        self.install_btn.setEnabled(True)
        self.status_label.setText("✅ Instalacja zakończona.")
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Zakończono", "Instalacja zakończona.")
