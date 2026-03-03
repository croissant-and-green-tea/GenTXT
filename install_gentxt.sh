#!/bin/bash

# ============================================
# Script d'installation de GenTxt pour Linux
# Version 2.4.0
# ============================================

INSTALL_DIR="/opt/gentxt"
DESKTOP_FILE_DEST="$HOME/.local/share/applications/gentxt.desktop"
DESKTOP_FILE_SOURCE="gentxt.desktop"

VERSION=$(python3 -c "from gentxt.__version__ import __version__; print(__version__)" 2>/dev/null || echo "inconnue")
echo "=== Installation de GenTxt v${VERSION} ==="

# Vérification : le fichier .desktop existe-t-il dans le projet ?
if [ ! -f "$DESKTOP_FILE_SOURCE" ]; then
    echo "ERREUR : Le fichier gentxt.desktop est introuvable dans la racine du projet."
    echo "Assurez-vous d'exécuter ce script depuis la racine du projet GenTxt."
    exit 1
fi

# Vérification : l'exécutable a-t-il été compilé ?
if [ ! -f "dist/gentxt" ] && [ ! -f "dist/GenTxt" ]; then
    echo "ERREUR : Aucun exécutable trouvé dans dist/"
    echo "Exécutez d'abord : pyinstaller GenTxt.spec"
    exit 1
fi

# Déterminer le nom exact de l'exécutable
if [ -f "dist/gentxt" ]; then
    EXEC_SOURCE="dist/gentxt"
else
    EXEC_SOURCE="dist/GenTxt"
fi

# Création du répertoire d'installation
echo "→ Création du répertoire d'installation..."
sudo mkdir -p "$INSTALL_DIR"

# Copie de l'exécutable, de l'icône et du script headless
echo "→ Copie de l'exécutable et de l'icône..."
sudo cp "$EXEC_SOURCE" "$INSTALL_DIR/gentxt"
sudo chmod +x "$INSTALL_DIR/gentxt"
sudo cp "src/icons/icons.png" "$INSTALL_DIR/icons.png"
sudo cp "concatenation_rapide.sh" "$INSTALL_DIR/concatenation_rapide.sh"
sudo chmod +x "$INSTALL_DIR/concatenation_rapide.sh"

# Installation des icônes système
echo "→ Installation des icônes..."
mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$HOME/.local/share/icons/hicolor/48x48/apps"
cp "src/icons/icons.png" "$HOME/.local/share/icons/hicolor/256x256/apps/gentxt.png"
cp "src/icons/icons.png" "$HOME/.local/share/icons/hicolor/48x48/apps/gentxt.png"

# Installation du fichier .desktop
echo "→ Installation du raccourci bureau..."
mkdir -p "$HOME/.local/share/applications"
cp "$DESKTOP_FILE_SOURCE" "$DESKTOP_FILE_DEST"

# Rafraîchissement des caches
echo "→ Rafraîchissement des caches..."
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo ""
echo "=== Installation terminée avec succès ! ==="
echo ""
echo "GenTxt v${VERSION} est maintenant installé dans : $INSTALL_DIR"
echo "L'icône est installée dans : ~/.local/share/icons/hicolor/"
echo "L'application apparaît dans votre menu d'applications"
echo ""
echo "Pour l'épingler au dock :"
echo "  1. Ouvrez le menu d'applications"
echo "  2. Cherchez 'GenTxt'"
echo "  3. Lancez l'application"
echo "  4. Clic droit sur l'icône dans le dock → 'Épingler' ou 'Ajouter aux favoris'"
echo ""
echo "Note: Si l'icône n'apparaît pas immédiatement, déconnectez-vous et reconnectez-vous."
echo ""