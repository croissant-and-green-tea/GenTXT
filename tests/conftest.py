#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixtures partagées entre tous les tests.
Fournit des dossiers temporaires, des configs types et des fichiers de test.
"""

import pytest
import os
import json


# === Fixtures : dossiers temporaires ==========================================

@pytest.fixture
def tmp_source_dir(tmp_path):
    """Dossier source vide prêt à l'emploi."""
    source = tmp_path / "source"
    source.mkdir()
    return source


@pytest.fixture
def tmp_output_file(tmp_path):
    """Chemin de fichier de sortie dans un dossier temporaire."""
    return tmp_path / "gentxt.txt"


# === Fixtures : structures de dossiers ========================================

@pytest.fixture
def simple_project(tmp_source_dir):
    """
    Projet minimal :
    source/
    ├== README.md
    ├== main.py
    └== data/
        └== notes.txt
    """
    (tmp_source_dir / "README.md").write_text("# Readme\n", encoding="utf-8")
    (tmp_source_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
    data_dir = tmp_source_dir / "data"
    data_dir.mkdir()
    (data_dir / "notes.txt").write_text("some notes\n", encoding="utf-8")
    return tmp_source_dir


@pytest.fixture
def project_with_binary(tmp_source_dir):
    """Projet contenant un fichier binaire (octets nuls)."""
    (tmp_source_dir / "script.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_source_dir / "binary.bin").write_bytes(b"\x00\x01\x02\x03" * 100)
    return tmp_source_dir


@pytest.fixture
def project_with_excluded_dirs(tmp_source_dir):
    """
    Projet avec des dossiers qui doivent être exclus par défaut
    (__pycache__, .git, node_modules).
    """
    (tmp_source_dir / "app.py").write_text("# app\n", encoding="utf-8")
    for excluded in ["__pycache__", ".git", "node_modules"]:
        d = tmp_source_dir / excluded
        d.mkdir()
        (d / "file.txt").write_text("should be excluded\n", encoding="utf-8")
    return tmp_source_dir


@pytest.fixture
def project_with_ods(tmp_source_dir):
    """Projet contenant le fichier ODS de test."""
    # Copie le fichier ODS depuis test_mano/
    import shutil
    ods_src = os.path.join(
        os.path.dirname(__file__), "..", "test_mano", "fichier_ods_deux_pages.ods"
    )
    if os.path.exists(ods_src):
        shutil.copy(ods_src, tmp_source_dir / "table.ods")
    return tmp_source_dir


@pytest.fixture
def project_with_odt(tmp_source_dir):
    """Projet contenant le fichier ODT de test."""
    import shutil
    odt_src = os.path.join(
        os.path.dirname(__file__), "..", "test_mano", "fichier_odt.odt"
    )
    if os.path.exists(odt_src):
        shutil.copy(odt_src, tmp_source_dir / "doc.odt")
    return tmp_source_dir


# === Fixtures : configurations ================================================

@pytest.fixture
def minimal_config():
    """Config minimale : toutes les listes vides sauf exclusion de gentxt.txt."""
    return {
        "exclude_tree_dirs": set(),
        "exclude_tree_files": {".concat_config.json", "gentxt.txt"},
        "exclude_tree_extensions": set(),
        "exclude_content_dirs": set(),
        "exclude_content_files": {".concat_config.json", "gentxt.txt"},
        "exclude_content_extensions": set(),
    }


@pytest.fixture
def config_with_exclusions():
    """Config avec des exclusions non triviales pour les tests d'intégration."""
    return {
        "exclude_tree_dirs": {"excluded_dir"},
        "exclude_tree_files": {"secret.txt"},
        "exclude_tree_extensions": {".log"},
        "exclude_content_dirs": {"excluded_dir"},
        "exclude_content_files": {"secret.txt"},
        "exclude_content_extensions": {".log", ".tmp"},
    }


@pytest.fixture
def write_config(tmp_source_dir):
    """
    Factory : écrit un .concat_config.json dans tmp_source_dir.
    Usage : write_config({"exclude_tree_dirs": ["foo"]})
    """
    def _write(config_dict):
        config_path = tmp_source_dir / ".concat_config.json"
        # Convertir les sets en listes pour la sérialisation JSON
        serializable = {
            k: sorted(list(v)) if isinstance(v, set) else v
            for k, v in config_dict.items()
        }
        config_path.write_text(json.dumps(serializable, indent=4), encoding="utf-8")
        return config_path
    return _write


# === Fixtures : fichiers spéciaux =============================================

@pytest.fixture
def binary_file(tmp_path):
    """Fichier binaire avec octets nuls."""
    f = tmp_path / "binary.bin"
    f.write_bytes(b"\x00\x01\x02\x03" * 256)
    return f


@pytest.fixture
def utf8_file(tmp_path):
    """Fichier texte UTF-8 avec contenu simple."""
    f = tmp_path / "utf8.txt"
    f.write_text("Contenu UTF-8 : éàü\n", encoding="utf-8")
    return f


@pytest.fixture
def latin1_file(tmp_path):
    """Fichier texte encodé en latin-1."""
    f = tmp_path / "latin1.txt"
    f.write_bytes("Contenu latin-1 : \xe9\xe0\xfc\n".encode("latin-1"))
    return f