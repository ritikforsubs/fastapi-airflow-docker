from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def check_database_connection():
    """Check if PostgreSQL database is accessible"""
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        logging.info(f"PostgreSQL version: {db_version}")
        cursor.close()
        conn.close()
        return "Database connection successful"
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise


def check_api_health():
    """Check if FastAPI service is healthy"""
    try:
        response = requests.get("http://fastapi:8000/health", timeout=10)
        if response.status_code == 200:
            logging.info(f"API Health Check: {response.json()}")
            return "API is healthy"
        else:
            logging.error(f"API returned status code: {response.status_code}")
            raise Exception(f"API health check failed with status {response.status_code}")
    except Exception as e:
        logging.error(f"API health check failed: {str(e)}")
        raise


def insert_sample_data():
    """Insert sample data into the database via API"""
    try:
        sample_items = [
            {"name": "Laptop", "description": "High-performance laptop", "price": 1299.99},
            {"name": "Mouse", "description": "Wireless mouse", "price": 29.99},
            {"name": "Keyboard", "description": "Mechanical keyboard", "price": 89.99}
        ]
        
        for item in sample_items:
            response = requests.post(
                "http://fastapi:8000/items",
                json=item,
                timeout=10
            )
            if response.status_code == 200:
                logging.info(f"Created item: {response.json()}")
            else:
                logging.warning(f"Failed to create item: {item}")
        
        return "Sample data inserted successfully"
    except Exception as e:
        logging.error(f"Failed to insert sample data: {str(e)}")
        raise


def query_items():
    """Query all items from the API"""
    try:
        response = requests.get("http://fastapi:8000/items", timeout=10)
        if response.status_code == 200:
            items = response.json()
            logging.info(f"Total items in database: {len(items)}")
            for item in items:
                logging.info(f"Item: {item}")
            return f"Retrieved {len(items)} items"
        else:
            raise Exception(f"Failed to query items, status: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to query items: {str(e)}")
        raise


# Define the DAG
with DAG(
    'example_etl_pipeline',
    default_args=default_args,
    description='An example ETL pipeline with FastAPI and PostgreSQL',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example', 'etl'],
) as dag:

    # Task 1: Check database connection
    check_db = PythonOperator(
        task_id='check_database',
        python_callable=check_database_connection,
    )

    # Task 2: Check API health
    check_api = PythonOperator(
        task_id='check_api_health',
        python_callable=check_api_health,
    )

    # Task 3: Create table if not exists (using PostgreSQL operator)
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL
            );
        """,
    )

    # Task 4: Insert sample data
    insert_data = PythonOperator(
        task_id='insert_sample_data',
        python_callable=insert_sample_data,
    )

    # Task 5: Query and log items
    query_data = PythonOperator(
        task_id='query_items',
        python_callable=query_items,
    )

    # Define task dependencies
    [check_db, check_api] >> create_table >> insert_data >> query_data

