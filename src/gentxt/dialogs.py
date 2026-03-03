#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module des dialogues pour GenTXT
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QTextEdit, QDialogButtonBox, QLabel,
    QLineEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

from .config import CONFIG_FILENAME, create_default_config, load_config, save_config


class SimpleFolderDialog(QDialog):
    """Dialogue de sélection de dossier avec barre d'adresse éditable et explorateur."""
    
    def __init__(self, title, start_dir="", parent=None, show_files=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 500)
        self.show_files = show_files
        
        if not start_dir or not os.path.isdir(start_dir):
            start_dir = os.path.expanduser("~")
        
        self.current_path = start_dir
        self.selected_path = start_dir
        
        layout = QVBoxLayout()
        
        # Barre d'adresse éditable
        addr_layout = QHBoxLayout()
        
        # Bouton Parent
        self.btn_up = QPushButton("↑ Dossier parent")
        self.btn_up.clicked.connect(self.go_parent)
        addr_layout.addWidget(self.btn_up)
        
        # Champ d'adresse
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_path)
        self.path_edit.returnPressed.connect(self.navigate_to_typed_path)
        addr_layout.addWidget(self.path_edit, stretch=1)
        
        layout.addLayout(addr_layout)
        
        # Liste des dossiers/fichiers
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Boutons OK/Annuler
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        
        # Empêcher le bouton OK d'être le bouton par défaut
        ok_button = button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setAutoDefault(False)
            ok_button.setDefault(False)
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setAutoDefault(False)
            cancel_button.setDefault(False)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Charger le dossier initial
        self.load_directory(self.current_path)
    
    def load_directory(self, path):
        """Charge et affiche le contenu d'un dossier."""
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Erreur", f"Le chemin n'est pas un dossier valide : {path}")
            return
        
        self.current_path = os.path.abspath(path)
        self.path_edit.setText(self.current_path)
        self.list_widget.clear()
        
        try:
            entries = sorted(os.listdir(self.current_path))
            
            for entry in entries:
                full_path = os.path.join(self.current_path, entry)
                item = QListWidgetItem(entry)
                
                if os.path.isdir(full_path):
                    item.setText("📁 " + entry)
                    item.setData(Qt.UserRole, full_path)
                    self.list_widget.addItem(item)
                elif self.show_files and os.path.isfile(full_path):
                    item.setText("📄 " + entry)
                    item.setData(Qt.UserRole, full_path)
                    self.list_widget.addItem(item)
                
        except PermissionError:
            QMessageBox.warning(self, "Erreur", f"Permission refusée pour accéder à : {self.current_path}")
    
    def item_double_clicked(self, item):
        """Gère le double-clic sur un élément."""
        path = item.data(Qt.UserRole)
        if path and os.path.isdir(path):
            self.load_directory(path)
    
    def go_parent(self):
        """Remonte au dossier parent."""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)
    
    def navigate_to_typed_path(self):
        """Navigue vers le chemin tapé dans la barre d'adresse."""
        path = self.path_edit.text().strip()
        if path and os.path.isdir(path):
            self.load_directory(path)
        else:
            QMessageBox.warning(self, "Erreur", f"Le chemin n'est pas valide : {path}")
            self.path_edit.setText(self.current_path)
    
    def accept_selection(self):
        """Valide la sélection."""
        path = self.current_path
        if not path:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un dossier.")
            return
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Erreur", "Le chemin n'est pas un dossier valide.")
            return
        self.selected_path = path
        self.accept()
    
    def get_selected_path(self):
        """Retourne le chemin sélectionné."""
        return self.selected_path
    
    def keyPressEvent(self, event):
        """Intercepte les événements clavier pour empêcher Entrée de valider."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.path_edit.hasFocus():
                self.navigate_to_typed_path()
            event.accept()
        else:
            super().keyPressEvent(event)


class SimpleFileSaveDialog(QDialog):
    """Dialogue de sauvegarde de fichier avec barre d'adresse éditable et explorateur."""
    
    def __init__(self, title, default_path="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(700, 550)
        
        if default_path and os.path.isfile(default_path):
            start_dir = os.path.dirname(default_path)
            default_filename = os.path.basename(default_path)
        elif default_path and os.path.isdir(default_path):
            start_dir = default_path
            default_filename = ""
        else:
            start_dir = os.path.expanduser("~")
            default_filename = ""
        
        self.current_path = start_dir
        self.selected_file = default_path
        
        layout = QVBoxLayout()
        
        # Barre d'adresse
        addr_layout = QHBoxLayout()
        self.btn_up = QPushButton("↑ Dossier parent")
        self.btn_up.clicked.connect(self.go_parent)
        addr_layout.addWidget(self.btn_up)
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_path)
        self.path_edit.returnPressed.connect(self.navigate_to_typed_path)
        addr_layout.addWidget(self.path_edit, stretch=1)
        
        layout.addLayout(addr_layout)
        
        # Liste
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)
        self.list_widget.itemClicked.connect(self.item_clicked)
        layout.addWidget(self.list_widget)
        
        # Champ nom de fichier
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("Nom du fichier :"))
        self.filename_edit = QLineEdit()
        self.filename_edit.setText(default_filename)
        self.filename_edit.returnPressed.connect(lambda: None)
        filename_layout.addWidget(self.filename_edit)
        layout.addLayout(filename_layout)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setAutoDefault(False)
            ok_button.setDefault(False)
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setAutoDefault(False)
            cancel_button.setDefault(False)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.load_directory(self.current_path)
    
    def load_directory(self, path):
        """Charge et affiche le contenu d'un dossier."""
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Erreur", f"Le chemin n'est pas un dossier valide : {path}")
            return
        
        self.current_path = os.path.abspath(path)
        self.path_edit.setText(self.current_path)
        self.list_widget.clear()
        
        try:
            entries = sorted(os.listdir(self.current_path))
            
            for entry in entries:
                full_path = os.path.join(self.current_path, entry)
                item = QListWidgetItem(entry)
                
                if os.path.isdir(full_path):
                    item.setText("📁 " + entry)
                    item.setData(Qt.UserRole, full_path)
                    item.setData(Qt.UserRole + 1, "dir")
                elif os.path.isfile(full_path):
                    item.setText("📄 " + entry)
                    item.setData(Qt.UserRole, full_path)
                    item.setData(Qt.UserRole + 1, "file")
                
                self.list_widget.addItem(item)
                
        except PermissionError:
            QMessageBox.warning(self, "Erreur", f"Permission refusée pour accéder à : {self.current_path}")
    
    def item_double_clicked(self, item):
        """Gère le double-clic."""
        item_type = item.data(Qt.UserRole + 1)
        path = item.data(Qt.UserRole)
        
        if item_type == "dir" and os.path.isdir(path):
            self.load_directory(path)
    
    def item_clicked(self, item):
        """Gère le clic simple."""
        item_type = item.data(Qt.UserRole + 1)
        if item_type == "file":
            filename = item.text().replace("📄 ", "")
            self.filename_edit.setText(filename)
    
    def go_parent(self):
        """Remonte au dossier parent."""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)
    
    def navigate_to_typed_path(self):
        """Navigue vers le chemin tapé."""
        path = self.path_edit.text().strip()
        if path and os.path.isdir(path):
            self.load_directory(path)
        else:
            QMessageBox.warning(self, "Erreur", f"Le chemin n'est pas valide : {path}")
            self.path_edit.setText(self.current_path)
    
    def accept_selection(self):
        """Valide la sélection."""
        filename = self.filename_edit.text().strip()
        if not filename:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir un nom de fichier.")
            return
        
        self.selected_file = os.path.join(self.current_path, filename)
        self.accept()
    
    def get_selected_file(self):
        """Retourne le chemin du fichier sélectionné."""
        return self.selected_file
    
    def keyPressEvent(self, event):
        """Intercepte les événements clavier."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.path_edit.hasFocus():
                self.navigate_to_typed_path()
            event.accept()
        else:
            super().keyPressEvent(event)


class ConfigEditorDialog(QDialog):
    """Dialogue pour créer ou modifier la configuration avec format simplifié."""
    
    def __init__(self, directory, parent=None):
        super().__init__(parent)
        self.directory = directory
        self.setWindowTitle("Éditeur de Configuration")
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(
            f"Éditer/Créer la configuration pour :\n{directory}\n\n"
            "Format : # section_name suivi d'une ligne par élément (sans guillemets ni virgules)."
        )
        layout.addWidget(info_label)
        
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        
        # Charger la config existante ou créer un template
        existing_config = load_config(directory)
        if existing_config:
            self.text_edit.setPlainText(self._config_to_text(existing_config))
        else:
            default_config = create_default_config()
            response = QMessageBox.question(
                self,
                "Aucune Configuration",
                "Aucune configuration existante. Voulez-vous créer un fichier de configuration avec les valeurs par défaut ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self.text_edit.setPlainText(self._config_to_text(default_config))
            else:
                self.reject()
                return
        
        layout.addWidget(self.text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _config_to_text(self, config):
        """Convertit la config dict en format texte simplifié."""
        lines = []
        for key, values in config.items():
            lines.append(f"# {key}")
            for value in sorted(values):
                lines.append(value)
            lines.append("")  # Ligne vide entre sections
        return "\n".join(lines)
    
    def _text_to_config(self, text):
        """Convertit le texte simplifié en config dict."""
        config = {}
        current_key = None
        
        for line in text.split("\n"):
            line = line.strip()
            
            # Ignorer les lignes vides
            if not line:
                continue
            
            # Détecter une section
            if line.startswith("#"):
                current_key = line[1:].strip()
                config[current_key] = set()
            # Ajouter une valeur à la section courante
            elif current_key:
                config[current_key].add(line)
        
        # Vérifier que toutes les clés attendues sont présentes
        default_keys = create_default_config().keys()
        for key in default_keys:
            if key not in config:
                config[key] = set()
        
        return config
    
    def save_config(self):
        """Sauvegarde la configuration."""
        content = self.text_edit.toPlainText()
        
        try:
            config_for_saving = self._text_to_config(content)
            
            if save_config(self.directory, config_for_saving, headless_mode=False):
                QMessageBox.information(self, "Succès", f"{CONFIG_FILENAME} sauvegardé avec succès.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")