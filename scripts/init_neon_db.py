"""
Initialize Neon PostgreSQL databases with schema
Creates 4 separate databases: ShopCore, ShipStream, PayGuard, CareDesk
"""

import os
import psycopg2
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Database schemas
SHOPCORE_SCHEMA = """
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    premium_status BOOLEAN DEFAULT FALSE,
    account_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    profile_data JSONB
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    sku VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PLACED',
    quantity INT DEFAULT 1,
    total_amount DECIMAL(10, 2),
    special_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
"""

SHIPSTREAM_SCHEMA = """
-- Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    manager_name VARCHAR(255),
    capacity INT,
    current_stock INT DEFAULT 0,
    phone_number VARCHAR(20)
);

-- Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    origin_warehouse_id INT REFERENCES warehouses(warehouse_id),
    destination_address TEXT NOT NULL,
    estimated_arrival TIMESTAMP,
    actual_arrival TIMESTAMP,
    shipment_status VARCHAR(50) DEFAULT 'PENDING',
    carrier_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracking Events Table
CREATE TABLE IF NOT EXISTS tracking_events (
    event_id SERIAL PRIMARY KEY,
    shipment_id INT REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    warehouse_id INT REFERENCES warehouses(warehouse_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_update VARCHAR(255),
    location VARCHAR(255),
    event_type VARCHAR(50),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_shipments_order_id ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_tracking_shipment_id ON tracking_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_tracking_timestamp ON tracking_events(timestamp);
"""

PAYGUARD_SCHEMA = """
-- Wallets Table
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    balance DECIMAL(12, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'INR',
    wallet_status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    wallet_id INT REFERENCES wallets(wallet_id),
    order_id INT,
    reference_id VARCHAR(100),
    amount DECIMAL(12, 2) NOT NULL,
    transaction_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'PENDING',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    metadata JSONB
);

-- Payment Methods Table
CREATE TABLE IF NOT EXISTS payment_methods (
    method_id SERIAL PRIMARY KEY,
    wallet_id INT REFERENCES wallets(wallet_id) ON DELETE CASCADE,
    provider VARCHAR(100),
    provider_token VARCHAR(255),
    expiry_date VARCHAR(7),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_wallet_id ON transactions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_transactions_order_id ON transactions(order_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
"""

CAREDESK_SCHEMA = """
-- Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    reference_id INT,
    reference_type VARCHAR(50),
    issue_type VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(50) DEFAULT 'OPEN',
    assigned_agent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Ticket Messages Table
CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    sender_type VARCHAR(20),
    sender_id INT,
    content TEXT NOT NULL,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT TRUE
);

-- Satisfaction Surveys Table
CREATE TABLE IF NOT EXISTS satisfaction_surveys (
    survey_id SERIAL PRIMARY KEY,
    ticket_id INT REFERENCES tickets(ticket_id),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment_analysis JSONB
);

CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_ticket_id ON ticket_messages(ticket_id);
"""

def init_database(connection_string: str, schema: str, db_name: str):
    """Initialize a single database with schema"""
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Execute schema
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
    """Initialize all 4 databases"""
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
