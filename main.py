# main.py – punkt wejścia do aplikacji

from PyQt5.QtWidgets import QApplication
import sys
from ui import InstallerApp


def main():
    app = QApplication(sys.argv)
    window = InstallerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()