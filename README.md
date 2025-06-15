# 🛡️ SCAN\_SOC\_FORENSIC Toolkit

Bienvenue dans **SCAN\_SOC\_FORENSIC**, un ensemble d’outils de cybersécurité conçus pour automatiser l'analyse réseau, l'analyse de malwares, le scan de ports et l'audit de vulnérabilités web. Tous les scripts sont compatibles avec Kali Linux.

---

## 🔧 Installation des Dépendances

Avant de commencer, assure-toi d'avoir les outils suivants installés sur ton système :

```bash
sudo apt update
sudo apt install python3-nmap zaproxy tshark
```

---

## ------------------------------- Foresnic -------------------

### Script : `forensic_analyzer.py`

Analyse statique d'un exécutable pour détecter des comportements suspects.

#### Exemple de commande :

```bash
python3 forensic_analyzer.py /chemin/vers/malware_test.exe --verbose
```

> ✅ Un malware de test a été créé pour simuler une analyse.

---

## ------------------------------------ ZAP -------------------------------------

### Outil : OWASP ZAP via `zap_scan.py`

Scan de vulnérabilités web automatisé grâce à OWASP ZAP en mode daemon.

#### Installation de ZAP :

```bash
sudo apt install zaproxy
```

#### Démarrage de ZAP en mode daemon : - si besoin

```bash
zaproxy -daemon -port 8080 \
  -config api.addrs.addr.name=.* \
  -config api.addrs.addr.regex=true \
  -config api.key=changeme
```

#### Lancer le scan avec le script Python :

```bash
python3 zap_scan.py https://supdevinci.fr/
```

---

## ------------------------------------ Nmap -------------------------------------

### Script : `nmap_scan.py`

Scan des ports sur une machine cible via le module Python `nmap`.

#### Installation :

```bash
sudo apt install python3-nmap
```

#### Exemple d'utilisation :

```bash
python3 nmap_scan.py 192.168.1.15
```

> ⚡ Fournit une vue rapide des ports ouverts sur une cible locale.

---

## ------------------------------------ Tshark -------------------------------------

### Script : `tshark_scan.py`

Capture de paquets réseau en ligne de commande avec `tshark`.

#### Exemple d'utilisation :

```bash
python3 tshark_scan.py eth0 10
```

* `eth0` : interface réseau à surveiller
* `10` : nombre de paquets à capturer (modulable selon besoin)

> 🚀 Peut être utilisé pour analyser rapidement du trafic en temps réel.

---
