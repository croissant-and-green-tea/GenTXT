#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le post-traitement des lignes vides (_clean_excessive_newlines).

Comportement implémenté : re.sub(r'\n{6,}', '\n\n\n', content)
→ 6+ sauts de ligne consécutifs remplacés par exactement 3 sauts de ligne.
→ 5 sauts de ligne ou moins : inchangés.
"""

import pytest

from gentxt.core import _clean_excessive_newlines


def write_and_clean(tmp_path, content: str) -> str:
    """Helper : écrit content dans un fichier, appelle _clean_excessive_newlines, retourne le résultat."""
    f = tmp_path / "test_output.txt"
    f.write_text(content, encoding="utf-8")
    _clean_excessive_newlines(str(f))
    return f.read_text(encoding="utf-8")


class TestCleanExcessiveNewlines:

    def test_six_newlines_reduced_to_three(self, tmp_path):
        """6 sauts de ligne consécutifs → 3."""
        result = write_and_clean(tmp_path, "avant\n\n\n\n\n\naprès")
        assert result == "avant\n\n\naprès"

    def test_ten_newlines_reduced_to_three(self, tmp_path):
        """10 sauts de ligne consécutifs → 3."""
        result = write_and_clean(tmp_path, "A" + "\n" * 10 + "B")
        assert result == "A\n\n\nB"

    def test_twenty_newlines_reduced_to_three(self, tmp_path):
        result = write_and_clean(tmp_path, "X" + "\n" * 20 + "Y")
        assert result == "X\n\n\nY"

    def test_five_newlines_unchanged(self, tmp_path):
        """5 sauts de ligne (seuil : regex démarre à 6) → inchangés."""
        original = "avant\n\n\n\n\naprès"  # exactement 5 \n
        result = write_and_clean(tmp_path, original)
        assert result == original

    def test_four_newlines_unchanged(self, tmp_path):
        original = "avant\n\n\n\naprès"
        result = write_and_clean(tmp_path, original)
        assert result == original

    def test_three_newlines_unchanged(self, tmp_path):
        original = "avant\n\n\naprès"
        result = write_and_clean(tmp_path, original)
        assert result == original

    def test_content_without_excessive_newlines_unchanged(self, tmp_path):
        original = "ligne1\nligne2\n\nligne3\n"
        result = write_and_clean(tmp_path, original)
        assert result == original

    def test_empty_file_does_not_crash(self, tmp_path):
        result = write_and_clean(tmp_path, "")
        assert result == ""

    def test_content_preserved_around_cleaned_newlines(self, tmp_path):
        """Le texte autour des sauts nettoyés est intact."""
        result = write_and_clean(tmp_path, "DEBUT\n" * 1 + "\n" * 8 + "FIN")
        assert result.startswith("DEBUT\n")
        assert result.endswith("FIN")
        assert "\n\n\n\n" not in result

    def test_multiple_excessive_blocks_all_cleaned(self, tmp_path):
        """Plusieurs blocs excessifs dans le même fichier sont tous réduits."""
        content = "A" + "\n" * 7 + "B" + "\n" * 9 + "C"
        result = write_and_clean(tmp_path, content)
        assert result == "A\n\n\nB\n\n\nC"

    def test_mixed_blocks_partial_clean(self, tmp_path):
        """Seuls les blocs >= 6 sont réduits, les autres restent inchangés."""
        # 2 \n entre A et B, 5 \n entre B et C (< 6 → inchangé), 2 \n entre C et D
        content = "A\n\nB\n\n\n\n\nC\n\nD"
        result = write_and_clean(tmp_path, content)
        assert result == "A\n\nB\n\n\n\n\nC\n\nD"  # 5 \n : inchangé

    def test_mixed_blocks_one_above_threshold(self, tmp_path):
        """Un bloc >= 6 est réduit, les blocs < 6 restent."""
        # 2 \n entre A et B, 7 \n entre B et C (réduit à 3), 2 \n entre C et D
        content = "A\n\nB\n\n\n\n\n\n\nC\n\nD"
        result = write_and_clean(tmp_path, content)
        assert result == "A\n\nB\n\n\nC\n\nD"

    def test_file_is_utf8_after_processing(self, tmp_path):
        """Le fichier résultant est toujours lisible en UTF-8."""
        content = "éàü\n" * 3 + "\n" * 8 + "ñß\n"
        result = write_and_clean(tmp_path, content)
        assert "éàü" in result
        assert "ñß" in result

    def test_exactly_six_newlines_is_the_threshold(self, tmp_path):
        """Vérification que 6 est bien le seuil minimum de réduction."""
        five = "A" + "\n" * 5 + "B"
        six = "A" + "\n" * 6 + "B"
        result_five = write_and_clean(tmp_path, five)
        # Réinitialiser le fichier pour le second test
        f = tmp_path / "test_output.txt"
        f.write_text(six, encoding="utf-8")
        _clean_excessive_newlines(str(f))
        result_six = f.read_text(encoding="utf-8")

        assert result_five == five       # 5 : inchangé
        assert result_six == "A\n\n\nB"  # 6 : réduit