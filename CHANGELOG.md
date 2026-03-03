# Changelog

## [2.4.1] -2025-03-02

Ajouté 
- documentation
- tests
- makefile
- ci cd github page avec tests et mkdocs automatique 

## [2.4.0] - 2025-02-16

### Ajouté
- **Dialogues de sélection personnalisés avec barre d'adresse éditable**
  - Remplacement des dialogues natifs par des dialogues Qt personnalisés
  - Barre d'adresse toujours visible et éditable (copier-coller, modification directe)
  - Navigation par double-clic dans les dossiers
  - Bouton "Dossier parent" pour remonter dans l'arborescence
  - Touche Entrée pour naviguer (ne valide plus automatiquement)
  - Affichage des fichiers et dossiers avec icônes (📁 📄)
  
- **Deux modes de démarrage distincts**
  - "Démarrer" : Enregistrement automatique dans le dossier source sous le nom `gentxt.txt`
  - "Démarrer - Choisir destination" : Dialogue complet pour choisir l'emplacement et le nom

- **Interface de configuration simplifiée**
  - Format texte simple sans syntaxe JSON
  - Une ligne par élément, sans guillemets ni virgules
  - Format : `# section_name` suivi des éléments ligne par ligne
  - Plus besoin de gérer l'indentation, les accolades ou la ponctuation JSON

- **Post-traitement automatique du fichier généré**
  - Réduction des passages à la ligne excessifs (5+ lignes vides → 2 lignes vides)
  - Améliore la lisibilité du fichier `gentxt.txt`

- **Refactorisation complète du code**
  - Structure modulaire avec package `gentxt/`
  - Séparation des responsabilités :
    - `config.py` : Gestion de la configuration
    - `core.py` : Logique de concaténation
    - `dialogs.py` : Interfaces graphiques
    - `main.py` : Point d'entrée (réduit de 945 à 185 lignes)
  - Dossier `assets/icons/` pour les ressources graphiques
  - Meilleure maintenabilité et testabilité

### Modifié
- **Configuration par défaut minimale**
  - Plus d'exclusions par défaut sauf `.concat_config.json` et `gentxt.txt`
  - Listes `exclude_tree_dirs`, `exclude_tree_extensions`, `exclude_content_dirs`, `exclude_content_extensions` vides par défaut
  - L'utilisateur contrôle entièrement ce qui est exclu

- **Nom du fichier de sortie standardisé**
  - Toujours `gentxt.txt` (au lieu de `nom_dossier_gentxt.txt`)
  - Cohérence dans tous les modes (GUI et headless)

- **Taille de police augmentée globalement**
  - Passage de 9-10pt (défaut système) à 12pt
  - Meilleure lisibilité dans toute l'application

- **Ordre des boutons dans l'interface principale**
  - "Démarrer" en premier (usage le plus fréquent)
  - "Démarrer - Choisir destination" en second
  - "Créer / Modifier Configuration" en troisième
  - "Quitter" en dernier

### Corrigé
- **Arborescence incomplète et dysfonctionnelle**
  - Les dossiers imbriqués s'affichent maintenant correctement
  - Correction de la logique récursive dans `generate_tree()`
  - Tous les niveaux de dossiers sont visibles avec la bonne indentation

- **Validation intempestive avec la touche Entrée**
  - La touche Entrée dans les dialogues navigue au lieu de valider
  - Seul le bouton "OK" valide la sélection
  - Interception des événements clavier via `keyPressEvent()`

### Technique
- Migration de fichier unique (945 lignes) vers architecture modulaire (4 fichiers)
- Utilisation de regex pour le post-traitement (`re.sub()`)
- Import relatif du package : `from gentxt.core import concat_files`
- Structure compatible avec PyInstaller pour compilation en exécutable  

## [2.3.0] - 2025-02-13

### Ajouté
- **Support Linux complet** : GenTxt fonctionne maintenant nativement sur Linux
- Script d'installation automatique `install_gentxt.sh` pour Linux
- Fichier `.desktop` pour intégration au menu d'applications et au dock Linux
- Script shell `concat_ici.sh` pour mode headless sur Linux (équivalent du `.bat` Windows)
- Documentation Linux complète `README_LINUX.md`
- Détection automatique du nom d'exécutable (GenTXT/GenTxt) dans les scripts

### Modifié
- **Migration de Tkinter vers PySide6** : Interface graphique modernisée
  - Sélecteur de fichiers moderne avec support natif du copier-coller
  - Support du Ctrl+A pour sélectionner/supprimer les chemins
  - Autocomplétion et navigation clavier améliorées
  - Look & feel natif automatique selon l'OS (Windows/Linux/macOS)
  - Performance et réactivité améliorées
- `GenTxt.spec` : Chemins adaptés pour compatibilité multiplateforme + support PySide6
- `requirements.txt` : Ajout de PySide6, remplacement de tkinter
- Structure du projet pour supporter Windows et Linux simultanément

### Technique
- Exécutable Linux généré : `dist/GenTXT` (sans extension)
- Installation par défaut : `/opt/gentxt/` (Linux) ou portable (Windows)
- Fichier `.desktop` : `~/.local/share/applications/gentxt.desktop` (Linux)
- Logique métier (concaténation, configuration JSON, mode headless) **inchangée**
- Taille exécutable : +20-30 MB due aux bibliothèques Qt (compensé par meilleure UX)

