# Utiliser une image Python légère
FROM python:3.9-slim

# Éviter les questions interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Mettre à jour le système et installer les dépendances système
RUN apt-get update && apt-get install -y \
    nmap \
    tshark \
    x11-apps \
    libmagic1 \
    libpcap-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
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
RUN pip install --no-cache-dir -r requirements.txt

# Créer les répertoires nécessaires
RUN mkdir -p results logs

# Exposer les ports
EXPOSE 5000

# Variables d'environnement
ENV DISPLAY=host.docker.internal:0.0
ENV QT_X11_NO_MITSHM=1
ENV PYTHONUNBUFFERED=1

# Commande par défaut pour lancer l'application
CMD ["python", "security_toolbox.py"] 
