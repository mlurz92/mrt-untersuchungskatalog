# MRT Untersuchungskatalog

Diese Anleitung beschreibt detailliert, wie du den **MRT Untersuchungskatalog** auf einem Raspberry Pi 4 mit einer frischen Installation von RaspberryPiOS lite (64bit) installierst, in Betrieb nimmst, aktualisierst und bei Bedarf vollständig entfernst. Die Anwendung besteht aus einem Python-Backend (Flask, SQLite) und einem React-Frontend (mit Animationen via GSAP, Drag‑&‑Drop via react‑beautiful‑dnd und API-Anbindung via Axios). Die Bereitstellung erfolgt über HTTPS (konfiguriert mit Certbot und Nginx).

> **Hinweis:**  
> Diese Anleitung setzt grundlegende Kenntnisse im Umgang mit der Kommandozeile sowie einen funktionierenden SSH-Zugang zu deinem Raspberry Pi voraus.

---

## Inhaltsverzeichnis

- [Systemvorbereitung](#systemvorbereitung)
- [Installation der Anwendung](#installation-der-anwendung)
  - [1. Klonen des Repositories](#1-klonen-des-repositories)
  - [2. Installation der Abhängigkeiten](#2-installation-der-abhängigkeiten)
    - [Backend (Python)](#backend-python)
    - [Frontend (Node.js & npm)](#frontend-nodejs--npm)
  - [3. Einrichtung und Import der Datenbank](#3-einrichtung-und-import-der-datenbank)
  - [4. Start der Backend-API und Frontend-Anwendung](#4-start-der-backend-api-und-frontend-anwendung)
  - [5. HTTPS-Bereitstellung via Certbot und Nginx](#5-https-bereitstellung-via-certbot-und-nginx)
- [Aufrufen der Anwendung](#aufrufen-der-anwendung)
- [Update der Anwendung](#update-der-anwendung)
- [Vollständige Entfernung der Anwendung](#vollständige-entfernung-der-anwendung-und-rücksetzung-des-raspberry-pi-os)
- [Problemlösungen und Hinweise](#problemlösungen-und-hinweise)

---

## Systemvorbereitung

1. **Frische Installation von RaspberryPiOS lite (64bit):**  
   - Lade das neueste Image von [RaspberryPiOS lite (64bit)](https://www.raspberrypi.com/software/operating-systems/) herunter.  
   - Schreibe das Image mit *balenaEtcher* (oder einem vergleichbaren Tool) auf eine microSD-Karte.
   - Stecke die microSD-Karte in deinen Raspberry Pi 4, verbinde ihn mit Strom und einem Netzwerk (Ethernet oder WLAN).

2. **SSH aktivieren:**  
   - Lege in der Boot-Partition der SD-Karte eine leere Datei mit dem Namen `ssh` (ohne Erweiterung) an.
   - Starte den Pi und verbinde dich per SSH:
     ```bash
     ssh pi@raspberrypi
     ```
   - Standardbenutzer ist `pi` mit dem Passwort `raspberry` (bitte ändere das Passwort umgehend).

3. **Systemupdate durchführen:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

---

## Installation der Anwendung

### 1. Klonen des Repositories

Führe folgende Befehle aus, um das Repository zu klonen:

```bash
cd ~
git clone https://github.com/mlurz92/mrt-untersuchungskatalog.git
cd mrt-untersuchungskatalog
```

### 2. Installation der Abhängigkeiten

#### Backend (Python)

Stelle sicher, dass Python 3 und pip installiert sind. Installiere dann die benötigten Pakete:

```bash
sudo apt install python3 python3-pip -y
cd backend
pip3 install -r requirements.txt
```

*Hinweis:* In der Datei `backend/requirements.txt` stehen folgende Abhängigkeiten:
```
Flask==2.2.5
flask-cors==3.0.10
```

#### Frontend (Node.js & npm)

1. **Installation von Node.js:**  
   Für eine stabile Node.js-Version auf dem Raspberry Pi wird die Installation über NodeSource empfohlen:
   ```bash
   curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

2. **Installiere die Frontend-Abhängigkeiten:**
   ```bash
   cd ../frontend
   npm install
   ```
   *Hinweis:* Neben React, Axios, GSAP und react‑scripts wird zusätzlich *react‑beautiful‑dnd* verwendet.

### 3. Einrichtung und Import der Datenbank

Wechsle in das Backend-Verzeichnis und führe das Import-Skript aus, um die SQLite-Datenbank zu initialisieren und `protocols.json` zu importieren:

```bash
cd ../backend
python3 db.py
```

Die Ausgabe sollte etwa Folgendes enthalten:  
„Datenbank nicht gefunden. Starte Import aus 'protocols.json' …“  
und danach „Datenbank erstellt und JSON-Daten erfolgreich importiert.“

### 4. Start der Backend-API und Frontend-Anwendung

#### Backend API starten

Starte die Flask-API:

```bash
cd backend
python3 app.py
```

Die API läuft auf Port 5000.

#### Frontend-Anwendung starten

In einem separaten Terminal oder einer neuen SSH-Session:

```bash
cd ~/mrt-untersuchungskatalog/frontend
npm start
```

Die React-Anwendung wird standardmäßig auf Port 3000 bereitgestellt ([http://localhost:3000](http://localhost:3000)).

### 5. HTTPS-Bereitstellung via Certbot und Nginx

Um die Anwendung über HTTPS bereitzustellen, nutze Certbot und konfiguriere Nginx als Reverse Proxy.

1. **Certbot installieren:**
   ```bash
   sudo apt install certbot -y
   ```

2. **HTTPS-Zertifikat via Certbot anfordern:**
   ```bash
   sudo certbot certonly --standalone --preferred-challenges http -d raspberrypi.deinedomain.tld --agree-tos -m deineemail@domain.de
   ```

3. **Nginx als Reverse Proxy konfigurieren:**  
   Erstelle eine Datei unter `/etc/nginx/sites-available/mrt-untersuchungskatalog` mit folgendem Inhalt:
   ```nginx
   server {
       listen 80;
       server_name raspberrypi.hyg6zkbn2mykr1go.myfritz.net/;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name raspberrypi.hyg6zkbn2mykr1go.myfritz.net;
       
       ssl_certificate /etc/letsencrypt/live/raspberrypi.hyg6zkbn2mykr1go.myfritz.net/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/raspberrypi.hyg6zkbn2mykr1go.myfritz.net/privkey.pem;

       location /api/ {
           proxy_pass http://localhost:5000/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           proxy_pass http://localhost:3000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Nginx aktivieren und neu starten:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/mrt-untersuchungskatalog /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

Nach erfolgreichem Neustart ist die Anwendung unter der URL  
**https://raspberrypi.hyg6zkbn2mykr1go.myfritz.net/**  
erreichbar.

---

## Aufrufen der Anwendung

- **Im Browser:**  
  Öffne die URL (z. B.) [https://raspberrypi.hyg6zkbn2mykr1go.myfritz.net/](https://raspberrypi.hyg6zkbn2mykr1go.myfritz.net/).  
  Die React-basierte Benutzeroberfläche wird angezeigt. Über die linke Navigation kannst du den gewünschten Protokolleintrag auswählen und bearbeiten.

---

## Update der Anwendung

Um die Anwendung zu aktualisieren, führe folgende Befehle im Hauptverzeichnis aus:

```bash
cd ~/mrt-untersuchungskatalog
git reset --hard HEAD
git pull
```

Falls sich in den Abhängigkeiten etwas ändert:

- Für das Backend:
  ```bash
  cd backend
  pip3 install -r requirements.txt
  ```
- Für das Frontend:
  ```bash
  cd ../frontend
  npm install
  ```

Starte anschließend beide Anwendungen neu.

---

## Vollständige Entfernung der Anwendung und Rücksetzung des Raspberry Pi OS

1. **Anwendung entfernen:**
   ```bash
   rm -rf ~/mrt-untersuchungskatalog
   ```

2. **Entfernen installierter Abhängigkeiten (optional):**
   - Entferne Node.js:
     ```bash
     sudo apt remove nodejs -y
     ```
   - Entferne Python-Abhängigkeiten ggf. über virtuelle Umgebungen.

3. **Nginx-Konfiguration entfernen (falls eingerichtet):**
   ```bash
   sudo rm /etc/nginx/sites-enabled/mrt-untersuchungskatalog
   sudo rm /etc/nginx/sites-available/mrt-untersuchungskatalog
   sudo systemctl restart nginx
   ```

4. **Rücksetzung des Raspberry Pi OS:**  
   Ein Neu-Flash der SD-Karte ist die empfohlene Methode.

---

## Problemlösungen und Hinweise

- **Datenbank-Fehler:**  
  Stelle sicher, dass `protocols.db` im Backend-Verzeichnis korrekt angelegt wurde. Führe ggf. `python3 db.py` erneut aus.

- **Netzwerkprobleme:**  
  Vergewissere dich, dass alle benötigten Ports (5000, 3000, 80, 443) erreichbar sind.

- **SSL-/Certbot-Probleme:**  
  Prüfe, ob die Zertifikate in `/etc/letsencrypt/live/raspberrypi.deinedomain.tld/` vorhanden sind. Teste die automatische Erneuerung mit:
  ```bash
  sudo certbot renew --dry-run
  ```

- **Fehler in der Anwendung:**  
  Überprüfe die Log-Ausgaben (Backend: `app.py`, Frontend: `npm start`) und die Konsolenausgabe im Browser.

---

## Zusammenfassung

Diese Anleitung fasst alle wesentlichen Schritte zusammen, um den MRT Untersuchungskatalog bereitzustellen. Die Anwendung umfasst:

- Einen einmaligen Import der JSON-Daten in eine SQLite-Datenbank (über `db.py`).
- Ein robustes Backend mit Flask, das alle CRUD-Operationen (einschließlich eines speziellen Endpunkts zur Aktualisierung der Sequenzliste) bereitstellt.
- Ein modernes React-Frontend mit dynamischer Navigation, Suchfunktion, vollständiger Hierarchieanzeige und Drag‑&‑Drop-Unterstützung in den Bearbeitungsoverlays.
- Eine vollständige Integration von Animationen (via GSAP) und responsive Gestaltung (dunkles Farbschema, Roboto-Schrift).

Bitte passe gegebenenfalls Domainnamen und E-Mail-Adressen in den Nginx- und Certbot-Konfigurationen an deine Gegebenheiten an.

---

*Diese README.md wurde erstellt, um eine vollständige und reproduzierbare Installation, Nutzung und Wartung der Anwendung zu gewährleisten.*
