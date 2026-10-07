.PHONY: setup dev seed test check types clean help

help:
	@echo "Available targets:"
	@echo "  make setup   - Install backend and frontend dependencies"
	@echo "  make dev     - Run backend and frontend development servers"
	@echo "  make seed    - Seed the database"
	@echo "  make test    - Run backend and frontend test suites"
	@echo "  make check   - Run linters, type checks, and tests"
	@echo "  make types   - Generate frontend TypeScript types from OpenAPI"

setup:
	python -m venv backend/.venv
	./backend/.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting backend and frontend..."
	python run.py dev

seed:
	python run.py seed

test:
	python run.py test

check:
	python run.py check

types:
	python run.py types

clean:
	rm -rf frontend/.next frontend/node_modules backend/.venv backend/__pycache__
