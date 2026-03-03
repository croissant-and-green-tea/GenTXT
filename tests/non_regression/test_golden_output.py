#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de non-régression par comparaison avec des golden files (snapshots figés).

Mode normal  : compare la sortie courante au snapshot → échec si divergence.
Mode update  : régénère les snapshots (UPDATE_SNAPSHOTS=1 pytest tests/non_regression/).

Usage :
    pytest tests/non_regression/
    UPDATE_SNAPSHOTS=1 pytest tests/non_regression/
"""

import os
import shutil

import pytest

from gentxt.core import concat_files

# === Constantes ===============================================================

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
UPDATE_SNAPSHOTS = os.environ.get("UPDATE_SNAPSHOTS", "0") == "1"

FIXTURE_SIMPLE = os.path.join(FIXTURES_DIR, "project_simple")
FIXTURE_WITH_CONFIG = os.path.join(FIXTURES_DIR, "project_with_config")
EXPECTED_SIMPLE = os.path.join(FIXTURES_DIR, "expected_simple.txt")
EXPECTED_WITH_CONFIG = os.path.join(FIXTURES_DIR, "expected_with_config.txt")

TEST_MANO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "test_mano")
REAL_ODS = os.path.join(TEST_MANO_DIR, "fichier_ods_deux_pages.ods")
REAL_ODT = os.path.join(TEST_MANO_DIR, "fichier_odt.odt")


# === Helper central ===========================================================

def run_and_compare(source_dir: str, expected_file: str, tmp_path) -> None:
    """
    Exécute concat_files sur source_dir.
    - UPDATE_SNAPSHOTS=1 : écrase expected_file avec la sortie courante, passe toujours.
    - Sinon : compare la sortie à expected_file, échec si divergence.

    Le snapshot attendu doit exister avant le premier passage en mode normal.
    Générez-le une fois avec UPDATE_SNAPSHOTS=1.
    """
    import pathlib
    pathlib.Path(tmp_path).mkdir(parents=True, exist_ok=True)
    output = pathlib.Path(tmp_path) / "output.txt"
    concat_files(source_dir, str(output), headless_mode=True)
    actual = output.read_text(encoding="utf-8")

    if UPDATE_SNAPSHOTS:
        os.makedirs(os.path.dirname(expected_file), exist_ok=True)
        with open(expected_file, "w", encoding="utf-8") as f:
            f.write(actual)
        return  # pas d'assertion : on régénère

    if not os.path.exists(expected_file):
        pytest.fail(
            f"Golden file absent : {expected_file}\n"
            f"Générez-le avec : UPDATE_SNAPSHOTS=1 pytest tests/non_regression/"
        )

    expected = open(expected_file, encoding="utf-8").read()

    if actual != expected:
        # Diff lisible ligne par ligne
        import difflib
        diff = difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual",
            n=3,
        )
        diff_str = "".join(list(diff))
        pytest.fail(
            f"Régression détectée sur {os.path.basename(source_dir)} :\n\n{diff_str}"
        )


# === Tests ====================================================================

class TestGoldenOutput:

    def test_simple_project_matches_snapshot(self, tmp_path):
        """
        Sortie sur fixtures/project_simple/ identique à expected_simple.txt.
        Structure : README.md, src/main.py, data/table.ods, data/doc.odt.
        """
        if not os.path.isdir(FIXTURE_SIMPLE):
            pytest.skip(f"Fixture absente : {FIXTURE_SIMPLE}")
        run_and_compare(FIXTURE_SIMPLE, EXPECTED_SIMPLE, tmp_path)

    def test_project_with_config_matches_snapshot(self, tmp_path):
        """
        Sortie sur fixtures/project_with_config/ identique à expected_with_config.txt.
        La config exclut certains dossiers et extensions.
        """
        if not os.path.isdir(FIXTURE_WITH_CONFIG):
            pytest.skip(f"Fixture absente : {FIXTURE_WITH_CONFIG}")
        run_and_compare(FIXTURE_WITH_CONFIG, EXPECTED_WITH_CONFIG, tmp_path)

    @pytest.mark.skipif(
        not os.path.exists(REAL_ODS),
        reason="test_mano/fichier_ods_deux_pages.ods absent"
    )
    def test_ods_extraction_matches_snapshot(self, tmp_path):
        """
        Sortie sur un dossier contenant le vrai fichier ODS identique au snapshot.
        """
        expected_file = os.path.join(FIXTURES_DIR, "expected_ods.txt")
        source = tmp_path / "ods_project"
        source.mkdir()
        shutil.copy(REAL_ODS, source / "fichier_ods_deux_pages.ods")
        run_and_compare(str(source), expected_file, tmp_path / "out")

    @pytest.mark.skipif(
        not os.path.exists(REAL_ODT),
        reason="test_mano/fichier_odt.odt absent"
    )
    def test_odt_extraction_matches_snapshot(self, tmp_path):
        """
        Sortie sur un dossier contenant le vrai fichier ODT identique au snapshot.
        """
        expected_file = os.path.join(FIXTURES_DIR, "expected_odt.txt")
        source = tmp_path / "odt_project"
        source.mkdir()
        shutil.copy(REAL_ODT, source / "fichier_odt.odt")
        run_and_compare(str(source), expected_file, tmp_path / "out")


# === Tests de robustesse du mécanisme de snapshot lui-même ====================

class TestSnapshotMechanism:

    def test_update_mode_creates_snapshot_if_absent(self, tmp_path, monkeypatch):
        """En mode UPDATE, un snapshot absent est créé sans erreur."""
        monkeypatch.setenv("UPDATE_SNAPSHOTS", "1")
        # Recharger la variable du module après monkeypatch
        import importlib
        import tests.non_regression.test_golden_output as nr_module
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", True)

        source = tmp_path / "src"
        source.mkdir()
        (source / "hello.txt").write_text("bonjour")
        expected_file = str(tmp_path / "snapshot.txt")

        nr_module.run_and_compare(str(source), expected_file, tmp_path / "out")
        assert os.path.exists(expected_file)
        content = open(expected_file, encoding="utf-8").read()
        assert "bonjour" in content

    def test_update_mode_overwrites_existing_snapshot(self, tmp_path, monkeypatch):
        """En mode UPDATE, un snapshot existant est écrasé avec la nouvelle sortie."""
        import tests.non_regression.test_golden_output as nr_module
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", True)

        source = tmp_path / "src"
        source.mkdir()
        (source / "hello.txt").write_text("nouveau contenu")
        expected_file = tmp_path / "snapshot.txt"
        expected_file.write_text("ancien snapshot", encoding="utf-8")

        nr_module.run_and_compare(str(source), str(expected_file), tmp_path / "out")
        content = expected_file.read_text(encoding="utf-8")
        assert "nouveau contenu" in content
        assert "ancien snapshot" not in content

    def test_normal_mode_fails_if_snapshot_absent(self, tmp_path, monkeypatch):
        """En mode normal, l'absence de snapshot fait échouer le test avec un message clair."""
        import tests.non_regression.test_golden_output as nr_module
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", False)

        source = tmp_path / "src"
        source.mkdir()
        (source / "hello.txt").write_text("contenu")
        expected_file = str(tmp_path / "inexistant_snapshot.txt")

        with pytest.raises(pytest.fail.Exception) as exc_info:
            nr_module.run_and_compare(str(source), expected_file, tmp_path / "out")
        assert "Golden file absent" in str(exc_info.value)
        assert "UPDATE_SNAPSHOTS=1" in str(exc_info.value)

    def test_normal_mode_passes_if_output_matches_snapshot(self, tmp_path, monkeypatch):
        """En mode normal, si la sortie correspond au snapshot, pas d'échec."""
        import tests.non_regression.test_golden_output as nr_module
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", False)

        source = tmp_path / "src"
        source.mkdir()
        (source / "hello.txt").write_text("contenu stable")

        # Générer le snapshot une première fois
        out1 = tmp_path / "out1"
        out1.mkdir()
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", True)
        expected_file = str(tmp_path / "snapshot.txt")
        nr_module.run_and_compare(str(source), expected_file, out1)

        # Comparer en mode normal : doit passer
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", False)
        out2 = tmp_path / "out2"
        out2.mkdir()
        nr_module.run_and_compare(str(source), expected_file, out2)  # ne doit pas lever

    def test_normal_mode_fails_if_output_differs_from_snapshot(self, tmp_path, monkeypatch):
        """En mode normal, une divergence fait échouer avec un diff lisible."""
        import tests.non_regression.test_golden_output as nr_module

        source = tmp_path / "src"
        source.mkdir()
        (source / "hello.txt").write_text("contenu v1")

        # Créer le snapshot avec v1
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", True)
        expected_file = str(tmp_path / "snapshot.txt")
        nr_module.run_and_compare(str(source), expected_file, tmp_path / "out1")

        # Modifier le source pour créer une divergence
        (source / "hello.txt").write_text("contenu v2 DIFFERENT")

        # Comparer en mode normal : doit échouer
        monkeypatch.setattr(nr_module, "UPDATE_SNAPSHOTS", False)
        with pytest.raises(pytest.fail.Exception) as exc_info:
            nr_module.run_and_compare(str(source), expected_file, tmp_path / "out2")
        assert "Régression détectée" in str(exc_info.value)
        # Le diff doit mentionner les deux versions
        assert "v1" in str(exc_info.value) or "v2" in str(exc_info.value)


