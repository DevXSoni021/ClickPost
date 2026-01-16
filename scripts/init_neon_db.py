import os
import psycopg2
from dotenv import load_dotenv
import sys

load_dotenv()

SHOPCORE_SCHEMA = 

SHIPSTREAM_SCHEMA = 

PAYGUARD_SCHEMA = 

CAREDESK_SCHEMA = 

def init_database(connection_string: str, schema: str, db_name: str):

    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute(schema)
        conn.commit()

        cursor.close()
        conn.close()

        print(f"✓ {db_name} database initialized successfully")
        return True

    except Exception as e:
        print(f"✗ Failed to initialize {db_name}: {e}")
        return False

def main():

    print("🚀 Starting Neon PostgreSQL Database Initialization...\n")

    databases = [
        ('DATABASE_URL_SHOPCORE', SHOPCORE_SCHEMA, 'DB_ShopCore'),
        ('DATABASE_URL_SHIPSTREAM', SHIPSTREAM_SCHEMA, 'DB_ShipStream'),
        ('DATABASE_URL_PAYGUARD', PAYGUARD_SCHEMA, 'DB_PayGuard'),
        ('DATABASE_URL_CAREDESK', CAREDESK_SCHEMA, 'DB_CareDesk')
    ]

    success_count = 0

    for env_var, schema, db_name in databases:
        connection_string = os.getenv(env_var)

        if not connection_string:
            print(f"⚠️  Warning: {env_var} not found in environment")
            continue

        if init_database(connection_string, schema, db_name):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Database Initialization Complete: {success_count}/4 successful")
    print(f"{'='*60}")

    if success_count < 4:
        sys.exit(1)

if __name__ == "__main__":
    main()
