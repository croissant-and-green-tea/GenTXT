


# Tests

## Structure

```
tests/
├── conftest.py          # fixtures partagées (dossiers tmp, configs, fichiers types)
├── unit/                # tests des fonctions isolées
│   ├── test_config.py
│   ├── test_core_binary.py
│   ├── test_core_postprocess.py
│   ├── test_core_readers.py
│   └── test_core_tree.py
├── integration/         # tests du pipeline complet
│   ├── test_concat_pipeline.py
│   └── test_headless_mode.py
└── non_regression/      # golden files
    ├── fixtures/
    │   ├── project_simple/
    │   └── project_with_config/
    ├── expected_*.txt
    └── test_golden_output.py
```

## Commandes

```bash
make test              # suite complète
make test-unit         # tests unitaires uniquement
make test-integration  # tests d'intégration uniquement
make test-nr           # tests de non-régression uniquement
make test-cov          # tests + rapport de couverture HTML (htmlcov/)
```

Ou directement avec pytest :

```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/ --cov=src/gentxt --cov-report=term-missing
```

---

## Tests de non-régression (golden files)

Les fichiers `tests/non_regression/expected_*.txt` contiennent la sortie de référence pour des projets fixtures.

Si un changement modifie intentionnellement le format de sortie, régénérer les golden files :

```bash
make update-snapshots
# équivalent : UPDATE_SNAPSHOTS=1 pytest tests/non_regression/ -v
```

Vérifier le diff des fichiers `expected_*.txt` avant de committer.

---

## Couverture

`dialogs.py` est exclu de la couverture (`.coveragerc`) — les composants PySide6 nécessitent un display server et sont difficiles à tester unitairement sans mock lourd.

Seuil attendu : les modules `core.py`, `config.py` et `headless.py` doivent être couverts à plus de 90 %.

---

## Fixtures partagées (`conftest.py`)

| Fixture | Description |
|---|---|
| `tmp_source_dir` | Dossier source vide dans un répertoire temporaire |
| `tmp_output_file` | Chemin de sortie dans un répertoire temporaire |
| `simple_project` | Projet minimal : `README.md`, `main.py`, `data/notes.txt` |
| `project_with_binary` | Projet avec un fichier binaire (`\x00` bytes) |
| `project_with_excluded_dirs` | Projet avec `__pycache__`, `.git`, `node_modules` |
| `project_with_ods` | Projet avec le fichier ODS de test (`test_mano/`) |
| `project_with_odt` | Projet avec le fichier ODT de test (`test_mano/`) |
| `minimal_config` | Config avec toutes les listes vides sauf `gentxt.txt` exclu |
| `config_with_exclusions` | Config avec exclusions non triviales pour les tests d'intégration |
| `write_config` | Factory : écrit un `.concat_config.json` dans `tmp_source_dir` |

---

## CI

Le workflow `.github/workflows/ci.yml` exécute à chaque push et PR :

- lint ruff
- tests avec couverture
- build de la documentation MkDocs

