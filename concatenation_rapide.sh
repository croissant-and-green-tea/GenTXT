#!/bin/bash
# Script de concaténation rapide pour Linux
# Version 2.4.0

# Lance GenTxt en mode headless (sans interface graphique)
# Gère les deux noms possibles de l'exécutable
if [ -f "./gentxt" ]; then
    ./gentxt --headless
elif [ -f "./GenTxt" ]; then
    ./GenTxt --headless
else
    echo "ERREUR : Exécutable gentxt/GenTxt introuvable dans le répertoire courant"
    exit 1
fi

# Pause pour que l'utilisateur puisse lire les messages
read -p "Appuyez sur Entrée pour fermer..."