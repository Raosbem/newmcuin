#!/bin/bash
set -e

# Generar .env desde variables de entorno
cat > /var/www/html/.env << EOF
APP_NAME="${APP_NAME:-AutoPartes}"
APP_ENV=${APP_ENV:-local}
APP_KEY=${APP_KEY:-base64:kJ5dNvTtKJBspXJDOdBptXMxR3U8pFHEi3Z2Vh8XFLA=}
APP_DEBUG=${APP_DEBUG:-true}
APP_URL=${APP_URL:-http://localhost:8080}

API_URL=${API_URL:-http://api:8000/api/v1}

LOG_CHANNEL=stack
LOG_LEVEL=debug

SESSION_DRIVER=file
SESSION_LIFETIME=120
CACHE_STORE=file
EOF

cd /var/www/html

# Limpiar cachés
php artisan config:clear 2>/dev/null || true
php artisan cache:clear  2>/dev/null || true

exec apache2-foreground
