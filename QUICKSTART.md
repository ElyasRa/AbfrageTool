# Quick Start Guide - NightDUTY Abfragetool

## 🚀 Schnellstart für Entwickler

### Lokale Entwicklung (Ohne Docker)

#### Backend starten
```bash
# In das Projektverzeichnis wechseln
cd AbfrageTool/backend

# Virtuelle Umgebung erstellen (optional)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# Server starten
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend läuft jetzt auf: http://localhost:8000

#### Frontend testen
```bash
# In das Frontend-Verzeichnis wechseln
cd AbfrageTool/frontend

# Einfachen HTTP-Server starten
python3 -m http.server 8080
```

Frontend läuft jetzt auf: http://localhost:8080

**Hinweis:** Für die volle Funktionalität müssen Backend und Frontend über den gleichen Origin laufen (Docker empfohlen).

### Mit Docker (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/ElyasRa/AbfrageTool.git
cd AbfrageTool

# Container starten
docker-compose up -d --build

# Logs anschauen
docker-compose logs -f

# Anwendung öffnen
# http://localhost
```

## 📊 API Endpoints

### Authentifizierung
- `POST /api/auth/login` - Login und JWT Token erhalten
- `GET /api/auth/me` - Aktuellen Benutzer abrufen

### Formulare
- `GET /api/forms/types` - Alle verfügbaren Formulare abrufen
- `POST /api/forms/submit` - Formulardaten übermitteln

### System
- `GET /api/health` - Health Check
- `GET /docs` - API Dokumentation (Swagger UI)
- `GET /redoc` - API Dokumentation (ReDoc)

## 🧪 API Tests

### Login Test
```bash
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ilias",
    "password": "Rania2019!"
  }'
```

Antwort:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Geschützte Endpoints testen
```bash
# Token aus vorheriger Antwort verwenden
TOKEN="your-token-here"

curl http://localhost/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Formulare abrufen
```bash
curl http://localhost/api/forms/types \
  -H "Authorization: Bearer $TOKEN"
```

## 🎨 Frontend-Struktur

```
frontend/
├── index.html          # Login-Seite
├── dashboard.html      # Hauptanwendung
├── css/
│   └── style.css       # Alle Styles (11KB)
└── js/
    ├── auth.js         # Authentifizierung (4KB)
    ├── app.js          # Hauptlogik (7KB)
    └── forms.js        # Alle 9 Formulare (36KB)
```

## 🔧 Backend-Struktur

```
backend/
├── main.py             # FastAPI App (3KB)
├── auth.py             # JWT & Bcrypt (3KB)
├── routes/
│   └── forms.py        # Form Endpoints (3KB)
├── users.json          # Benutzer-DB (121 Bytes)
└── requirements.txt    # Python Dependencies
```

## 📝 Formulare im Detail

### 1. Panne/Unfall (Rot)
- Schadensursache & Details
- Standort & Personen
- Terminvereinbarung
- **Features:** Kopieren

### 2. Ölspur (Blau)
- Melder & Anrufer
- Verunreinigungsdetails
- Einsatzort & Absicherung
- **Features:** Kopieren

### 3. Mobi (Gelb)
- Auftragsdetails
- Fahrzeug- & Kundendetails
- Ortsdetails
- **Features:** Safar-Info, Kopieren

### 4. Kilian (Grün)
- PKW-Annahme
- GDV-Annahme (PKW/LKW)
- Fahrerauswahl
- **Features:** WhatsApp, Kopieren

### 5. Rudolph (Lila)
- FUBZ/BVG Aufträge
- Umsetzung/Sicherstellung
- **Features:** Kopieren

### 6. Wehner Motors (Orange)
- PKW/Polizei/LKW/Ölspur
- Flexible Auftragstypen
- **Features:** Kopieren

### 7. Falschparker (Teal)
- Falschparker-Details
- Abschleppgrund
- Fahrerauswahl
- **Features:** WhatsApp, Kopieren, Abtretung

### 8. Unterhaslberger (Teal)
- Panne/Unfall/Sicherstellung
- Standard-Auftragsdetails
- **Features:** Kopieren

### 9. Safar & BHG Report (Rot)
- Zweispalten-Layout
- Wartezeit-Tracking
- Fahrerplanung
- **Features:** Separate Kopier-Buttons

## 🎯 Code-Beispiele

### Neues Formularfeld hinzufügen (Frontend)

```javascript
// In forms.js
const field = createFormField(
  'Label:', 
  'fieldName', 
  'text',  // oder 'select', 'textarea'
  {
    placeholder: 'Platzhalter',
    required: true,
    values: ['Option 1', 'Option 2']  // nur für select
  }
);
```

### Neuen Benutzer hinzufügen (Backend)

```bash
# Passwort hashen
python3 << 'EOF'
from passlib.context import CryptContext
import json

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
password = input("Passwort: ")
hashed = pwd_context.hash(password)

