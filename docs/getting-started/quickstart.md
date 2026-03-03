

# Démarrage rapide

## Mode GUI

1. Lancer GenTXT (`python src/main.py` ou exécutable)
2. Cliquer **Démarrer**
3. Naviguer jusqu'au dossier à concaténer, valider
4. Le fichier `gentxt.txt` est généré dans ce dossier

Pour choisir un emplacement de sortie différent, utiliser **Démarrer - Choisir destination** à la place.

---

## Mode headless

Depuis n'importe quel dossier :

```bash
cd /chemin/vers/mon_projet
python /chemin/vers/GenTXT/src/main.py --headless
```

Ou avec le script fourni (Linux) :

```bash
cp /opt/gentxt/concatenation_rapide.sh /chemin/vers/mon_projet/
cd /chemin/vers/mon_projet
./concatenation_rapide.sh
```

Le fichier `gentxt.txt` est créé dans le répertoire courant.

!!! warning "En cas d'erreur"
    Si la génération échoue, un fichier `gentxt_headless_error.log` est créé dans le même dossier avec le détail de l'erreur.

---

## Résultat attendu

```text
# === Arborescence du dossier ===

mon_projet/
├── src/
│   └── main.py
├── README.md
└── .concat_config.json    ← exclu du contenu par défaut

# === Contenu des fichiers ===

--- Fichier : README.md ---
# Mon projet
...

--- Fichier : src/main.py ---
print("hello")
```

Les fichiers binaires (`.exe`, `.jpg`, `.zip`…) et les dossiers système (`__pycache__`, `.git`, `venv`…) sont exclus par défaut. Voir [Configuration](configuration.md) pour adapter ces règles.

