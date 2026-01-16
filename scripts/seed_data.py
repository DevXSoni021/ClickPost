"""
Seed sample data into all 4 Neon databases
Creates realistic test data for development and testing
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

def seed_shopcore():
    """Seed ShopCore database with users, products, and orders"""
    conn_string = os.getenv('DATABASE_URL_SHOPCORE')
    if not conn_string:
        print("⚠️  ShopCore connection string not found")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Insert users
        users_data = [
            ('john.doe@example.com', 'John Doe', '+91-9876543210', True),
            ('jane.smith@example.com', 'Jane Smith', '+91-9876543211', False),
            ('bob.wilson@example.com', 'Bob Wilson', '+91-9876543212', True),
        ]
        
        cursor.executemany(
            "INSERT INTO users (email, name, phone, premium_status) VALUES (%s, %s, %s, %s) ON CONFLICT (email) DO NOTHING",
            users_data
        )
        
        # Insert products
        products_data = [
            ('Gaming Monitor', 'Electronics', '27-inch 144Hz Gaming Monitor', 35000.00, 50, 'GM-27-144'),
            ('Wireless Mouse', 'Electronics', 'Ergonomic Wireless Mouse', 1500.00, 200, 'WM-ERG-01'),
            ('Mechanical Keyboard', 'Electronics', 'RGB Mechanical Keyboard', 8500.00, 100, 'KB-MECH-RGB'),
            ('Laptop Stand', 'Accessories', 'Adjustable Aluminum Laptop Stand', 2500.00, 150, 'LS-ALU-ADJ'),
            ('USB-C Hub', 'Accessories', '7-in-1 USB-C Hub', 3500.00, 80, 'HUB-USBC-7'),
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, description, price, stock_quantity, sku) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (sku) DO NOTHING",
            products_data
        )
        
        # Insert orders
        orders_data = [
            (1, 1, datetime.now() - timedelta(days=5), 'SHIPPED', 1, 35000.00, 'Please deliver before 5 PM'),
            (1, 2, datetime.now() - timedelta(days=3), 'DELIVERED', 2, 3000.00, None),
            (2, 3, datetime.now() - timedelta(days=2), 'CONFIRMED', 1, 8500.00, None),
            (3, 4, datetime.now() - timedelta(days=1), 'PLACED', 1, 2500.00, 'Gift wrap please'),
        ]
        
        cursor.executemany(
            "INSERT INTO orders (user_id, product_id, order_date, status, quantity, total_amount, special_notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            orders_data
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ ShopCore data seeded successfully")
        return True
    
    except Exception as e:
        print(f"✗ Failed to seed ShopCore: {e}")
        return False

def seed_shipstream():
    """Seed ShipStream database with warehouses, shipments, and tracking"""
    conn_string = os.getenv('DATABASE_URL_SHIPSTREAM')
    if not conn_string:
        print("⚠️  ShipStream connection string not found")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Insert warehouses
        warehouses_data = [
            ('Delhi Distribution Center', 'Delhi', 'India', 'Rajesh Kumar', 10000, 7500, '+91-11-12345678'),
            ('Mumbai Distribution Center', 'Mumbai', 'India', 'Priya Sharma', 12000, 9000, '+91-22-87654321'),
            ('Bangalore Hub', 'Bangalore', 'India', 'Amit Patel', 8000, 6000, '+91-80-11223344'),
        ]
        
        cursor.executemany(
            "INSERT INTO warehouses (location, city, country, manager_name, capacity, current_stock, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            warehouses_data
        )
        
        # Insert shipments
        shipments_data = [
            (1, 'TRK10242847', 1, '123 Main St, Mumbai, Maharashtra 400001', 
             datetime.now() + timedelta(days=1), None, 'IN_TRANSIT', 'BlueDart'),
            (2, 'TRK10242848', 1, '456 Park Ave, Delhi, Delhi 110001', 
             datetime.now() - timedelta(days=1), datetime.now(), 'DELIVERED', 'DTDC'),
        ]
        
        cursor.executemany(
            "INSERT INTO shipments (order_id, tracking_number, origin_warehouse_id, destination_address, estimated_arrival, actual_arrival, shipment_status, carrier_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (tracking_number) DO NOTHING",
            shipments_data
        )
        
        # Insert tracking events
        tracking_data = [
            (1, 1, datetime.now() - timedelta(days=4, hours=9), 'Package picked from warehouse', 'Delhi Distribution Center', 'PICKED', None),
            (1, None, datetime.now() - timedelta(days=3, hours=14), 'In transit to destination city', 'Gurgaon Hub', 'IN_TRANSIT', None),
            (1, 2, datetime.now() - timedelta(days=1, hours=8), 'Arrived at destination warehouse', 'Mumbai Distribution Center', 'AT_WAREHOUSE', None),
            (2, 1, datetime.now() - timedelta(days=2, hours=10), 'Package picked from warehouse', 'Delhi Distribution Center', 'PICKED', None),
            (2, None, datetime.now() - timedelta(days=1, hours=15), 'Out for delivery', 'Delhi Local', 'OUT_FOR_DELIVERY', None),
            (2, None, datetime.now(), 'Package delivered successfully', 'Customer Location', 'DELIVERED', 'Signed by customer'),
        ]
        
        cursor.executemany(
            "INSERT INTO tracking_events (shipment_id, warehouse_id, timestamp, status_update, location, event_type, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            tracking_data
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ ShipStream data seeded successfully")
        return True
    
    except Exception as e:
        print(f"✗ Failed to seed ShipStream: {e}")
        return False

def seed_payguard():
    """Seed PayGuard database with wallets, transactions, and payment methods"""
    conn_string = os.getenv('DATABASE_URL_PAYGUARD')
    if not conn_string:
        print("⚠️  PayGuard connection string not found")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Insert wallets
        wallets_data = [
            (1, 5000.00, 'INR', 'ACTIVE'),
            (2, 12000.00, 'INR', 'ACTIVE'),
            (3, 3500.00, 'INR', 'ACTIVE'),
        ]
        
        cursor.executemany(
            "INSERT INTO wallets (user_id, balance, currency, wallet_status) VALUES (%s, %s, %s, %s)",
            wallets_data
        )
        
        # Insert transactions
        transactions_data = [
            (1, 1, 'REF-ORD-1', 35000.00, 'DEBIT', 'COMPLETED', datetime.now() - timedelta(days=5), 'Payment for Gaming Monitor', None),
            (1, 1, 'REF-REFUND-1', 35000.00, 'REFUND', 'COMPLETED', datetime.now() - timedelta(days=1), 'Refund for Gaming Monitor', None),
            (1, 2, 'REF-ORD-2', 3000.00, 'DEBIT', 'COMPLETED', datetime.now() - timedelta(days=3), 'Payment for Wireless Mouse', None),
            (2, 3, 'REF-ORD-3', 8500.00, 'DEBIT', 'COMPLETED', datetime.now() - timedelta(days=2), 'Payment for Mechanical Keyboard', None),
        ]
        
        cursor.executemany(
            "INSERT INTO transactions (wallet_id, order_id, reference_id, amount, transaction_type, status, timestamp, description, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            transactions_data
        )
        
        # Insert payment methods
        payment_methods_data = [
            (1, 'CREDIT_CARD', 'tok_visa_4242', '12/26', True),
            (2, 'UPI', 'upi_jane@paytm', None, True),
            (3, 'DEBIT_CARD', 'tok_mc_5555', '08/25', True),
        ]
        
        cursor.executemany(
            "INSERT INTO payment_methods (wallet_id, provider, provider_token, expiry_date, is_default) VALUES (%s, %s, %s, %s, %s)",
            payment_methods_data
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ PayGuard data seeded successfully")
        return True
    
    except Exception as e:
        print(f"✗ Failed to seed PayGuard: {e}")
        return False

def seed_caredesk():
    """Seed CareDesk database with tickets, messages, and surveys"""
    conn_string = os.getenv('DATABASE_URL_CAREDESK')
    if not conn_string:
        print("⚠️  CareDesk connection string not found")
        return False
    
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Insert tickets
        tickets_data = [
            (1, 1, 'ORDER', 'DELIVERY_ISSUE', 'Gaming Monitor not delivered', 
             'I ordered a gaming monitor 5 days ago but it has not been delivered yet. Tracking shows it is in Mumbai but I have not received any delivery attempt.', 
             'HIGH', 'IN_PROGRESS', 101, datetime.now() - timedelta(days=1), None, None),
            (2, 3, 'ORDER', 'PRODUCT_QUALITY', 'Keyboard has defective keys', 
             'The mechanical keyboard I received has some keys that are not working properly.', 
             'MEDIUM', 'OPEN', None, datetime.now() - timedelta(hours=12), None, None),
        ]
        
        cursor.executemany(
            "INSERT INTO tickets (user_id, reference_id, reference_type, issue_type, title, description, priority, status, assigned_agent_id, created_at, resolved_at, resolution_notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            tickets_data
        )
        
        # Insert ticket messages
        messages_data = [
            (1, 'USER', 1, 'I really need this monitor urgently for work. Can you please expedite?', None, True),
            (1, 'AGENT', 101, 'We apologize for the delay. I have contacted the delivery partner and they will attempt delivery today by 6 PM.', None, True),
            (1, 'USER', 1, 'Thank you! Please keep me updated.', None, True),
        ]
        
        cursor.executemany(
            "INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, content, attachments, is_public) VALUES (%s, %s, %s, %s, %s, %s)",
            messages_data
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ CareDesk data seeded successfully")
        return True
    
    except Exception as e:
        print(f"✗ Failed to seed CareDesk: {e}")
        return False

def main():
    """Seed all databases"""
    print("🌱 Starting Database Seeding...\n")
    
    results = []
    results.append(('ShopCore', seed_shopcore()))
    results.append(('ShipStream', seed_shipstream()))
    results.append(('PayGuard', seed_payguard()))
    results.append(('CareDesk', seed_caredesk()))
    
    success_count = sum(1 for _, success in results if success)
    
    print(f"\n{'='*60}")
    print(f"Data Seeding Complete: {success_count}/4 successful")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
