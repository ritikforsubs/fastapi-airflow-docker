from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
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


def log_table_statistics():
    """Log statistics about the items table"""
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM items;")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(price) FROM items;")
        avg_price = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(price) FROM items;")
        max_price = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(price) FROM items;")
        min_price = cursor.fetchone()[0]
        
        logging.info(f"Table Statistics:")
        logging.info(f"  Total items: {count}")
        logging.info(f"  Average price: ${avg_price if avg_price else 0:.2f}")
        logging.info(f"  Maximum price: ${max_price if max_price else 0:.2f}")
        logging.info(f"  Minimum price: ${min_price if min_price else 0:.2f}")
        
        cursor.close()
        conn.close()
        
        return "Statistics logged successfully"
    except Exception as e:
        logging.error(f"Failed to log statistics: {str(e)}")
        raise


# Define the DAG
with DAG(
    'database_maintenance',
    default_args=default_args,
    description='Database maintenance and monitoring tasks',
    schedule_interval='@daily',
    catchup=False,
    tags=['maintenance', 'database'],
) as dag:

    # Task 1: Log table statistics
    log_stats = PythonOperator(
        task_id='log_table_statistics',
        python_callable=log_table_statistics,
    )

    # Task 2: Vacuum and analyze
    vacuum_analyze = PostgresOperator(
        task_id='vacuum_analyze',
        postgres_conn_id='postgres_default',
        sql="""
            VACUUM ANALYZE items;
        """,
    )

    # Define task dependencies
    log_stats >> vacuum_analyze

