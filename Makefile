.PHONY: dev build lint test \
	backend-install backend-migrate backend-seed backend-marts backend-quality \
	frontend-install frontend-dev frontend-build \
	db-up db-down db-reset

# Runs backend + frontend dev servers together (requires two terminals in
# practice; this target just documents the two commands).
dev:
	@echo "Run these in two terminals:"
	@echo "  make backend-dev   (cd backend && source .venv/bin/activate && python manage.py runserver)"
	@echo "  make frontend-dev"

build: frontend-build

lint:
	cd frontend && npm run lint

test: backend-test frontend-build

backend-install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend-migrate:
	cd backend && . .venv/bin/activate && python manage.py migrate

backend-seed:
	cd backend && . .venv/bin/activate && python manage.py seed_synthetic_claims

backend-marts:
	cd backend && . .venv/bin/activate && python manage.py build_marts

backend-quality:
	cd backend && . .venv/bin/activate && python manage.py run_quality_checks

backend-test:
	cd backend && . .venv/bin/activate && python manage.py test tests

backend-dev:
	cd backend && . .venv/bin/activate && python manage.py runserver

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

db-up:
	docker compose up -d

db-down:
	docker compose down

db-reset:
	cd backend && . .venv/bin/activate && python manage.py reset_warehouse
