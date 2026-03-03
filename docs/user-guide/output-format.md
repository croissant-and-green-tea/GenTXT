

# Format de sortie

## Fichier produit

Le fichier de sortie s'appelle toujours **`gentxt.txt`**, qu'il soit généré en mode GUI (destination automatique) ou headless.

---

## Structure

Le fichier est composé de deux sections séparées par une ligne vide.

### Section arborescence

```text
# === Arborescence du dossier ===

nom_du_dossier/
├── sous_dossier/
│   ├── fichier_a.py
│   └── fichier_b.txt
├── README.md
└── main.py
```

Les dossiers et fichiers correspondant aux règles `exclude_tree_*` de la configuration sont omis de cette section.

### Section contenu

```text
# === Contenu des fichiers ===

--- Fichier : README.md ---
# Mon projet
...

--- Fichier : sous_dossier/fichier_a.py ---
def hello():
    pass
```

Chaque fichier est précédé de `--- Fichier : <chemin_relatif> ---`. Le chemin est relatif au dossier source.

---

## Formats de fichiers lus

| Extension | Traitement |
|---|---|
| Tout fichier texte (`.py`, `.md`, `.txt`, `.json`, `.yaml`…) | Lu directement en UTF-8 avec fallback latin-1 |
| `.odt` | Extraction texte paragraphe par paragraphe via `odfpy` |
| `.ods` | Extraction feuille par feuille via `pyexcel-ods3`, format tabulaire |
| Fichier binaire détecté | Ignoré (pas de section contenu générée) |
| Extension dans `exclude_content_extensions` | Ignoré |

### Détection binaire

Un fichier est considéré binaire si :

- il contient des octets nuls (`\x00`), **ou**
- plus de 30 % des 8 192 premiers octets ne sont pas des caractères texte, **ou**
- il est vide, **ou**
- il est illisible (permissions, OSError)

### Lecture ODS

```text
=== Feuille: Sheet1 ===

colonne_a    colonne_b    colonne_c
valeur1      valeur2      valeur3
```

### Lecture ODT

Chaque paragraphe est extrait et concaténé avec un saut de ligne. Les métadonnées et styles sont ignorés.

---

## Post-traitement

Après génération, les blocs de 6 sauts de ligne consécutifs ou plus sont réduits à 3. Les blocs de 5 ou moins sont conservés tels quels.

```
Avant : "A\n\n\n\n\n\n\n\nB"   (8 \n)
Après : "A\n\n\nB"             (3 \n)
```

---

## Encodage

Le fichier de sortie est écrit en **UTF-8**. Les fichiers source encodés en latin-1 sont lus avec un fallback automatique si la lecture UTF-8 échoue.

