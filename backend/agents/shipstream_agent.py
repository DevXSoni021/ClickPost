from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

SHIPSTREAM_SCHEMA = 

class ShipStreamAgent(BaseAgent):

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

        shipment_sql = 

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

        tracking_sql = 

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

        shipment_sql = 

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

        tracking_sql = 

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

        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def _extract_tracking_number(self, query: str) -> Optional[str]:

        import re
        pattern = r'TRK\d+'
        match = re.search(pattern, query.upper())
        return match.group(0) if match else None

    def get_warehouse_info(self, warehouse_id: Optional[int] = None) -> Dict[str, Any]:

        if warehouse_id:
            sql = "SELECT * FROM warehouses WHERE warehouse_id = %s"
            params = (warehouse_id,)
        else:
            sql = "SELECT * FROM warehouses ORDER BY city"
            params = ()

        results = self.execute_query(sql, params)
        return self.format_response(results)
