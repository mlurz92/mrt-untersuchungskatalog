# MRT Untersuchungskatalog

Diese Anleitung beschreibt detailliert, wie du den **MRT Untersuchungskatalog** auf einem Raspberry Pi 4 mit einer frischen Installation von RaspberryPiOS lite (64bit) installierst, in Betrieb nimmst, aktualisierst und bei Bedarf vollständig entfernst. Die Anwendung besteht aus einem Python-Backend (Flask, SQLite) und einem React-Frontend (mit Animationen via GSAP, Drag‑&‑Drop via react‑beautiful‑dnd und API-Anbindung via Axios). Die Bereitstellung erfolgt über HTTPS (konfiguriert mit Certbot und Nginx).

> **Wichtig:**  
> Aufgrund der systemseitigen Python-Konfiguration (externally-managed-environment gemäß [PEP 668](https://www.python.org/dev/peps/pep-0668/)) wird empfohlen, für das Backend eine virtuelle Umgebung zu erstellen. Die Python-Pakete werden somit isoliert installiert, ohne die Systeminstallation zu beeinflussen.

---

## Inhaltsverzeichnis

- [Systemvorbereitung](#systemvorbereitung)
- [Installation der Anwendung](#installation-der-anwendung)
  - [1. Klonen des Repositories](#1-klonen-des-repositories)
  - [2. Einrichtung der virtuellen Python-Umgebung und Installation der Backend-Abhängigkeiten](#2-einrichtung-der-virtuellen-python-umgebung-und-installation-der-backend-abhängigkeiten)
  - [3. Installation der Frontend-Abhängigkeiten](#3-installation-der-frontend-abhängigkeiten)
  - [4. Einrichtung und Import der Datenbank](#4-einrichtung-und-import-der-datenbank)
  - [5. Start der Backend-API und Frontend-Anwendung](#5-start-der-backend-api-und-frontend-anwendung)
  - [6. HTTPS-Bereitstellung via Certbot und Nginx](#6-https-bereitstellung-via-certbot-und-nginx)
- [Aufrufen der Anwendung](#aufrufen-der-anwendung)
- [Update der Anwendung](#update-der-anwendung)
- [Vollständige Entfernung der Anwendung und Rücksetzung des Raspberry Pi OS](#vollständige-entfernung-der-anwendung-und-rücksetzung-des-raspberry-pi-os)
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
   - Der Standardbenutzer ist `pi` mit dem Passwort `raspberry` (bitte ändere das Passwort umgehend).

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

### 2. Einrichtung der virtuellen Python-Umgebung und Installation der Backend-Abhängigkeiten

Aufgrund des "externally-managed-environment"-Hinweises solltest du für das Python-Backend eine virtuelle Umgebung erstellen, um alle Pakete isoliert zu installieren:

1. **Virtuelle Umgebung erstellen und aktivieren**  
   Im Hauptverzeichnis des Projekts (`mrt-untersuchungskatalog`), wechsle in das `backend`-Verzeichnis und erstelle dort die virtuelle Umgebung:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```
   (Um die virtuelle Umgebung später zu verlassen, kannst du `deactivate` eingeben.)

2. **Upgrade von pip und Installation der Backend-Abhängigkeiten:**  
   **Wichtig:** Da du dich bereits im `backend`-Verzeichnis befindest, verwendest du den relativen Pfad zur Datei `requirements.txt` ohne einen zusätzlichen Ordnernamen – also:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   Falls du Pakete systemweit installieren möchtest (was nicht empfohlen wird), kannst du alternativ den Schalter `--break-system-packages` verwenden:
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```

### 3. Installation der Frontend-Abhängigkeiten

1. **Installation von Node.js:**  
   Für eine stabile Node.js-Version auf dem Raspberry Pi empfiehlt sich die Installation über NodeSource:
   ```bash
   curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

2. **Installiere die Frontend-Abhängigkeiten:**
   ```bash
   cd ../frontend
   npm install
   ```
   *Hinweis:* Neben React, Axios, GSAP und react‑beautiful‑dnd wird zusätzlich *react‑scripts* verwendet.

### 4. Einrichtung und Import der Datenbank

Wechsle in das Backend-Verzeichnis (sicherstellen, dass die virtuelle Umgebung aktiv ist) und führe das Import-Skript aus, um die SQLite-Datenbank zu initialisieren und `protocols.json` zu importieren:

```bash
cd ../backend
python db.py
```

Die Ausgabe sollte etwa Folgendes enthalten:  
„Datenbank nicht gefunden. Starte Import aus 'protocols.json' …“  
und danach „Datenbank erstellt und JSON-Daten erfolgreich importiert.“

### 5. Start der Backend-API und Frontend-Anwendung

#### Backend API starten

Starte die Flask-API (sicherstellen, dass die virtuelle Umgebung aktiviert ist):

```bash
cd backend
python app.py
```

Die API läuft auf Port 5000.

#### Frontend-Anwendung starten

Öffne für den Frontend-Start ein weiteres Terminal (oder eine neue SSH-Session) und wechsle in den Frontend-Ordner:
```bash
cd ~/mrt-untersuchungskatalog/frontend
npm start
```

Die React-Anwendung wird standardmäßig auf Port 3000 bereitgestellt ([http://localhost:3000](http://localhost:3000)).

### 6. HTTPS-Bereitstellung via Certbot und Nginx

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
       server_name raspberrypi.deinedomain.tld;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl;
       server_name raspberrypi.deinedomain.tld;
       
       ssl_certificate /etc/letsencrypt/live/raspberrypi.deinedomain.tld/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/raspberrypi.deinedomain.tld/privkey.pem;

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
**https://raspberrypi.deinedomain.tld/**  
erreichbar.

---

## Aufrufen der Anwendung

- **Im Browser:**  
  Öffne die URL (z. B.) [https://raspberrypi.deinedomain.tld/](https://raspberrypi.deinedomain.tld/).  
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

- Für das Backend (sicherstellen, dass die virtuelle Umgebung aktiviert ist):
  ```bash
  cd backend
  pip install -r requirements.txt
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
   - Entferne ggf. die virtuelle Umgebung, wenn diese separat erstellt wurde.

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
  Stelle sicher, dass `protocols.db` im Backend-Verzeichnis korrekt angelegt wurde. Führe ggf. `python db.py` (in der aktiven virtuellen Umgebung) erneut aus.

- **Virtuelle Umgebung:**  
  Achte darauf, dass du im Backend stets deine virtuelle Umgebung aktivierst (z. B. mit `source venv/bin/activate`), bevor du Python-Befehle ausführst.  
  Falls du Pakete systemweit installieren möchtest (was nicht empfohlen ist), benutze alternativ den Schalter `--break-system-packages`.

- **Pfadangaben:**  
  **Wichtig:** Wenn du dich im `backend`-Verzeichnis befindest, installiere die Pakete mit:
  ```bash
  pip install -r requirements.txt
  ```
  und nicht mit `pip install -r backend/requirements.txt`, da letzterer Pfad nicht existiert und den Fehler "Could not open requirements" verursacht.

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
- Die Verwendung einer virtuellen Python-Umgebung, um Konflikte im systemweiten Paketmanagement zu vermeiden (aufgrund des "externally managed environment").
- Eine vollständige Integration von Animationen (via GSAP) und responsive Gestaltung (dunkles Farbschema, Roboto-Schrift).

Bitte passe gegebenenfalls Domainnamen, E-Mail-Adressen und weitere Umgebungsvariablen in den Nginx- und Certbot-Konfigurationen an deine Gegebenheiten an.

---
