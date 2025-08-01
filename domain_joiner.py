# domain_joiner.py
import subprocess


def join_domain(domain_name: str) -> (bool, str):
    try:
        command = [
            "powershell",
            "-Command",
            f"Add-Computer -DomainName {domain_name} -Force -ErrorAction Stop"
        ]
        subprocess.run(command, check=True)
        return True, "✅ Dołączono do domeny. Uruchom ponownie komputer."
    except subprocess.CalledProcessError as e:
        return False, f"❌ Błąd podczas dołączania do domeny: {e}"
