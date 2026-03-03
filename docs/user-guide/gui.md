

# Interface graphique

## Lancement

=== "Depuis les sources"

    ```bash
    python src/main.py
    ```

=== "Exécutable"

    ```bash
    ./gentxt          # Linux
    gentxt.exe        # Windows
    ```

---

## Fenêtre principale

La fenêtre présente quatre boutons dans l'ordre d'usage décroissant :

| Bouton | Comportement |
|---|---|
| **Démarrer** | Ouvre un sélecteur de dossier source. Le fichier de sortie est automatiquement nommé `gentxt.txt` dans ce même dossier. |
| **Démarrer - Choisir destination** | Idem, puis ouvre un second dialogue pour choisir le nom et l'emplacement du fichier de sortie. |
| **Créer / Modifier Configuration** | Ouvre un sélecteur de dossier, puis l'éditeur de configuration pour ce dossier. |
| **Quitter** | Ferme l'application. |

---

## Dialogue de sélection de dossier

Le dialogue est personnalisé (pas un dialogue natif OS) et expose :

- **Barre d'adresse éditable** — copier-coller un chemin directement, modifier manuellement, naviguer avec Entrée
- **Double-clic** — entre dans un sous-dossier
- **Bouton Dossier parent** — remonte d'un niveau
- **Touche Entrée** — navigue vers le chemin tapé, ne valide **pas** la sélection
- **Bouton OK** — seul moyen de valider

!!! warning "Touche Entrée"
    Appuyer sur Entrée dans la barre d'adresse navigue vers le chemin — il ne valide pas le dialogue. Utiliser le bouton OK pour confirmer.

---

## Éditeur de configuration

L'éditeur affiche le contenu de `.concat_config.json` dans un format texte simplifié (voir [Configuration](../getting-started/configuration.md#format-texte-simplifié-éditeur-intégré)).

- Si aucun fichier de config n'existe pour ce dossier, l'éditeur propose de créer une config par défaut.
- Le bouton **Enregistrer** convertit le texte en JSON et écrit `.concat_config.json`.
- En cas de syntaxe invalide, une erreur est affichée et rien n'est écrit sur disque.

---

## Messages d'erreur courants

| Message | Cause | Résolution |
|---|---|---|
| `Dossier invalide.` | Le chemin sélectionné n'est pas un dossier accessible | Vérifier le chemin dans la barre d'adresse |
| `Erreur lors de la concaténation : ...` | Exception dans `concat_files` | Voir le détail dans le message, vérifier les permissions |
| `Erreur lors de la sauvegarde: ...` | Impossible d'écrire `.concat_config.json` | Vérifier les permissions en écriture sur le dossier |

