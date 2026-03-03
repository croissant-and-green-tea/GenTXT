#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests d'intégration pour run_headless_mode().
"""

import os

import pytest

from gentxt.headless import run_headless_mode, HEADLESS_ERROR_LOG_FILE


# === Helpers ==================================================================

def error_log_path(directory) -> str:
    return os.path.join(str(directory), HEADLESS_ERROR_LOG_FILE)


def output_path(directory) -> str:
    return os.path.join(str(directory), "gentxt.txt")


# === Comportement nominal =====================================================

class TestHeadlessMode:

    def test_creates_gentxt_txt_in_cwd(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        assert (simple_project / "gentxt.txt").exists()

    def test_output_filename_is_always_gentxt_txt(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        files = list(simple_project.iterdir())
        output_files = [f for f in files if f.suffix == ".txt" and "gentxt" in f.name]
        assert len(output_files) == 1
        assert output_files[0].name == "gentxt.txt"

    def test_output_contains_tree_and_content_sections(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        content = (simple_project / "gentxt.txt").read_text(encoding="utf-8")
        assert "# === Arborescence du dossier ===" in content
        assert "# === Contenu des fichiers ===" in content

    def test_output_contains_source_files(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        content = (simple_project / "gentxt.txt").read_text(encoding="utf-8")
        assert "# Readme" in content
        assert "print('hello')" in content

    def test_no_error_log_created_on_success(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        assert not (simple_project / HEADLESS_ERROR_LOG_FILE).exists()


# === Gestion du fichier de log d'erreur =======================================

class TestHeadlessModeErrorLog:

    def test_removes_old_error_log_before_run(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        old_log = simple_project / HEADLESS_ERROR_LOG_FILE
        old_log.write_text("ancien log", encoding="utf-8")
        assert old_log.exists()
        run_headless_mode()
        assert not old_log.exists()

    def test_creates_error_log_on_failure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from unittest.mock import patch
        with patch("gentxt.headless.concat_files", side_effect=RuntimeError("erreur simulée")):
            run_headless_mode()
        log = tmp_path / HEADLESS_ERROR_LOG_FILE
        assert log.exists()

    def test_error_log_contains_error_message(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from unittest.mock import patch
        with patch("gentxt.headless.concat_files", side_effect=RuntimeError("message_erreur_unique")):
            run_headless_mode()
        log = tmp_path / HEADLESS_ERROR_LOG_FILE
        content = log.read_text(encoding="utf-8")
        assert "message_erreur_unique" in content

    def test_error_log_contains_source_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from unittest.mock import patch
        with patch("gentxt.headless.concat_files", side_effect=RuntimeError("boom")):
            run_headless_mode()
        log = tmp_path / HEADLESS_ERROR_LOG_FILE
        content = log.read_text(encoding="utf-8")
        assert str(tmp_path) in content

    def test_error_log_contains_output_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from unittest.mock import patch
        with patch("gentxt.headless.concat_files", side_effect=RuntimeError("boom")):
            run_headless_mode()
        log = tmp_path / HEADLESS_ERROR_LOG_FILE
        content = log.read_text(encoding="utf-8")
        assert "gentxt.txt" in content

    def test_old_error_log_deleted_even_if_new_run_also_fails(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        old_log = tmp_path / HEADLESS_ERROR_LOG_FILE
        old_log.write_text("ancien log d'erreur", encoding="utf-8")
        from unittest.mock import patch
        with patch("gentxt.headless.concat_files", side_effect=RuntimeError("nouvelle erreur")):
            run_headless_mode()
        log = tmp_path / HEADLESS_ERROR_LOG_FILE
        content = log.read_text(encoding="utf-8")
        assert "ancien log d'erreur" not in content
        assert "nouvelle erreur" in content


# === Comportement sur différentes structures de projet ========================

class TestHeadlessModeProjectVariants:

    def test_empty_directory(self, tmp_source_dir, monkeypatch):
        monkeypatch.chdir(tmp_source_dir)
        run_headless_mode()
        assert (tmp_source_dir / "gentxt.txt").exists()

    def test_project_with_binary_files(self, project_with_binary, monkeypatch):
        monkeypatch.chdir(project_with_binary)
        run_headless_mode()
        content = (project_with_binary / "gentxt.txt").read_text(encoding="utf-8")
        assert "[Fichier binaire ou illisible, contenu ignoré]" in content

    def test_project_with_excluded_dirs(self, project_with_excluded_dirs, monkeypatch):
        monkeypatch.chdir(project_with_excluded_dirs)
        run_headless_mode()
        content = (project_with_excluded_dirs / "gentxt.txt").read_text(encoding="utf-8")
        assert "should be excluded" not in content

    def test_overwrites_existing_gentxt(self, simple_project, monkeypatch):
        existing = simple_project / "gentxt.txt"
        existing.write_text("contenu obsolète", encoding="utf-8")
        monkeypatch.chdir(simple_project)
        run_headless_mode()
        content = existing.read_text(encoding="utf-8")
        assert "contenu obsolète" not in content
        assert "# === Arborescence du dossier ===" in content

    def test_headless_does_not_launch_qt(self, simple_project, monkeypatch):
        monkeypatch.chdir(simple_project)
        from unittest.mock import patch, MagicMock
        mock_qapp = MagicMock()
        with patch("PySide6.QtWidgets.QApplication", mock_qapp):
            run_headless_mode()
        mock_qapp.assert_not_called()