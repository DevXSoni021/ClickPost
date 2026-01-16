"""
Create 4 databases in Neon PostgreSQL
This script creates the databases before schema initialization
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Base connection string (connect to default database)
BASE_CONNECTION_STRING = "postgresql://neondb_owner:npg_ko0K9UXcAltG@ep-lucky-smoke-ahh5mazo-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Database names to create
DATABASES = ['db_shopcore', 'db_shipstream', 'db_payguard', 'db_caredesk']

def create_database(db_name: str):
    """Create a database if it doesn't exist"""
    try:
        # Connect to default database to create new database
        conn = psycopg2.connect(BASE_CONNECTION_STRING)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database {db_name} already exists")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✓ Created database {db_name}")
        
        cursor.close()
        conn.close()
        return True
    
    except Exception as e:
        print(f"✗ Failed to create database {db_name}: {e}")
        return False

def main():
    """Create all 4 databases"""
    print("🚀 Creating Neon PostgreSQL Databases...\n")
    
    success_count = 0
    
    for db_name in DATABASES:
        if create_database(db_name):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Database Creation Complete: {success_count}/4 successful")
    print(f"{'='*60}")
    
    if success_count < 4:
        print("\n⚠️  Some databases failed to create. Please check your connection string.")
        sys.exit(1)
    
    print("\n✅ All databases created successfully!")
    print("\nNext step: Run 'python scripts/init_neon_db.py' to initialize schemas")

if __name__ == "__main__":
    main()
