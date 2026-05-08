#!/bin/sh

echo "Executando migrations..."

alembic upgrade head

echo "Iniciando aplicação..."

exec "$@"
