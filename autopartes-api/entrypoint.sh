#!/bin/bash
set -e

echo "Esperando conexión a la BD..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
    sys.exit(0)
except Exception as e:
    print(f'BD no disponible: {e}', flush=True)
    sys.exit(1)
" 2>&1; do
  echo "Reintentando en 3s..."
  sleep 3
done

echo "Corriendo migraciones de Alembic..."
alembic upgrade head

echo "Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
