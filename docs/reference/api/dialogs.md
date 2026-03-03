


# API — `gentxt.dialogs`

Composants GUI PySide6. **Exclu de la couverture de tests** (`.coveragerc`).

---

## `SimpleFolderDialog`

Dialogue de sélection de dossier avec barre d'adresse éditable.

```python
SimpleFolderDialog(
    title: str,
    initial_path: str,
    parent: QWidget | None = None,
    show_files: bool = False,
)
```

| Paramètre | Description |
|---|---|
| `title` | Titre de la fenêtre de dialogue |
| `initial_path` | Chemin affiché à l'ouverture |
| `parent` | Widget parent Qt |
| `show_files` | Si `True`, les fichiers sont visibles (pas sélectionnables, pour repère visuel) |

**Méthode publique**

```python
def get_selected_path(self) -> str
```

Retourne le chemin du dossier validé, ou une chaîne vide si annulation.

---

## `SimpleFileSaveDialog`

Dialogue de sélection d'emplacement et nom de fichier de sortie.

```python
SimpleFileSaveDialog(
    title: str,
    default_path: str,
    parent: QWidget | None = None,
)
```

**Méthode publique**

```python
def get_selected_file(self) -> str
```

Retourne le chemin complet du fichier de sortie choisi.

---

## `ConfigEditorDialog`

Éditeur de `.concat_config.json` en format texte simplifié.

```python
ConfigEditorDialog(
    directory: str,
    parent: QWidget | None = None,
)
```

| Paramètre | Description |
|---|---|
| `directory` | Dossier dans lequel lire/écrire `.concat_config.json` |

Charge le fichier existant s'il est présent, sinon propose de créer une config par défaut. Le bouton Enregistrer appelle `save_config` après conversion du texte en dict via `_text_to_config`.

**Méthodes internes** (non publiques) :

- `_config_to_text(config: dict) -> str` — sérialise en format texte pour l'éditeur
- `_text_to_config(text: str) -> dict` — parse le texte vers un dict Python
- `save_config(self) -> None` — lit l'éditeur, convertit, écrit sur disque