# === Tests de contenu des fixtures figées =====================================

class TestFixtureContent:
    """
    Vérifie que les fixtures elles-mêmes ont le contenu attendu.
    Ces tests protègent contre une modification accidentelle des fixtures.
    """

    def test_fixture_simple_readme_exists(self):
        readme = os.path.join(FIXTURE_SIMPLE, "README.md")
        if not os.path.isdir(FIXTURE_SIMPLE):
            pytest.skip("Fixture absente")
        assert os.path.exists(readme)

    def test_fixture_simple_src_main_exists(self):
        main = os.path.join(FIXTURE_SIMPLE, "src", "main.py")
        if not os.path.isdir(FIXTURE_SIMPLE):
            pytest.skip("Fixture absente")
        assert os.path.exists(main)

    def test_fixture_simple_src_main_content_unchanged(self):
        main = os.path.join(FIXTURE_SIMPLE, "src", "main.py")
        if not os.path.isfile(main):
            pytest.skip("Fixture absente")
        content = open(main, encoding="utf-8").read()
        # Contenu figé connu
        assert "def hello()" in content
        assert 'return "hello"' in content

    def test_fixture_with_config_app_exists(self):
        app = os.path.join(FIXTURE_WITH_CONFIG, "src", "app.py")
        if not os.path.isdir(FIXTURE_WITH_CONFIG):
            pytest.skip("Fixture absente")
        assert os.path.exists(app)

    def test_fixture_with_config_app_content_unchanged(self):
        app = os.path.join(FIXTURE_WITH_CONFIG, "src", "app.py")
        if not os.path.isfile(app):
            pytest.skip("Fixture absente")
        content = open(app, encoding="utf-8").read()
        assert "def run()" in content

    def test_fixture_with_config_has_concat_config(self):
        """project_with_config doit avoir un .concat_config.json pour tester les exclusions."""
        config = os.path.join(FIXTURE_WITH_CONFIG, ".concat_config.json")
        if not os.path.isdir(FIXTURE_WITH_CONFIG):
            pytest.skip("Fixture absente")
        # Si absent, rappeler à l'utilisateur de le créer
        if not os.path.exists(config):
            pytest.fail(
                f".concat_config.json absent de {FIXTURE_WITH_CONFIG}\n"
                f"Créez-le manuellement pour que la fixture project_with_config ait du sens."
            )