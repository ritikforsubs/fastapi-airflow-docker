from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os

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

