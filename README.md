# NightDUTY Abfragetool - Web Version

Moderne Web-Anwendung für das NightDUTY Abfragetool, konvertiert von der Desktop-Version (CustomTkinter) zu einer webbasierten Lösung.

## 📋 Übersicht

Diese Anwendung ist eine vollständige Web-Konvertierung des NightDUTY Abfragetools mit:
- **Backend:** Python + FastAPI
- **Frontend:** HTML/CSS/JavaScript
- **Webserver:** Nginx
- **Deployment:** Docker + Docker Compose
- **Authentifizierung:** JWT-basierte Session-Verwaltung
- **Sicherheit:** Bcrypt-gehashte Passwörter

## 🎨 Features

### Authentifizierung
- Login-System mit bcrypt-gehashten Passwörtern
- JWT-basierte Session-Verwaltung
- Sichere Token-Validierung

### 9 Formulare
1. **Abklärung Panne/Unfall** (Rot) - Umfassende Abklärung von Pannen und Unfällen
2. **Annahme Ölspur** (Blau) - Erfassung von Ölspuren und Umwelteinsätzen
3. **Annahme Mobi** (Gelb) - Bearbeitung von Mobilitätsgarantie-Fällen
4. **Annahme Kilian** (Grün) - Aufträge für Polizei, GDV und Bus/LKW
5. **Annahme Rudolph** (Lila) - Umsetzungen und Sicherstellungen für FUBZ/BVG
6. **Annahme Wehner Motors** (Orange) - PKW, Polizei, LKW und Ölspur Aufträge
7. **Falschparker | Privat** (Teal) - Private Falschparker-Meldungen
8. **Annahme Unterhaslberger** (Teal) - Pannen, Unfälle und Sicherstellungen
9. **Report Safar & BHG** (Rot) - Tägliche Reports für Safar und Bad Homburg

### Funktionen
- ✅ **Kopieren in Zwischenablage** für alle Formulare
- ✅ **WhatsApp-Integration** (öffnet WhatsApp Web mit vorausgefüllter Nachricht)
- ✅ **Responsive Design** (Desktop + Mobile)
- ✅ **Sidebar-Navigation** wie im Original
- ✅ **Originales Farbschema** beibehalten

## 🚀 Deployment auf Hetzner Server

### Server-Informationen
- **IP:** 46.224.68.34
- **OS:** Ubuntu 24.04
- **Benutzer:** ilias

### Voraussetzungen

Auf dem Server müssen folgende Pakete installiert sein:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose git curl
```

Docker-Dienst starten und aktivieren:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Benutzer zur Docker-Gruppe hinzufügen:
```bash
sudo usermod -aG docker $USER
# Neu anmelden, damit die Änderung wirksam wird
```

### Installation

1. **Repository klonen:**
```bash
cd ~
git clone https://github.com/ElyasRa/AbfrageTool.git
cd AbfrageTool
```

2. **Umgebungsvariablen setzen (Optional):**
```bash
# Erstelle eine .env Datei für Produktionsgeheimnisse
cat > .env << 'EOF'
SECRET_KEY=ihr-sehr-sicherer-geheimer-schluessel-hier-mindestens-32-zeichen-lang
EOF
```

3. **Docker-Container bauen und starten:**
```bash
docker-compose up -d --build
```

4. **Status überprüfen:**
```bash
docker-compose ps
docker-compose logs -f
```

5. **Anwendung testen:**
```bash
# Health Check
curl http://localhost/api/health

# Oder im Browser öffnen:
# http://46.224.68.34
```

### Login-Zugangsdaten

| Benutzername | Passwort | Rolle |
|--------------|----------|-------|
| ilias | Rania2019! | Admin |

## 🔧 Verwaltung

### Container-Verwaltung

**Container stoppen:**
```bash
cd ~/AbfrageTool
docker-compose down
```

**Container neu starten:**
```bash
cd ~/AbfrageTool
docker-compose restart
```

**Container neu bauen:**
```bash
cd ~/AbfrageTool
docker-compose down
docker-compose up -d --build
```

**Logs anzeigen:**
```bash
# Alle Logs
docker-compose logs -f

# Nur Backend
docker-compose logs -f backend

