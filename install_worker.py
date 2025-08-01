from PyQt5.QtCore import QThread, pyqtSignal
from installer_engine import InstallerEngine

class InstallWorker(QThread):
    progress = pyqtSignal(str)
    step = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, selected_programs):
        super().__init__()
        self.selected_programs = selected_programs
        self.abort_flag = False

    def run(self):
        import pythoncom
        pythoncom.CoInitialize()

        engine = InstallerEngine(self.emit_log)
        total = len(self.selected_programs)
        for idx, prog in enumerate(self.selected_programs, start=1):
            if self.abort_flag:
                self.emit_log("❌ Instalacja anulowana.")
                break
            engine.install(prog)
            self.step.emit(idx, total)
        self.finished.emit()


    def emit_log(self, msg):
        self.progress.emit(msg)

    def abort(self):
        self.abort_flag = True
