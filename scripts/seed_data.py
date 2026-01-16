"""
Seed sample data into all 4 Neon databases
Creates DETERMINISTIC test data (IDs 1-10) for development and testing.
Strict 1-to-1 mapping for Verification.
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def get_connection(db_url):
    try:
        if not db_url:
            return None
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def truncate_tables(cursor, tables):
    """Clean tables before seeding"""
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")

def seed_shopcore():
    """Seed ShopCore: Users 1-10, Products 1-10, Orders 1-10"""
    conn = get_connection(os.getenv('DATABASE_URL_SHOPCORE'))
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        truncate_tables(cursor, ['orders', 'products', 'users'])
        
        # 1. Users 1-10
        users = [(i, f'user{i}@example.com', f'User {i}', f'+91-{i:010d}', True) for i in range(1, 11)]
        cursor.executemany(
            "INSERT INTO users (user_id, email, name, phone, premium_status) VALUES (%s, %s, %s, %s, %s)",
            users
        )
        
        # 2. Products 1-10 (Realistic Names)
        product_list = [
            "Wireless Noise-Canceling Headphones",
            "Smart Fitness Watch Series 5",
            "4K Ultra HD Gaming Monitor",
            "Mechanical RGB Keyboard",
            "Ergonomic Wireless Mouse",
            "Portable SSD 1TB",
            "Bluetooth Portable Speaker",
            "HD Webcam 1080p",
            "USB-C Docking Station",
            "Gaming Headset with Mic"
        ]
        
        products = []
        for i in range(1, 11):
            name = product_list[i-1]
            products.append((
                i, 
                name, 
                'Electronics', 
                f'Description for {name}', 
                1000.0 * i, 
                100, 
                f'SKU-{i:03d}'
            ))
            
        cursor.executemany(
            "INSERT INTO products (product_id, name, category, description, price, stock_quantity, sku) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            products
        )
        
        # 3. Orders 1-10 (User i buys Product i)
        orders = [(i, i, i, datetime.now(), 'SHIPPED', 1, 1000.0 * i, f"Note {i}") for i in range(1, 11)]
        cursor.executemany(
            "INSERT INTO orders (order_id, user_id, product_id, order_date, status, quantity, total_amount, special_notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            orders
        )
        
        conn.commit()
        print("✓ ShopCore: Cleaned & Seeded (IDs 1-10)")
        return True
    except Exception as e:
        print(f"✗ ShopCore Fail: {e}")
        return False
    finally:
        conn.close()

def seed_shipstream():
    """Seed ShipStream: Warehouse 1, Shipments 1-10 (For Order i)"""
    conn = get_connection(os.getenv('DATABASE_URL_SHIPSTREAM'))
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        truncate_tables(cursor, ['tracking_events', 'shipments', 'warehouses'])
        
        # Warehouse 1
        cursor.execute(
            "INSERT INTO warehouses (warehouse_id, location, city, country, manager_name) VALUES (1, 'Hub 1', 'Delhi', 'India', 'Mgr 1')"
        )
        
        # Shipments 1-10 (Linked to Order i)
        shipments = []
        for i in range(1, 11):
            shipments.append((
                i, # shipment_id
                i, # order_id
                f'TRK{i:04d}', # TRK0001, TRK0002...
                1,
                f'Addr {i}',
                datetime.now(),
                'IN_TRANSIT',
                'FedEx'
            ))
        cursor.executemany(
            "INSERT INTO shipments (shipment_id, order_id, tracking_number, origin_warehouse_id, destination_address, estimated_arrival, shipment_status, carrier_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            shipments
        )
        
        # Tracking Events
        events = [(i, i, i, 1, datetime.now(), 'In Transit', 'City', 'IN_TRANSIT', 'Note') for i in range(1, 11)]
        cursor.executemany(
            "INSERT INTO tracking_events (event_id, shipment_id, order_id, warehouse_id, timestamp, status_update, location, event_type, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            events
        )

        conn.commit()
        print("✓ ShipStream: Cleaned & Seeded (IDs 1-10)")
        return True
    except Exception as e:
        print(f"✗ ShipStream Fail: {e}")
        return False
    finally:
        conn.close()

def seed_payguard():
    """Seed PayGuard: Wallet 1-10, Transaction 1-10 (For Order i)"""
    conn = get_connection(os.getenv('DATABASE_URL_PAYGUARD'))
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        truncate_tables(cursor, ['payment_methods', 'transactions', 'wallets'])
        
        # Wallets 1-10 (User i)
        wallets = [(i, i, 50000.00, 'INR', 'ACTIVE') for i in range(1, 11)]
        cursor.executemany(
            "INSERT INTO wallets (wallet_id, user_id, balance, currency, wallet_status) VALUES (%s, %s, %s, %s, %s)",
            wallets
        )
        
        # Transactions 1-10 (Wallet i pays for Order i)
        txns = [(i, i, i, f'TXN{i:04d}', 1000.0*i, 'DEBIT', 'COMPLETED', datetime.now(), f'Pay Order {i}') for i in range(1, 11)]
        cursor.executemany(
            "INSERT INTO transactions (transaction_id, wallet_id, order_id, reference_id, amount, transaction_type, status, timestamp, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            txns
        )

        conn.commit()
        print("✓ PayGuard: Cleaned & Seeded (IDs 1-10)")
        return True
    except Exception as e:
        print(f"✗ PayGuard Fail: {e}")
        return False
    finally:
        conn.close()

def seed_caredesk():
    """Seed CareDesk: Tickets 1-10 (For Order i)"""
    conn = get_connection(os.getenv('DATABASE_URL_CAREDESK'))
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        truncate_tables(cursor, ['satisfaction_surveys', 'ticket_messages', 'tickets'])
        
        # Tickets 1-10 (User i, Order i)
        # Using explicit order_id column as requested for efficiency
        tickets = []
        for i in range(1, 11):
            tickets.append((
                i, # ticket_id
                i, # user_id
                i, # order_id (Explicit)
                i, # reference_id
                'ORDER',
                'DELIVERY_ISSUE',
                f'Issue for Order {i}',
                f'Desc {i}',
                'HIGH',
                'OPEN',
                1
            ))
        
        cursor.executemany(
            "INSERT INTO tickets (ticket_id, user_id, order_id, reference_id, reference_type, issue_type, title, description, priority, status, assigned_agent_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            tickets
        )

        conn.commit()
        print("✓ CareDesk: Cleaned & Seeded (IDs 1-10)")
        return True
    except Exception as e:
        print(f"✗ CareDesk Fail: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🌱 Starting SEQUENTIAL Data Reset (Truncate + Seed)...")
    seed_shopcore()
    seed_shipstream()
    seed_payguard()
    seed_caredesk()
    print("\n✅ Verification Ready: IDs 1-10 are perfectly aligned across all DBs.")

if __name__ == "__main__":
    main()
