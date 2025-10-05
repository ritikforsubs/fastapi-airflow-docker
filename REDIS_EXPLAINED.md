# 🔴 Redis in This Project - Complete Guide

## ✅ Redis Status

**Currently Running:**
```
Container: redis_cache
Image: redis:7-alpine
Version: 7.4.6
Port: 6379
Status: ✅ Healthy (PONG response)
Connected Clients: 11
Commands Processed: 4,421+
Memory Usage: 1.44M
```

---

## 🎯 What is Redis?

**Redis** = **RE**mote **DI**ctionary **S**erver

**Simple Explanation:**
Think of Redis as a super-fast, in-memory database that acts like a key-value store (like a Python dictionary, but accessible across multiple applications).

```python
# Like Python dictionary, but distributed:
my_dict = {
    "task_123": "pending",
    "result_456": {"status": "complete", "data": [1,2,3]}
}

# Redis does the same thing, but:
# - Multiple apps can access it
# - Lightning fast (in-memory)
# - Survives restarts (optional persistence)
```

---

## 🔧 Why Do We Need Redis?

### **In This Project, Redis Serves as:**

### 1️⃣ **Message Broker for Celery**

**What's Celery?**
Celery is Airflow's task execution system. It distributes tasks across multiple workers.

**How Redis Fits:**
```
┌─────────────┐
│  Scheduler  │ "Here's a task to run!"
└──────┬──────┘
       │
       ↓ (Publish task)
┌─────────────┐
│   REDIS     │ ← Message Queue
│  (Broker)   │
└──────┬──────┘
       │
       ↓ (Pick up task)
┌─────────────┐
│   Workers   │ "I'll execute this!"
└─────────────┘
```

**Real Example:**
```
1. Airflow Scheduler: "Run task: download_script_from_s3"
   ↓
2. Redis Queue: [task: download_script_from_s3, args: {...}]
   ↓
3. Airflow Worker: *picks up task from Redis*
   ↓
4. Worker executes task
   ↓
5. Worker reports result back through Redis
```

---

### 2️⃣ **Result Backend for Celery**

**Purpose**: Store task execution results temporarily

**Flow:**
```
Task completes → Store result in Redis → Scheduler retrieves result

Example:
Task: "Count items in database"
Result stored in Redis: {"count": 42, "status": "success"}
```

