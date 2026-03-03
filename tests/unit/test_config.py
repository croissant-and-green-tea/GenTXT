#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour gentxt/config.py.
"""

import json
import os
import stat

import pytest

from gentxt.config import (
    CONFIG_FILENAME,
    create_default_config,
    get_effective_config,
    load_config,
    save_config,
)


# === create_default_config ====================================================

class TestCreateDefaultConfig:

    def test_returns_all_six_keys(self):
        config = create_default_config()
        expected_keys = {
            "exclude_tree_dirs",
            "exclude_tree_files",
            "exclude_tree_extensions",
            "exclude_content_dirs",
            "exclude_content_files",
            "exclude_content_extensions",
        }
        assert set(config.keys()) == expected_keys

    def test_values_are_sets(self):
        config = create_default_config()
        for key, value in config.items():
            assert isinstance(value, set), f"{key} devrait être un set, got {type(value)}"

    def test_default_excludes_content_extensions_not_empty(self):
        config = create_default_config()
        # Les extensions binaires connues doivent être présentes par défaut
        assert len(config["exclude_content_extensions"]) > 0

    def test_default_excludes_tree_dirs_not_empty(self):
        config = create_default_config()
        assert len(config["exclude_tree_dirs"]) > 0

    def test_config_filename_excluded_from_tree_files(self):
        config = create_default_config()
        assert CONFIG_FILENAME in config["exclude_tree_files"]

    def test_config_filename_excluded_from_content_files(self):
        config = create_default_config()
        assert CONFIG_FILENAME in config["exclude_content_files"]

    def test_common_binary_extensions_excluded_from_content(self):
        config = create_default_config()
        for ext in [".exe", ".dll", ".jpg", ".png", ".zip", ".pdf"]:
            assert ext in config["exclude_content_extensions"], f"{ext} devrait être exclu par défaut"

    def test_common_dirs_excluded_from_tree(self):
        config = create_default_config()
        for d in ["__pycache__", ".git", "node_modules", "venv"]:
            assert d in config["exclude_tree_dirs"], f"{d} devrait être exclu par défaut"


# === load_config ==============================================================

class TestLoadConfig:

    def test_returns_none_if_file_absent(self, tmp_path):
        result = load_config(str(tmp_path))
        assert result is None

    def test_returns_none_if_json_malformed(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        config_path.write_text("{ pas du json valide ::::", encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is None

    def test_returns_none_if_root_is_not_dict(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        config_path.write_text(json.dumps(["liste", "pas", "un", "dict"]), encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is None

    def test_returns_sets_for_each_key(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        data = {"exclude_tree_dirs": ["__pycache__"], "exclude_tree_files": []}
        config_path.write_text(json.dumps(data), encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is not None
        for value in result.values():
            assert isinstance(value, set)

    def test_missing_keys_filled_with_empty_sets(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        # On n'écrit qu'une seule clé sur 6
        config_path.write_text(json.dumps({"exclude_tree_dirs": ["foo"]}), encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is not None
        expected_keys = set(create_default_config().keys())
        assert set(result.keys()) == expected_keys
        # Les clés absentes sont des sets vides
        assert result["exclude_tree_files"] == set()
        assert result["exclude_content_dirs"] == set()

    def test_loads_values_correctly(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        data = {
            "exclude_tree_dirs": ["__pycache__", ".git"],
            "exclude_tree_files": [".DS_Store"],
            "exclude_tree_extensions": [".pyc"],
            "exclude_content_dirs": ["venv"],
            "exclude_content_files": [],
            "exclude_content_extensions": [".exe", ".dll"],
        }
        config_path.write_text(json.dumps(data), encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is not None
        assert result["exclude_tree_dirs"] == {"__pycache__", ".git"}
        assert result["exclude_tree_files"] == {".DS_Store"}
        assert result["exclude_tree_extensions"] == {".pyc"}
        assert result["exclude_content_dirs"] == {"venv"}
        assert result["exclude_content_files"] == set()
        assert result["exclude_content_extensions"] == {".exe", ".dll"}

    def test_handles_extra_keys_gracefully(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        data = {
            "exclude_tree_dirs": ["foo"],
            "cle_inconnue_xyz": ["bar"],  # clé non reconnue
        }
        config_path.write_text(json.dumps(data), encoding="utf-8")
        # Ne doit pas lever d'exception
        result = load_config(str(tmp_path))
        assert result is not None
        # La clé inconnue n'est pas dans le résultat
        assert "cle_inconnue_xyz" not in result

    def test_non_list_value_treated_as_empty(self, tmp_path):
        """Une valeur qui n'est pas une liste est traitée comme liste vide."""
        config_path = tmp_path / CONFIG_FILENAME
        data = {"exclude_tree_dirs": "pas_une_liste"}
        config_path.write_text(json.dumps(data), encoding="utf-8")
        result = load_config(str(tmp_path))
        assert result is not None
        assert result["exclude_tree_dirs"] == set()


# === save_config ==============================================================

