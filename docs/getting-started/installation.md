



# Installation

## Prérequis

| Dépendance | Version minimale | Rôle |
|---|---|---|
| Python | 3.9 | Runtime |
| PySide6 | dernière stable | Interface graphique |
| pyexcel-ods3 | dernière stable | Lecture des fichiers `.ods` |
| odfpy | dernière stable | Lecture des fichiers `.odt` |

OS supportés : **Linux** (testé), **Windows** (testé). macOS non officiellement supporté.

---

## Depuis les sources

```bash
git clone https://github.com/croissant-and-green-tea/GenTXT.git
cd GenTXT
pip install -r requirements.txt
```

Pour les outils de développement (ruff, pytest, mypy) :

```bash
pip install -r requirements-dev.txt
```

Vérification :

```bash
python src/main.py --headless
# → GenTXT: Mode Headless activé.
```

---

## Exécutable Linux (sans Python)

Un exécutable standalone peut être généré via PyInstaller (voir [Build & Release](../development/build-release.md)) ou téléchargé depuis les releases GitHub.

### Installation système via script

```bash
chmod +x install_gentxt.sh
./install_gentxt.sh
```

Ce script installe GenTXT dans `/opt/gentxt/`, copie l'icône dans `~/.local/share/icons/hicolor/`, et crée le fichier `.desktop` dans `~/.local/share/applications/`.

L'application devient alors accessible depuis le menu d'applications.

### Désinstallation

```bash
chmod +x uninstall_gentxt.sh
./uninstall_gentxt.sh
```

---

## Vérification post-installation

=== "Depuis les sources"

    ```bash
    python src/main.py
    ```

=== "Exécutable"

    ```bash
    ./GenTXT
    ```

La fenêtre principale GenTXT doit s'ouvrir.

