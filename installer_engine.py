# installer_engine.py – logika instalacji

import os
import zipfile
import shutil
import subprocess
import tempfile
from utils import resource_path, remove_tightvnc_viewer


class InstallerEngine:
    def __init__(self, logger):
        self.logger = logger

    def load_programs(self):
        import json
        config_path = resource_path("config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def install(self, prog):
        name = prog["name"]
        prog_type = prog["type"]
        self.logger(f"\nInstaluję: {name}...")

        try:
            if prog_type == "exe":
                path = resource_path(prog["path"])
                params = prog.get("params", [])
                subprocess.run([path, *params], check=True)

            elif prog_type == "msi":
                msi_src = resource_path(prog["path"])
                temp_dir = tempfile.gettempdir()
                msi_dst = os.path.join(temp_dir, os.path.basename(msi_src))
                shutil.copy(msi_src, msi_dst)
                params = prog.get("params", ["/quiet"])
                subprocess.run(["msiexec", "/i", msi_dst, *params], check=True)

            elif prog_type == "zip_installer":
                zip_path = resource_path(prog["zip"])
                installer = prog["installer"]
                params = prog.get("params", [])

                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(tmpdir)

                    setup_path = os.path.join(tmpdir, installer)
                    subprocess.run([setup_path, *params], check=True)

            elif prog_type == "custom_haos":
                self.install_haos(prog)

            elif prog_type == "jre" or prog_type == "vc_redist":
                path = resource_path(prog["path"])
                params = prog.get("params", [])
                subprocess.run([path, *params], check=True)

            elif prog_type == "anyconnect_zip":
                self.install_anyconnect_from_zip(prog)

            if name == "TightVNC":
                remove_tightvnc_viewer()
                self.logger("🧹 TightVNC Viewer został usunięty.")

            self.logger(f"✔ {name} zainstalowany.")

        except subprocess.CalledProcessError as e:
            if e.returncode == 3010:
                self.logger(f"⚠ {name} wymaga ponownego uruchomienia systemu (kod 3010) – uznaję za sukces.")
                self.logger(f"✔ {name} zainstalowany (z ostrzeżeniem).")
            else:
                self.logger(f"❌ Błąd podczas instalacji {name} (kod {e.returncode}): {e}")

    def install_haos(self, prog):
        zip_path = resource_path(prog["zip"])
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("C:\\")

        src = os.path.join("C:\\haos", "haos_start.bat")
        shortcut = os.path.join(os.path.expanduser("~"), "Desktop", "HAOS.lnk")
        icon_path = os.path.join("C:\\haos", "HAOS Client.ico")

        import pythoncom
        from win32com.client import Dispatch

        shell = Dispatch('WScript.Shell')
        shortcut_obj = shell.CreateShortCut(shortcut)
        shortcut_obj.Targetpath = src
        shortcut_obj.IconLocation = icon_path
        shortcut_obj.WorkingDirectory = os.path.dirname(src)
        shortcut_obj.save()

        os.makedirs("C:\\haos\\temp", exist_ok=True)
        self.logger("✔ HAOS zainstalowany.")

    def install_anyconnect_from_zip(self, prog):
        zip_path = resource_path(prog['zip'])
        extract_path = os.path.join(tempfile.gettempdir(), 'anyconnect_temp')

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        installer_path = os.path.join(extract_path, 'anyconnect-win-4.8.03052-core-vpn-predeploy-k9.msi')
        if not os.path.isfile(installer_path):
            raise FileNotFoundError(f"Nie znaleziono {installer_path}")

        subprocess.run(["msiexec", "/i", installer_path, "/quiet"], check=True)
