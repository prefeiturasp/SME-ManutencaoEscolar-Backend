#!/bin/sh
set -e

DB_HOST="${POSTGRES_HOST}"
DB_PORT="${POSTGRES_PORT}"

BROKER_HOST="${KEYDB_HOST}"
BROKER_PORT="${KEYDB_PORT}"

echo "========================================="
echo "Iniciando Celery"
echo "========================================="

echo "Aguardando KeyDB (${BROKER_HOST}:${BROKER_PORT})..."

until nc -z "$BROKER_HOST" "$BROKER_PORT"; do
    sleep 2
done

echo "KeyDB disponível."

echo "Aguardando PostgreSQL (${DB_HOST}:${DB_PORT})..."

until nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 2
done

echo "PostgreSQL disponível."

echo "Executando: $*"

exec "$@"
