#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion de la configuration pour gentxt
"""

import os
import json
from typing import Optional

# ============================================
# CONSTANTES
# ============================================

CONFIG_FILENAME = ".concat_config.json"

# Extensions pour lesquelles on n'insère pas le contenu dans l'arborescence
DEFAULT_EXCLUDE_CONTENT_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".db", ".sqlite",
    ".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".pyc", ".pyo", ".class", ".o", ".a", ".lib",
    ".ttf", ".otf", ".woff", ".woff2", ".eot"
}

# Extensions à exclure de l'arborescence
DEFAULT_EXCLUDE_TREE_EXTENSIONS = set()

# Dossiers à exclure de l'arborescence
DEFAULT_EXCLUDE_TREE_DIRS = {
    "__pycache__", ".git", ".svn", "node_modules", ".vscode", ".idea",
    "venv", "env", ".venv", ".env", "dist", "build"
}

# Fichiers à exclure de l'arborescence
DEFAULT_EXCLUDE_TREE_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini", ".gitignore", ".gitattributes",
    CONFIG_FILENAME
}

# Dossiers à exclure du contenu
DEFAULT_EXCLUDE_CONTENT_DIRS = {
    "__pycache__", ".git", ".svn", "node_modules", ".vscode", ".idea",
    "venv", "env", ".venv", ".env", "dist", "build"
}

# Fichiers à exclure du contenu
DEFAULT_EXCLUDE_CONTENT_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini", ".gitignore", ".gitattributes",
    CONFIG_FILENAME
}


# ============================================
# FONCTIONS
# ============================================

def create_default_config() -> dict[str, set[str]]:
    """Retourne un dictionnaire avec la configuration par défaut."""
    return {
        "exclude_tree_dirs": DEFAULT_EXCLUDE_TREE_DIRS,
        "exclude_tree_files": DEFAULT_EXCLUDE_TREE_FILES,
        "exclude_tree_extensions": DEFAULT_EXCLUDE_TREE_EXTENSIONS,
        "exclude_content_dirs": DEFAULT_EXCLUDE_CONTENT_DIRS,
        "exclude_content_files": DEFAULT_EXCLUDE_CONTENT_FILES,
        "exclude_content_extensions": DEFAULT_EXCLUDE_CONTENT_EXTENSIONS,
    }


def load_config(directory: str) -> Optional[dict[str, set[str]]]:
    """
    Charge la configuration depuis le fichier .concat_config.json du répertoire.
    Retourne un dictionnaire de sets pour les exclusions, ou None en cas d'erreur.
    """
    config_path = os.path.join(directory, CONFIG_FILENAME)
    if not os.path.isfile(config_path):
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            return None
        
        config = {}
        for key in create_default_config().keys():
            value = data.get(key, [])
            if not isinstance(value, list):
                value = []
            config[key] = set(value)
        
        return config
    
    except (json.JSONDecodeError, IOError):
        return None


def save_config(directory: str, config: dict[str, set[str]], headless_mode: bool = False) -> bool:
    """
    Sauvegarde la configuration dans le fichier .concat_config.json.
    config doit être un dictionnaire contenant des sets.
    Retourne True en cas de succès, False en cas d'échec.
    """
    config_path = os.path.join(directory, CONFIG_FILENAME)
    
    try:
        data_to_write = {}
        for key, value in config.items():
            if isinstance(value, set):
                data_to_write[key] = sorted(list(value))
            elif isinstance(value, list):
                data_to_write[key] = sorted(value)
            else:
                data_to_write[key] = value
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_write, f, indent=4, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        if not headless_mode:
            print(f"Erreur lors de la sauvegarde de la configuration : {e}")
        return False


def get_effective_config(directory: str, headless_mode: bool = False) -> dict[str, set[str]]:
    """
    Retourne la configuration effective : celle du fichier ou la configuration par défaut.
    """
    loaded_config = load_config(directory)
    
    if loaded_config:
        if not headless_mode:
            print(f"Configuration chargée depuis {os.path.join(directory, CONFIG_FILENAME)}")
        return loaded_config
    else:
        if not headless_mode:
            print("Aucune configuration trouvée ou invalide. Utilisation de la configuration par défaut.")
        return create_default_config()