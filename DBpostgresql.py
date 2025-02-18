# database.py
import psycopg2
import psycopg2.extras
import json
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "dbname": "demo",
    "user": "postgres",
    "password": "@Kemenangan1",
    "port": 5432
}

# Connect to Database
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# Initialize Database (with TEXT columns)
def initialize_db():
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS transcriptDat (
                        serial SERIAL PRIMARY KEY,
                        jsonserial TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                print("✅ Database initialized with updated schema.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        conn.close()

def insert_data(json_data, summary):
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO transcriptDat (jsonserial, summary, created_at)
                    VALUES (%s, %s, %s) RETURNING serial;
                ''', (json_data, summary, datetime.now()))
                serial = cur.fetchone()[0]
                conn.commit()
                print(f"✅ Data inserted with serial: {serial}")
                return serial
    except Exception as e:
        print(f"❌ Error inserting data: {e}")


def fetch_all():
    with connect_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('SELECT * FROM transcriptDat;')
            records = cur.fetchall()
            for record in records:
                print(dict(record))
