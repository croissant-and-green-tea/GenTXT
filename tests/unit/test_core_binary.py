#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour la détection de fichiers binaires (is_binary_file).
"""

import pytest
from unittest.mock import patch

from gentxt.core import is_binary_file


class TestIsBinaryFile:

    def test_returns_true_for_file_with_null_bytes(self, tmp_path):
        f = tmp_path / "with_null.bin"
        f.write_bytes(b"du texte normal\x00puis un octet nul")
        assert is_binary_file(str(f)) is True

    def test_returns_false_for_pure_utf8_text(self, tmp_path):
        f = tmp_path / "text.py"
        f.write_text("# -*- coding: utf-8 -*-\nprint('hello world')\n", encoding="utf-8")
        assert is_binary_file(str(f)) is False

    def test_returns_false_for_utf8_with_accents(self, tmp_path):
        f = tmp_path / "accents.txt"
        f.write_text("éàü ñ ß — texte avec accents\n", encoding="utf-8")
        assert is_binary_file(str(f)) is False

    def test_returns_true_for_png_header(self, tmp_path):
        f = tmp_path / "image.png"
        # Header PNG minimal : magic bytes + données aléatoires
        f.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x01\x02\x03" * 200)
        assert is_binary_file(str(f)) is True

    def test_returns_true_for_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        assert is_binary_file(str(f)) is True

    def test_returns_true_on_permission_error(self, tmp_path):
        f = tmp_path / "noperm.txt"
        f.write_text("contenu", encoding="utf-8")
        with patch("builtins.open", side_effect=PermissionError("accès refusé")):
            assert is_binary_file(str(f)) is True

    def test_returns_true_on_os_error(self, tmp_path):
        f = tmp_path / "inexistant.txt"
        # Fichier qui n'existe pas → OSError
        assert is_binary_file(str(f)) is True

    def test_threshold_just_below_30_percent(self, tmp_path):
        """
        Construit un chunk où ~29% des octets sont non-texte.
        text_characters inclut 0x20-0xFF sauf 0x7F, plus quelques ctrl.
        On utilise des octets dans la plage 0x20-0x7E (ASCII imprimable, 100% texte)
        et on y ajoute exactement 29% d'octet 0x01 (non-texte).
        """
        f = tmp_path / "mostly_text.bin"
        total = 1000
        non_text_count = 290  # 29%
        text_count = total - non_text_count
        content = b"A" * text_count + b"\x01" * non_text_count
        f.write_bytes(content)
        assert is_binary_file(str(f)) is False

    def test_threshold_just_above_30_percent(self, tmp_path):
        """31% de caractères non-texte → détecté comme binaire."""
        f = tmp_path / "mostly_binary.bin"
        total = 1000
        non_text_count = 310  # 31%
        text_count = total - non_text_count
        content = b"A" * text_count + b"\x01" * non_text_count
        f.write_bytes(content)
        assert is_binary_file(str(f)) is True

    def test_latin1_text_is_not_binary(self, tmp_path):
        """
        Un fichier latin-1 sans octets nuls ne doit pas être détecté comme binaire.
        Les octets 0x80-0xFF sont dans text_characters (range(0x20, 0x100)).
        """
        f = tmp_path / "latin1.txt"
        # Texte latin-1 pur : tous les octets sont >= 0x20 sauf les fins de ligne
        f.write_bytes("Contenu latin-1 : éàü\nDeux lignes.\n".encode("latin-1"))
        assert is_binary_file(str(f)) is False

    def test_exe_header_detected_as_binary(self, tmp_path):
        """Header MZ d'un exécutable Windows."""
        f = tmp_path / "prog.exe"
        f.write_bytes(b"MZ" + b"\x00\x01\x02\x03" * 500)
        assert is_binary_file(str(f)) is True

    def test_large_text_file_not_binary(self, tmp_path):
        """Un gros fichier texte (> 8192 octets) : seuls les premiers 8192 sont lus."""
        f = tmp_path / "large.txt"
        # 20Ko de texte ASCII pur
        f.write_bytes(b"a" * 20000)
        assert is_binary_file(str(f)) is False