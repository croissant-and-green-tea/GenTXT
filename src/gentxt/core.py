#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de logique métier pour la concaténation de fichiers
"""

import os
import re
from typing import Optional

from .config import get_effective_config


# ============================================
# DÉTECTION DE FICHIERS BINAIRES
# ============================================

def is_binary_file(filepath: str) -> bool:
    """
    Tente de déterminer si un fichier est binaire en lisant ses premiers octets.
    Retourne True si le fichier semble binaire, False sinon.
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if not chunk:
                return True
            if b'\x00' in chunk:
                return True
            text_characters = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            non_text = sum(1 for byte in chunk if byte not in text_characters)
            return non_text / len(chunk) > 0.3
    except Exception:
        return True


# ============================================
# LECTURE DU CONTENU DES FICHIERS
# ============================================

def read_file_content(filepath: str) -> Optional[str]:
    """
    Lit et retourne le contenu d'un fichier texte.
    Retourne None si le fichier est binaire ou illisible.
    """
    if is_binary_file(filepath):
        return None

    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        except Exception:
            continue

    return None


def read_ods_file(filepath: str) -> str:
    """
    Lit le contenu d'un fichier ODS et retourne une chaîne formatée.
    """
    try:
        import pyexcel_ods3 as ods
        data = ods.get_data(filepath)

        output_lines = []
        for sheet_name, rows in data.items():
            output_lines.append(f"=== Feuille: {sheet_name} ===\n")
            for row in rows:
                row_str = "\t".join(str(cell) for cell in row)
                output_lines.append(row_str)
            output_lines.append("\n")

        return "\n".join(output_lines)

    except ImportError:
        return "[ERREUR: La bibliothèque pyexcel-ods3 n'est pas installée. Installez-la pour lire les fichiers .ods]"
    except Exception as e:
        return f"[ERREUR lors de la lecture du fichier ODS: {e}]"


def read_odt_file(filepath: str) -> str:
    """
    Lit le contenu d'un fichier ODT et retourne le texte extrait.
    """
    try:
        from odf import text as odf_text, teletype
        from odf.opendocument import load as odf_load

        doc = odf_load(filepath)
        all_paragraphs = doc.getElementsByType(odf_text.P)
        text_content = "\n".join(teletype.extractText(p) for p in all_paragraphs)

        return text_content if text_content.strip() else "[Fichier ODT vide ou sans contenu textuel extractible]"

    except ImportError:
        return "[ERREUR: La bibliothèque odfpy n'est pas installée. Installez-la pour lire les fichiers .odt]"
    except Exception as e:
        return f"[ERREUR lors de la lecture du fichier ODT: {e}]"


# ============================================
# GÉNÉRATION DE L'ARBORESCENCE
# ============================================

def generate_tree(
    directory: str,
    config: dict[str, set[str]],
    prefix: str = "",
    is_last: bool = True,
    is_root: bool = True,
) -> list[str]:
    """
    Génère une représentation textuelle de l'arborescence du répertoire.
    """
    exclude_tree_dirs = config["exclude_tree_dirs"]
    exclude_tree_files = config["exclude_tree_files"]
    exclude_tree_extensions = config["exclude_tree_extensions"]

    lines = []

    if is_root:
        lines.append(os.path.basename(os.path.abspath(directory)))

    try:
        entries = sorted(os.listdir(directory))
    except PermissionError:
        return lines

    dirs = []
    files = []

    for entry in entries:
        entry_path = os.path.join(directory, entry)

        if os.path.isdir(entry_path):
            if entry not in exclude_tree_dirs:
                dirs.append(entry)
        elif os.path.isfile(entry_path):
            if entry in exclude_tree_files:
                continue
            _, ext = os.path.splitext(entry)
            if ext.lower() in exclude_tree_extensions:
                continue
            files.append(entry)

    all_items = dirs + files

    for i, item in enumerate(all_items):
        is_last_item = (i == len(all_items) - 1)
        connector = "└── " if is_last_item else "├── "
        lines.append(prefix + connector + item)

        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            extension = "    " if is_last_item else "│   "
            sub_lines = generate_tree(
                item_path,
                config,
                prefix=prefix + extension,
                is_last=is_last_item,
                is_root=False,
            )
            lines.extend(sub_lines)

    return lines


# ============================================
# CONCATÉNATION DES FICHIERS
# ============================================

def concat_files(source_directory: str, output_file: str, headless_mode: bool = False) -> None:
    """
    Concatène les fichiers du répertoire source dans le fichier de sortie.
    Les erreurs par fichier sont collectées et reportées en fin de traitement
    sans interrompre le pipeline.
    """
    config = get_effective_config(source_directory, headless_mode=headless_mode)

    exclude_content_dirs = config["exclude_content_dirs"]
    exclude_content_files = config["exclude_content_files"]
    exclude_content_extensions = config["exclude_content_extensions"]

    file_errors: list[tuple[str, str]] = []

    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.write("# === Arborescence du dossier ===\n\n")

        tree_lines = generate_tree(source_directory, config)
        out_f.write("\n".join(tree_lines))
        out_f.write("\n\n\n")

        out_f.write("# === Contenu des fichiers ===\n\n")

        for root, dirs, files in os.walk(source_directory, topdown=True):
            dirs[:] = sorted(d for d in dirs if d not in exclude_content_dirs)

            for file in sorted(files):
                if file in exclude_content_files:
                    continue

                _, ext = os.path.splitext(file)
                if ext.lower() in exclude_content_extensions:
                    continue

                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, source_directory)

                out_f.write(f"--- Fichier : {relative_path} ---\n")

                try:
                    if ext.lower() == ".ods":
                        content = read_ods_file(filepath)
                        out_f.write(content + "\n\n")
                    elif ext.lower() == ".odt":
                        content = read_odt_file(filepath)
                        out_f.write(content + "\n\n")
                    else:
                        content = read_file_content(filepath)
                        if content is not None:
                            out_f.write(content + "\n\n")
                        else:
                            out_f.write("[Fichier binaire ou illisible, contenu ignoré]\n\n")
                except Exception as exc:
                    error_msg = f"[ERREUR lors de la lecture : {exc}]"
                    out_f.write(error_msg + "\n\n")
                    file_errors.append((relative_path, str(exc)))

    if file_errors:
        error_summary = "\n".join(f"  - {path}: {err}" for path, err in file_errors)
        if headless_mode:
            print(f"GenTXT: {len(file_errors)} fichier(s) en erreur :\n{error_summary}")
        else:
            print(f"Avertissement : {len(file_errors)} fichier(s) en erreur :\n{error_summary}")

    _clean_excessive_newlines(output_file)


def _clean_excessive_newlines(filepath: str) -> None:
    """
    Réduit les passages à la ligne de plus de 5 lignes vides consécutives à seulement 2 lignes vides.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    cleaned_content = re.sub(r'\n{6,}', '\n\n\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)