


# Configuration

## Principe

gentxt cherche un fichier `.concat_config.json` à la racine du **dossier source** avant chaque exécution.

- **Fichier présent** : la config est chargée et remplace intégralement les valeurs par défaut.
- **Fichier absent ou invalide** : les valeurs par défaut s'appliquent (voir [Schéma de configuration](../reference/config-schema.md)).

---

## Créer ou modifier la configuration

### Via l'interface GUI

1. Cliquer **Créer / Modifier Configuration**
2. Sélectionner le dossier cible
3. L'éditeur s'ouvre avec le format texte simplifié

### Manuellement

Créer `.concat_config.json` à la racine du dossier source.

---

## Format texte simplifié (éditeur intégré)

L'éditeur GUI utilise un format texte lisible — pas de JSON brut, pas de guillemets, pas de virgules.

```
# exclude_tree_dirs
__pycache__
.git
venv
node_modules

# exclude_tree_extensions
.pyc

# exclude_content_dirs
venv

# exclude_content_extensions
.exe
.dll
.jpg
.png
.zip
.pdf
```

Chaque section commence par `# nom_de_la_clé`. Les valeurs suivent, une par ligne. Les lignes vides sont ignorées.

---

## Format JSON interne

Le fichier stocké sur disque est un JSON standard :

```json
{
    "exclude_tree_dirs": ["__pycache__", ".git", "venv"],
    "exclude_tree_files": [".concat_config.json", "gentxt.txt"],
    "exclude_tree_extensions": [".pyc"],
    "exclude_content_dirs": ["venv"],
    "exclude_content_files": [".concat_config.json", "gentxt.txt"],
    "exclude_content_extensions": [".exe", ".dll", ".jpg", ".png", ".zip", ".pdf"]
}
```

---

## Exemple : projet Python typique

```json
{
    "exclude_tree_dirs": ["__pycache__", ".git", "venv", ".venv", "dist", "build", "htmlcov"],
    "exclude_tree_files": [".concat_config.json", "gentxt.txt"],
    "exclude_tree_extensions": [".pyc", ".pyo"],
    "exclude_content_dirs": ["__pycache__", "venv", ".venv"],
    "exclude_content_files": [".concat_config.json", "gentxt.txt"],
    "exclude_content_extensions": [".exe", ".dll", ".jpg", ".png", ".ico", ".zip", ".pdf", ".whl"]
}
```

!!! note "Clé manquante"
    Si une clé est absente du fichier JSON, elle est complétée par une liste vide — pas par la valeur par défaut. La config fichier est souveraine.

