

# API — `gentxt.core`

Module central. Aucune dépendance GUI. Importable sans PySide6.

---

## `concat_files`

```python
def concat_files(
    source_directory: str,
    output_path: str,
    headless_mode: bool = False,
) -> None
```

Point d'entrée principal du moteur. Orchestre l'ensemble du pipeline :

1. Chargement de la configuration effective via `get_effective_config`
2. Génération de l'arborescence texte via `generate_tree`
3. Écriture de la section arborescence dans `output_path`
4. Parcours récursif et écriture du contenu fichier par fichier
5. Post-traitement du fichier de sortie via `_clean_excessive_newlines`

**Paramètres**

| Paramètre | Type | Description |
|---|---|---|
| `source_directory` | `str` | Chemin absolu du dossier à traiter |
| `output_path` | `str` | Chemin absolu du fichier de sortie |
| `headless_mode` | `bool` | Si `True`, les erreurs non-critiques sont loguées en stdout plutôt qu'affichées en GUI |

**Exceptions** : propage les `OSError` / `PermissionError` en cas d'impossibilité d'écrire le fichier de sortie.

---

## `generate_tree`

```python
def generate_tree(
    directory: str,
    config: dict,
    prefix: str = "",
) -> str
```

Génère la représentation textuelle de l'arborescence du dossier, en appliquant les filtres `exclude_tree_*` de la config.

Retourne une chaîne multiligne avec indentation par `├──` / `└──` / `│`.

---

## `is_binary_file`

```python
def is_binary_file(filepath: str) -> bool
```

Détecte si un fichier est binaire en lisant les 8 192 premiers octets.

Retourne `True` si :
- le fichier est vide
- il contient des octets nuls
- plus de 30 % des octets ne sont pas des caractères texte
- toute `OSError` ou `PermissionError` est levée à la lecture

---

## `read_file_content`

```python
def read_file_content(filepath: str) -> str
```

Lit un fichier texte. Tente d'abord UTF-8, puis latin-1 en fallback. Retourne le contenu sous forme de chaîne.

---

## `read_ods_file`

```python
def read_ods_file(filepath: str) -> str
```

Lit un fichier `.ods` via `pyexcel-ods3`. Retourne une chaîne formatée feuille par feuille :

```text
=== Feuille: NomFeuille ===

col1    col2    col3
val1    val2    val3
```

Lève une `ImportError` si `pyexcel-ods3` n'est pas installé.

---

## `read_odt_file`

```python
def read_odt_file(filepath: str) -> str
```

Lit un fichier `.odt` via `odfpy`. Extrait le texte de chaque paragraphe. Retourne les paragraphes concaténés avec `\n`.

Lève une `ImportError` si `odfpy` n'est pas installé.

---

## `_clean_excessive_newlines`

```python
def _clean_excessive_newlines(filepath: str) -> None
```

Post-traitement in-place. Applique `re.sub(r'\n{6,}', '\n\n\n', content)` sur le fichier de sortie. 5 sauts de ligne consécutifs ou moins sont conservés tels quels.