class TestSaveConfig:

    def test_writes_valid_json(self, tmp_path):
        config = create_default_config()
        save_config(str(tmp_path), config)
        config_path = tmp_path / CONFIG_FILENAME
        assert config_path.exists()
        content = config_path.read_text(encoding="utf-8")
        parsed = json.loads(content)  # ne doit pas lever d'exception
        assert isinstance(parsed, dict)

    def test_converts_sets_to_sorted_lists(self, tmp_path):
        config = {
            "exclude_tree_dirs": {"z_dir", "a_dir", "m_dir"},
            "exclude_tree_files": set(),
            "exclude_tree_extensions": set(),
            "exclude_content_dirs": set(),
            "exclude_content_files": set(),
            "exclude_content_extensions": set(),
        }
        save_config(str(tmp_path), config)
        config_path = tmp_path / CONFIG_FILENAME
        parsed = json.loads(config_path.read_text(encoding="utf-8"))
        assert parsed["exclude_tree_dirs"] == ["a_dir", "m_dir", "z_dir"]

    def test_returns_true_on_success(self, tmp_path):
        config = create_default_config()
        result = save_config(str(tmp_path), config)
        assert result is True

    def test_returns_false_on_permission_error(self, tmp_path):
        config = create_default_config()
        # Rendre le dossier en lecture seule
        tmp_path.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            result = save_config(str(tmp_path), config, headless_mode=True)
            assert result is False
        finally:
            # Restaurer les permissions pour que pytest puisse nettoyer
            tmp_path.chmod(stat.S_IRWXU)

    def test_creates_file_at_correct_path(self, tmp_path):
        config = create_default_config()
        save_config(str(tmp_path), config)
        expected_path = tmp_path / CONFIG_FILENAME
        assert expected_path.exists()
        assert expected_path.name == CONFIG_FILENAME

    def test_existing_file_is_overwritten(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        config_path.write_text("ancien contenu", encoding="utf-8")
        config = {"exclude_tree_dirs": {"new_dir"}, "exclude_tree_files": set(),
                  "exclude_tree_extensions": set(), "exclude_content_dirs": set(),
                  "exclude_content_files": set(), "exclude_content_extensions": set()}
        save_config(str(tmp_path), config)
        parsed = json.loads(config_path.read_text(encoding="utf-8"))
        assert parsed["exclude_tree_dirs"] == ["new_dir"]


# === get_effective_config =====================================================

class TestGetEffectiveConfig:

    def test_returns_file_config_if_present(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        data = {
            "exclude_tree_dirs": ["custom_dir"],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": [],
            "exclude_content_extensions": [],
        }
        config_path.write_text(json.dumps(data), encoding="utf-8")
        result = get_effective_config(str(tmp_path), headless_mode=True)
        assert result["exclude_tree_dirs"] == {"custom_dir"}

    def test_returns_defaults_if_file_absent(self, tmp_path):
        result = get_effective_config(str(tmp_path), headless_mode=True)
        default = create_default_config()
        assert result["exclude_tree_dirs"] == default["exclude_tree_dirs"]
        assert result["exclude_content_extensions"] == default["exclude_content_extensions"]

    def test_returns_defaults_if_file_invalid(self, tmp_path):
        config_path = tmp_path / CONFIG_FILENAME
        config_path.write_text("{ json cassé", encoding="utf-8")
        result = get_effective_config(str(tmp_path), headless_mode=True)
        default = create_default_config()
        assert result["exclude_tree_dirs"] == default["exclude_tree_dirs"]

    def test_file_config_overrides_defaults_completely(self, tmp_path):
        """La config fichier remplace les défauts — même si elle est plus restrictive."""
        config_path = tmp_path / CONFIG_FILENAME
        # Config minimaliste : aucune exclusion
        data = {k: [] for k in create_default_config().keys()}
        config_path.write_text(json.dumps(data), encoding="utf-8")
        result = get_effective_config(str(tmp_path), headless_mode=True)
        # Toutes les exclusions sont vides (pas les défauts)
        assert result["exclude_tree_dirs"] == set()
        assert result["exclude_content_extensions"] == set()


# === Round-trip ===============================================================

class TestRoundTrip:

    def test_save_then_load_produces_same_config(self, tmp_path):
        original = {
            "exclude_tree_dirs": {"__pycache__", ".git", "venv"},
            "exclude_tree_files": {".DS_Store", "Thumbs.db"},
            "exclude_tree_extensions": {".pyc"},
            "exclude_content_dirs": {"node_modules"},
            "exclude_content_files": {CONFIG_FILENAME},
            "exclude_content_extensions": {".exe", ".dll", ".jpg"},
        }
        save_config(str(tmp_path), original)
        loaded = load_config(str(tmp_path))
        assert loaded is not None
        assert loaded == original

    def test_round_trip_with_empty_sets(self, tmp_path):
        original = {k: set() for k in create_default_config().keys()}
        save_config(str(tmp_path), original)
        loaded = load_config(str(tmp_path))
        assert loaded is not None
        assert loaded == original

    def test_round_trip_with_default_config(self, tmp_path):
        original = create_default_config()
        save_config(str(tmp_path), original)
        loaded = load_config(str(tmp_path))
        assert loaded is not None
        assert loaded == original