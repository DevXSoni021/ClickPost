"""
Create a new database entry across all 4 databases
Creates a complete order flow: Order -> Shipment -> Transaction -> Ticket
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

def create_new_order_entry():
    """Create a new order entry with related data across all databases"""
    
    # Connect to ShopCore
    shopcore_conn = psycopg2.connect(os.getenv('DATABASE_URL_SHOPCORE'))
    shopcore_cursor = shopcore_conn.cursor()
    
    # Create a new order for user_id=1 (John Doe) - USB-C Hub
    # First, get product_id for USB-C Hub
    shopcore_cursor.execute("SELECT product_id FROM products WHERE name = 'USB-C Hub'")
    product_result = shopcore_cursor.fetchone()
    
    if not product_result:
        print("❌ USB-C Hub product not found. Creating it first...")
        shopcore_cursor.execute(
            "INSERT INTO products (name, category, description, price, stock_quantity, sku) VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id",
            ('USB-C Hub', 'Accessories', '7-in-1 USB-C Hub', 3500.00, 80, 'HUB-USBC-7')
        )
        product_id = shopcore_cursor.fetchone()[0]
    else:
        product_id = product_result[0]
    
    # Create new order
    order_date = datetime.now() - timedelta(days=2)
    shopcore_cursor.execute(
        """INSERT INTO orders (user_id, product_id, order_date, status, quantity, total_amount, special_notes) 
           VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING order_id""",
        (1, product_id, order_date, 'SHIPPED', 1, 3500.00, 'Please handle with care - fragile item')
    )
    new_order_id = shopcore_cursor.fetchone()[0]
    shopcore_conn.commit()
    print(f"✅ Created new order: Order ID {new_order_id} - USB-C Hub - ₹3,500")
    
    # Connect to ShipStream
    shipstream_conn = psycopg2.connect(os.getenv('DATABASE_URL_SHIPSTREAM'))
    shipstream_cursor = shipstream_conn.cursor()
    
    # Create shipment
    tracking_number = f'TRK{random.randint(10000000, 99999999)}'
    estimated_arrival = datetime.now() + timedelta(days=1)
    
    shipstream_cursor.execute(
        """INSERT INTO shipments (order_id, tracking_number, origin_warehouse_id, destination_address, 
           estimated_arrival, shipment_status, carrier_name) 
           VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING shipment_id""",
        (new_order_id, tracking_number, 1, '123 Main St, Mumbai, Maharashtra 400001', 
         estimated_arrival, 'IN_TRANSIT', 'BlueDart')
    )
    shipment_id = shipstream_cursor.fetchone()[0]
    
    # Create tracking events
    tracking_events = [
        (shipment_id, 1, datetime.now() - timedelta(days=2, hours=10), 
         'Package picked from warehouse', 'Delhi Distribution Center', 'PICKED', None),
        (shipment_id, None, datetime.now() - timedelta(days=1, hours=14), 
         'In transit to destination city', 'Gurgaon Hub', 'IN_TRANSIT', None),
        (shipment_id, 2, datetime.now() - timedelta(hours=6), 
         'Arrived at destination warehouse', 'Mumbai Distribution Center', 'AT_WAREHOUSE', None),
    ]
    
    shipstream_cursor.executemany(
        """INSERT INTO tracking_events (shipment_id, warehouse_id, timestamp, status_update, location, event_type, notes) 
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        tracking_events
    )
    shipstream_conn.commit()
    print(f"✅ Created shipment: Tracking #{tracking_number} - Status: IN_TRANSIT")
    
    # Connect to PayGuard
    payguard_conn = psycopg2.connect(os.getenv('DATABASE_URL_PAYGUARD'))
    payguard_cursor = payguard_conn.cursor()
    
    # Get wallet_id for user_id=1
    payguard_cursor.execute("SELECT wallet_id FROM wallets WHERE user_id = 1")
    wallet_result = payguard_cursor.fetchone()
    wallet_id = wallet_result[0] if wallet_result else 1
    
    # Create transaction
    payguard_cursor.execute(
        """INSERT INTO transactions (wallet_id, order_id, reference_id, amount, transaction_type, status, timestamp, description) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING transaction_id""",
        (wallet_id, new_order_id, f'REF-ORD-{new_order_id}', 3500.00, 'DEBIT', 'COMPLETED', 
         order_date, 'Payment for USB-C Hub')
    )
    transaction_id = payguard_cursor.fetchone()[0]
    payguard_conn.commit()
    print(f"✅ Created transaction: Transaction ID {transaction_id} - ₹3,500 DEBIT - COMPLETED")
    
    # Connect to CareDesk
    caredesk_conn = psycopg2.connect(os.getenv('DATABASE_URL_CAREDESK'))
    caredesk_cursor = caredesk_conn.cursor()
    
    # Create a support ticket
    caredesk_cursor.execute(
        """INSERT INTO tickets (user_id, reference_id, reference_type, issue_type, title, description, priority, status, created_at) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ticket_id""",
        (1, new_order_id, 'ORDER', 'DELIVERY_QUERY', 'USB-C Hub delivery status', 
         'I ordered a USB-C Hub 2 days ago. Can you please provide an update on when it will be delivered?', 
         'MEDIUM', 'OPEN', datetime.now() - timedelta(hours=6))
    )
    ticket_id = caredesk_cursor.fetchone()[0]
    
    # Add a message to the ticket
    caredesk_cursor.execute(
        """INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, content, is_public) 
           VALUES (%s, %s, %s, %s, %s)""",
        (ticket_id, 'USER', 1, 'I need this hub urgently for my work setup. Please expedite if possible.', True)
    )
    caredesk_conn.commit()
    print(f"✅ Created support ticket: Ticket ID {ticket_id} - DELIVERY_QUERY")
    
    # Close all connections
    shopcore_cursor.close()
    shopcore_conn.close()
    shipstream_cursor.close()
    shipstream_conn.close()
    payguard_cursor.close()
    payguard_conn.close()
    caredesk_cursor.close()
    caredesk_conn.close()
    
    print(f"\n{'='*60}")
    print("✅ NEW DATABASE ENTRY CREATED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"\n📦 Order Details:")
    print(f"   Order ID: {new_order_id}")
    print(f"   Product: USB-C Hub")
    print(f"   Amount: ₹3,500")
    print(f"   Status: SHIPPED")
    print(f"\n🚚 Shipment Details:")
    print(f"   Tracking #: {tracking_number}")
    print(f"   Status: IN_TRANSIT")
    print(f"   Estimated Arrival: {estimated_arrival.strftime('%Y-%m-%d %H:%M')}")
    print(f"\n💳 Transaction Details:")
    print(f"   Transaction ID: {transaction_id}")
    print(f"   Amount: ₹3,500")
    print(f"   Type: DEBIT")
    print(f"   Status: COMPLETED")
    print(f"\n🎫 Support Ticket:")
    print(f"   Ticket ID: {ticket_id}")
    print(f"   Issue: DELIVERY_QUERY")
    print(f"   Status: OPEN")
    print(f"\n{'='*60}")
    print("\n💡 SUGGESTED QUESTIONS TO TEST:")
    print("   1. 'Where is my USB-C Hub?'")
    print("   2. 'What's the status of my USB-C Hub order?'")
    print("   3. 'I ordered a USB-C Hub 2 days ago, when will it arrive?'")
    print("   4. 'Check my USB-C Hub delivery status and payment confirmation'")
    print("   5. 'I opened a ticket about my USB-C Hub, what's the status?'")
    print(f"{'='*60}\n")
    
    return {
        'order_id': new_order_id,
        'tracking_number': tracking_number,
        'transaction_id': transaction_id,
        'ticket_id': ticket_id
    }

if __name__ == "__main__":
    create_new_order_entry()
