# Local S3 Setup with MinIO

This guide shows you how to run S3 functionality **completely offline** using MinIO, an S3-compatible object storage server that runs locally on your computer.

## 🎯 Why Use Local S3 (MinIO)?

✅ **No AWS Account Required** - Test S3 features without AWS credentials  
✅ **100% Offline** - Works without internet connection  
✅ **Fast & Free** - No AWS costs, lightning-fast local storage  
✅ **S3 Compatible** - Same API as AWS S3  
✅ **Perfect for Development** - Test before deploying to AWS  

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Start the Local Stack**

```bash
# Use the local docker-compose file
docker-compose -f docker-compose.local.yml up -d
```

This will start:
- **FastAPI** (Port 8000)
- **Airflow** (Port 8080)
- **PostgreSQL** (Port 5432)
- **Redis** (Port 6379)
- **MinIO** (Port 9000 - API, Port 9001 - Web UI) ✨

### **Step 2: Access MinIO Web UI**

Open your browser: **http://localhost:9001**

**Login credentials:**
- **Username**: `minioadmin`
- **Password**: `minioadmin`

You'll see a beautiful web interface where you can:
- Browse buckets
- Upload/download files
- Manage objects
- View statistics

### **Step 3: Upload Test Scripts**

#### **Option A: Using MinIO Web UI (Easiest)**

1. Go to http://localhost:9001
2. Login with `minioadmin` / `minioadmin`
3. Click on **"my-scripts"** bucket (created automatically)
4. Click **"Upload"** button
5. Drag & drop your Python/shell scripts
6. Create a folder called **"scripts/"** and upload files there

#### **Option B: Using MinIO Client (CLI)**

```bash
# Install MinIO client (one-time setup)
# On macOS:
brew install minio/stable/mc

# On Linux:
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure MinIO client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create bucket
mc mb local/my-scripts

# Upload files
mc cp my_script.py local/my-scripts/scripts/
mc cp data_pipeline.sh local/my-scripts/scripts/

# List files
mc ls local/my-scripts/scripts/
```

#### **Option C: Using Python Script**

Create a file `upload_to_minio.py`:

```python
import boto3

# Connect to local MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1',
    use_ssl=False
)

# Upload a file
s3.upload_file(
    'my_script.py',                    # Local file
    'my-scripts',                       # Bucket name
    'scripts/my_script.py'             # S3 key (path in bucket)
)

print("File uploaded successfully!")
```

Run it:
```bash
python upload_to_minio.py
```

---

## 🧪 Test the Integration

### **Test 1: List Files via FastAPI**

```bash
curl -X POST http://localhost:8000/s3/list-files \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-scripts",
    "prefix": "scripts/"
  }'
```

**Expected Response:**
```json
{
  "bucket": "my-scripts",
  "prefix": "scripts/",
  "count": 2,
  "files": [
    "scripts/my_script.py",
    "scripts/data_pipeline.sh"
  ]
}
```

### **Test 2: Download a Script via FastAPI**

```bash
curl -X POST http://localhost:8000/s3/download-script \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-scripts",
    "s3_key": "scripts/my_script.py",
    "local_path": "/tmp"
  }'
```

**Expected Response:**
```json
{
  "message": "Script downloaded successfully",
  "local_path": "/tmp/my_script.py",
  "s3_path": "s3://my-scripts/scripts/my_script.py"
}
```

### **Test 3: Check if File Exists**

```bash
curl http://localhost:8000/s3/check/my-scripts/scripts/my_script.py
```

### **Test 4: Run Airflow DAG**

1. Open Airflow UI: http://localhost:8080
2. Login: `admin` / `admin`
3. Find **"s3_script_download_pipeline"**
4. Toggle it **ON**
5. Click **Trigger DAG** ▶️
6. Watch it download files from local MinIO!

---

## 📂 Directory Structure in MinIO

Recommended structure for your local MinIO:

```
my-scripts/
├── scripts/
│   ├── etl_pipeline.py
│   ├── data_processing.sh
│   ├── validation.py
│   └── transform.sql
├── configs/
│   └── settings.json
└── data/
    └── sample_data.csv
```

---

## 🔄 Switching Between Local MinIO and AWS S3

### **Use Local MinIO (Default)**

```bash
# Start with local setup
docker-compose -f docker-compose.local.yml up -d
```

### **Switch to Real AWS S3**

```bash
# Stop local stack
docker-compose -f docker-compose.local.yml down

# Edit .env file with real AWS credentials
# Remove or comment out AWS_ENDPOINT_URL

# Start with AWS S3
docker-compose up -d
```

---

## 🛠️ Advanced: MinIO CLI Commands

```bash
# Set alias (one-time)
mc alias set local http://localhost:9000 minioadmin minioadmin

# List all buckets
mc ls local/

# Create bucket
mc mb local/my-new-bucket

# Upload file
mc cp file.txt local/my-scripts/scripts/

# Upload directory
mc cp --recursive ./my-scripts/ local/my-scripts/scripts/

# Download file
mc cp local/my-scripts/scripts/file.txt ./

# Remove file
mc rm local/my-scripts/scripts/old-file.txt

# Mirror local directory to MinIO (sync)
mc mirror ./local-scripts/ local/my-scripts/scripts/

# Watch bucket for changes
mc watch local/my-scripts

# Get file info
mc stat local/my-scripts/scripts/file.txt

# Share file (generate presigned URL)
mc share download local/my-scripts/scripts/file.txt
```

