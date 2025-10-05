.PHONY: help up down build logs restart clean test health local local-down minio-ui

help:
	@echo "Available commands:"
	@echo ""
	@echo "AWS S3 (requires AWS credentials):"
	@echo "  make up        - Start all services with AWS S3"
	@echo "  make down      - Stop all services"
	@echo ""
	@echo "Local S3 with MinIO (no AWS needed):"
	@echo "  make local     - Start all services with local MinIO S3"
	@echo "  make local-down- Stop local services"
	@echo "  make minio-ui  - Open MinIO web interface"
	@echo ""
	@echo "General:"
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

local:
	@echo "🚀 Starting LOCAL environment with MinIO (no AWS needed)..."
	@echo "MinIO Web UI will be available at: http://localhost:9001"
	@echo "  Username: minioadmin"
	@echo "  Password: minioadmin"
	docker-compose -f docker-compose.local.yml up -d
	@echo ""
	@echo "✅ Services starting..."
	@echo "   FastAPI:     http://localhost:8000"
	@echo "   Airflow:     http://localhost:8080 (admin/admin)"
	@echo "   MinIO API:   http://localhost:9000"
	@echo "   MinIO UI:    http://localhost:9001 (minioadmin/minioadmin)"

local-down:
	docker-compose -f docker-compose.local.yml down

minio-ui:
	@echo "Opening MinIO Web UI..."
	@echo "Login with: minioadmin / minioadmin"
	@open http://localhost:9001 || xdg-open http://localhost:9001 || echo "Open http://localhost:9001 in your browser"

