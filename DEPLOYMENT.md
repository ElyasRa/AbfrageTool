# Deployment Checklist für Hetzner Server (46.224.68.34)

## Pre-Deployment (Auf dem Server)

### 1. Server vorbereiten
```bash
# Als Benutzer 'ilias' anmelden
ssh ilias@46.224.68.34

# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Docker installieren
sudo apt install -y docker.io docker-compose git curl

# Docker-Dienst starten
sudo systemctl start docker
sudo systemctl enable docker

# Benutzer zu Docker-Gruppe hinzufügen
sudo usermod -aG docker ilias
# Neu anmelden nach diesem Schritt!
```

### 2. Firewall konfigurieren
```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (optional, für später)
sudo ufw enable
sudo ufw status
```

## Deployment

### 3. Repository klonen
```bash
cd ~
git clone https://github.com/ElyasRa/AbfrageTool.git
cd AbfrageTool
```

### 4. Umgebungsvariablen setzen (Optional aber empfohlen)
```bash
# Sicheren SECRET_KEY generieren
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# .env Datei erstellen
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
EOF

echo "✅ .env Datei erstellt"
```

### 5. Application starten
```bash
# Container bauen und starten
docker-compose up -d --build

# Status überprüfen
docker-compose ps

# Logs anzeigen
docker-compose logs -f
```

### 6. Testen
```bash
# Health Check
curl http://localhost/api/health

# Sollte zurückgeben: {"status":"healthy","service":"NightDUTY Abfragetool"}
```

### 7. Browser-Test
- Öffne: http://46.224.68.34
- Login mit:
  - **Benutzername:** ilias
  - **Passwort:** Rania2019!

## Post-Deployment

### 8. Monitoring einrichten
```bash
# Cron-Job für automatische Updates (optional)
crontab -e

# Folgende Zeile hinzufügen (täglich um 3 Uhr):
# 0 3 * * * cd ~/AbfrageTool && git pull && docker-compose up -d --build >> /tmp/abfragetool-update.log 2>&1
```

### 9. Backup-Strategie
```bash
# Backup-Script erstellen
cat > ~/backup-abfragetool.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/abfragetool
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# users.json sichern
cp ~/AbfrageTool/backend/users.json $BACKUP_DIR/users_$DATE.json

# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "users_*.json" -mtime +30 -delete

echo "✅ Backup erstellt: $BACKUP_DIR/users_$DATE.json"
EOF

chmod +x ~/backup-abfragetool.sh

# Cron-Job für tägliches Backup
crontab -e
# 0 2 * * * ~/backup-abfragetool.sh >> /tmp/abfragetool-backup.log 2>&1
```

## Troubleshooting

### Container starten nicht
```bash
docker-compose logs
docker-compose down -v
docker-compose up -d --build
```

### Port 80 bereits verwendet
```bash
sudo lsof -i :80
# Falls Nginx bereits läuft:
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### Logs überprüfen
```bash
# Alle Logs
docker-compose logs -f

# Nur Backend
docker-compose logs -f backend

# Nur Nginx
docker-compose logs -f nginx
```

### Container neu starten
```bash
cd ~/AbfrageTool
docker-compose restart
```

### Kompletter Neustart
```bash
cd ~/AbfrageTool
docker-compose down
docker-compose up -d --build
```

## Wichtige URLs

- **Anwendung:** http://46.224.68.34
- **API Health Check:** http://46.224.68.34/api/health
- **API Dokumentation:** http://46.224.68.34/docs (FastAPI Swagger UI)

## Sicherheitshinweise

1. ✅ Passwörter sind bcrypt-gehasht
2. ✅ JWT-Tokens für Session-Management
3. ⚠️ HTTPS noch nicht konfiguriert (für Produktion empfohlen)
4. ⚠️ SECRET_KEY sollte geändert werden
5. ⚠️ Firewall ist konfiguriert

## Nächste Schritte für Produktion

1. **SSL/TLS einrichten:**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Monitoring einrichten:**
   - Docker container health checks
   - Log-Rotation konfigurieren
   - Uptime-Monitoring (z.B. UptimeRobot)

3. **Backup automatisieren:**
   - users.json täglich sichern
   - Docker volumes sichern

## Support Kontakte

- **Repository:** https://github.com/ElyasRa/AbfrageTool
- **Issues:** https://github.com/ElyasRa/AbfrageTool/issues

---

**Status:** ✅ Deployment-bereit  
**Version:** 1.0.0  
**Datum:** 2026-01-01
