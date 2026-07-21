CONTAINER = backend
COMPOSE_FILE = docker-compose-dev.yml
DC = docker compose -f $(COMPOSE_FILE)
EXEC = $(DC) exec $(CONTAINER)

.PHONY: help makemigrations migrate createsuperuser shell startapp test coverage lint format typecheck precommit docs bash

help: ## Mostra esta mensagem de ajuda com os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ==========================================
# Comandos do Docker
# ==========================================
up: ## Inicializa os containers em segundo plano (background)
	$(DC) up -d

down: ## Para e remove todos os containers, redes e volumes locais
	$(DC) down

build: ## Reconstrói as imagens do Docker (necessário após alterar pacotes/requirements)
	$(DC) build

logs: ## Visualiza os logs dos containers em tempo real
	$(DC) logs -f

restart: ## Reinicia todos os serviços do docker-compose
	$(DC) restart

status: ## Exibe o status atual de execução dos containers
	$(DC) ps

# ==========================================
# Comandos do Django
# ==========================================
makemigrations: ## Cria novas migrações baseadas nas mudanças dos models
	$(EXEC) python manage.py makemigrations

migrate: ## Aplica as migrações ao banco de dados Postgres
	$(EXEC) python manage.py migrate

shell: ## Abre o shell interativo do Django
	$(EXEC) python manage.py shell

# ==========================================
# Testes e Cobertura
# ==========================================
test: ## Roda a suíte de testes com o pytest. Opcional: path=caminho/do/teste
	$(EXEC) pytest $(path)

coverage: ## Roda os testes, gera o relatório de cobertura em HTML na pasta htmlcov/ e abre o relatório no navegador.
	$(EXEC) pytest --cov --cov-report=html && xdg-open htmlcov/index.html

# ==========================================
# Qualidade de Código (Linting/Tipagem)
# ==========================================
lint: ## Verifica problemas no código usando o Ruff
	$(EXEC) ruff check .

format: ## Formata o código automaticamente usando o Black
	$(EXEC) black .

typecheck: ## Verifica a tipagem estática do código usando o MyPy
	$(EXEC) mypy .

# ==========================================
# Documentação (Sphinx)
# ==========================================
docs: ## Gera a documentação do projeto em HTML usando o Sphinx (assume que existe uma pasta 'docs')
	$(EXEC) sphinx-build -b html docs/ docs/_build/html

# ==========================================
# Utilitários
# ==========================================
bash: ## Abre um terminal interativo (Bash) dentro do container backend
	$(EXEC) bash

terminal: ## Alias para o comando bash (Abre o terminal dentro do container)
	$(EXEC) bash


