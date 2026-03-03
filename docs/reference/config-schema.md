


# Schéma de configuration

## Fichier

`.concat_config.json` — placé à la racine du **dossier source** (pas du projet gentxt).

## Clés disponibles

| Clé | Type JSON | Effet |
|---|---|---|
| `exclude_tree_dirs` | `list[str]` | Dossiers exclus de l'arborescence (et donc aussi du contenu) |
| `exclude_tree_files` | `list[str]` | Fichiers exclus de l'arborescence par nom exact |
| `exclude_tree_extensions` | `list[str]` | Extensions exclues de l'arborescence (ex : `".pyc"`) |
| `exclude_content_dirs` | `list[str]` | Dossiers dont le contenu n'est pas inclus (mais peuvent apparaître dans l'arbre) |
| `exclude_content_files` | `list[str]` | Fichiers dont le contenu n'est pas inclus |
| `exclude_content_extensions` | `list[str]` | Extensions dont le contenu n'est pas inclus |

Les exclusions `tree` et `content` sont indépendantes : un dossier peut apparaître dans l'arbre sans que son contenu soit inclus, et vice-versa.

## Valeurs par defaut

Appliquées quand le fichier `.concat_config.json` est **absent ou invalide** (JSON malformé, racine non-dict) :

| Clé | Valeurs par défaut |
|---|---|
| `exclude_tree_dirs` | `__pycache__`, `.git`, `venv`, `.venv`, `node_modules`, `dist`, `build`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `htmlcov`, `.eggs`, `*.egg-info` |
| `exclude_tree_files` | `.concat_config.json`, `gentxt.txt` |
| `exclude_tree_extensions` | `.pyc`, `.pyo` |
| `exclude_content_dirs` | identique à `exclude_tree_dirs` |
| `exclude_content_files` | `.concat_config.json`, `gentxt.txt` |
| `exclude_content_extensions` | `.exe`, `.dll`, `.so`, `.dylib`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.ico`, `.bmp`, `.zip`, `.tar`, `.gz`, `.rar`, `.7z`, `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.whl`, `.egg` |

!!! warning "Remplacement total"
    Dès qu'un `.concat_config.json` valide est trouvé, **toutes** les valeurs par défaut sont remplacées par la config fichier. Une clé absente du fichier JSON est traitée comme une liste vide — pas comme la valeur par défaut.

## Comportement à la validation

En cas de valeur non-liste pour une clé (ex : `"exclude_tree_dirs": "pas_une_liste"`), la clé est normalisée en `set()` vide. Aucune exception n'est levée.

Les clés inconnues sont ignorées silencieusement.

