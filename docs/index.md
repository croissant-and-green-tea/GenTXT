

# gentxt

**gentxt** concatène l'arborescence et le contenu d'un dossier en un unique fichier texte.
Cas d'usage principal : préparer un contexte projet complet à fournir à un LLM en une seule opération.

---

## Fonctionnalités

- **Mode GUI** — interface PySide6, sélection de dossier avec barre d'adresse éditable
- **Mode headless** — invocation CLI (`--headless`), intégrable dans scripts et pipelines CI/CD
- **Configuration par projet** — fichier `.concat_config.json` pour contrôler finement les exclusions
- **Lecture de formats riches** — `.odt` (odfpy) et `.ods` (pyexcel-ods3) en plus des fichiers texte
- **Post-traitement automatique** — réduction des blocs de lignes vides excessifs (6+ → 3)
- **Multiplateforme** — Linux et Windows, exécutable standalone via PyInstaller

## Structure du fichier produit

```text
# === Arborescence du dossier ===
mon_projet/
├── src/
│   └── main.py
└── README.md

# === Contenu des fichiers ===

--- Fichier : README.md ---
...

--- Fichier : src/main.py ---
...
```

## Liens rapides

| | |
|---|---|
| [Installation](getting-started/installation.md) | Installer gentxt depuis les sources ou en exécutable |
| [Démarrage rapide](getting-started/quickstart.md) | Générer votre premier fichier en 2 minutes |
| [Configuration](getting-started/configuration.md) | Contrôler les exclusions par projet |
| [Référence API](reference/api/core.md) | Documentation des modules Python |
| [Changelog](changelog.md) | Historique des versions |

## Licence

MIT — voir [LICENCE](https://github.com/croissant-and-green-tea/gentxt/LICENCE).