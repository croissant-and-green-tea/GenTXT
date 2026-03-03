#!/bin/bash

# ============================================
# Script de désinstallation de GenTxt
# ============================================

echo "=== Désinstallation de GenTxt ==="

# Supprimer l'application
echo "→ Suppression de l'application..."
sudo rm -rf /opt/gentxt

# Supprimer le raccourci
echo "→ Suppression du raccourci..."
rm -f "$HOME/.local/share/applications/gentxt.desktop"

# Supprimer les icônes
echo "→ Suppression des icônes..."
rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/gentxt.png"
rm -f "$HOME/.local/share/icons/hicolor/48x48/apps/gentxt.png"

# Rafraîchir les caches
echo "→ Rafraîchissement des caches..."
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo ""
echo "=== Désinstallation terminée ==="
echo "GenTxt a été complètement supprimé de votre système."
echo ""