

# API — `gentxt.headless`

Mode sans interface graphique. Aucune dépendance PySide6.

---

## Constante

```python
HEADLESS_ERROR_LOG_FILE: str = "gentxt_headless_error.log"
```

Nom du fichier de log d'erreur créé dans le répertoire courant en cas d'échec.

---

## `run_headless_mode`

```python
def run_headless_mode() -> None
```

Exécute la concaténation sur le répertoire de travail courant (`os.getcwd()`).

**Comportement** :

1. Supprime `gentxt_headless_error.log` s'il existe dans le CWD
2. Affiche en stdout le répertoire source et le chemin de sortie
3. Appelle `concat_files(source_directory, output_path, headless_mode=True)`
4. En cas de succès : affiche un message de confirmation
5. En cas d'exception : écrit le traceback dans `gentxt_headless_error.log` et affiche en stdout

**Fichier de sortie** : toujours `<CWD>/gentxt.txt`.

!!! note "Pas de sys.exit"
    `run_headless_mode` ne fait pas de `sys.exit`. C'est `main()` dans `gentxt.main` qui gère le cycle de vie du processus.

