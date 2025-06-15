#!/bin/bash

# Activer le mode debug
set -x

# Démarrer Xvfb
Xvfb :0 -screen 0 1024x768x24 &
export DISPLAY=:0

# Vérifier les dépendances
echo "Vérification des dépendances..."
which python3 || { echo "Python3 non trouvé"; exit 1; }
which nmap || { echo "Nmap non trouvé"; exit 1; }
which tshark || { echo "Tshark non trouvé"; exit 1; }
which binwalk || { echo "Binwalk non trouvé"; exit 1; }

# Vérifier les répertoires
echo "Vérification des répertoires..."
[ -d "/app" ] || { echo "Répertoire /app non trouvé"; exit 1; }
[ -d "/app/results" ] || { echo "Répertoire /app/results non trouvé"; exit 1; }
[ -d "/app/logs" ] || { echo "Répertoire /app/logs non trouvé"; exit 1; }

# Vérifier les fichiers Python
echo "Vérification des fichiers Python..."
[ -f "/app/security_toolbox.py" ] || { echo "security_toolbox.py non trouvé"; exit 1; }
[ -d "/app/Forensic" ] || { echo "Répertoire Forensic non trouvé"; exit 1; }
[ -d "/app/Nmap" ] || { echo "Répertoire Nmap non trouvé"; exit 1; }
[ -d "/app/Tshark" ] || { echo "Répertoire Tshark non trouvé"; exit 1; }
[ -d "/app/Zap" ] || { echo "Répertoire Zap non trouvé"; exit 1; }

# Vérifier les variables d'environnement
echo "Vérification des variables d'environnement..."
[ -n "$DISPLAY" ] || { echo "DISPLAY non défini"; exit 1; }

# Démarrer l'application
echo "Démarrage de l'application..."
cd /app
exec python3 security_toolbox.py 2>&1 | tee /app/logs/app.log 