### Notes
- L'icône `.ico` génère un warning sur Linux (normal, format non supporté)
- Le icons PNG est utilisé pour l'affichage système sur Linux
- PySide6 nécessite Python 3.7+ minimum
- L'interface PySide6 est identique visuellement à Tkinter mais plus moderne et portable

## [2.2.0] - 2025-02-08

### Added

*   **Prise en charge de la lecture des fichiers ODT (OpenDocument Text)**
    *   Intégration de la bibliothèque `odfpy` pour extraire le contenu textuel des fichiers `.odt`.
    *   Le texte de chaque paragraphe du fichier ODT est extrait et inclus dans le fichier de sortie.
    *   Le programme affiche un message d'erreur informatif si un fichier `.odt` est rencontré mais que la bibliothèque requise n'est pas installée.
    *   La nouvelle dépendance a été ajoutée au fichier `requirements.txt`.

### Changed

*   **Configuration par défaut**
    *   L'extension `.odt` a été **retirée** de la liste d'exclusion par défaut (`DEFAULT_EXCLUDE_CONTENT_EXTENSIONS`).
    *   Les fichiers `.odt` sont maintenant traités par défaut et leur contenu textuel est extrait automatiquement.



## [2.1.1] - 2025-10-16 

Modification du .concat_config.json 

## [2.1.0] - 2025-04-21

*   **Prise en charge de la lecture des fichiers ODS (OpenDocument Spreadsheet)**
    *   Intégration de la bibliothèque `pyexcel-ods3` pour extraire les données des fichiers `.ods`.
    *   Le contenu de chaque feuille du fichier ODS est maintenant formaté et inclus dans le fichier de sortie, avec des en-têtes clairs pour identifier chaque feuille.
    *   Le programme affiche un message d'erreur informatif si un fichier `.ods` est rencontré mais que la bibliothèque requise n'est pas installée.
    *   La nouvelle dépendance a été ajoutée au fichier `requirements.txt`.

*   **Gestion des ressources**
    *   Ajout d'une nouvelle icône (`icons_v2.png`) dans le dossier `src`.

### Changed

*   **Configuration par défaut**
    *   Les extensions `.ods` et `.odt` ont été ajoutées à la liste d'exclusion par défaut pour le contenu (`DEFAULT_EXCLUDE_CONTENT_EXTENSIONS`).
    *   **Note :** Pour activer la lecture des fichiers `.ods`, l'utilisateur doit manuellement retirer l'extension `".ods"` de la liste `exclude_content_extensions` dans son fichier de configuration `.concat_config.json`.

## [1.0.0] - avant 2025-04-21

Il s'agit de la version initiale de GenTXT.

### Added

*   **Moteur de Concaténation Principal**
    *   Génération d'une arborescence textuelle du répertoire source.
    *   Concaténation du contenu des fichiers texte dans un unique fichier de sortie.
    *   Détection basique des fichiers binaires pour éviter d'inclure leur contenu.
    *   Gestion des erreurs d'encodage lors de la lecture des fichiers (UTF-8 par défaut).

*   **Système de Configuration**
    *   Introduction du fichier de configuration `.concat_config.json` à la racine du dossier source.
    *   Support pour six types d'exclusions :
        *   `exclude_tree_dirs`, `exclude_tree_files`, `exclude_tree_extensions` pour l'arborescence.
        *   `exclude_content_dirs`, `exclude_content_files`, `exclude_content_extensions` pour le contenu.
    *   Application de filtres d'exclusion par défaut si le fichier de configuration est absent ou invalide.

*   **Mode GUI (Interface Graphique)**
    *   Interface utilisateur simple construite avec Tkinter.
    *   Fenêtre principale avec trois options : "Démarrer", "Configurer" et "Quitter".
    *   Boîtes de dialogue natives pour la sélection du dossier source et du fichier de destination.
    *   Éditeur de configuration intégré pour créer ou modifier le fichier `.concat_config.json` directement depuis l'application.
    *   Affichage de messages de succès ou d'erreur à la fin du processus.

*   **Mode Headless (Ligne de Commande)**
    *   Activation via l'argument de ligne de commande `--headless` ou `--auto`.
    *   Le mode headless traite automatiquement le répertoire de travail courant.
    *   Génération automatique du nom du fichier de sortie (ex: `nom_du_dossier_gentxt.txt`).
    *   Script `concat_ici.bat` fourni pour un lancement rapide sous Windows.
    *   Création d'un fichier de log `gentxt_headless_error.log` en cas d'échec critique.

*   **Packaging et Distribution**
    *   Configuration via `GenTxt.spec` pour compiler le projet en un seul exécutable `.exe` avec PyInstaller.
    *   Inclusion d'une icône personnalisée (`icons.ico`) pour l'exécutable.
    *   Le mode console est désactivé pour l'exécution en mode GUI.

*   **Documentation**
    *   Création du fichier `README.md` initial détaillant toutes les fonctionnalités et les modes d'utilisation.