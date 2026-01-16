"""
ShipStream Agent - Handles logistics, shipments, and tracking queries
"""

from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

SHIPSTREAM_SCHEMA = """
Tables:
1. warehouses (warehouse_id, location, city, country, manager_name, capacity, current_stock, phone_number)
2. shipments (shipment_id, order_id, tracking_number, origin_warehouse_id, destination_address, 
              estimated_arrival, actual_arrival, shipment_status, carrier_name, created_at)
3. tracking_events (event_id, shipment_id, warehouse_id, timestamp, status_update, location, event_type, notes)

Relationships:
- shipments.origin_warehouse_id -> warehouses.warehouse_id
- tracking_events.shipment_id -> shipments.shipment_id
- tracking_events.warehouse_id -> warehouses.warehouse_id

Shipment Status: PENDING, PICKED, IN_TRANSIT, AT_WAREHOUSE, OUT_FOR_DELIVERY, DELIVERED
Event Types: PICKED, IN_TRANSIT, AT_WAREHOUSE, OUT_FOR_DELIVERY, DELIVERED
"""

class ShipStreamAgent(BaseAgent):
    """Agent for handling logistics and shipment tracking queries"""

    def __init__(self):
        super().__init__(
            agent_name="ShipStream",
            db_name="shipstream",
            schema_description=SHIPSTREAM_SCHEMA
        )

    def process_query(
        self, 
        natural_language_query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process shipment and tracking queries

        Args:
            natural_language_query: User's query about shipments
            context: Additional context (order_id from ShopCore, etc.)

        Returns:
            Formatted response with shipment data
        """
        try:
            order_id = self._extract_order_id_from_text(natural_language_query)

            if not order_id and context:
                order_id = context.get('order_id')

            if order_id:
                logger.info(f"Looking up shipment for Order {order_id} (Prioritized ID Lookup)")
                return self._get_shipment_by_order_id(order_id)

            tracking_number = self._extract_tracking_number(natural_language_query)
            if tracking_number:
                return self._get_shipment_by_tracking(tracking_number)

            return {
                "agent": self.agent_name,
                "database": self.db_name,
                "success": True,
                "record_count": 0,
                "data": [],
                "message": "No order_id or tracking number provided. Please provide order details first."
            }

        except Exception as e:
            return self.handle_error(e)

    def _get_shipment_by_order_id(self, order_id: int) -> Dict[str, Any]:
        """Get shipment details by order ID"""

        shipment_sql = """
        SELECT s.shipment_id, s.order_id, s.tracking_number, s.shipment_status,
               s.estimated_arrival, s.actual_arrival, s.carrier_name,
               w.location as origin_location, w.city as origin_city
        FROM shipments s
        LEFT JOIN warehouses w ON s.origin_warehouse_id = w.warehouse_id
        WHERE s.order_id = %s
        """

        shipment_results = self.execute_query(shipment_sql, (order_id,))

        if not shipment_results:
            return {
                "agent": self.agent_name,
                "success": True,
                "message": "No shipment found for this order",
                "data": []
            }

        shipment = shipment_results[0]
        shipment_id = shipment['shipment_id']

        tracking_sql = """
        SELECT te.timestamp, te.status_update, te.location, te.event_type, te.notes,
               w.location as warehouse_location
        FROM tracking_events te
        LEFT JOIN warehouses w ON te.warehouse_id = w.warehouse_id
        WHERE te.shipment_id = %s
        ORDER BY te.timestamp DESC
        """

        tracking_results = self.execute_query(tracking_sql, (shipment_id,))

        response_data = {
            "shipment": shipment,
            "tracking_events": tracking_results,
            "current_location": tracking_results[0]['location'] if tracking_results else "Unknown"
        }

        return {
            "agent": self.agent_name,
            "database": self.db_name,
            "record_count": 1,
            "data": [response_data],
            "success": True
        }

    def _get_shipment_by_tracking(self, tracking_number: str) -> Dict[str, Any]:
        """Get shipment details by tracking number"""

        shipment_sql = """
        SELECT s.shipment_id, s.order_id, s.tracking_number, s.shipment_status,
               s.estimated_arrival, s.actual_arrival, s.carrier_name,
               w.location as origin_location
        FROM shipments s
        LEFT JOIN warehouses w ON s.origin_warehouse_id = w.warehouse_id
        WHERE s.tracking_number = %s
        """

        shipment_results = self.execute_query(shipment_sql, (tracking_number,))

        if not shipment_results:
            return {
                "agent": self.agent_name,
                "success": True,
                "message": "No shipment found with this tracking number",
                "data": []
            }

        shipment = shipment_results[0]
        shipment_id = shipment['shipment_id']

        tracking_sql = """
        SELECT timestamp, status_update, location, event_type, notes
        FROM tracking_events
        WHERE shipment_id = %s
        ORDER BY timestamp DESC
        """

        tracking_results = self.execute_query(tracking_sql, (shipment_id,))

        response_data = {
            "shipment": shipment,
            "tracking_events": tracking_results
        }

        return self.format_response([response_data])

    def _handle_generic_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle generic shipment queries"""

        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def _extract_tracking_number(self, query: str) -> Optional[str]:
        """Extract tracking number from query"""
        import re
        pattern = r'TRK\d+'
        match = re.search(pattern, query.upper())
        return match.group(0) if match else None

    def get_warehouse_info(self, warehouse_id: Optional[int] = None) -> Dict[str, Any]:
        """Get warehouse information"""

        if warehouse_id:
            sql = "SELECT * FROM warehouses WHERE warehouse_id = %s"
            params = (warehouse_id,)
        else:
            sql = "SELECT * FROM warehouses ORDER BY city"
            params = ()

        results = self.execute_query(sql, params)
        return self.format_response(results)
