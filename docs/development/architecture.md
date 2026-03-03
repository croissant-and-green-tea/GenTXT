


# Architecture

## Vue d'ensemble des modules

```
src/
└── gentxt/
    ├── __init__.py       # exposition de __version__
    ├── __version__.py    # version sémantique
    ├── config.py         # chargement / sauvegarde .concat_config.json
    ├── core.py           # moteur de concaténation (sans GUI)
    ├── dialogs.py        # composants PySide6 (GUI uniquement)
    ├── headless.py       # mode CLI sans GUI
    └── main.py           # point d'entrée, dispatch GUI vs headless
```

## Séparation des responsabilités

| Module | Responsabilité | Dépendance GUI |
|---|---|---|
| `config.py` | Lecture/écriture `.concat_config.json`, valeurs par défaut | ❌ |
| `core.py` | Arborescence, lecture fichiers, concaténation, post-traitement | ❌ |
| `headless.py` | Orchestration mode CLI, log d'erreur | ❌ |
| `dialogs.py` | Dialogues Qt personnalisés | ✅ PySide6 |
| `main.py` | Dispatch `--headless` vs GUI, instanciation `QApplication` | ✅ PySide6 (lazy) |

`core.py` et `config.py` n'importent jamais PySide6. Ils sont utilisables dans tout contexte sans serveur d'affichage.

## Flux d'exécution

### Mode GUI

```
main() → QApplication → MainWindow
  └── Démarrer → SimpleFolderDialog
        └── concat_files(source, output, headless_mode=False)
              ├── get_effective_config(source)
              ├── generate_tree(source, config)
              ├── [lecture fichier par fichier]
              └── _clean_excessive_newlines(output)
```

### Mode headless

```
main() → run_headless_mode()
  └── concat_files(cwd, cwd/gentxt.txt, headless_mode=True)
        ├── get_effective_config(cwd)
        ├── generate_tree(cwd, config)
        ├── [lecture fichier par fichier]
        └── _clean_excessive_newlines(output)
```

## Import lazy de PySide6

`main.py` n'importe PySide6 que si le mode GUI est activé (`_build_main_window()` est appelé uniquement quand `--headless` est absent). Cela permet d'invoquer `--headless` dans un environnement sans Qt installé (si `core.py` et `config.py` sont utilisés directement).

## Compatibilité PyInstaller

`GenTxt.spec` collecte explicitement tous les fichiers `.py` du package `gentxt/` et déclare les `hiddenimports` PySide6. L'icône n'est incluse que sur Windows (`sys.platform == 'win32'`).


