#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QLineEdit, QComboBox, QTabWidget, QMessageBox,
                            QFileDialog, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import json
import datetime
import subprocess
import threading
import queue
import netifaces
import requests

class ToolOutputThread(QThread):
    """Thread pour exécuter les outils en arrière-plan"""
    output = pyqtSignal(str)
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, tool_name, params):
        super().__init__()
        self.tool_name = tool_name
        self.params = params
        self.output_queue = queue.Queue()

    def run(self):
        try:
            if self.tool_name == "nmap":
                self.run_nmap()
            elif self.tool_name == "tshark":
                self.run_tshark()
            elif self.tool_name == "zap":
                self.run_zap()
            elif self.tool_name == "forensic":
                self.run_forensic()
        except Exception as e:
            self.output.emit(f"Erreur: {str(e)}")
            self.finished.emit({"error": str(e)})

    def run_nmap(self):
        target = self.params.get("target", "")
        options = self.params.get("options", "-sT -sV -O -A -p 1-1000")
        
        cmd = ["python", "nmap_scan.py", target]
        if options:
            cmd.append(options)
            
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output.emit(output.strip())
                # Mise à jour de la progression basée sur la sortie
                if "Scanning" in output:
                    self.progress.emit(50)
                elif "Nmap done" in output:
                    self.progress.emit(100)

        # Récupérer les résultats JSON
        try:
            with open(f"results/nmap_scan_{target.replace('.', '_')}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json", 'r') as f:
                results = json.load(f)
                self.finished.emit(results)
        except Exception as e:
            self.finished.emit({"error": f"Erreur lors de la lecture des résultats: {str(e)}"})

    def run_tshark(self):
        interface = self.params.get("interface", "")
        packet_count = self.params.get("packet_count", "10")
        
        cmd = ["python", "tshark_scan.py", interface, packet_count]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        packets_captured = 0
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output.emit(output.strip())
                if "paquet capturé" in output.lower():
                    packets_captured += 1
                    progress = int((packets_captured / int(packet_count)) * 100)
                    self.progress.emit(progress)

        # Récupérer les résultats JSON
        try:
            with open(f"results/tshark_capture_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json", 'r') as f:
                results = json.load(f)
                self.finished.emit(results)
        except Exception as e:
            self.finished.emit({"error": f"Erreur lors de la lecture des résultats: {str(e)}"})

    def run_zap(self):
        target = self.params.get("target", "")
        
        cmd = ["python", "zap_scan.py", target]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output.emit(output.strip())
                # Mise à jour de la progression basée sur la sortie
                if "Scanning" in output:
                    self.progress.emit(50)
                elif "Scan completed" in output:
                    self.progress.emit(100)

        # Récupérer les résultats JSON
        try:
            with open(f"results/zap_scan_{target.replace('.', '_')}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json", 'r') as f:
                results = json.load(f)
                self.finished.emit(results)
        except Exception as e:
            self.finished.emit({"error": f"Erreur lors de la lecture des résultats: {str(e)}"})

    def run_forensic(self):
        target = self.params.get("target", "")
        
        cmd = ["python", "forensic_analyzer.py", target]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.output.emit(output.strip())
                # Mise à jour de la progression basée sur la sortie
                if "Analyse" in output:
                    self.progress.emit(50)
                elif "Analyse terminée" in output:
                    self.progress.emit(100)

        # Récupérer les résultats JSON
        try:
            with open(f"results/forensic-result-{os.path.basename(target).replace('.', '_')}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json", 'r') as f:
                results = json.load(f)
                self.finished.emit(results)
        except Exception as e:
            self.finished.emit({"error": f"Erreur lors de la lecture des résultats: {str(e)}"})

