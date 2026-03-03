


# CLI

## Synopsis

```bash
gentxt [OPTIONS]
# ou
python src/main.py [OPTIONS]
```

## Options

| Option | Alias | Comportement |
|---|---|---|
| `--headless` | `--auto` | Lance le mode headless : traite le CWD, écrit `gentxt.txt`, pas d'interface graphique |
| *(aucune option)* | | Lance le mode GUI (PySide6) |

Les deux flags `--headless` et `--auto` sont strictement équivalents — l'un ou l'autre suffit.

## Point d'entrée installé

Si GenTXT est installé via `pip install -e .` ou `pip install .`, la commande `gentxt` est disponible directement :

```bash
gentxt             # mode GUI
gentxt --headless  # mode headless
```

Défini dans `pyproject.toml` :

```toml
[project.scripts]
gentxt = "gentxt.main:main"
```

## Codes de sortie

| Code | Signification |
|---|---|
| `0` | Succès (mode headless) ou fermeture normale (mode GUI) |
| non-zéro | Erreur non gérée — rare, les erreurs métier sont loguées dans `gentxt_headless_error.log` |

