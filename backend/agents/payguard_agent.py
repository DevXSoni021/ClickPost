from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

PAYGUARD_SCHEMA = 

class PayGuardAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_name="PayGuard",
            db_name="payguard",
            schema_description=PAYGUARD_SCHEMA
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
                logger.info(f"Extracted Order {text_id} from text for PayGuard (Overriding context)")
                context['order_id'] = text_id

            if 'refund' in query_lower:
                return self._handle_refund_query(context)

            elif 'balance' in query_lower or 'wallet' in query_lower:
                return self._handle_wallet_query(context)

            elif 'transaction' in query_lower or 'payment' in query_lower:
                return self._handle_transaction_query(context)

            else:
                return self._handle_generic_query(natural_language_query, context)

        except Exception as e:
            return self.handle_error(e)

    def _handle_refund_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        order_id = context.get('order_id') if context else None
        user_id = context.get('user_id') if context else None

        if order_id:
            sql = 
            params = (order_id,)

        elif user_id:
            sql = 
            params = (user_id,)

        else:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "order_id or user_id required for refund query",
                "data": []
            }

        results = self.execute_query(sql, params)

        if not results:
            return {
                "agent": self.agent_name,
                "success": True,
                "message": "No refund found",
                "data": []
            }

        return self.format_response(results)

    def _handle_wallet_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        user_id = context.get('user_id') if context else None
        order_id = context.get('order_id') if context else None

        if order_id:
            sql = 
            return self.format_response(self.execute_query(sql, (order_id,)))

        elif user_id:
            sql = 
            return self.format_response(self.execute_query(sql, (user_id,)))

        else:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id or order_id required for wallet query",
                "data": []
            }

    def _handle_transaction_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        order_id = context.get('order_id') if context else None
        user_id = context.get('user_id') if context else None

        if order_id:
            sql = 
            params = (order_id,)

        elif user_id:
            sql = 
            params = (user_id,)

        else:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "order_id or user_id required for transaction query",
                "data": []
            }

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def _handle_generic_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:

        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def get_payment_methods(self, user_id: int) -> Dict[str, Any]:

        sql = 

        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)

    def get_transaction_by_order(self, order_id: int) -> Dict[str, Any]:

        sql = 

        results = self.execute_query(sql, (order_id,))
        return self.format_response(results)
