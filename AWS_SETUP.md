# AWS S3 Integration Setup Guide

This guide explains how to configure AWS S3 integration to download scripts from your S3 buckets.

## 📋 Prerequisites

1. **AWS Account** with S3 access
2. **AWS Access Keys** (Access Key ID and Secret Access Key)
3. **S3 Bucket** with your scripts

---

## 🔑 Step 1: Get AWS Credentials

### Option A: Create IAM User (Recommended)

1. Go to AWS Console → **IAM** → **Users**
2. Click **Create user**
3. User name: `airflow-s3-access`
4. Click **Next**
5. Attach policies: Select **AmazonS3ReadOnlyAccess** (or custom policy)
6. Click **Create user**
7. Click on the user → **Security credentials** tab
8. Click **Create access key**
9. Select **Application running outside AWS**
10. **Copy** both:
    - Access Key ID
    - Secret Access Key

### Option B: Use Existing IAM User

If you already have an IAM user, create new access keys from the IAM console.

---

## 🔐 Step 2: Configure Environment Variables

### Create `.env` file in project root:

```bash
# Copy the example file
cp .env.example .env
```

### Edit `.env` file:

```bash
# AWS Credentials - Replace with your actual credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration - Replace with your bucket details
S3_BUCKET_NAME=my-scripts-bucket
S3_SCRIPT_PREFIX=scripts/
```

**⚠️ Important:** Never commit `.env` file to git (it's already in `.gitignore`)

---

## 📁 Step 3: Organize Your S3 Bucket

### Recommended structure:

```
my-scripts-bucket/
├── scripts/
│   ├── data_processing.py
│   ├── etl_job.sh
│   ├── validation.py
│   └── transform.sql
└── configs/
    └── settings.json
```

### Upload scripts to S3:

```bash
# Using AWS CLI
aws s3 cp my_script.py s3://my-scripts-bucket/scripts/
aws s3 cp my_script.sh s3://my-scripts-bucket/scripts/

# Or use AWS Console to upload
```

---

## 🚀 Step 4: Restart Services

After configuring AWS credentials:

```bash
# Stop all services
docker-compose down

# Rebuild and start with new environment variables
docker-compose up -d --build
```

---

## 📊 Step 5: Test AWS Integration

### Test via FastAPI

1. **Open** http://localhost:8000/docs

2. **List S3 files:**
   ```bash
   curl -X POST http://localhost:8000/s3/list-files \
     -H "Content-Type: application/json" \
     -d '{
       "bucket_name": "my-scripts-bucket",
       "prefix": "scripts/"
     }'
   ```

3. **Download a script:**
   ```bash
   curl -X POST http://localhost:8000/s3/download-script \
     -H "Content-Type: application/json" \
     -d '{
       "bucket_name": "my-scripts-bucket",
       "s3_key": "scripts/my_script.py",
       "local_path": "/tmp"
     }'
   ```

4. **Check if file exists:**
   ```bash
   curl http://localhost:8000/s3/check/my-scripts-bucket/scripts/my_script.py
   ```

### Test via Airflow

1. **Open** Airflow UI: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

2. **Enable DAG:** Find `s3_script_download_pipeline` and toggle it ON

3. **Trigger DAG:** Click the play button ▶️

4. **Monitor:** Watch the DAG execution in real-time

5. **Check logs:** Click on tasks to see S3 download logs

---

## 🔧 Available Airflow DAGs

### 1. `s3_script_download_pipeline`

**Purpose:** Download and process scripts from S3

**Tasks:**
- **list_s3_bucket:** Lists all files in your S3 bucket
- **download_scripts:** Downloads scripts from specified prefix
- **process_scripts:** Processes downloaded scripts (customize as needed)

**Schedule:** Daily (adjust in `s3_download_dag.py`)

**Configuration:**
- Modify `S3_BUCKET_NAME` and `S3_SCRIPT_PREFIX` in `.env`

---

## 🛠️ Customization

### Modify Download Logic

Edit `airflow/dags/s3_download_dag.py`:

```python
def download_scripts_from_s3(**context):
    bucket_name = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
    script_prefix = os.getenv('S3_SCRIPT_PREFIX', 'scripts/')
    
    # Add your custom logic here
    ...
```

### Add Custom Processing

```python
def process_downloaded_scripts(**context):
    downloaded_files = context['task_instance'].xcom_pull(
        task_ids='download_scripts',
        key='downloaded_files'
    )
    
    for file_path in downloaded_files:
        # Add your processing logic
        if file_path.endswith('.py'):
            # Execute Python script
            subprocess.run(['python3', file_path])
        elif file_path.endswith('.sh'):
            # Execute shell script
            subprocess.run(['bash', file_path])
```

---

## 🔒 Security Best Practices

1. **Use IAM Roles** when running on AWS (EC2, ECS, etc.)
2. **Least Privilege:** Grant only necessary S3 permissions
3. **Rotate Keys:** Regularly rotate access keys
4. **Never commit** `.env` file to version control
5. **Use AWS Secrets Manager** or **Parameter Store** for production

### Example IAM Policy (Read-Only):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-scripts-bucket",
        "arn:aws:s3:::my-scripts-bucket/*"
      ]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Error: "Access Denied"

- Check AWS credentials are correct
- Verify IAM user has S3 read permissions
- Ensure bucket name is correct

### Error: "No such bucket"

- Verify `S3_BUCKET_NAME` in `.env`
- Check bucket exists in specified region
- Confirm bucket region matches `AWS_DEFAULT_REGION`

### Error: "Unable to locate credentials"

- Ensure `.env` file exists in project root
- Verify environment variables are set
- Restart Docker containers after changing `.env`

### Check AWS Configuration:

```bash
# View FastAPI logs
docker-compose logs fastapi | grep -i aws

# View Airflow worker logs
docker-compose logs airflow-worker | grep -i s3

# Verify environment variables
docker exec fastapi_app env | grep AWS
```

---

## 📚 Additional Resources

- [AWS SDK for Python (Boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Airflow AWS Provider Documentation](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/index.html)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

---

## 📝 Next Steps

1. ✅ Configure AWS credentials in `.env`
2. ✅ Upload scripts to S3 bucket
3. ✅ Test S3 integration via FastAPI
4. ✅ Run Airflow DAG to download scripts
5. ✅ Customize processing logic for your use case

**Happy scripting! 🎉**

