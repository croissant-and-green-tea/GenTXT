#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mode headless — aucune dépendance GUI."""

import os

from gentxt.core import concat_files

HEADLESS_ERROR_LOG_FILE = "gentxt_headless_error.log"


def run_headless_mode() -> None:
    source_directory = os.getcwd()
    output_path = os.path.join(source_directory, "gentxt.txt")
    error_log_path = os.path.join(source_directory, HEADLESS_ERROR_LOG_FILE)

    if os.path.exists(error_log_path):
        try:
            os.remove(error_log_path)
        except OSError as e:
            print(f"Avertissement: Impossible de supprimer l'ancien fichier de log : {e}")

    print("gentxt: Mode Headless activé.")
    print(f"Répertoire source : {source_directory}")
    print(f"Fichier de sortie : {output_path}")

    try:
        concat_files(source_directory, output_path, headless_mode=True)
        print(f"gentxt: Succès ! Fichier généré : {output_path}")
    except Exception as e:
        error_message = (
            f"gentxt ERREUR: Une erreur est survenue lors de la concaténation headless:\n{e}\n"
            f"Répertoire source tenté: {source_directory}\n"
            f"Fichier de sortie tenté: {output_path}\n"
        )
        print(error_message)
        try:
            with open(error_log_path, "w", encoding="utf-8") as f_err:
                f_err.write(error_message)
        except Exception as log_e:
            print(f"gentxt ERREUR CRITIQUE: Impossible d'écrire le log : {log_e}")