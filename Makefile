.PHONY: help up down build logs restart clean test health

help:
	@echo "Available commands:"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make build     - Build/rebuild all services"
	@echo "  make logs      - View logs for all services"
	@echo "  make restart   - Restart all services"
	@echo "  make clean     - Stop services and remove volumes"
	@echo "  make test      - Test API endpoints"
	@echo "  make health    - Check health of all services"

up:
	docker-compose up -d
	@echo "Services starting... Wait a moment for initialization"
	@echo "FastAPI: http://localhost:8000"
	@echo "Airflow: http://localhost:8080 (admin/admin)"

down:
	docker-compose down

build:
	docker-compose up -d --build

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	@echo "All containers stopped and volumes removed"

test:
	@echo "Testing FastAPI health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "Service not ready"
	@echo "\nTesting FastAPI root..."
	@curl -s http://localhost:8000/ | python3 -m json.tool || echo "Service not ready"

health:
	@echo "Checking service health..."
	@docker-compose ps

