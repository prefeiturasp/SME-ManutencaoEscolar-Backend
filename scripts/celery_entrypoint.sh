
#!/bin/sh

set -e

echo "Aguardando banco..."

until nc -z postgres 5432; do
    sleep 2
done

echo "Banco disponível."

exec "$@"
