# utils.py – funkcje pomocnicze

import os
import sys
import ctypes
import shutil


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    sys.exit()


def remove_tightvnc_viewer():
    try:
        install_dir = r"C:\Program Files\TightVNC"
        viewer_path = os.path.join(install_dir, "tvnviewer.exe")
        if os.path.exists(viewer_path):
            os.remove(viewer_path)
    except Exception:
        pass
