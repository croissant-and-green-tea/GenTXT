

# Contribuer

## Setup développement

```bash
git clone https://github.com/croissant-and-green-tea/GenTXT.git
cd GenTXT
pip install -r requirements-dev.txt
```

Dépendances dev : `ruff` (lint/format), `pytest` + `pytest-cov` (tests), `mypy` (types).

---

## Conventions de code

- **Style** : `ruff` avec `line-length = 100`, `target-version = "py39"`
- **Types** : mypy strict sur `core.py` et `config.py` — les nouveaux modules doivent être typés
- **Docstrings** : format Google (pour mkdocstrings)
- **Encodage** : UTF-8 systématique, déclaration `# -*- coding: utf-8 -*-` en tête de chaque fichier

Vérifier avant tout commit :

```bash
make lint
make typecheck
make test
```

---

## Ajouter le support d'un nouveau format de fichier

1. Ajouter une fonction `read_xyz_file(filepath: str) -> str` dans `core.py`
2. L'appeler dans le pipeline de `concat_files` pour l'extension concernée
3. Retirer l'extension de `exclude_content_extensions` dans `create_default_config` si elle y était
4. Ajouter les tests unitaires dans `tests/unit/test_core_readers.py`
5. Mettre à jour les golden files si nécessaire (`make update-snapshots`)
6. Documenter dans [Format de sortie](../user-guide/output-format.md#formats-de-fichiers-lus)

---

## Workflow PR

1. Créer une branche depuis `main` : `git checkout -b feat/ma-feature`
2. Développer, tester localement (`make test-cov`)
3. Ouvrir une PR sur `main`
4. Le CI (`ci.yml`) doit passer : lint + tests + build docs