---

## 📊 MinIO Web UI Features

Access: **http://localhost:9001**

**Features:**
- 📁 **Browser** - Visual file management
- 🔍 **Search** - Find files quickly
- 📤 **Upload/Download** - Drag & drop interface
- 🔐 **Access Keys** - Manage API credentials
- 📈 **Monitoring** - View storage metrics
- 🔧 **Settings** - Configure buckets and policies
- 👥 **Users** - Manage access control

---

## 🐳 Docker Container Details

### **MinIO API (Port 9000)**
- S3-compatible API endpoint
- Used by boto3, AWS CLI, and applications
- Access: `http://localhost:9000`

### **MinIO Console (Port 9001)**
- Beautiful web interface
- Manage buckets, files, and settings
- Access: `http://localhost:9001`

### **Data Persistence**
- MinIO data stored in Docker volume: `minio_data`
- Survives container restarts
- To reset: `docker-compose -f docker-compose.local.yml down -v`

---

## 🔧 Troubleshooting

### **Problem: Can't access MinIO Web UI**

**Solution:**
```bash
# Check if MinIO is running
docker ps | grep minio

# Check logs
docker logs minio_s3

# Restart MinIO
docker-compose -f docker-compose.local.yml restart minio
```

### **Problem: Bucket not found**

**Solution:**
```bash
# Check if setup ran
docker logs minio_setup

# Manually create bucket
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/my-scripts
```

### **Problem: Connection refused**

**Solution:**
- Ensure MinIO is running: `docker ps`
- Check endpoint URL is correct: `http://minio:9000` (from containers) or `http://localhost:9000` (from host)
- Verify network: `docker network ls`

### **Problem: Upload fails from Airflow/FastAPI**

**Solution:**
```bash
# Test connectivity from inside container
docker exec fastapi_app curl http://minio:9000/minio/health/live

# Should return: "OK"
```

### **View Container Logs**

```bash
# FastAPI logs
docker logs fastapi_app

# Airflow logs
docker logs airflow_webserver
docker logs airflow_worker

# MinIO logs
docker logs minio_s3
```

---

## 🎓 Learning Resources

### **Test Your Local S3 Skills**

1. **Upload files** via MinIO web UI
2. **List files** via FastAPI endpoint
3. **Download files** via FastAPI endpoint
4. **Run Airflow DAG** to process files
5. **Monitor** in MinIO console

### **Example: Complete Workflow**

```bash
# 1. Upload a script to MinIO
echo 'print("Hello from S3!")' > test_script.py
mc cp test_script.py local/my-scripts/scripts/

# 2. List files via FastAPI
curl -X POST http://localhost:8000/s3/list-files \
  -H "Content-Type: application/json" \
  -d '{"bucket_name": "my-scripts", "prefix": "scripts/"}'

# 3. Download via FastAPI
curl -X POST http://localhost:8000/s3/download-script \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-scripts",
    "s3_key": "scripts/test_script.py",
    "local_path": "/tmp"
  }'

# 4. Verify download
docker exec fastapi_app cat /tmp/test_script.py
# Output: print("Hello from S3!")
```

---

## 💡 Pro Tips

1. **Use MinIO Browser** - Fastest way to manage files during development
2. **Keep containers running** - MinIO is lightweight and fast
3. **Test locally first** - Verify your code before deploying to AWS
4. **Use same code** - Your app works with both MinIO and AWS S3 (same API)
5. **Backup important data** - Export from MinIO before running `down -v`

---

## 🔄 Cleanup

```bash
# Stop all services
docker-compose -f docker-compose.local.yml down

# Stop and remove all data (WARNING: deletes all files!)
docker-compose -f docker-compose.local.yml down -v
```

---

## 🆚 Comparison: Local vs AWS

| Feature | Local MinIO | AWS S3 |
|---------|------------|--------|
| **Internet Required** | ❌ No | ✅ Yes |
| **Cost** | 🆓 Free | 💰 Pay per usage |
| **Speed** | ⚡ Very Fast | 🐢 Network latency |
| **Setup** | 🎯 1 command | 🔧 AWS account needed |
| **Development** | ✅ Perfect | ⚠️ Costs add up |
| **Production** | ⚠️ Self-hosted | ✅ Managed service |

---

## 🎉 Summary

You now have a **complete local S3 environment**!

✅ **No AWS account needed**  
✅ **No internet required**  
✅ **100% free**  
✅ **S3-compatible API**  
✅ **Visual web interface**  
✅ **Perfect for development**  

**When you're ready for production**, just switch to real AWS S3 by:
1. Adding AWS credentials to `.env`
2. Removing `AWS_ENDPOINT_URL`
3. Using regular `docker-compose.yml`

**Your code doesn't need to change - it works with both!** 🚀

---

## 📚 Additional Resources

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [MinIO Console Guide](https://min.io/docs/minio/linux/administration/minio-console.html)
- [MinIO Client (mc) Reference](https://min.io/docs/minio/linux/reference/minio-mc.html)
- [S3 API Compatibility](https://docs.min.io/docs/minio-s3-select.html)

---

**Happy Local Development! 🎊**

