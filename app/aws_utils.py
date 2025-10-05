import boto3
from botocore.config import Config
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class S3Client:
    """AWS S3 Client for downloading and uploading files"""
    
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.endpoint_url = os.getenv("AWS_ENDPOINT_URL")  # For MinIO/LocalStack
        
        # Initialize S3 client
        # If endpoint_url is set (e.g., for MinIO), use it
        if self.endpoint_url:
            # Using local S3-compatible service (MinIO/LocalStack)
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region,
                use_ssl=False,  # MinIO typically runs without SSL locally
                config=Config(signature_version='s3v4')
            )
            logger.info(f"Using local S3 endpoint: {self.endpoint_url}")
        else:
            # Using real AWS S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            logger.info("Using AWS S3")
    
    def download_file(self, bucket_name: str, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3 bucket
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            local_path: Local path where file will be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading {s3_key} from bucket {bucket_name}")
            self.s3_client.download_file(bucket_name, s3_key, local_path)
            logger.info(f"Successfully downloaded to {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            return False
    
    def upload_file(self, local_path: str, bucket_name: str, s3_key: str) -> bool:
        """
        Upload a file to S3 bucket
        
        Args:
            local_path: Local file path to upload
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) where file will be stored in S3
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Uploading {local_path} to bucket {bucket_name}/{s3_key}")
            self.s3_client.upload_file(local_path, bucket_name, s3_key)
            logger.info(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return False
    
    def list_files(self, bucket_name: str, prefix: str = "") -> list:
        """
        List files in S3 bucket with optional prefix
        
        Args:
            bucket_name: Name of the S3 bucket
            prefix: Optional prefix to filter files
            
        Returns:
            list: List of file keys
        """
        try:
            logger.info(f"Listing files in bucket {bucket_name} with prefix {prefix}")
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            files = [obj['Key'] for obj in response['Contents']]
            logger.info(f"Found {len(files)} files")
            return files
        except ClientError as e:
            logger.error(f"Error listing files from S3: {str(e)}")
            return []
    
    def download_script(self, bucket_name: str, script_key: str, local_dir: str = "/tmp") -> str:
        """
        Download a script from S3 and return the local path
        
        Args:
            bucket_name: Name of the S3 bucket
            script_key: Key (path) of the script in S3
            local_dir: Local directory to save the script (default: /tmp)
            
        Returns:
            str: Local path of the downloaded script, or None if failed
        """
        try:
            filename = script_key.split('/')[-1]
            local_path = os.path.join(local_dir, filename)
            
            if self.download_file(bucket_name, script_key, local_path):
                # Make the script executable
                os.chmod(local_path, 0o755)
                return local_path
            return None
        except Exception as e:
            logger.error(f"Error downloading script: {str(e)}")
            return None
    
    def file_exists(self, bucket_name: str, s3_key: str) -> bool:
        """
        Check if a file exists in S3 bucket
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_key: Key (path) of the file in S3
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

