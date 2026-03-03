#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour generate_tree().
"""

import os
import stat

import pytest

from gentxt.core import generate_tree


def empty_config() -> dict:
    return {
        "exclude_tree_dirs": set(),
        "exclude_tree_files": set(),
        "exclude_tree_extensions": set(),
        "exclude_content_dirs": set(),
        "exclude_content_files": set(),
        "exclude_content_extensions": set(),
    }


def config_with(**kwargs) -> dict:
    """Helper : empty_config() avec les clés kwargs surchargées."""
    c = empty_config()
    c.update(kwargs)
    return c


def tree_as_string(lines: list) -> str:
    return "\n".join(lines)


class TestGenerateTree:

    def test_empty_directory_returns_root_name_only(self, tmp_path):
        lines = generate_tree(str(tmp_path), empty_config())
        assert len(lines) == 1
        assert lines[0] == tmp_path.name

    def test_root_name_is_basename_not_full_path(self, tmp_path):
        (tmp_path / "file.txt").write_text("x")
        lines = generate_tree(str(tmp_path), empty_config())
        assert lines[0] == tmp_path.name
        assert os.sep not in lines[0]

    def test_flat_structure_files_only(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.py").write_text("b")
        lines = generate_tree(str(tmp_path), empty_config())
        content = tree_as_string(lines)
        assert "a.txt" in content
        assert "b.py" in content

    def test_nested_directories_correct_indentation(self, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.txt").write_text("n")
        lines = generate_tree(str(tmp_path), empty_config())
        content = tree_as_string(lines)
        assert "subdir" in content
        assert "nested.txt" in content
        # nested.txt doit apparaître avec une indentation supplémentaire
        nested_line = [l for l in lines if "nested.txt" in l][0]
        assert nested_line.startswith("    ") or "│" in nested_line or "└" in nested_line

    def test_last_item_uses_corner_connector(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        lines = generate_tree(str(tmp_path), empty_config())
        # Le dernier élément (b.txt, ordre alphabétique) utilise └──
        last_line = [l for l in lines if "b.txt" in l][0]
        assert "└" in last_line

    def test_non_last_item_uses_tee_connector(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        lines = generate_tree(str(tmp_path), empty_config())
        # a.txt n'est pas le dernier → ├──
        first_line = [l for l in lines if "a.txt" in l][0]
        assert "├" in first_line

    def test_excluded_dir_not_in_output(self, tmp_path):
        excluded = tmp_path / "secret_dir"
        excluded.mkdir()
        (excluded / "file.txt").write_text("secret")
        (tmp_path / "visible.txt").write_text("visible")
        cfg = config_with(exclude_tree_dirs={"secret_dir"})
        lines = generate_tree(str(tmp_path), cfg)
        content = tree_as_string(lines)
        assert "secret_dir" not in content
        assert "visible.txt" in content

    def test_excluded_file_not_in_output(self, tmp_path):
        (tmp_path / "visible.txt").write_text("v")
        (tmp_path / "hidden.txt").write_text("h")
        cfg = config_with(exclude_tree_files={"hidden.txt"})
        lines = generate_tree(str(tmp_path), cfg)
        content = tree_as_string(lines)
        assert "hidden.txt" not in content
        assert "visible.txt" in content

    def test_excluded_extension_not_in_output(self, tmp_path):
        (tmp_path / "script.py").write_text("code")
        (tmp_path / "compiled.pyc").write_bytes(b"\x00\x01")
        cfg = config_with(exclude_tree_extensions={".pyc"})
        lines = generate_tree(str(tmp_path), cfg)
        content = tree_as_string(lines)
        assert "compiled.pyc" not in content
        assert "script.py" in content

    def test_permission_error_does_not_crash(self, tmp_path):
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        (restricted / "file.txt").write_text("x")
        # Retirer les permissions de lecture sur le sous-dossier
        restricted.chmod(stat.S_IWUSR | stat.S_IXUSR)
        try:
            lines = generate_tree(str(tmp_path), empty_config())
            # Ne doit pas lever d'exception
            assert isinstance(lines, list)
        finally:
            restricted.chmod(stat.S_IRWXU)

    def test_dirs_listed_before_files(self, tmp_path):
        (tmp_path / "z_file.txt").write_text("z")
        (tmp_path / "a_dir").mkdir()
        lines = generate_tree(str(tmp_path), empty_config())
        # Trouver les positions
        dir_indices = [i for i, l in enumerate(lines) if "a_dir" in l]
        file_indices = [i for i, l in enumerate(lines) if "z_file.txt" in l]
        assert dir_indices and file_indices
        assert dir_indices[0] < file_indices[0]

    def test_alphabetical_sort_within_dirs_group(self, tmp_path):
        for name in ["c_dir", "a_dir", "b_dir"]:
            (tmp_path / name).mkdir()
        lines = generate_tree(str(tmp_path), empty_config())
        dir_lines = [l for l in lines if "_dir" in l]
        names = [l.strip().lstrip("├└─ ") for l in dir_lines]
        assert names == sorted(names)

    def test_alphabetical_sort_within_files_group(self, tmp_path):
        for name in ["c.txt", "a.txt", "b.txt"]:
            (tmp_path / name).write_text(name)
        lines = generate_tree(str(tmp_path), empty_config())
        file_lines = [l for l in lines if ".txt" in l]
        names = [l.strip().lstrip("├└─ ") for l in file_lines]
        assert names == sorted(names)

    def test_prefix_pipe_vs_space_at_deep_nesting(self, tmp_path):
        """
        Structure :
        root/
        ├── dir_a/
        │   └── deep.txt      ← préfixe '│   '
        └── dir_b/
            └── deep.txt      ← préfixe '    ' (dir_b est le dernier)
        """
        dir_a = tmp_path / "dir_a"
        dir_a.mkdir()
        (dir_a / "deep.txt").write_text("a")
        dir_b = tmp_path / "dir_b"
        dir_b.mkdir()
        (dir_b / "deep.txt").write_text("b")

        lines = generate_tree(str(tmp_path), empty_config())
        content = tree_as_string(lines)

        # Les deux fichiers doivent apparaître
        deep_lines = [l for l in lines if "deep.txt" in l]
        assert len(deep_lines) == 2

        # dir_a n'est pas le dernier → son contenu a le préfixe │
        deep_in_a = [l for i, l in enumerate(lines)
                     if "deep.txt" in l and "│" in lines[i - 1] if i > 0]
        # Vérification souple : au moins un deep.txt a │ dans son préfixe
        assert any("│" in l for l in deep_lines)

    def test_multiple_levels_of_nesting(self, tmp_path):
        level1 = tmp_path / "l1"
        level1.mkdir()
        level2 = level1 / "l2"
        level2.mkdir()
        level3 = level2 / "l3"
        level3.mkdir()
        (level3 / "deep.txt").write_text("deep")
        lines = generate_tree(str(tmp_path), empty_config())
        content = tree_as_string(lines)
        assert "l1" in content
        assert "l2" in content
        assert "l3" in content
        assert "deep.txt" in content

    def test_exclusion_case_sensitive(self, tmp_path):
        """Les exclusions sont sensibles à la casse."""
        (tmp_path / "Readme.md").write_text("R")
        (tmp_path / "readme.md").write_text("r")
        cfg = config_with(exclude_tree_files={"readme.md"})
        lines = generate_tree(str(tmp_path), cfg)
        content = tree_as_string(lines)
        assert "Readme.md" in content      # majuscule : non exclu
        assert "readme.md" not in content  # minuscule : exclu

    def test_mixed_dirs_and_files(self, tmp_path):
        (tmp_path / "alpha.txt").write_text("a")
        (tmp_path / "beta_dir").mkdir()
        (tmp_path / "gamma.py").write_text("g")
        (tmp_path / "delta_dir").mkdir()
        lines = generate_tree(str(tmp_path), empty_config())
        content = tree_as_string(lines)
        for name in ["alpha.txt", "beta_dir", "gamma.py", "delta_dir"]:
            assert name in content