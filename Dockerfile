# Utiliser une image Python légère
FROM python:3.9-slim

# Éviter les questions interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Mettre à jour le système et installer les dépendances système utiles
RUN apt-get update && apt-get install -y \
    nmap \
    tshark \
    default-jre \
    wget \
    unzip \
    curl \
    git \
    build-essential \
    libpcap-dev \
    libmagic1 \
    libnetfilter-queue1 \
    libjpeg-dev \
    zlib1g-dev \
    binwalk \
    foremost \
    exiftool \
    xxd \
    file \
    md5deep \
    python3-magic \
    python3-yara \
    yara \
    && rm -rf /var/lib/apt/lists/*

# Installer ZAP manuellement (version stable connue)
RUN wget https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2.14.0_Linux.tar.gz \
    && tar -xf ZAP_2.14.0_Linux.tar.gz \
    && mv ZAP_2.14.0 /opt/zap \
    && rm ZAP_2.14.0_Linux.tar.gz

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
RUN mkdir -p results logs input output rules

# Exposer les ports
EXPOSE 5000

# Variables d'environnement
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/zap:${PATH}"

# Commande par défaut
CMD ["python", "security_toolbox.py"]
