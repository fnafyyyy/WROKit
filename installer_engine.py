# installer_engine.py – logika instalacji

import os
import zipfile
import shutil
import subprocess
import tempfile
import json
import glob
import winreg
from utils import resource_path, remove_tightvnc_viewer
import pythoncom
from win32com.client import Dispatch
import psutil


class InstallerEngine:
    def __init__(self, logger):
        self.logger = logger

    def load_programs(self):
        config_path = resource_path("config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_gui_user_desktop(self):
        try:
            current_user = None
            for proc in psutil.process_iter(['name', 'username']):
                if proc.info['name'] == "explorer.exe" and proc.info['username']:
                    current_user = proc.info['username'].split("\\")[-1]
                    break

            if not current_user:
                self.logger("⚠️ Nie znaleziono aktywnego użytkownika GUI")
                return None

            self.logger(f"🔍 Szukam pulpitu dla użytkownika: {current_user}")

            possible_paths = [
                f"C:\\Users\\{current_user}\\OneDrive\\Pulpit",
                f"C:\\Users\\{current_user}\\OneDrive\\Desktop",
                f"C:\\Users\\{current_user}\\OneDrive - *\\Pulpit",
                f"C:\\Users\\{current_user}\\OneDrive - *\\Desktop",
                f"C:\\Users\\{current_user}\\Desktop",
                f"C:\\Users\\{current_user}\\Pulpit"
            ]

            for path in possible_paths:
                if "*" in path:
                    matches = glob.glob(path)
                    for match in matches:
                        if os.path.exists(match) and os.path.isdir(match):
                            self.logger(f"✔ Znaleziono pulpit: {match}")
                            return match
                else:
                    if os.path.exists(path) and os.path.isdir(path):
                        self.logger(f"✔ Znaleziono pulpit: {path}")
                        return path

            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                if os.path.exists(desktop_path) and os.path.isdir(desktop_path):
                    self.logger(f"✔ Znaleziono pulpit przez rejestr: {desktop_path}")
                    return desktop_path
        except Exception as e:
            self.logger(f"❌ Błąd podczas szukania pulpitu: {e}")

        return None

    def install(self, prog):
        pythoncom.CoInitialize()
        name = prog.get("name", "(brak nazwy)")
        self.logger(f"\nInstaluję: {name}...")

        try:
            prog_type = prog.get("type")

            if prog_type == "custom_haos":
                self.install_haos(prog)
            elif prog_type == "custom_inflot":
                self.install_inflot(prog)
            elif prog_type == "anyconnect_zip":
                self.install_anyconnect_from_zip(prog)
            elif prog_type == "msi":
                self.install_msi(prog)
            elif prog_type == "exe":
                self.install_exe(prog)
            else:
                self.logger(f"⚠️ Nieznany typ instalatora: {prog_type}")
        except Exception as e:
            self.logger(f"❌ Błąd przy instalacji {name}: {e}")

    def install_haos(self, prog):
        zip_path = resource_path(prog["zip"])
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("C:\\")

        src = os.path.join(r"C:\\haos", "haos_start.bat")
        icon_path = os.path.join(r"C:\\haos", "HAOS Client.ico")

        if not os.path.isfile(src):
            self.logger("❌ Nie znaleziono haos_start.bat – pomijam tworzenie skrótu.")
            return

        shell = Dispatch("WScript.Shell")
        desktop_path = self.get_gui_user_desktop() or shell.SpecialFolders("Desktop")
        if not os.path.isdir(desktop_path):
            self.logger(f"❌ Ścieżka pulpitu nie istnieje: {desktop_path}")
            return

        shortcut = os.path.join(desktop_path, "HAOS.lnk")
        shortcut_obj = shell.CreateShortCut(shortcut)
        shortcut_obj.Targetpath = src
        shortcut_obj.WorkingDirectory = os.path.dirname(src)
        if os.path.exists(icon_path):
            shortcut_obj.IconLocation = icon_path
        shortcut_obj.save()

        self.logger(f"📌 Ścieżka skrótu HAOS: {shortcut}")
        self.logger("✔ Skrót HAOS został utworzony.")
        os.makedirs(r"C:\\Temp\\out", exist_ok=True)
        self.logger("✔ HAOS zainstalowany.")

    def install_inflot(self, prog):
        zip_path = resource_path(prog["zip"])
        extract_parent = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_parent)

        src_folder = os.path.join(extract_parent, "inflot")
        dest_folder = r"C:\\inflot"

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        for item in os.listdir(src_folder):
            s = os.path.join(src_folder, item)
            d = os.path.join(dest_folder, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        self.grant_folder_access_to_everyone(dest_folder)

        fis_exe_path = os.path.join(dest_folder, "FIS.exe")
        shell = Dispatch("WScript.Shell")
        desktop_path = self.get_gui_user_desktop() or shell.SpecialFolders("Desktop")
        shortcut_path = os.path.join(desktop_path, "FIS.lnk")

        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = fis_exe_path
        shortcut.WorkingDirectory = dest_folder
        shortcut.IconLocation = fis_exe_path
        shortcut.save()

        self.logger("✔ Inflot zainstalowany.")

    def install_anyconnect_from_zip(self, prog):
        zip_path = resource_path(prog["zip"])
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
        self.logger("✔ AnyConnect VPN zainstalowany.")

    def install_msi(self, prog):
        original_path = resource_path(prog['path'])
        if not os.path.isfile(original_path):
            raise FileNotFoundError(f"Nie znaleziono pliku MSI: {original_path}")

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, os.path.basename(original_path))
        shutil.copyfile(original_path, temp_path)

        self.logger(f"📦 Ścieżka MSI (tymczasowa): {temp_path}")

        subprocess.run(["msiexec", "/i", temp_path, "/quiet"], check=True)
        self.logger("✔ Pakiet MSI zainstalowany.")

        if "tightvnc" in original_path.lower():
            remove_tightvnc_viewer()
            self.logger("🧹 Usunięto TightVNC Viewer po instalacji.")

    def install_exe(self, prog):
        installer_path = resource_path(prog['path'])
        if not os.path.isfile(installer_path):
            raise FileNotFoundError(f"Nie znaleziono pliku EXE: {installer_path}")
        params = prog.get("params", ["/quiet", "/norestart"])
        subprocess.run([installer_path] + params, check=True)
        self.logger("✔ Instalator EXE zakończył działanie.")

    def grant_folder_access_to_everyone(self, folder_path):
        try:
            result = subprocess.run(["icacls", folder_path, "/grant", "Everyone:(OI)(CI)F", "/T", "/C"], check=True)
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["icacls", folder_path, "/grant", "Wszyscy:(OI)(CI)F", "/T", "/C"], check=True)
            except subprocess.CalledProcessError as e:
                self.logger(f"❌ Błąd podczas nadawania uprawnień do {folder_path}: {e}")
