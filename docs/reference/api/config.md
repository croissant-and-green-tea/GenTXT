

# API — `gentxt.config`

Gestion du fichier `.concat_config.json` : chargement, sauvegarde, valeurs par défaut.

---

## Constante

```python
CONFIG_FILENAME: str = ".concat_config.json"
```

---

## `create_default_config`

```python
def create_default_config() -> dict[str, set]
```

Retourne un dictionnaire avec les 6 clés de configuration remplies avec les exclusions par défaut (sets Python). Voir [Schéma de configuration](../config-schema.md#valeurs-par-defaut) pour la liste complète.

---

## `load_config`

```python
def load_config(directory: str) -> dict[str, set] | None
```

Charge et parse `.concat_config.json` depuis `directory`.

- Retourne `None` si le fichier est absent, illisible, JSON invalide, ou si la racine n'est pas un dict.
- En cas de succès, retourne un dict avec les 6 clés. Les clés manquantes dans le fichier sont complétées par des `set()` vides. Les valeurs non-listes sont normalisées en `set()` vide. Les clés inconnues sont ignorées.

---

## `save_config`

```python
def save_config(
    directory: str,
    config: dict[str, set],
    headless_mode: bool = False,
) -> bool
```

Sérialise `config` en JSON (les sets sont convertis en listes triées) et écrit `.concat_config.json` dans `directory`. Écrase le fichier existant.

Retourne `True` en cas de succès, `False` en cas d'erreur (permission, IOError). L'erreur est loguée en stdout si `headless_mode=True`, sinon elle est silencieuse (l'appelant GUI affiche son propre message).

---

## `get_effective_config`

```python
def get_effective_config(
    directory: str,
    headless_mode: bool = False,
) -> dict[str, set]
```

Retourne la configuration à utiliser pour un dossier donné :

- Si `load_config` réussit → retourne la config fichier
- Sinon → retourne `create_default_config()`

C'est la fonction appelée par `concat_files` — ne pas appeler `load_config` directement dans le pipeline.

