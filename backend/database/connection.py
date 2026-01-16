"""
Database connection management for Neon PostgreSQL
Handles connection pooling for 4 separate databases
"""

import os
import psycopg2
from psycopg2 import pool
from typing import Optional, Dict, Any, List
import logging
from contextlib import contextmanager
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)

def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert database types to JSON-serializable types
    
    Args:
        obj: Object that may contain Decimal, datetime, etc.
    
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_json_serializable(item) for item in obj)
    else:
        return obj

class DatabaseManager:
    """Manages connections to multiple Neon PostgreSQL databases"""
    
    def __init__(self):
        self.pools: Dict[str, pool.SimpleConnectionPool] = {}
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Initialize connection pools for all 4 databases"""
        databases = {
            'shopcore': os.getenv('DATABASE_URL_SHOPCORE'),
            'shipstream': os.getenv('DATABASE_URL_SHIPSTREAM'),
            'payguard': os.getenv('DATABASE_URL_PAYGUARD'),
            'caredesk': os.getenv('DATABASE_URL_CAREDESK')
        }
        
        for db_name, connection_string in databases.items():
            if not connection_string:
                logger.warning(f"No connection string found for {db_name}")
                continue
            
            try:
                self.pools[db_name] = pool.SimpleConnectionPool(
                    minconn=2,
                    maxconn=10,
                    dsn=connection_string
                )
                logger.info(f"✓ Connection pool initialized for {db_name}")
            except Exception as e:
                logger.error(f"✗ Failed to initialize pool for {db_name}: {e}")
                raise
    
    @contextmanager
    def get_connection(self, db_name: str):
        """
        Get a database connection from the pool
        
        Args:
            db_name: Name of database (shopcore, shipstream, payguard, caredesk)
        
        Yields:
            Database connection
        """
        if db_name not in self.pools:
            raise ValueError(f"Unknown database: {db_name}")
        
        conn = None
        try:
            conn = self.pools[db_name].getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error in {db_name}: {e}")
            raise
        finally:
            if conn:
                self.pools[db_name].putconn(conn)
    
    def execute_query(
        self, 
        db_name: str, 
        query: str, 
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query with parameters
        
        Args:
            db_name: Database name
            query: SQL query with %s placeholders
            params: Query parameters
            fetch: Whether to fetch results
        
        Returns:
            List of dictionaries with query results
        """
        with self.get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                
                if fetch and cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    # Convert rows to dictionaries and make JSON-serializable
                    results = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        # Convert Decimal and other non-JSON types
                        results.append(convert_to_json_serializable(row_dict))
                    return results
                
                return []
    
    def close_all(self):
        """Close all connection pools"""
        for db_name, pool_obj in self.pools.items():
            try:
                pool_obj.closeall()
                logger.info(f"✓ Closed connection pool for {db_name}")
            except Exception as e:
                logger.error(f"Error closing pool for {db_name}: {e}")

# Global database manager instance
db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def cleanup_db_manager():
    """Cleanup database connections"""
    global db_manager
    if db_manager:
        db_manager.close_all()
        db_manager = None