**Why Redis for this?**
- ⚡ Super fast (in-memory)
- 🔄 Temporary storage (results don't need to be permanent)
- 🚀 Low latency (instant access)

---

### 3️⃣ **Task State Management**

Redis tracks:
- Which tasks are running
- Which tasks are queued
- Which tasks completed
- Task metadata

**Example Redis Data:**
```
Key: "celery-task-meta-abc123"
Value: {
  "status": "SUCCESS",
  "result": {"files_downloaded": 3},
  "traceback": null,
  "children": [],
  "date_done": "2025-10-05T12:00:00"
}
```

---

## 📊 Redis in Your Architecture

### **Current Setup:**

```
┌──────────────────────────────────────────┐
│         Airflow Scheduler                │
│  - Decides what tasks to run             │
│  - Publishes tasks to Redis              │
└────────────┬─────────────────────────────┘
             │
             ↓ (Task messages)
┌──────────────────────────────────────────┐
│            REDIS (Port 6379)             │
│  ┌────────────────────────────────┐     │
│  │  Queue: celery                 │     │
│  │  - task_1: download_script     │     │
│  │  - task_2: process_data        │     │
│  │  - task_3: check_health        │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Results Storage               │     │
│  │  - task_abc123: SUCCESS        │     │
│  │  - task_def456: PENDING        │     │
│  └────────────────────────────────┘     │
└────────────┬─────────────────────────────┘
             │
             ↓ (Pick up tasks)
┌──────────────────────────────────────────┐
│         Airflow Workers                  │
│  - Worker 1: Processing task_1           │
│  - Worker 2: Idle                        │
│  - Worker 3: Processing task_2           │
└──────────────────────────────────────────┘
```

---

## 🔍 See Redis in Action

### **1. View Redis Configuration in Docker Compose**

```yaml
# docker-compose.local.yml (or docker-compose.yml)

redis:
  image: redis:7-alpine        # Lightweight Redis version
  container_name: redis_cache  # Container name
  ports:
    - "6379:6379"             # Redis default port
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]  # Health check
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - app_network             # Connected to app network
```

### **2. Airflow Configuration Using Redis**

```yaml
# In docker-compose.local.yml - Airflow services

environment:
  AIRFLOW__CORE__EXECUTOR: CeleryExecutor
  
  # Redis as Celery broker (message queue)
  AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
  #                              ↑      ↑     ↑    ↑
  #                              |      |     |    └─ Database number
  #                              |      |     └────── Port
  #                              |      └────────── Container name
  #                              └───────────────── Protocol
  
  # Redis as result backend (store task results)
  AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://admin:admin123@postgres/appdb
  # Note: Results also stored in PostgreSQL for persistence
```

---

## 🧪 Test Redis

### **1. Ping Redis (Health Check)**

```bash
docker exec redis_cache redis-cli ping
# Expected output: PONG
```

### **2. Get Redis Info**

```bash
docker exec redis_cache redis-cli info
# Shows detailed statistics
```

### **3. List All Keys**

```bash
docker exec redis_cache redis-cli keys '*'
# Shows all keys stored in Redis
```

### **4. Monitor Redis in Real-Time**

```bash
docker exec -it redis_cache redis-cli
> MONITOR
# Shows all commands being executed in real-time
# Press Ctrl+C to stop
```

### **5. Check Connected Clients**

```bash
docker exec redis_cache redis-cli CLIENT LIST
# Shows all applications connected to Redis
```

### **6. Get a Specific Key**

```bash
docker exec redis_cache redis-cli GET "some_key"
```

---

## 🔬 See Celery Tasks in Redis

### **Monitor Task Queue:**

```bash
# Enter Redis CLI
docker exec -it redis_cache redis-cli

# List all keys (you'll see Celery keys)
> KEYS celery*

# Example output:
# 1) "celery-task-meta-abc123"
# 2) "celery-task-meta-def456"
# 3) "_kombu.binding.celery"

# Get task details
> GET "celery-task-meta-abc123"
# Shows task status, result, etc.

# Check queue length
> LLEN celery
# Shows how many tasks are waiting
```

---

## 📈 Redis Performance Stats

### **Current Stats from Your Running Instance:**

```
✅ Redis Version: 7.4.6 (latest stable)
✅ Connected Clients: 11
   - Airflow Scheduler
   - Airflow Workers (multiple)
   - Airflow Webserver
   
✅ Commands Processed: 4,421+
   - Task publishes
   - Result retrievals
   - Health checks
   
✅ Memory Usage: 1.44M
   - Very efficient!
   - In-memory storage
   
✅ Health Status: Healthy
   - Responding to pings
   - All clients connected
```

---

## 🎯 Why Redis is Perfect for This Use Case

### **Comparison with Other Options:**

```
┌──────────────┬─────────┬────────────┬──────────┬──────────┐
│ Feature      │ Redis   │ PostgreSQL │ RabbitMQ │ Kafka    │
├──────────────┼─────────┼────────────┼──────────┼──────────┤
│ Speed        │ ⚡⚡⚡   │ ⚡         │ ⚡⚡     │ ⚡⚡     │
│ Simplicity   │ ⭐⭐⭐ │ ⭐⭐      │ ⭐       │ ⭐       │
│ Lightweight  │ ✅      │ ❌         │ ❌       │ ❌       │
│ Setup Time   │ 1 min   │ 2 min      │ 5 min    │ 10 min   │
│ Memory Usage │ ~2MB    │ ~30MB      │ ~50MB    │ ~200MB   │
└──────────────┴─────────┴────────────┴──────────┴──────────┘

Winner for this use case: Redis! ✅
```

**Why Redis Wins:**
1. 🚀 Blazing fast (sub-millisecond)
2. 🪶 Lightweight (low memory footprint)
3. 🎯 Simple (minimal configuration)
4. 🔧 Built-in for Airflow (default choice)
5. 💪 Reliable (battle-tested)

---

## 🔄 Data Flow with Redis

### **Complete Task Execution Flow:**

```
Step 1: DAG Triggers
├─ User clicks "Trigger DAG" in Airflow UI (port 8080)
│
Step 2: Scheduler Processes
├─ Airflow Scheduler reads DAG
├─ Creates task instances
├─ Publishes tasks to Redis queue
│   └─ redis://redis:6379/0
│
Step 3: Redis Queues Task
├─ LPUSH celery "task_message"
├─ Task stored in Redis list
│   └─ {
│         "task": "download_scripts",
│         "args": ["my-bucket", "scripts/"],
│         "kwargs": {}
│       }
│
Step 4: Worker Picks Up Task
├─ Airflow Worker polls Redis
├─ RPOP celery (gets oldest task)
├─ Worker receives task
│
Step 5: Worker Executes
├─ Worker runs Python function
├─ Downloads files from MinIO/S3
├─ Processes data
│
Step 6: Result Stored
├─ Worker publishes result to Redis
├─ SET "celery-task-meta-abc123" "result_json"
│   └─ {"status": "SUCCESS", "result": {...}}
│
Step 7: Scheduler Retrieves Result
├─ Scheduler polls Redis for result
├─ GET "celery-task-meta-abc123"
├─ Updates task state in PostgreSQL
├─ Shows "SUCCESS" in Airflow UI
│
Step 8: Cleanup
├─ Redis expires old keys (TTL)
├─ Memory freed automatically
└─ Ready for next task!
```

---

## 🛠️ Redis Configuration Details

### **In Your Project:**

#### **Connection String Format:**
```
redis://[host]:[port]/[db]
       ↑      ↑       ↑
       |      |       └─ Database number (0-15)
       |      └───────── Port (default 6379)
       └──────────────── Hostname or IP

Examples:
- redis://localhost:6379/0  (from host machine)
- redis://redis:6379/0       (from containers)
- redis://192.168.1.100:6379/1 (remote Redis)
```

#### **Multiple Databases:**
Redis has 16 databases (0-15) in single instance:
```
db 0: Celery task queue (your project uses this)
db 1: Could be used for caching
db 2: Could be used for sessions
... etc
```

---

## 🎓 Redis Commands You Should Know

### **Basic Commands:**

```bash
# Key-Value Operations
SET key value          # Store a value
GET key               # Retrieve a value
DEL key               # Delete a key
EXISTS key            # Check if key exists
KEYS pattern          # Find keys matching pattern

# List Operations (used for queues)
LPUSH list value      # Add to left (queue)
RPUSH list value      # Add to right
LPOP list             # Remove from left
RPOP list             # Remove from right
LLEN list             # Get list length

# Expiration
EXPIRE key seconds    # Set key to expire
TTL key              # Time to live remaining

# Server
PING                 # Health check
INFO                 # Server info
CLIENT LIST          # Connected clients
MONITOR             # Watch commands real-time
```

### **Example Session:**

```bash
$ docker exec -it redis_cache redis-cli

127.0.0.1:6379> PING
PONG

127.0.0.1:6379> SET mykey "Hello Redis!"
OK

127.0.0.1:6379> GET mykey
"Hello Redis!"

127.0.0.1:6379> KEYS celery*
1) "celery-task-meta-abc123"
2) "_kombu.binding.celery"

127.0.0.1:6379> LLEN celery
(integer) 0  # No tasks waiting

127.0.0.1:6379> INFO memory
# Memory
used_memory:1444648
used_memory_human:1.44M

127.0.0.1:6379> exit
```

---

## 🔍 Troubleshooting Redis

### **Problem: Can't connect to Redis**

```bash
# Check if Redis is running
docker ps | grep redis

# Check Redis logs
docker logs redis_cache

# Test connection
docker exec redis_cache redis-cli ping
# Should return: PONG
```

### **Problem: Tasks not executing**

```bash
# Check if tasks are in queue
docker exec redis_cache redis-cli LLEN celery

# Monitor Redis activity
docker exec redis_cache redis-cli MONITOR

# Check connected clients
docker exec redis_cache redis-cli CLIENT LIST
# Should see airflow workers connected
```

### **Problem: Redis memory high**

```bash
# Check memory usage
docker exec redis_cache redis-cli INFO memory

# Clear all data (CAREFUL!)
docker exec redis_cache redis-cli FLUSHALL

# Restart Redis
docker restart redis_cache
```

---

## 📊 Redis vs PostgreSQL - When to Use What?

### **In Your Project:**

```
┌─────────────────────┬──────────────┬──────────────┐
│ Use Case            │ Redis        │ PostgreSQL   │
├─────────────────────┼──────────────┼──────────────┤
│ Task Queue          │ ✅ YES       │ ❌ No        │
│ Task Results (temp) │ ✅ YES       │ ❌ No        │
│ Application Data    │ ❌ No        │ ✅ YES       │
│ DAG Metadata        │ ❌ No        │ ✅ YES       │
│ Caching             │ ✅ YES       │ ❌ No        │
│ Session Storage     │ ✅ YES       │ ❌ No        │
│ Permanent Storage   │ ❌ No        │ ✅ YES       │
│ Complex Queries     │ ❌ No        │ ✅ YES       │
│ Speed Priority      │ ✅ YES       │ ❌ No        │
│ Data Integrity      │ ❌ No        │ ✅ YES       │
└─────────────────────┴──────────────┴──────────────┘
```

**Rule of Thumb:**
- **Redis**: Fast, temporary, simple key-value
- **PostgreSQL**: Permanent, structured, complex queries

---

## 🎯 Summary

### **Redis in Your Project:**

✅ **Role**: Message broker & result backend for Airflow  
✅ **Container**: redis_cache  
✅ **Image**: redis:7-alpine  
✅ **Port**: 6379  
✅ **Status**: Healthy and active  
✅ **Connected Clients**: 11 (Airflow components)  
✅ **Usage**: Task queuing, result storage, state management  

### **Why It Matters:**

Without Redis:
- ❌ Tasks can't be distributed
- ❌ Workers can't communicate
- ❌ Airflow can't scale
- ❌ No task queuing

With Redis:
- ✅ Tasks distributed efficiently
- ✅ Workers coordinate seamlessly  
- ✅ Scalable architecture
- ✅ Fast task execution
- ✅ Real-time updates

---

## 🚀 Next Steps

1. **Monitor Redis** while tasks run:
   ```bash
   docker exec -it redis_cache redis-cli MONITOR
   ```

2. **Trigger an Airflow DAG** and watch Redis activity

3. **Check task queue**:
   ```bash
   docker exec redis_cache redis-cli LLEN celery
   ```

4. **View task results**:
   ```bash
   docker exec redis_cache redis-cli KEYS celery-task-meta-*
   ```

---

## 📚 Learn More

- [Redis Official Docs](https://redis.io/docs/)
- [Redis Commands](https://redis.io/commands/)
- [Celery with Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
- [Airflow Celery Executor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/celery.html)

---

**Redis is a critical component that makes your distributed Airflow setup possible!** 🔴⚡

