.PHONY: help install install-backend install-frontend run-backend run-frontend run-docs test test-backend test-frontend clean lint format

# Default target
help:
	@echo "Sistema de Reconhecimento Facial - Comandos Disponíveis"
	@echo ""
	@echo "Instalação:"
	@echo "  make install         - Instala backend e frontend"
	@echo "  make install-backend - Instala dependências do backend"
	@echo "  make install-frontend- Instala dependências do frontend"
	@echo ""
	@echo "Execução:"
	@echo "  make run-backend     - Inicia o servidor backend (porta 8000)"
	@echo "  make run-frontend    - Inicia o servidor frontend (porta 3000)"
	@echo "  make run-docs        - Inicia a documentação (porta 8001)"
	@echo "  make run-all         - Inicia backend, frontend e docs (requer tmux)"
	@echo ""
	@echo "Testes:"
	@echo "  make test            - Executa todos os testes"
	@echo "  make test-backend    - Executa testes do backend"
	@echo "  make test-frontend   - Executa testes do frontend"
	@echo ""
	@echo "Manutenção:"
	@echo "  make clean           - Remove arquivos temporários e caches"
	@echo "  make lint            - Verifica qualidade do código"
	@echo "  make format          - Formata o código automaticamente"

# Instalação
install: install-backend install-frontend
	@echo "✅ Instalação completa!"

install-backend:
	@echo "📦 Instalando backend..."
	python3 -m venv .venv
	. .venv/bin/activate && cd backend && pip install -r requirements.txt
	@echo "✅ Backend instalado!"

install-frontend:
	@echo "📦 Instalando frontend..."
	cd frontend && npm install
	@echo "✅ Frontend instalado!"

# Execução
run-backend:
	@echo "🚀 Iniciando backend em http://localhost:8000"
	. .venv/bin/activate && cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "🚀 Iniciando frontend em http://localhost:3000"
	cd frontend && npm start

run-docs:
	@echo "📚 Iniciando documentação em http://localhost:8001"
	. .venv/bin/activate && mkdocs serve --dev-addr=127.0.0.1:8001

run-all:
	@echo "🚀 Iniciando todos os serviços..."
	@command -v tmux >/dev/null 2>&1 || { echo "❌ tmux não encontrado. Instale com: brew install tmux"; exit 1; }
	tmux new-session -d -s integrador "make run-backend"
	tmux split-window -h "make run-frontend"
	tmux split-window -v "make run-docs"
	tmux attach-session -t integrador

# Testes
test: test-backend test-frontend
	@echo "✅ Todos os testes concluídos!"

test-backend:
	@echo "🧪 Executando testes do backend..."
	. .venv/bin/activate && cd backend && pytest tests/ -v

test-frontend:
	@echo "🧪 Executando testes do frontend..."
	cd frontend && npm test -- --watchAll=false

test-coverage:
	@echo "📊 Gerando relatório de cobertura..."
	. .venv/bin/activate && cd backend && pytest tests/ --cov=app --cov-report=html
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "✅ Relatórios em: backend/htmlcov/ e frontend/coverage/"

# Linting e Formatação
lint: lint-backend lint-frontend
	@echo "✅ Linting completo!"

lint-backend:
	@echo "🔍 Verificando código do backend..."
	. .venv/bin/activate && cd backend && flake8 app/ --max-line-length=120 || true
	. .venv/bin/activate && cd backend && mypy app/ --ignore-missing-imports || true

lint-frontend:
	@echo "🔍 Verificando código do frontend..."
	cd frontend && npm run lint || true

format:
	@echo "✨ Formatando código..."
	. .venv/bin/activate && cd backend && black app/ --line-length=120 || echo "⚠️  black não instalado"
	. .venv/bin/activate && cd backend && isort app/ || echo "⚠️  isort não instalado"
	cd frontend && npm run format || echo "⚠️  prettier não configurado"

# Limpeza
clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage 2>/dev/null || true
	rm -rf frontend/coverage frontend/build 2>/dev/null || true
	rm -rf site .mkdocs_cache 2>/dev/null || true
	@echo "✅ Limpeza concluída!"

# Database
db-migrate:
	@echo "🗄️  Executando migrações do banco de dados..."
	. .venv/bin/activate && cd backend && alembic upgrade head

db-reset:
	@echo "⚠️  Resetando banco de dados..."
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		. .venv/bin/activate && cd backend && alembic downgrade base && alembic upgrade head; \
	fi

# Docker (opcional)
docker-build:
	@echo "🐳 Construindo imagens Docker..."
	docker-compose build

docker-up:
	@echo "🐳 Iniciando containers..."
	docker-compose up -d

docker-down:
	@echo "🐳 Parando containers..."
	docker-compose down

docker-logs:
	@echo "📋 Exibindo logs dos containers..."
	docker-compose logs -f

# Desenvolvimento
dev-setup: install
	@echo "🔧 Configurando ambiente de desenvolvimento..."
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Arquivo .env não encontrado. Copie backend/.env.example para backend/.env"; \
	fi
	@echo "✅ Ambiente configurado! Execute 'make run-backend' e 'make run-frontend'"

# Git hooks
setup-hooks:
	@echo "🪝 Configurando Git hooks..."
	@echo "#!/bin/sh\nmake lint" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook instalado!"
