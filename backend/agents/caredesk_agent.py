from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

CAREDESK_SCHEMA = 

class CareDeskAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_name="CareDesk",
            db_name="caredesk",
            schema_description=CAREDESK_SCHEMA
        )

    def process_query(
        self, 
        natural_language_query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        try:
            query_lower = natural_language_query.lower()

            text_id = self._extract_order_id_from_text(natural_language_query)
            if text_id and context:
                logger.info(f"Extracted Order {text_id} from text for CareDesk (Overriding context)")
                context['order_id'] = text_id

            if 'ticket' in query_lower or 'support' in query_lower:
                return self._handle_ticket_query(context)

            elif 'complaint' in query_lower or 'issue' in query_lower:
                return self._handle_issue_query(context)

            else:
                return self._handle_generic_query(natural_language_query, context)

        except Exception as e:
            return self.handle_error(e)

    def _handle_ticket_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        user_id = context.get('user_id') if context else None
        order_id = context.get('order_id') if context else None

        if order_id:
            logger.info(f"Looking up tickets via explicit Order ID: {order_id}")
            sql = 
            params = (order_id,)

        elif user_id:
            sql = 
            params = (user_id,)

        else:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id or order_id required for ticket query",
                "data": []
            }

        results = self.execute_query(sql, params)

        if results:
            ticket_id = results[0]['ticket_id']
            messages = self._get_ticket_messages(ticket_id)
            results[0]['messages'] = messages

        return self.format_response(results)

    def _handle_issue_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        user_id = context.get('user_id') if context else None

        if not user_id:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id required for issue query",
                "data": []
            }

        sql = 

        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)

    def _get_ticket_messages(self, ticket_id: int) -> List[Dict[str, Any]]:

        sql = 

        return self.execute_query(sql, (ticket_id,))

    def _handle_generic_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:

        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def get_ticket_by_id(self, ticket_id: int) -> Dict[str, Any]:

        sql = 

        results = self.execute_query(sql, (ticket_id,))

        if results:
            messages = self._get_ticket_messages(ticket_id)
            results[0]['messages'] = messages

        return self.format_response(results)

    def get_tickets_by_order(self, order_id: int) -> Dict[str, Any]:

        sql = 

        results = self.execute_query(sql, (order_id,))
        return self.format_response(results)

    def get_satisfaction_rating(self, ticket_id: int) -> Dict[str, Any]:

        sql = 

        results = self.execute_query(sql, (ticket_id,))
        return self.format_response(results)