class SecurityToolbox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Security Toolbox")
        self.setMinimumSize(1200, 800)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        layout = QVBoxLayout(main_widget)
        
        # Création des onglets
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Onglet Nmap
        nmap_tab = QWidget()
        nmap_layout = QVBoxLayout(nmap_tab)
        
        # Configuration Nmap
        nmap_config = QHBoxLayout()
        nmap_config.addWidget(QLabel("Cible:"))
        self.nmap_target = QLineEdit()
        nmap_config.addWidget(self.nmap_target)
        nmap_config.addWidget(QLabel("Options:"))
        self.nmap_options = QLineEdit("-sT -sV -O -A -p 1-1000")
        nmap_config.addWidget(self.nmap_options)
        nmap_layout.addLayout(nmap_config)
        
        # Bouton Nmap
        nmap_button = QPushButton("Lancer le scan Nmap")
        nmap_button.clicked.connect(lambda: self.run_tool("nmap"))
        nmap_layout.addWidget(nmap_button)
        
        # Barre de progression Nmap
        self.nmap_progress = QProgressBar()
        nmap_layout.addWidget(self.nmap_progress)
        
        # Terminal Nmap
        self.nmap_terminal = QTextEdit()
        self.nmap_terminal.setReadOnly(True)
        nmap_layout.addWidget(self.nmap_terminal)
        
        # Bouton d'envoi à l'API
        nmap_api_button = QPushButton("Envoyer les résultats à l'API")
        nmap_api_button.clicked.connect(lambda: self.send_to_api("nmap"))
        nmap_layout.addWidget(nmap_api_button)
        
        tabs.addTab(nmap_tab, "Nmap")
        
        # Onglet Tshark
        tshark_tab = QWidget()
        tshark_layout = QVBoxLayout(tshark_tab)
        
        # Configuration Tshark
        tshark_config = QHBoxLayout()
        tshark_config.addWidget(QLabel("Interface:"))
        self.tshark_interface = QComboBox()
        self.tshark_interface.addItems(netifaces.interfaces())
        tshark_config.addWidget(self.tshark_interface)
        tshark_config.addWidget(QLabel("Nombre de paquets:"))
        self.tshark_packets = QLineEdit("10")
        tshark_config.addWidget(self.tshark_packets)
        tshark_layout.addLayout(tshark_config)
        
        # Bouton Tshark
        tshark_button = QPushButton("Lancer la capture Tshark")
        tshark_button.clicked.connect(lambda: self.run_tool("tshark"))
        tshark_layout.addWidget(tshark_button)
        
        # Barre de progression Tshark
        self.tshark_progress = QProgressBar()
        tshark_layout.addWidget(self.tshark_progress)
        
        # Terminal Tshark
        self.tshark_terminal = QTextEdit()
        self.tshark_terminal.setReadOnly(True)
        tshark_layout.addWidget(self.tshark_terminal)
        
        # Bouton d'envoi à l'API
        tshark_api_button = QPushButton("Envoyer les résultats à l'API")
        tshark_api_button.clicked.connect(lambda: self.send_to_api("tshark"))
        tshark_layout.addWidget(tshark_api_button)
        
        tabs.addTab(tshark_tab, "Tshark")
        
        # Onglet ZAP
        zap_tab = QWidget()
        zap_layout = QVBoxLayout(zap_tab)
        
        # Configuration ZAP
        zap_config = QHBoxLayout()
        zap_config.addWidget(QLabel("URL cible:"))
        self.zap_target = QLineEdit()
        zap_config.addWidget(self.zap_target)
        zap_layout.addLayout(zap_config)
        
        # Bouton ZAP
        zap_button = QPushButton("Lancer le scan ZAP")
        zap_button.clicked.connect(lambda: self.run_tool("zap"))
        zap_layout.addWidget(zap_button)
        
        # Barre de progression ZAP
        self.zap_progress = QProgressBar()
        zap_layout.addWidget(self.zap_progress)
        
        # Terminal ZAP
        self.zap_terminal = QTextEdit()
        self.zap_terminal.setReadOnly(True)
        zap_layout.addWidget(self.zap_terminal)
        
        # Bouton d'envoi à l'API
        zap_api_button = QPushButton("Envoyer les résultats à l'API")
        zap_api_button.clicked.connect(lambda: self.send_to_api("zap"))
        zap_layout.addWidget(zap_api_button)
        
        tabs.addTab(zap_tab, "ZAP")
        
        # Onglet Forensic
        forensic_tab = QWidget()
        forensic_layout = QVBoxLayout(forensic_tab)
        
        # Configuration Forensic
        forensic_config = QHBoxLayout()
        forensic_config.addWidget(QLabel("Fichier cible:"))
        self.forensic_target = QLineEdit()
        forensic_config.addWidget(self.forensic_target)
        forensic_browse = QPushButton("Parcourir...")
        forensic_browse.clicked.connect(lambda: self.browse_file("forensic"))
        forensic_config.addWidget(forensic_browse)
        forensic_layout.addLayout(forensic_config)
        
        # Bouton Forensic
        forensic_button = QPushButton("Lancer l'analyse forensique")
        forensic_button.clicked.connect(lambda: self.run_tool("forensic"))
        forensic_layout.addWidget(forensic_button)
        
        # Barre de progression Forensic
        self.forensic_progress = QProgressBar()
        forensic_layout.addWidget(self.forensic_progress)
        
        # Terminal Forensic
        self.forensic_terminal = QTextEdit()
        self.forensic_terminal.setReadOnly(True)
        forensic_layout.addWidget(self.forensic_terminal)
        
        # Bouton d'envoi à l'API
        forensic_api_button = QPushButton("Envoyer les résultats à l'API")
        forensic_api_button.clicked.connect(lambda: self.send_to_api("forensic"))
        forensic_layout.addWidget(forensic_api_button)
        
        tabs.addTab(forensic_tab, "Forensic")
        
        # Création du dossier results s'il n'existe pas
        os.makedirs("results", exist_ok=True)

    def browse_file(self, tool_name):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier",
            "",
            "Tous les fichiers (*.*)"
        )
        if file_name:
            if tool_name == "forensic":
                self.forensic_target.setText(file_name)

    def run_tool(self, tool_name):
        # Récupération des paramètres selon l'outil
        params = {}
        if tool_name == "nmap":
            params["target"] = self.nmap_target.text()
            params["options"] = self.nmap_options.text()
            terminal = self.nmap_terminal
            progress = self.nmap_progress
        elif tool_name == "tshark":
            params["interface"] = self.tshark_interface.currentText()
            params["packet_count"] = self.tshark_packets.text()
            terminal = self.tshark_terminal
            progress = self.tshark_progress
        elif tool_name == "zap":
            params["target"] = self.zap_target.text()
            terminal = self.zap_terminal
            progress = self.zap_progress
        elif tool_name == "forensic":
            params["target"] = self.forensic_target.text()
            terminal = self.forensic_terminal
            progress = self.forensic_progress

        # Vérification des paramètres
        if not all(params.values()):
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs requis.")
            return

        # Effacer le terminal et réinitialiser la progression
        terminal.clear()
        progress.setValue(0)

        # Créer et démarrer le thread
        self.thread = ToolOutputThread(tool_name, params)
        self.thread.output.connect(lambda text: terminal.append(text))
        self.thread.progress.connect(progress.setValue)
        self.thread.finished.connect(lambda results: self.handle_results(tool_name, results))
        self.thread.start()

    def handle_results(self, tool_name, results):
        if "error" in results:
            QMessageBox.warning(self, "Erreur", f"Une erreur est survenue: {results['error']}")
        else:
            QMessageBox.information(self, "Succès", f"L'analyse {tool_name} est terminée avec succès.")

    def send_to_api(self, tool_name):
        try:
            # Trouver le dernier fichier de résultats
            results_dir = "results"
            files = [f for f in os.listdir(results_dir) if f.startswith(f"{tool_name}_")]
            if not files:
                QMessageBox.warning(self, "Erreur", "Aucun résultat trouvé à envoyer.")
                return

            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
            file_path = os.path.join(results_dir, latest_file)

            # Lire et envoyer les résultats
            with open(file_path, 'r') as f:
                results = json.load(f)

            response = requests.post(
                "http://127.0.0.1:5000/api/v1/report/upload_json/",
                json=results,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            QMessageBox.information(self, "Succès", "Résultats envoyés avec succès à l'API.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'envoi à l'API: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle("Fusion")
    
    # Police moderne
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = SecurityToolbox()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 