# users.json bearbeiten
with open('backend/users.json', 'r+') as f:
    users = json.load(f)
    users['neuer_user'] = {
        "password": hashed,
        "role": "User"
    }
    f.seek(0)
    json.dump(users, f, indent=2)
    
print("✅ Benutzer hinzugefügt")
EOF
```

## 🔍 Debugging

### Backend-Logs
```bash
docker-compose logs -f backend
```

### Frontend-Debugging
- Browser DevTools (F12)
- Console für JavaScript-Fehler
- Network Tab für API-Calls

### Häufige Probleme

**Problem:** Login funktioniert nicht
```bash
# Passwort-Hash überprüfen
cat backend/users.json

# Backend-Logs checken
docker-compose logs backend | grep -i error
```

**Problem:** Formulare werden nicht geladen
```bash
# API-Endpoint testen
curl http://localhost/api/forms/types -H "Authorization: Bearer YOUR_TOKEN"

# Browser Console checken
# DevTools > Console > Fehler?
```

## 📱 Mobile Testing

### Auf lokalem Netzwerk testen
```bash
# IP-Adresse finden
ip addr show  # Linux
ipconfig      # Windows

# Firewall-Port öffnen (Linux)
sudo ufw allow 80/tcp

# Von Smartphone zugreifen
# http://YOUR_IP_ADDRESS
```

## 🚢 Deployment-Workflow

```bash
# 1. Änderungen committen
git add .
git commit -m "Beschreibung"
git push

# 2. Auf dem Server
ssh ilias@46.224.68.34
cd ~/AbfrageTool

# 3. Updates holen
git pull

# 4. Container neu starten
docker-compose down
docker-compose up -d --build

# 5. Testen
curl http://localhost/api/health
```

## 🔒 Sicherheits-Checklist

- [x] Passwörter sind bcrypt-gehasht
- [x] JWT-Tokens für Authentication
- [x] CORS richtig konfiguriert
- [x] Umgebungsvariablen für Secrets
- [ ] HTTPS einrichten (TODO)
- [ ] Rate Limiting (TODO)
- [ ] Input Validation (TODO)

## 📚 Weiterführende Ressourcen

- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [JWT Tokens](https://jwt.io/)
- [Bcrypt](https://en.wikipedia.org/wiki/Bcrypt)

## 💡 Tipps & Tricks

### Produktive Entwicklung
```bash
# Backend mit Auto-Reload
uvicorn main:app --reload

# Frontend mit Live-Server (VS Code Extension)
# Live Server Extension installieren
# Rechtsklick auf index.html > "Open with Live Server"
```

### Schnelles Testen
```bash
# Alle Tests in einem
curl http://localhost/api/health && \
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ilias","password":"Rania2019!"}' && \
echo -e "\n✅ Alle Tests erfolgreich!"
```

---

**Version:** 1.0.0  
**Aktualisiert:** 2026-01-01  
**Lizenz:** Intern
