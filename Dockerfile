# Utiliser une image Python légère
FROM python:3.9-slim

# Éviter les questions interactives pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Mettre à jour le système et installer les dépendances système
RUN apt-get update && apt-get install -y \
    gnupg2 \
    software-properties-common \
    && echo "deb http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list \
    && echo "deb http://security.debian.org/debian-security bullseye-security main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y \
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
    # Qt dependencies
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    xvfb \
    # Outils forensiques
    binwalk \
    foremost \
    exiftool \
    xxd \
    file \
    # Outils de hachage
    hashdeep \
    # Outils supplémentaires pour l'analyse forensique
    python3-magic \
    python3-yara \
    yara \
    && rm -rf /var/lib/apt/lists/*

# Installation de Radare2
RUN git clone https://github.com/radareorg/radare2.git \
    && cd radare2 \
    && ./sys/install.sh \
    && cd .. \
    && rm -rf radare2

# Installation de Volatility3
RUN git clone https://github.com/volatilityfoundation/volatility3.git \
    && cd volatility3 \
    && pip install -e . \
    && cd .. \
    && rm -rf volatility3

# Installation de ZAP
RUN wget https://github.com/zaproxy/zaproxy/releases/download/v2.15.0/ZAP_2.15.0_Linux.tar.gz \
    && tar -xf ZAP_2.15.0_Linux.tar.gz \
    && mv ZAP_2.15.0 /opt/zap \
    && rm ZAP_2.15.0_Linux.tar.gz

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
ENV QT_DEBUG_PLUGINS=1
ENV QT_LOGGING_RULES="*.debug=true"
ENV QT_X11_NO_MITSHM=1
ENV QT_QPA_PLATFORM=offscreen

# Script de démarrage
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Commande par défaut
CMD ["/start.sh"] 
