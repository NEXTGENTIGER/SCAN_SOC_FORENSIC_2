# Utiliser une image de base Kali Linux pour avoir accès aux outils de sécurité
FROM kalilinux/kali-rolling

# Éviter les questions interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Mettre à jour le système et installer les dépendances
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pyqt6 \
    nmap \
    tshark \
    python3-nmap \
    python3-magic \
    python3-netifaces \
    python3-requests \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire pour l'application
WORKDIR /app

# Copier les fichiers de l'application
COPY requirements.txt .
COPY security_toolbox.py .
COPY Forensic/ ./Forensic/
COPY Nmap/ ./Nmap/
COPY Tshark/ ./Tshark/
COPY Zap/ ./Zap/

# Installer les dépendances Python
RUN pip3 install -r requirements.txt

# Créer un répertoire pour les résultats
RUN mkdir -p results

# Exposer le port pour l'API
EXPOSE 5000

# Variables d'environnement pour X11
ENV DISPLAY=host.docker.internal:0.0
ENV QT_X11_NO_MITSHM=1

# Commande par défaut pour lancer l'application
CMD ["python3", "security_toolbox.py"] 