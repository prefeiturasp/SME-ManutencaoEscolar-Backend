# SME-ManutencaoEscolar-Backend


---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (para rodar via container)

---

## Rodar localmente (sem Docker)

```bash
# 1. Copiar o .env
cp .env.example .env

# 2. Instalar dependências
pip install -r requirements/local.txt

# 3. Rodar o servidor
python manage.py runserver 0.0.0.0:8002
```

Acesse em: http://localhost:8002/api/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:8002/api/docs/

---

## Pre-commit

O projeto usa `pre-commit` para rodar validações antes do commit:

- `black` para formatação;
- `ruff --fix` para lint e correções automáticas;
- `mypy` para checagem de tipos.

### Instalar localmente

Depois de instalar as dependências de desenvolvimento:

```bash
pip install -r requirements/local.txt
pre-commit install
```

A partir disso, os hooks rodam automaticamente a cada `git commit`.

### Rodar manualmente

Para validar todos os arquivos localmente:

```bash
pre-commit run --all-files
```

Ou via Docker:

```bash
./scripts/executar_precommit.sh
```

Quando `black` ou `ruff` alterarem arquivos, revise as mudanças e rode o
comando novamente antes de commitar.

---
