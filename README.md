# 💼 WROKit – Installer Engine

`installer_engine.py` to moduł logiki instalatora aplikacji WROKit — stworzonego do automatycznej instalacji programów, konfiguracji środowiska pracy oraz tworzenia skrótów w systemie Windows (również w środowisku domenowym i z OneDrive).

---

## 🧩 Funkcje

- ✅ Automatyczna instalacja na podstawie `config.json`
- ✅ Obsługa różnych typów instalatorów:
  - `.exe` (z parametrami np. `/quiet`, `/norestart`)
  - `.msi` (kopiowane do `%TEMP%`, aby uniknąć błędów 1619)
  - `.zip` (wypakowanie i uruchomienie wskazanego pliku)
  - `custom_haos`, `custom_inflot`, `anyconnect_zip`
- ✅ Tworzenie skrótów na realnym pulpicie GUI użytkownika (również OneDrive)
- ✅ Nadawanie uprawnień do folderów instalacyjnych (`icacls`)
- ✅ Usuwanie TightVNC Viewer po instalacji TightVNC

---

## ⚙️ Struktura `config.json`

```json
[
  {
    "name": "TightVNC",
    "type": "msi",
    "path": "instalki/tightvnc-setup.msi"
  },
  {
    "name": "Java",
    "type": "exe",
    "path": "instalki/java.exe",
    "params": ["/s"]
  },
  {
    "name": "HAOS",
    "type": "custom_haos",
    "zip": "instalki/haos.zip"
  }
]
```

---

## 🔧 Parametry `config.json`

| Pole      | Opis                                                  |
|-----------|-------------------------------------------------------|
| `name`    | Nazwa programu (do wyświetlania w logach)            |
| `type`    | `exe`, `msi`, `zip_installer`, `custom_haos`, ...    |
| `path`    | Ścieżka do pliku `.exe` lub `.msi`                   |
| `zip`     | Ścieżka do pliku `.zip`, jeśli typ to `custom_*`     |
| `params`  | (opcjonalnie) lista parametrów dla `exe/msi`         |

---

## 🖥️ Budowanie z PyInstaller

```bash
pyinstaller main.py --onefile --noconsole --name WROKit --icon=WROKit.ico --uac-admin --clean ^
  --add-data "config.json;." ^
  --add-data "instalki\tightvnc-setup.msi;instalki" ^
  --add-data "instalki\haos.zip;instalki" ^
  --add-data "instalki\java.exe;instalki"
```

---

## 📁 Powiązane pliki w projekcie

| Plik                 | Opis                                           |
|----------------------|------------------------------------------------|
| `main.py`            | Punkt wejścia aplikacji (GUI)                  |
| `ui.py`              | Interfejs użytkownika (PyQt5, zakładki)        |
| `installer_engine.py`| Logika instalacji, tworzenie skrótów, itp.     |
| `install_worker.py`  | Wątek instalacyjny                             |
| `domain_joiner.py`   | Dołączenie do domeny Windows                   |
| `utils.py`           | Funkcje pomocnicze (m.in. `resource_path`)     |

---

## 📌 Wymagania

- Python 3.10+
- PyQt5
- PyInstaller (do budowy wersji `.exe`)
- Uprawnienia administratora (dla niektórych operacji)

---

## 🛠️ Autor

Adrian Pachura — młodszy administrator systemowy  
Projekt realizowany na potrzeby automatyzacji instalacji środowiska roboczego WRO-LOT.
