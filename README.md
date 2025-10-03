# Docker Project: FastAPI + Airflow + PostgreSQL

A complete Docker-based project integrating FastAPI, Apache Airflow, and PostgreSQL for building data pipelines and REST APIs.

## 🚀 Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Apache Airflow**: Workflow orchestration platform for data pipelines
- **PostgreSQL**: Robust relational database
- **Docker Compose**: Easy multi-container orchestration
- **Redis**: Message broker for Airflow Celery executor

## 📁 Project Structure

```
Docker/
├── app/
│   └── main.py                    # FastAPI application
├── airflow/
│   └── dags/
│       ├── example_dag.py         # Sample ETL pipeline DAG
│       └── database_maintenance_dag.py  # Database maintenance DAG
├── docker-compose.yml             # Docker Compose configuration
├── Dockerfile.fastapi             # FastAPI Dockerfile
├── Dockerfile.airflow             # Airflow Dockerfile
├── requirements.fastapi.txt       # FastAPI dependencies
├── requirements.airflow.txt       # Airflow dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## 🛠️ Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

## 🚀 Quick Start

### 1. Clone or Navigate to Project Directory

```bash
cd /Users/ritikmacsilver/Desktop/Docker
```

### 2. Start All Services

```bash
docker-compose up -d
```

This will start the following services:
- **PostgreSQL** on port `5432`
- **FastAPI** on port `8000`
- **Airflow Webserver** on port `8080`
- **Redis** on port `6379`
- **Airflow Scheduler** (background)
- **Airflow Worker** (background)

### 3. Wait for Services to Initialize

The first time you run the project, it may take a few minutes to:
- Download Docker images
- Initialize the Airflow database
- Create the admin user

Check the status with:
```bash
docker-compose ps
```

### 4. Access the Services

- **FastAPI Docs**: http://localhost:8000/docs
- **FastAPI API**: http://localhost:8000
- **Airflow UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`

## 📖 Using the FastAPI Application

### Available Endpoints

1. **GET /** - Welcome message with endpoint list
```bash
curl http://localhost:8000/
```

2. **GET /health** - Health check
```bash
curl http://localhost:8000/health
```

3. **POST /items** - Create a new item
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","description":"High-performance laptop","price":1299.99}'
```

4. **GET /items** - Get all items
```bash
curl http://localhost:8000/items
```

5. **GET /items/{item_id}** - Get item by ID
```bash
curl http://localhost:8000/items/1
```

6. **DELETE /items/{item_id}** - Delete item by ID
```bash
curl -X DELETE http://localhost:8000/items/1
```

## 📊 Using Apache Airflow

### Accessing the Airflow UI

1. Navigate to http://localhost:8080
2. Login with credentials:
   - Username: `admin`
   - Password: `admin`

### Available DAGs

1. **example_etl_pipeline**: Demonstrates an ETL pipeline that:
   - Checks database and API health
   - Creates database tables
   - Inserts sample data via API
   - Queries and logs items

2. **database_maintenance**: Performs database maintenance:
   - Logs table statistics
   - Runs VACUUM ANALYZE on tables

### Running a DAG

1. Go to the Airflow UI
2. Click on the DAG name
3. Toggle the DAG to "On" (if it's paused)
4. Click "Trigger DAG" button (play icon)
5. Monitor the progress in the Graph or Grid view

## 🗄️ Database Access

### Connect to PostgreSQL

```bash
docker exec -it postgres_db psql -U admin -d appdb
```

### Common PostgreSQL Commands

```sql
-- List tables
\dt

-- View items table
SELECT * FROM items;

-- Count items
SELECT COUNT(*) FROM items;

-- Exit psql
\q
```

## 🔧 Configuration

### Environment Variables

You can customize the configuration by creating a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Then edit the `.env` file with your desired values.

### Database Configuration

Default PostgreSQL credentials:
- **Host**: postgres (within Docker network) or localhost (from host)
- **Database**: appdb
- **User**: admin
- **Password**: admin123
- **Port**: 5432

## 🛑 Stopping the Services

```bash
docker-compose down
```

To also remove volumes (this will delete all data):
```bash
docker-compose down -v
```

## 🔄 Rebuilding Services

If you make changes to the code or Dockerfiles:

```bash
docker-compose up -d --build
```

## 📝 Logs

### View logs for all services
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f fastapi
docker-compose logs -f airflow-webserver
docker-compose logs -f postgres
```

## 🧪 Testing the Complete Workflow

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Check FastAPI health**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Create some items via API**:
   ```bash
   curl -X POST http://localhost:8000/items \
     -H "Content-Type: application/json" \
     -d '{"name":"Mouse","description":"Wireless mouse","price":29.99}'
   ```

4. **Access Airflow UI** at http://localhost:8080

5. **Enable and trigger the `example_etl_pipeline` DAG**

6. **Monitor the DAG execution** in Airflow UI

7. **Check the items via API**:
   ```bash
   curl http://localhost:8000/items
   ```

## 🐛 Troubleshooting

### Services not starting
- Check if ports 5432, 6379, 8000, or 8080 are already in use
- Run `docker-compose down` and try again

### Airflow webserver not accessible
- Wait a few minutes for initialization
- Check logs: `docker-compose logs airflow-webserver`

### Database connection errors
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`

### Permission issues
- On Linux, you may need to set proper permissions:
  ```bash
  sudo chown -R $(id -u):$(id -g) airflow/
  ```

## 🔐 Security Notes

⚠️ **Important**: This setup uses default credentials and is intended for development only. For production:
- Change all default passwords
- Use proper secrets management
- Configure SSL/TLS
- Implement proper authentication
- Review and harden security settings

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Happy Coding! 🎉**

