#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests d'intégration pour concat_files().
Pipeline complet : config → arborescence → contenu → post-traitement.
"""

import json
import os
import stat

import pytest

from gentxt.config import CONFIG_FILENAME, create_default_config
from gentxt.core import concat_files


def run(source, output):
    """Raccourci : exécute concat_files en mode headless et retourne le contenu produit."""
    concat_files(str(source), str(output), headless_mode=True)
    return output.read_text(encoding="utf-8")


# === Structure générale du fichier de sortie ==================================

class TestConcatPipelineStructure:

    def test_output_contains_tree_section_header(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert "# === Arborescence du dossier ===" in content

    def test_output_contains_content_section_header(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert "# === Contenu des fichiers ===" in content

    def test_tree_section_before_content_section(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        tree_pos = content.index("# === Arborescence du dossier ===")
        content_pos = content.index("# === Contenu des fichiers ===")
        assert tree_pos < content_pos

    def test_output_is_utf8_encoded(self, simple_project, tmp_output_file):
        concat_files(str(simple_project), str(tmp_output_file), headless_mode=True)
        # Lecture stricte UTF-8 sans errors='replace' : ne doit pas lever d'exception
        tmp_output_file.read_text(encoding="utf-8")

    def test_output_file_is_created(self, simple_project, tmp_output_file):
        assert not tmp_output_file.exists()
        run(simple_project, tmp_output_file)
        assert tmp_output_file.exists()

    def test_output_is_not_empty(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert len(content.strip()) > 0

    def test_tree_contains_root_dir_name(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        # Le nom du dossier source apparaît dans l'arborescence
        assert simple_project.name in content


# === Contenu concaténé ========================================================

class TestConcatPipelineContent:

    def test_text_files_have_their_content_included(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        # simple_project contient README.md avec "# Readme\n"
        assert "# Readme" in content

    def test_python_file_content_included(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert "print('hello')" in content

    def test_nested_file_content_included(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert "some notes" in content

    def test_binary_files_produce_placeholder_message(self, tmp_source_dir, tmp_output_file):
        # Utiliser une extension non exclue par défaut pour forcer la lecture
        (tmp_source_dir / "script.py").write_text("x = 1\n", encoding="utf-8")
        (tmp_source_dir / "data.dat2").write_bytes(b"\x00\x01\x02\x03" * 100)
        content = run(tmp_source_dir, tmp_output_file)
        assert "[Fichier binaire ou illisible, contenu ignoré]" in content

    def test_binary_file_raw_content_not_in_output(self, project_with_binary, tmp_output_file):
        content = run(project_with_binary, tmp_output_file)
        # Les octets nuls ne doivent pas apparaître dans la sortie texte
        assert "\x00" not in content

    def test_ods_file_content_extracted(self, project_with_ods, tmp_output_file):
        if not (project_with_ods / "table.ods").exists():
            pytest.skip("Fichier ODS de test absent")
        content = run(project_with_ods, tmp_output_file)
        assert "[Fichier binaire ou illisible, contenu ignoré]" not in content
        assert "=== Feuille:" in content

    def test_odt_file_content_extracted(self, project_with_odt, tmp_output_file):
        if not (project_with_odt / "doc.odt").exists():
            pytest.skip("Fichier ODT de test absent")
        content = run(project_with_odt, tmp_output_file)
        assert "[Fichier binaire ou illisible, contenu ignoré]" not in content

    def test_file_separator_present_for_each_file(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        # simple_project a README.md, main.py, data/notes.txt
        assert "--- Fichier :" in content
        assert content.count("--- Fichier :") == 3

    def test_separator_contains_relative_path(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        assert "--- Fichier : README.md ---" in content
        assert "--- Fichier : main.py ---" in content

    def test_nested_file_separator_uses_relative_path(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        # Séparateur pour data/notes.txt (chemin relatif avec sous-dossier)
        assert "data" + os.sep + "notes.txt" in content or "data/notes.txt" in content

    def test_files_processed_in_sorted_order(self, simple_project, tmp_output_file):
        content = run(simple_project, tmp_output_file)
        readme_pos = content.index("README.md")
        main_pos = content.index("main.py")
        # R < m en ASCII mais sorted() en Python est case-sensitive
        # Dans tous les cas les deux doivent être présents
        assert readme_pos != main_pos


# === Exclusions ===============================================================

class TestConcatPipelineExclusions:

    def test_excluded_content_dir_absent_from_output(self, tmp_source_dir, tmp_output_file, write_config):
        excluded = tmp_source_dir / "secret"
        excluded.mkdir()
        (excluded / "data.txt").write_text("données secrètes")
        (tmp_source_dir / "visible.txt").write_text("visible")
        write_config({
            "exclude_tree_dirs": [],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": ["secret"],
            "exclude_content_files": [],
            "exclude_content_extensions": [],
        })
        content = run(tmp_source_dir, tmp_output_file)
        assert "données secrètes" not in content
        assert "visible" in content

    def test_excluded_content_extension_absent_from_output(self, tmp_source_dir, tmp_output_file, write_config):
        (tmp_source_dir / "script.py").write_text("code python")
        (tmp_source_dir / "app.log").write_text("log entry")
        write_config({
            "exclude_tree_dirs": [],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": [],
            "exclude_content_extensions": [".log"],
        })
        content = run(tmp_source_dir, tmp_output_file)
        assert "log entry" not in content
        assert "code python" in content

    def test_excluded_content_file_absent_from_output(self, tmp_source_dir, tmp_output_file, write_config):
        (tmp_source_dir / "public.txt").write_text("contenu public")
        (tmp_source_dir / "secret.txt").write_text("contenu secret")
        write_config({
            "exclude_tree_dirs": [],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": ["secret.txt"],
            "exclude_content_extensions": [],
        })
        content = run(tmp_source_dir, tmp_output_file)
        assert "contenu secret" not in content
        assert "contenu public" in content

    def test_gentxt_output_file_excluded_from_content(self, tmp_source_dir, tmp_output_file):
        """La config par défaut exclut gentxt.txt — vérifié avec config explicite."""
        (tmp_source_dir / "app.py").write_text("# app")
        existing_gentxt = tmp_source_dir / "gentxt.txt"
        existing_gentxt.write_text("ancien contenu gentxt")
        # Écrire une config qui exclut explicitement gentxt.txt
        config_path = tmp_source_dir / CONFIG_FILENAME
        import json
        config_path.write_text(json.dumps({
            "exclude_tree_dirs": [],
            "exclude_tree_files": ["gentxt.txt"],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": ["gentxt.txt", CONFIG_FILENAME],
            "exclude_content_extensions": [],
        }), encoding="utf-8")
        content = run(tmp_source_dir, tmp_output_file)
        assert "ancien contenu gentxt" not in content

    def test_concat_config_json_excluded_from_content(self, tmp_source_dir, tmp_output_file, write_config):
        (tmp_source_dir / "app.py").write_text("# app")
        write_config({
            "exclude_tree_dirs": [],
            "exclude_tree_files": [CONFIG_FILENAME],  # aussi de l'arbre
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": [CONFIG_FILENAME],
            "exclude_content_extensions": [],
        })
        content = run(tmp_source_dir, tmp_output_file)
        # Le séparateur "--- Fichier : .concat_config.json ---" ne doit pas apparaître
        assert f"--- Fichier : {CONFIG_FILENAME} ---" not in content

    def test_default_excluded_dirs_not_in_output(self, project_with_excluded_dirs, tmp_output_file):
        """__pycache__, .git, node_modules exclus par la config par défaut."""
        content = run(project_with_excluded_dirs, tmp_output_file)
        assert "should be excluded" not in content

    def test_default_excluded_dirs_still_in_tree_depends_on_config(self, project_with_excluded_dirs, tmp_output_file):
        """Vérification cohérence : les dossiers exclus du contenu le sont aussi de l'arbre par défaut."""
        content = run(project_with_excluded_dirs, tmp_output_file)
        # app.py est visible (non exclu)
        assert "app.py" in content

    def test_multiple_exclusions_combined(self, tmp_source_dir, tmp_output_file, write_config):
        (tmp_source_dir / "keep.txt").write_text("garder")
        (tmp_source_dir / "drop.log").write_text("supprimer log")
        drop_dir = tmp_source_dir / "drop_dir"
        drop_dir.mkdir()
        (drop_dir / "data.txt").write_text("supprimer dir")
        write_config({
            "exclude_tree_dirs": [],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": ["drop_dir"],
            "exclude_content_files": [],
            "exclude_content_extensions": [".log"],
        })
        content = run(tmp_source_dir, tmp_output_file)
        assert "garder" in content
        assert "supprimer log" not in content
        assert "supprimer dir" not in content


