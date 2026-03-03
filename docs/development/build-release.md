


# Build & Release

## Prérequis build

```bash
pip install -r requirements-build.txt
# contient requirements.txt + pyinstaller>=6.0
```

---

## Build PyInstaller

```bash
make build
# équivalent : pyinstaller GenTxt.spec
```

L'exécutable est produit dans `dist/GenTXT` (Linux) ou `dist/GenTXT.exe` (Windows).

`GenTxt.spec` configure :

- Point d'entrée : `src/main.py`
- Collecte automatique des `.py` du package `gentxt/`
- `hiddenimports` : `PySide6.QtCore`, `PySide6.QtGui`, `PySide6.QtWidgets`, `gentxt.*`
- Icône : `src/icons/icons.ico` (Windows uniquement — le format `.ico` génère un warning sur Linux)
- `console=False` : pas de fenêtre console en mode GUI

---

## Cibles Makefile

```bash
make help            # liste toutes les cibles avec description
make all             # lint + tests + couverture + build + docs (pipeline complet)
make build           # build PyInstaller
make clean           # supprime build/, dist/, site/, htmlcov/, .coverage, __pycache__
make install-system  # build + install_gentxt.sh (Linux)
make uninstall-system
make docs            # mkdocs build
make serve-docs      # mkdocs serve (http://127.0.0.1:8000)
make deploy-docs     # mkdocs gh-deploy --force (GitHub Pages)
```

---

## Documentation

```bash
make docs-deps   # pip install -r requirements-docs.txt
make docs        # génère le site dans site/
make serve-docs  # serveur local de prévisualisation
make deploy-docs # déploiement GitHub Pages
```

---

## Processus de release

1. Mettre à jour `src/gentxt/__version__.py` avec le nouveau numéro de version
2. Mettre à jour `CHANGELOG.md` : ajouter la section `## [x.y.z] - YYYY-MM-DD`
3. Vérifier que `make all` passe sans erreur
4. Committer : `git commit -m "chore: release vx.y.z"`
5. Tagger : `git tag vx.y.z && git push --tags`
6. Le CI déploie automatiquement la documentation sur GitHub Pages

---

## Installation système Linux (script)

`install_gentxt.sh` effectue les opérations suivantes :

- Copie `dist/GenTXT` dans `/opt/gentxt/`
- Copie `concatenation_rapide.sh` dans `/opt/gentxt/`
- Installe l'icône PNG dans `~/.local/share/icons/hicolor/{256x256,48x48}/apps/`
- Crée `~/.local/share/applications/gentxt.desktop`
- Rafraîchit les caches `update-desktop-database` et `gtk-update-icon-cache`

