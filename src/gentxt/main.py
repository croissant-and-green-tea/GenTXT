#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Point d'entrée gentxt — GUI PySide6."""

import os
import sys

from gentxt.headless import run_headless_mode, HEADLESS_ERROR_LOG_FILE  # noqa: F401


def _build_main_window():
    """Instancie MainWindow — importe PySide6 uniquement à l'appel."""
    from PySide6.QtWidgets import (
        QDialog, QMainWindow, QMessageBox,
        QPushButton, QVBoxLayout, QWidget,
    )
    from gentxt.core import concat_files
    from gentxt.dialogs import ConfigEditorDialog, SimpleFolderDialog, SimpleFileSaveDialog

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("gentxt - Concaténation v2.4.1")
            self.resize(500, 300)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(10)

            btn_start_auto = QPushButton("Démarrer")
            btn_start_auto.setMinimumHeight(50)
            btn_start_auto.clicked.connect(lambda: self.start_process(choose_destination=False))

            btn_start_choose = QPushButton("Démarrer - Choisir destination")
            btn_start_choose.setMinimumHeight(50)
            btn_start_choose.clicked.connect(lambda: self.start_process(choose_destination=True))

            btn_config = QPushButton("Créer / Modifier Configuration")
            btn_config.setMinimumHeight(50)
            btn_config.clicked.connect(self.create_or_edit_config)

            btn_quit = QPushButton("Quitter")
            btn_quit.setMinimumHeight(50)
            btn_quit.clicked.connect(self.close)

            layout.addWidget(btn_start_auto)
            layout.addWidget(btn_start_choose)
            layout.addWidget(btn_config)
            layout.addWidget(btn_quit)
            layout.addStretch()

            central_widget.setLayout(layout)

        def start_process(self, choose_destination: bool = True) -> None:
            dialog = SimpleFolderDialog(
                "Sélection du dossier source",
                os.path.expanduser("~"),
                self,
                show_files=True,
            )
            if dialog.exec() != QDialog.Accepted:
                return

            source_directory = dialog.get_selected_path()
            if not source_directory or not os.path.isdir(source_directory):
                QMessageBox.warning(self, "Erreur", "Dossier invalide.")
                return

            if choose_destination:
                default_path = os.path.join(source_directory, "gentxt.txt")
                save_dialog = SimpleFileSaveDialog(
                    "Choisir le fichier de sortie", default_path, self
                )
                if save_dialog.exec() != QDialog.Accepted:
                    return
                output_file = save_dialog.get_selected_file()
            else:
                output_file = os.path.join(source_directory, "gentxt.txt")

            try:
                concat_files(source_directory, output_file, headless_mode=False)
                QMessageBox.information(self, "Succès", f"Fichier généré : {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la concaténation : {e}")

        def create_or_edit_config(self) -> None:
            dialog = SimpleFolderDialog(
                "Sélection du dossier pour la configuration",
                os.path.expanduser("~"),
                self,
                show_files=False,
            )
            if dialog.exec() != QDialog.Accepted:
                return

            directory = dialog.get_selected_path()
            if not directory or not os.path.isdir(directory):
                QMessageBox.warning(self, "Erreur", "Dossier invalide.")
                return

            config_dialog = ConfigEditorDialog(directory, self)
            config_dialog.exec()

    return MainWindow()


def main() -> None:
    if "--headless" in sys.argv or "--auto" in sys.argv:
        run_headless_mode()
    else:
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        font = app.font()
        font.setPointSize(12)
        app.setFont(font)
        window = _build_main_window()
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()