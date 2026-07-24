#!/usr/bin/env bash

set -e

APP_NAME="$1"

if [ -z "$APP_NAME" ]; then
    echo "Uso: ./scripts/create_app.sh <nome_do_app>"
    exit 1
fi

APP_PATH="apps/$APP_NAME"

if [ -d "$APP_PATH" ]; then
    echo "Erro: o app '$APP_NAME' já existe."
    exit 1
fi

echo "---> Criando estrutura..."

mkdir -p "$APP_PATH"

python manage.py startapp "$APP_NAME" "$APP_PATH"

echo "---> Reorganizando estrutura..."

# cria diretórios
mkdir -p "$APP_PATH/api"
mkdir -p "$APP_PATH/tests"

# move arquivos
mv "$APP_PATH/views.py" "$APP_PATH/api/views.py"
mv "$APP_PATH/tests.py" "$APP_PATH/tests/test_views.py"

# remove o admin
rm "$APP_PATH/admin.py"

# cria arquivos
touch "$APP_PATH/repository.py"
touch "$APP_PATH/services.py"
touch "$APP_PATH/serializers.py"
touch "$APP_PATH/constants.py"
touch "$APP_PATH/queries.py"
touch "$APP_PATH/schemas.py"
touch "$APP_PATH/exceptions.py"

touch "$APP_PATH/api/__init__.py"
touch "$APP_PATH/api/urls.py"

touch "$APP_PATH/tests/__init__.py"
touch "$APP_PATH/tests/test_services.py"
touch "$APP_PATH/tests/test_repository.py"

echo "---> App '$APP_NAME' criado com sucesso!"

tree "$APP_PATH"
