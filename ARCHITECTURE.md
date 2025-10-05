# Complete Architecture Guide

## 📚 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components Explained](#components-explained)
4. [File-by-File Breakdown](#file-by-file-breakdown)
5. [Data Flow](#data-flow)
6. [Key Concepts](#key-concepts)
7. [How Everything Works Together](#how-everything-works-together)

---

## 🏗️ System Overview

This is a **microservices-based data pipeline system** that combines:
- **FastAPI** (REST API for data operations)
- **Apache Airflow** (Workflow orchestration)
- **PostgreSQL** (Data storage)
- **MinIO/AWS S3** (Object storage for files/scripts)
- **Redis** (Message broker for distributed tasks)

### What Problem Does This Solve?

**Real-world use case**: 
Imagine you have Python scripts stored in S3 that need to:
1. Be downloaded automatically
2. Processed by a data pipeline
3. Results stored in a database
4. All orchestrated and scheduled

This system does exactly that - and you can develop/test it 100% offline!

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER / CLIENT                        │
└────────────┬──────────────────────────┬─────────────────────┘
             │                          │
             │ HTTP Requests            │ Browse UI
             ↓                          ↓
    ┌────────────────┐         ┌──────────────┐
    │   FastAPI      │         │   Airflow    │
    │   Port 8000    │         │   Port 8080  │
    │  (REST API)    │         │  (Web UI)    │
    └────────┬───────┘         └──────┬───────┘
             │                        │
             │ SQL Queries            │ Job Scheduling
             │                        │
    ┌────────▼────────────────────────▼───────┐
    │          PostgreSQL Database             │
    │              Port 5432                   │
    │  (Stores: Items, Airflow Metadata)      │
    └─────────────────────────────────────────┘
             
    ┌──────────────────┐         ┌─────────────────┐
    │   MinIO (S3)     │         │   Redis         │
    │   Port 9000      │◄────────┤   Port 6379     │
    │  (File Storage)  │         │ (Message Broker)│
    └──────────────────┘         └─────────────────┘
             ▲                           │
             │ Download Scripts          │ Task Queue
             │                           ▼
    ┌────────┴──────────────────────────────────┐
    │        Airflow Workers (Celery)           │
    │  - Download scripts from S3               │
    │  - Process data                           │
    │  - Run scheduled jobs                     │
    └───────────────────────────────────────────┘
```

---

## 🔧 Components Explained

### 1️⃣ **FastAPI** (Port 8000)

**What it is**: Modern Python web framework for building APIs

**Role in this project**:
- Provides REST API endpoints for CRUD operations
- Handles HTTP requests from users/applications
- Connects to PostgreSQL for data persistence
- Integrates with S3/MinIO for file operations

**Why FastAPI?**
- ⚡ Fast (as fast as Node.js or Go)
- 🎯 Automatic API documentation (Swagger UI)
- 🔍 Type checking with Pydantic
- 🚀 Async support for high performance

**Example Endpoints**:
```
GET  /                 - Welcome message
GET  /health           - Health check
GET  /items            - List all items
POST /items            - Create new item
POST /s3/list-files    - List files in S3
POST /s3/download-script - Download from S3
```

---

### 2️⃣ **Apache Airflow** (Port 8080)

**What it is**: Platform to programmatically author, schedule, and monitor workflows

**Role in this project**:
- Orchestrates data pipelines (ETL processes)
- Schedules recurring jobs (daily, hourly, etc.)
- Monitors task execution
- Manages dependencies between tasks

**Why Airflow?**
- 📅 Powerful scheduling (cron-like)
- 🔄 Handles retries and failures
- 📊 Visual workflow monitoring
- 🔗 Task dependencies management

**Components**:
```
┌─────────────────┐
│ Airflow         │
│ Components      │
├─────────────────┤
│ Webserver       │ ← User Interface
│ Scheduler       │ ← Triggers DAGs
│ Workers         │ ← Executes tasks
│ Database        │ ← Stores metadata
└─────────────────┘
```

**DAG (Directed Acyclic Graph)**: 
A workflow definition - sequence of tasks with dependencies

```python
Task A → Task B → Task C
         ↓
         Task D
```

---

### 3️⃣ **PostgreSQL** (Port 5432)

**What it is**: Powerful open-source relational database

**Role in this project**:
- Stores application data (items table)
- Stores Airflow metadata (DAG runs, task states)
- Provides ACID transactions
- Supports complex queries

**Tables**:
1. **items** (created by FastAPI)
   - id, name, description, price
   
2. **Airflow tables** (auto-created)
   - dag_run, task_instance, connection, etc.

---

### 4️⃣ **MinIO / AWS S3** (Port 9000, 9001)

**What it is**: Object storage (like AWS S3)

**Role in this project**:
- Stores files, scripts, datasets
- Provides S3-compatible API
- Accessible via web UI (Port 9001)

**MinIO vs AWS S3**:
```
┌─────────────────┬──────────────┬─────────────┐
│ Feature         │ MinIO (Local)│ AWS S3      │
├─────────────────┼──────────────┼─────────────┤
│ Internet needed │ ❌ No        │ ✅ Yes      │
│ Cost            │ 💰 Free      │ 💰 Pay/use  │
│ Speed           │ ⚡ Very Fast │ 🐢 Network  │
│ Use case        │ Development  │ Production  │
└─────────────────┴──────────────┴─────────────┘
```

**Why MinIO?**
- 100% S3-compatible API
- Perfect for local development
- Same code works with both MinIO and AWS S3

---

### 5️⃣ **Redis** (Port 6379)

**What it is**: In-memory data store, message broker

**Role in this project**:
- Message queue for Celery (Airflow's task executor)
- Stores task states temporarily
- Enables distributed task processing

**How it works**:
```
Scheduler → Redis (Queue) → Workers (Pick tasks)
```

---

## 📁 File-by-File Breakdown

### **Configuration Files**

#### `docker-compose.yml` - Main orchestration file
```yaml
Purpose: Defines all services and how they connect
Key Sections:
  - services: postgres, redis, fastapi, airflow, minio
  - networks: app_network (connects all containers)
  - volumes: persistent storage
  - environment: configuration variables
  - depends_on: service startup order
  - healthcheck: service health monitoring
```

#### `docker-compose.local.yml` - Local development with MinIO
```yaml
Purpose: Same as above but uses MinIO instead of AWS S3
Differences:
  - Adds minio service (ports 9000, 9001)
  - Adds minio-setup (creates buckets)
  - Sets AWS_ENDPOINT_URL to MinIO
  - No AWS credentials needed
```

#### `Dockerfile.fastapi` - FastAPI container definition
```dockerfile
FROM python:3.11-slim           # Base image
WORKDIR /app                    # Working directory
RUN apt-get install gcc         # System dependencies
COPY requirements.fastapi.txt   # Python dependencies
RUN pip install -r requirements # Install packages
COPY app/ /app/                 # Copy application code
CMD ["uvicorn", "main:app"]     # Start server
```

#### `Dockerfile.airflow` - Airflow container definition
```dockerfile
FROM apache/airflow:2.7.3       # Official Airflow image
USER root                       # Switch to root
RUN apt-get install gcc         # System dependencies
USER airflow                    # Back to airflow user
COPY requirements.airflow.txt   # Python dependencies
RUN pip install -r requirements # Install packages
```

---

### **Application Code**

#### `app/main.py` - FastAPI Application
```python
Structure:
├── Imports & Setup
├── Database Configuration (PostgreSQL connection)
├── Pydantic Models (Data validation)
│   ├── Item, ItemResponse
│   └── S3DownloadRequest, S3ListRequest
├── Database Helper Functions
│   ├── get_db_connection()
│   └── startup_event() - creates tables
├── API Endpoints
│   ├── Root & Health Check
│   ├── CRUD Operations (items)
│   └── S3 Operations
└── Error Handling

Key Concepts:
- Pydantic: Type validation (ensures data correctness)
- Async/Await: Non-blocking operations
- HTTP Methods: GET, POST, DELETE
- Status Codes: 200 OK, 404 Not Found, 500 Error
```

**Example Flow**:
```
1. User sends POST /items with JSON data
2. FastAPI validates with Pydantic model
3. If valid → insert to PostgreSQL
4. Return newly created item
5. If invalid → return 422 error
```

#### `app/aws_utils.py` - S3 Client Wrapper
```python
Purpose: Abstraction layer for S3 operations

Class: S3Client
├── __init__() - Initialize boto3 client
│   - Detects AWS vs MinIO (via endpoint_url)
│   - Configures credentials
├── download_file() - Download from S3
├── upload_file() - Upload to S3
├── list_files() - List objects in bucket
├── download_script() - Download + make executable
└── file_exists() - Check object existence

Why this wrapper?
- Centralizes S3 logic
- Handles errors gracefully
- Works with both AWS and MinIO
- Provides logging
```

**Boto3 Explained**:
```python
# Boto3 is AWS SDK for Python
s3_client = boto3.client('s3', ...)

# Basic operations:
s3_client.upload_file(local_file, bucket, key)
s3_client.download_file(bucket, key, local_file)
s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
```

---

### **Airflow DAGs**

#### `airflow/dags/example_dag.py` - ETL Pipeline
```python
Structure:
├── Default Arguments (retry policy, schedule)
├── Python Functions (task logic)
│   ├── check_database_connection()
│   ├── check_api_health()
│   ├── insert_sample_data()
│   └── query_items()
├── DAG Definition
│   ├── Schedule: daily
│   ├── Tags: example, etl
└── Task Dependencies
    [check_db, check_api] >> create_table >> insert >> query

Operators Used:
- PythonOperator: Executes Python functions
- PostgresOperator: Runs SQL queries
```

**DAG Flow**:
```
Start
  ↓
Check DB ──┐
           ├──→ Create Table → Insert Data → Query Data → End
Check API ─┘

If any task fails → Retry (configured in default_args)
```

**Key Concepts**:
- **Operator**: A task template (PythonOperator, BashOperator)
- **Task**: An instance of an operator
- **Task Instance**: A task execution for a specific date
- **XCom**: Cross-communication between tasks (share data)

#### `airflow/dags/s3_download_dag.py` - S3 Processing Pipeline
```python
Purpose: Download scripts from S3 and process them

Tasks:
1. list_s3_bucket - Check what's in S3
2. download_scripts - Pull files from S3 to local
3. process_scripts - Handle downloaded files

S3Hook: Airflow's built-in S3 integration
- Uses 'aws_default' connection
- Automatically uses endpoint_url if configured
- Provides helper methods (list_keys, read_key)

XCom Usage:
task1 → xcom_push(key='files', value=['file1.py'])
task2 → xcom_pull(task_ids='task1', key='files')
```

#### `airflow/dags/database_maintenance_dag.py` - DB Maintenance
```python
Purpose: Regular database maintenance tasks

Tasks:
1. log_table_statistics - Count, avg, min, max
2. vacuum_analyze - Optimize database

PostgresHook:
- Connects to PostgreSQL
- Executes queries
- Returns results

Schedule: @daily (runs every midnight)
```

---

### **Dependencies**

#### `requirements.fastapi.txt`
```
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # ASGI server
pydantic==2.5.0           # Data validation
psycopg2-binary==2.9.9    # PostgreSQL driver
python-multipart==0.0.6   # Form data parsing
boto3==1.34.0             # AWS SDK
botocore==1.34.0          # Boto3 dependency
```

#### `requirements.airflow.txt`
```
apache-airflow-providers-postgres==5.7.1  # PostgreSQL integration
psycopg2-binary==2.9.9                    # PostgreSQL driver
requests==2.31.0                          # HTTP client
celery==5.3.4                             # Distributed task queue
redis==5.0.1                              # Redis client
boto3==1.34.0                             # AWS SDK
apache-airflow-providers-amazon==8.14.0   # AWS integration
```

---

### **Documentation**

#### `README.md` - Main documentation
- Quick start guide
- Features overview
- Setup instructions
- Available endpoints
- Troubleshooting

#### `AWS_SETUP.md` - AWS S3 integration guide
- AWS credentials setup
- IAM policy examples
- Configuration steps
- Testing procedures
- Security best practices

#### `LOCAL_S3_SETUP.md` - MinIO setup guide
- Local S3 with MinIO
- No AWS account needed
- MinIO CLI commands
- Upload/download examples
- Web UI guide

#### `ARCHITECTURE.md` - This file!
- Complete system explanation
- Component details
- Code walkthrough

---

## 🔄 Data Flow

### **Flow 1: Create Item via API**

```
User → POST /items
  ↓
FastAPI receives request
  ↓
Pydantic validates JSON
  ↓
get_db_connection() → PostgreSQL
  ↓
INSERT INTO items (name, description, price)
  ↓
PostgreSQL returns new row with ID
  ↓
FastAPI returns JSON response
  ↓
User receives new item with ID
```

### **Flow 2: S3 Download via Airflow**

```
Scheduler triggers DAG (daily schedule)
  ↓
Task 1: list_s3_bucket
  - S3Hook connects to MinIO/AWS
  - list_keys(bucket='my-scripts')
  - Returns list of file keys
  ↓
Task 2: download_scripts
  - For each file in list:
    - s3_hook.read_key(key)
    - Save to /tmp/scripts/
    - chmod +x (make executable)
  - Push file paths to XCom
  ↓
Task 3: process_scripts
  - Pull file paths from XCom
  - Read each file
  - Log contents or execute
  ↓
Mark DAG run as SUCCESS
```

### **Flow 3: Database Query**

```
Airflow Task → PostgresHook
  ↓
hook.get_conn() → PostgreSQL connection
  ↓
cursor.execute("SELECT COUNT(*) FROM items")
  ↓
fetchone() → Get result
  ↓
Log statistics
  ↓
Close connection
```

---

## 🎓 Key Concepts

### **1. Microservices Architecture**

```
Monolith (Traditional):
┌─────────────────────┐
│   One Big App       │
│  - API              │
│  - Database         │
│  - Background Jobs  │
│  - Everything!      │
└─────────────────────┘
Problem: Hard to scale, deploy, maintain

Microservices (This Project):
┌────────┐  ┌─────────┐  ┌──────────┐
│FastAPI │  │ Airflow │  │PostgreSQL│
│  API   │  │  Jobs   │  │   Data   │
└────────┘  └─────────┘  └──────────┘
Benefits: 
- Each service scales independently
- Failure isolated
- Different tech stacks possible
```

### **2. Docker Containers**

```
Container = Lightweight VM
- Packages app + dependencies
- Isolated environment
- Consistent across machines

Docker Compose = Container orchestrator
- Defines multiple containers
- Networks them together
- Manages startup order
```

### **3. REST API**

```
REST = Representational State Transfer

HTTP Methods:
- GET: Read data (idempotent)
- POST: Create data
- PUT/PATCH: Update data
- DELETE: Remove data

Status Codes:
- 2xx: Success (200 OK, 201 Created)
- 4xx: Client error (404 Not Found, 422 Validation)
- 5xx: Server error (500 Internal Error)
```

### **4. Database Connections**

```
Connection Pool:
┌─────────┐
│ FastAPI │
└────┬────┘
     │ Opens connection
     ↓
┌─────────────┐
│  PostgreSQL │
│  ┌───┐ ┌───┐│
│  │ 1 │ │ 2 ││  ← Connection pool
│  └───┘ └───┘│
└─────────────┘

Why pool?
- Reuse connections (faster)
- Limit concurrent connections
- Auto-reconnect on failure
```

### **5. Async/Await in FastAPI**

```python
# Synchronous (blocking):
def get_items():
    # Waits here, blocks other requests
    result = database.query("SELECT * FROM items")
    return result

# Asynchronous (non-blocking):
async def get_items():
    # Can handle other requests while waiting
    result = await database.query("SELECT * FROM items")
    return result

Benefits:
- Handle more concurrent requests
- Better performance
- Efficient resource usage
```

### **6. Message Queue (Celery + Redis)**

```
Producer (Scheduler) → Queue (Redis) → Consumer (Worker)

Example:
Airflow Scheduler says: "Run task X"
  ↓
Task X goes into Redis queue
  ↓
Worker picks up task X
  ↓
Worker executes task X
  ↓
Worker reports result to database
```

---

## 🤝 How Everything Works Together

### **Complete Workflow Example**

**Scenario**: Daily job to download scripts from S3, process them, and store results

```
1. SCHEDULE (00:00 daily)
   Airflow Scheduler: "Time to run s3_download_dag!"
   
2. QUEUE
   Scheduler → Redis: "Add these tasks to queue"
   
3. EXECUTION
   Worker picks up task: "list_s3_bucket"
   ↓
   Connects to MinIO (port 9000)
   ↓
   Lists files: ['script1.py', 'script2.py']
   ↓
   Stores in XCom (PostgreSQL)
   
4. NEXT TASK
   Worker picks up: "download_scripts"
   ↓
   Pulls file list from XCom
   ↓
   For each file:
     - Download from MinIO to /tmp/
     - Make executable (chmod +x)
   ↓
   Store paths in XCom
   
5. PROCESS
   Worker picks up: "process_scripts"
   ↓
   Pulls paths from XCom
   ↓
   Reads each script
   ↓
   Could execute, validate, or transform
   ↓
   Logs results
   
6. COMPLETE
   Mark DAG run as SUCCESS
   ↓
   Store execution metadata in PostgreSQL
   ↓
   Display in Airflow UI (port 8080)
```

### **API Request Example**

```
1. USER ACTION
   curl POST http://localhost:8000/items
   Body: {"name": "Laptop", "price": 999}

2. FASTAPI RECEIVES
   main.py → create_item() function
   ↓
   Pydantic validates:
   - name: string ✓
   - price: float ✓
   
3. DATABASE
   get_db_connection() → PostgreSQL
   ↓
   INSERT INTO items (name, price) VALUES ('Laptop', 999)
   ↓
   RETURNING * → Get new row with ID
   
4. RESPONSE
   FastAPI formats response:
   {
     "id": 1,
     "name": "Laptop",
     "description": null,
     "price": 999.0
   }
   ↓
   User receives JSON
```

---

## 🔍 Debugging & Monitoring

### **Check Service Health**

```bash
# View all containers
docker-compose ps

# View logs
docker-compose logs fastapi
docker-compose logs airflow-worker

# Check database
docker exec postgres_db psql -U admin -d appdb -c "SELECT * FROM items"

# Test API
curl http://localhost:8000/health

# Check MinIO
curl http://localhost:9000/minio/health/live
```

### **Airflow Monitoring**

```
1. Open http://localhost:8080
2. Click on DAG name
3. View Graph or Grid
4. Click on task → View Logs
5. Check task duration, retries
```

---

## 📚 Learn More

**Key Technologies**:
- FastAPI: https://fastapi.tiangolo.com/
- Airflow: https://airflow.apache.org/
- PostgreSQL: https://www.postgresql.org/
- Docker: https://docs.docker.com/
- Boto3: https://boto3.amazonaws.com/
- MinIO: https://min.io/docs/

**Concepts to Study**:
- REST APIs
- SQL databases
- Container orchestration
- Workflow management
- Object storage
- Asynchronous programming

---

## 🎯 Summary

This codebase demonstrates:
1. ✅ Modern API development (FastAPI)
2. ✅ Workflow orchestration (Airflow)
3. ✅ Database integration (PostgreSQL)
4. ✅ Cloud storage patterns (S3/MinIO)
5. ✅ Containerization (Docker)
6. ✅ Microservices architecture
7. ✅ Distributed task processing (Celery)
8. ✅ Local development workflow

**You've learned**:
- How to build a production-ready data pipeline
- How services communicate
- How to orchestrate workflows
- How to handle file storage
- How to containerize applications
- How to develop without cloud dependencies

**Next Steps**:
1. Modify DAGs to add your own tasks
2. Create new FastAPI endpoints
3. Integrate with external APIs
4. Add data transformations
5. Deploy to production!

---

**Questions? Check the other docs or explore the code!** 🚀