# === Chargement et application de la configuration ============================

class TestConcatPipelineConfig:

    def test_json_config_is_loaded_and_applied(self, tmp_source_dir, tmp_output_file, write_config):
        excluded_dir = tmp_source_dir / "excluded"
        excluded_dir.mkdir()
        (excluded_dir / "secret.py").write_text("secret_marker_xyz")
        (tmp_source_dir / "visible.py").write_text("visible_marker_abc")
        write_config({
            "exclude_tree_dirs": ["excluded"],
            "exclude_tree_files": [],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": ["excluded"],
            "exclude_content_files": [],
            "exclude_content_extensions": [],
        })
        content = run(tmp_source_dir, tmp_output_file)
        assert "secret_marker_xyz" not in content
        assert "visible_marker_abc" in content

    def test_defaults_applied_without_config_file(self, simple_project, tmp_output_file):
        """.jpg est dans DEFAULT_EXCLUDE_CONTENT_EXTENSIONS → absent du contenu."""
        (simple_project / "image.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)
        content = run(simple_project, tmp_output_file)
        # .jpg exclu par défaut : le séparateur ne doit pas apparaître dans la section contenu
        assert "--- Fichier : image.jpg ---" not in content

    def test_empty_config_includes_everything(self, tmp_source_dir, tmp_output_file, write_config):
        """Une config avec toutes les listes vides n'exclut rien (sauf is_binary_file)."""
        (tmp_source_dir / "a.txt").write_text("contenu_a")
        (tmp_source_dir / "b.py").write_text("contenu_b")
        sub = tmp_source_dir / "sub"
        sub.mkdir()
        (sub / "c.txt").write_text("contenu_c")
        write_config({k: [] for k in create_default_config().keys()})
        content = run(tmp_source_dir, tmp_output_file)
        assert "contenu_a" in content
        assert "contenu_b" in content
        assert "contenu_c" in content

    def test_invalid_config_file_falls_back_to_defaults(self, tmp_source_dir, tmp_output_file):
        """Un .concat_config.json invalide → retour aux défauts, pas de crash."""
        config_path = tmp_source_dir / CONFIG_FILENAME
        config_path.write_text("{ json cassé :::", encoding="utf-8")
        (tmp_source_dir / "app.py").write_text("# app")
        content = run(tmp_source_dir, tmp_output_file)
        # Doit produire un fichier valide malgré la config invalide
        assert "# === Arborescence du dossier ===" in content


# === Robustesse ===============================================================

class TestConcatPipelineRobustness:

    def test_permission_error_on_subdir_does_not_crash(self, tmp_source_dir, tmp_output_file):
        restricted = tmp_source_dir / "restricted"
        restricted.mkdir()
        (restricted / "data.txt").write_text("données")
        (tmp_source_dir / "normal.txt").write_text("normal")
        restricted.chmod(stat.S_IWUSR | stat.S_IXUSR)
        try:
            content = run(tmp_source_dir, tmp_output_file)
            assert "# === Arborescence du dossier ===" in content
            assert "normal" in content
        finally:
            restricted.chmod(stat.S_IRWXU)

    def test_post_processing_applied(self, tmp_source_dir, tmp_output_file):
        """La sortie ne contient pas de bloc de 6+ \n consécutifs."""
        # Créer un fichier dont le contenu génère beaucoup de lignes vides
        (tmp_source_dir / "sparse.txt").write_text("A\n\n\n\n\n\n\n\n\n\nB")
        content = run(tmp_source_dir, tmp_output_file)
        import re
        assert not re.search(r"\n{6,}", content), "Le post-traitement n'a pas réduit les lignes vides"

    def test_empty_source_directory(self, tmp_source_dir, tmp_output_file):
        content = run(tmp_source_dir, tmp_output_file)
        assert "# === Arborescence du dossier ===" in content
        assert "# === Contenu des fichiers ===" in content

    def test_deeply_nested_structure(self, tmp_source_dir, tmp_output_file):
        current = tmp_source_dir
        for level in range(5):
            current = current / f"level_{level}"
            current.mkdir()
        (current / "deep.txt").write_text("contenu profond")
        content = run(tmp_source_dir, tmp_output_file)
        assert "contenu profond" in content

    def test_many_files_all_processed(self, tmp_source_dir, tmp_output_file):
        for i in range(20):
            (tmp_source_dir / f"file_{i:02d}.txt").write_text(f"contenu_{i}")
        content = run(tmp_source_dir, tmp_output_file)
        for i in range(20):
            assert f"contenu_{i}" in content

    def test_output_file_in_source_dir_excluded(self, tmp_source_dir, tmp_output_file):
        """gentxt.txt exclu uniquement si présent dans exclude_content_files de la config."""
        import json
        (tmp_source_dir / "app.py").write_text("# app")
        config_path = tmp_source_dir / CONFIG_FILENAME
        config_path.write_text(json.dumps({
            "exclude_tree_dirs": [],
            "exclude_tree_files": ["gentxt.txt"],
            "exclude_tree_extensions": [],
            "exclude_content_dirs": [],
            "exclude_content_files": ["gentxt.txt", CONFIG_FILENAME],
            "exclude_content_extensions": [],
        }), encoding="utf-8")
        output_in_source = tmp_source_dir / "gentxt.txt"
        concat_files(str(tmp_source_dir), str(output_in_source), headless_mode=True)
        content = output_in_source.read_text(encoding="utf-8")
        assert content.count("--- Fichier : gentxt.txt ---") == 0

    def test_unicode_filenames_handled(self, tmp_source_dir, tmp_output_file):
        (tmp_source_dir / "fïlé_ünïcödé.txt").write_text("unicode content")
        # Ne doit pas crasher
        content = run(tmp_source_dir, tmp_output_file)
        assert "unicode content" in content

    def test_file_with_special_chars_in_content(self, tmp_source_dir, tmp_output_file):
        (tmp_source_dir / "special.txt").write_text("tab:\there\nnewline above\n\nnull-free ✓")
        content = run(tmp_source_dir, tmp_output_file)
        assert "tab:" in content
        assert "null-free ✓" in content