# Nur Nginx
docker-compose logs -f nginx
```

### Updates durchführen

1. **Code aktualisieren:**
```bash
cd ~/AbfrageTool
git pull origin main
```

2. **Container neu starten:**
```bash
docker-compose down
docker-compose up -d --build
```

### Backup

**Benutzer-Daten sichern:**
```bash
cp ~/AbfrageTool/backend/users.json ~/AbfrageTool/backend/users.json.backup
```

**Restore:**
```bash
cp ~/AbfrageTool/backend/users.json.backup ~/AbfrageTool/backend/users.json
docker-compose restart backend
```

## 🔐 Sicherheit

### Passwort ändern

Um das Passwort zu ändern, führe folgendes aus:

```bash
cd ~/AbfrageTool
docker-compose exec backend python3 << 'EOF'
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
password = input("Neues Passwort eingeben: ")
hashed = pwd_context.hash(password)
print(f"\nGehashtes Passwort:\n{hashed}")
EOF
```

Dann in `backend/users.json` das gehashte Passwort einfügen und Container neu starten:
```bash
docker-compose restart backend
```

### Secret Key ändern

Bearbeite die `.env` Datei und ändere den `SECRET_KEY`:
```bash
nano .env
# SECRET_KEY auf einen sicheren, zufälligen String setzen
docker-compose restart backend
```

### Firewall-Einstellungen

Stelle sicher, dass nur die notwendigen Ports offen sind:
```bash
# UFW installieren und konfigurieren
sudo apt install -y ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (für zukünftige SSL-Einrichtung)
sudo ufw enable
```

## 📱 Nutzung

### Desktop
1. Öffne `http://46.224.68.34` im Browser
2. Melde dich mit den Zugangsdaten an
3. Wähle ein Formular aus der Sidebar
4. Fülle das Formular aus
5. Klicke auf "Kopieren" um den Text in die Zwischenablage zu kopieren
6. Oder nutze "Per WhatsApp versenden" für direkte WhatsApp-Integration

### Mobile
- Die Anwendung ist vollständig responsive
- Alle Funktionen sind auch auf Mobilgeräten verfügbar
- WhatsApp-Integration funktioniert besonders gut auf Smartphones

## 🛠️ Entwicklung

### Lokale Entwicklung

**Backend starten:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend testen:**
- Öffne `frontend/index.html` im Browser
- Oder verwende einen einfachen HTTP-Server:
```bash
cd frontend
python3 -m http.server 8080
```

### Projektstruktur

```
AbfrageTool/
├── backend/
│   ├── main.py              # FastAPI Server
│   ├── auth.py              # Authentifizierung
│   ├── routes/
│   │   └── forms.py         # API Endpoints für Formulare
│   ├── users.json           # Benutzer-Daten
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Login-Seite
│   ├── dashboard.html       # Hauptseite mit Sidebar
│   ├── css/
│   │   └── style.css        # Stylesheet
│   └── js/
│       ├── app.js           # Haupt-JavaScript
│       ├── auth.js          # Login-Logik
│       └── forms.js         # Formular-Logik (alle 9 Formulare)
├── nginx/
│   └── nginx.conf           # Nginx Konfiguration
├── docker-compose.yml       # Docker Compose Konfiguration
├── Dockerfile               # Docker Image Definition
└── README.md                # Diese Datei
```

## 🐛 Troubleshooting

### Container starten nicht

```bash
# Logs überprüfen
docker-compose logs

# Container und Images neu bauen
docker-compose down -v
docker-compose up -d --build
```

### Port 80 bereits in Verwendung

```bash
# Prüfe welcher Prozess Port 80 verwendet
sudo lsof -i :80

# Stoppe den Prozess oder ändere den Port in docker-compose.yml
```

### Login funktioniert nicht

```bash
# Überprüfe users.json
cat backend/users.json

# Backend-Logs überprüfen
docker-compose logs backend

# Passwort neu generieren (siehe Sicherheit-Sektion)
```

### Frontend wird nicht geladen

```bash
# Nginx-Logs überprüfen
docker-compose logs nginx

# Nginx-Konfiguration testen
docker-compose exec nginx nginx -t

# Nginx neu laden
docker-compose restart nginx
```

## 📊 Monitoring

### Health Checks

```bash
# API Health Check
curl http://localhost/api/health

# Container Status
docker-compose ps
```

### Ressourcen-Nutzung

```bash
# Docker Stats
docker stats

# Disk Usage
docker system df
```

## 🔄 Zukünftige Erweiterungen

- [ ] SSL/TLS-Zertifikate (Let's Encrypt)
- [ ] Datenbank-Integration für Formular-Speicherung
- [ ] Mehrsprachige Unterstützung
- [ ] Export-Funktionen (PDF, Excel)
- [ ] Erweiterte Berechtigungsverwaltung
- [ ] Audit-Logs

## 📝 Lizenz

Internes Projekt für NightDUTY

## 👥 Support

Bei Problemen oder Fragen:
- Überprüfe die Logs: `docker-compose logs -f`
- Kontaktiere den Administrator

---

**Version:** 1.0.0  
**Letztes Update:** 2026-01-01  
**Status:** ✅ Produktionsbereit
