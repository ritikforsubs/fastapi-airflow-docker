from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from aws_utils import S3Client

app = FastAPI(title="FastAPI with Docker, Airflow & PostgreSQL")

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "appdb"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin123"),
}


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float


def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize database table on startup"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI + Airflow + PostgreSQL Docker Project",
        "endpoints": {
            "GET /": "This welcome message",
            "GET /health": "Health check",
            "GET /items": "Get all items",
            "POST /items": "Create a new item",
            "GET /items/{item_id}": "Get item by ID",
            "DELETE /items/{item_id}": "Delete item by ID"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": f"error: {str(e)}"}


@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """Create a new item in the database"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "INSERT INTO items (name, description, price) VALUES (%s, %s, %s) RETURNING *",
        (item.name, item.description, item.price)
    )
    new_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    return new_item


@app.get("/items", response_model=List[ItemResponse])
async def get_items():
    """Get all items from the database"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return items


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item by ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
    deleted = cur.fetchone()
    conn.commit()
    
    cur.close()
    conn.close()
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": f"Item {item_id} deleted successfully"}


# AWS S3 Endpoints
class S3DownloadRequest(BaseModel):
    bucket_name: str
    s3_key: str
    local_path: Optional[str] = "/tmp"


class S3ListRequest(BaseModel):
    bucket_name: str
    prefix: Optional[str] = ""


@app.post("/s3/download-script")
async def download_script_from_s3(request: S3DownloadRequest):
    """Download a script from AWS S3"""
    try:
        s3_client = S3Client()
        local_path = s3_client.download_script(
            bucket_name=request.bucket_name,
            script_key=request.s3_key,
            local_dir=request.local_path
        )
        
        if local_path:
            return {
                "message": "Script downloaded successfully",
                "local_path": local_path,
                "s3_path": f"s3://{request.bucket_name}/{request.s3_key}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to download script from S3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 download error: {str(e)}")


@app.post("/s3/list-files")
async def list_s3_files(request: S3ListRequest):
    """List files in an S3 bucket"""
    try:
        s3_client = S3Client()
        files = s3_client.list_files(
            bucket_name=request.bucket_name,
            prefix=request.prefix
        )
        
        return {
            "bucket": request.bucket_name,
            "prefix": request.prefix,
            "count": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 list error: {str(e)}")


@app.get("/s3/check/{bucket_name}/{s3_key:path}")
async def check_s3_file_exists(bucket_name: str, s3_key: str):
    """Check if a file exists in S3"""
    try:
        s3_client = S3Client()
        exists = s3_client.file_exists(bucket_name, s3_key)
        
        return {
            "bucket": bucket_name,
            "key": s3_key,
            "exists": exists,
            "s3_path": f"s3://{bucket_name}/{s3_key}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 check error: {str(e)}")

