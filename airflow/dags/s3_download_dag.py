from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
import logging
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def download_scripts_from_s3(**context):
    """Download scripts from S3 bucket"""
    try:
        # Configuration - Update these values
        bucket_name = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
        script_prefix = os.getenv('S3_SCRIPT_PREFIX', 'scripts/')
        local_download_path = '/tmp/scripts'
        
        # Create local directory if it doesn't exist
        os.makedirs(local_download_path, exist_ok=True)
        
        # Initialize S3 Hook (uses 'aws_default' connection)
        # This will automatically use endpoint_url if configured in the connection
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        # List all files in the bucket with the prefix
        logging.info(f"Listing files in bucket: {bucket_name} with prefix: {script_prefix}")
        keys = s3_hook.list_keys(bucket_name=bucket_name, prefix=script_prefix)
        
        if not keys:
            logging.warning(f"No files found in s3://{bucket_name}/{script_prefix}")
            return []
        
        downloaded_files = []
        
        # Download each file
        for key in keys:
            if key.endswith('/'):  # Skip directories
                continue
                
            filename = key.split('/')[-1]
            local_path = os.path.join(local_download_path, filename)
            
            logging.info(f"Downloading {key} to {local_path}")
            
            # Download file from S3
            file_content = s3_hook.read_key(key=key, bucket_name=bucket_name)
            
            # Save to local file
            with open(local_path, 'wb') as f:
                f.write(file_content.encode() if isinstance(file_content, str) else file_content)
            
            # Make scripts executable
            if filename.endswith(('.sh', '.py')):
                os.chmod(local_path, 0o755)
                logging.info(f"Made {filename} executable")
            
            downloaded_files.append(local_path)
            logging.info(f"Successfully downloaded: {local_path}")
        
        # Push downloaded file paths to XCom for downstream tasks
        context['task_instance'].xcom_push(key='downloaded_files', value=downloaded_files)
        
        return downloaded_files
        
    except Exception as e:
        logging.error(f"Error downloading scripts from S3: {str(e)}")
        raise


def process_downloaded_scripts(**context):
    """Process the downloaded scripts"""
    try:
        # Get the list of downloaded files from previous task
        task_instance = context['task_instance']
        downloaded_files = task_instance.xcom_pull(
            task_ids='download_scripts',
            key='downloaded_files'
        )
        
        if not downloaded_files:
            logging.warning("No files were downloaded")
            return
        
        logging.info(f"Processing {len(downloaded_files)} downloaded scripts")
        
        for file_path in downloaded_files:
            logging.info(f"Processing: {file_path}")
            
            # Example: Read and log the first few lines of each script
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()[:5]  # Read first 5 lines
                    logging.info(f"First lines of {file_path}:")
                    for line in lines:
                        logging.info(f"  {line.strip()}")
            
            # Add your custom processing logic here
            # For example: validate script, execute it, transform it, etc.
        
        return "Scripts processed successfully"
        
    except Exception as e:
        logging.error(f"Error processing scripts: {str(e)}")
        raise


def list_s3_bucket_contents(**context):
    """List all contents in the S3 bucket"""
    try:
        bucket_name = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
        
        s3_hook = S3Hook(aws_conn_id='aws_default')
        
        logging.info(f"Listing all contents in bucket: {bucket_name}")
        
        # List all keys in the bucket
        all_keys = s3_hook.list_keys(bucket_name=bucket_name)
        
        if all_keys:
            logging.info(f"Found {len(all_keys)} objects in bucket:")
            for key in all_keys[:10]:  # Log first 10 keys
                logging.info(f"  - {key}")
            
            if len(all_keys) > 10:
                logging.info(f"  ... and {len(all_keys) - 10} more files")
        else:
            logging.warning(f"Bucket {bucket_name} is empty or doesn't exist")
        
        return all_keys
        
    except Exception as e:
        logging.error(f"Error listing S3 bucket: {str(e)}")
        raise


# Define the DAG
with DAG(
    's3_script_download_pipeline',
    default_args=default_args,
    description='Download and process scripts from AWS S3',
    schedule_interval='@daily',  # Run daily
    catchup=False,
    tags=['aws', 's3', 'etl'],
) as dag:

    # Task 1: List S3 bucket contents
    list_bucket = PythonOperator(
        task_id='list_s3_bucket',
        python_callable=list_s3_bucket_contents,
    )

    # Task 2: Download scripts from S3
    download_scripts = PythonOperator(
        task_id='download_scripts',
        python_callable=download_scripts_from_s3,
    )

    # Task 3: Process downloaded scripts
    process_scripts = PythonOperator(
        task_id='process_scripts',
        python_callable=process_downloaded_scripts,
    )

    # Define task dependencies
    list_bucket >> download_scripts >> process_scripts

