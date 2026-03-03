

# Mode headless

## Cas d'usage

- Intégration dans un script shell ou Makefile
- Pipeline CI/CD (GitHub Actions, GitLab CI…)
- Raccourci de bureau ou clic-droit contextuel sous Linux

---

## Invocation

```bash
python src/main.py --headless
# ou
python src/main.py --auto
```

Les deux flags sont équivalents. L'application traite le **répertoire de travail courant** (`os.getcwd()`) et écrit `gentxt.txt` dans ce même répertoire.

Avec l'exécutable :

```bash
cd /chemin/vers/mon_projet
/opt/gentxt/gentxt --headless
```

---

## Script `concatenation_rapide.sh`

Script fourni dans le dépôt pour usage Linux. Copier dans le dossier à traiter :

```bash
cp /opt/gentxt/concatenation_rapide.sh ./
chmod +x concatenation_rapide.sh
./concatenation_rapide.sh
```

Le script gère les deux noms d'exécutables possibles (`gentxt` et `GenTxt`) et s'arrête avec un message explicite si aucun n'est trouvé.

---

## Cible Makefile

```bash
make headless   # équivalent à : python src/main.py --headless
```

---

## Intégration GitHub Actions

```yaml
# .github/workflows/generate-context.yml
- name: Generate gentxt context
  run: |
    cd ${{ github.workspace }}
    python src/main.py --headless
  working-directory: mon_sous_dossier   # optionnel
```

---

## Log d'erreur

En cas d'échec, `gentxt_headless_error.log` est créé dans le répertoire courant.

```text
gentxt ERREUR: Une erreur est survenue lors de la concaténation headless:
<traceback>
Répertoire source tenté: /chemin/source
Fichier de sortie tenté: /chemin/source/gentxt.txt
```

Ce fichier est supprimé au début de chaque exécution headless, si il existe.
Si le log lui-même ne peut pas être écrit (permissions), un message ERREUR CRITIQUE est affiché en stdout uniquement.

---

## Comportement sans GUI

Le module `headless.py` n'importe aucune dépendance PySide6. Il est utilisable dans un environnement sans serveur d'affichage (serveur CI, container Docker sans X11).

