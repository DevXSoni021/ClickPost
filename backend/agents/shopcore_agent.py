from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

SHOPCORE_SCHEMA = 

class ShopCoreAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            agent_name="ShopCore",
            db_name="shopcore",
            schema_description=SHOPCORE_SCHEMA
        )

    def process_query(
        self, 
        natural_language_query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        try:
            query_type = self._classify_query(natural_language_query)

            if query_type == "ORDER_LOOKUP":
                return self._handle_order_lookup(natural_language_query, context)
            elif query_type == "PRODUCT_SEARCH":
                return self._handle_product_search(natural_language_query, context)
            elif query_type == "USER_ORDERS":
                return self._handle_user_orders(context)
            else:
                return self._handle_generic_query(natural_language_query, context)

        except Exception as e:
            return self.handle_error(e)

    def _classify_query(self, query: str) -> str:

        query_lower = query.lower()

        if any(word in query_lower for word in ['order', 'ordered', 'purchase', 'bought']):
            return "ORDER_LOOKUP"
        elif 'where is my' in query_lower:
            return "ORDER_LOOKUP"
        elif any(word in query_lower for word in ['product', 'item', 'find', 'search']):
            return "PRODUCT_SEARCH"
        elif 'my orders' in query_lower or 'order history' in query_lower:
            return "USER_ORDERS"
        elif 'my' in query_lower and len(self._extract_product_keywords(query)) > 0:
            return "ORDER_LOOKUP"
        else:
            return "GENERIC"

    def _handle_order_lookup(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:

        user_id = context.get('user_id') if context else None

        order_id = self._extract_order_id_from_text(query)

        is_new_name_search = any(word in query.lower() for word in ['where', 'find', 'status of', 'search', 'buy', 'bought'])

        if not order_id and context and not is_new_name_search:
            order_id = context.get('order_id')

        product_keywords = self._extract_product_keywords(query)

        if user_id:
            if product_keywords and len(product_keywords) > 2 and not order_id:
                pass

            if order_id:
                logger.info(f"Looking up specific Order {order_id} (ignoring strict user ownership for efficiency)")
                sql = 
                params = (order_id,)
            else:
                sql = 
                clean_kw = product_keywords.replace('-', ' ')
                hyphen_kw = product_keywords.replace(' ', '-')

                params = (
                    user_id, 
                    f"%{product_keywords}%",
                    f"%{clean_kw}%",
                    f"%{hyphen_kw}%",
                    f"%{product_keywords.replace(' ', '')}%"
                )
        else:
            if product_keywords and len(product_keywords) > 2:
                sql = 
                params = (f"%{product_keywords}%",)
            else:
                sql = 
                params = ()

        results = self.execute_query(sql, params)

        if results and len(results) > 0:
            context = context or {}
            context['order_id'] = results[0].get('order_id')
            context['product_name'] = results[0].get('product_name')

        response = self.format_response(results)
        if context:
            response['context'] = context
        return response

    def _handle_product_search(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:

        keywords = self._extract_product_keywords(query)

        sql = 

        search_term = f"%{keywords}%"
        params = (search_term, search_term)

        results = self.execute_query(sql, params)
        return self.format_response(results)

    def _handle_user_orders(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:

        user_id = context.get('user_id') if context else None

        if not user_id:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id required for order history",
                "data": []
            }

        sql = 

        results = self.execute_query(sql, (user_id,))
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

    def _extract_product_keywords(self, query: str) -> str:

        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'my', 'i', 'where', 'what', 'find', 'search', 'ordered', 'order', 'purchase', 'bought', 'when', 'will', 'it', 'arrive', 'status', 'payment', 'days', 'ago', 'do', 'have', 'any', 'support', 'tickets', 'for'}

        clean_query = query.replace('?', '').replace('.', '').replace(',', '').strip()

        import re
        product_patterns = re.findall(r'\b[A-Z][a-zA-Z0-9-]+\b(?:\s+[A-Z][a-zA-Z0-9-]+\b)*', clean_query)

        if product_patterns:
            for pattern in product_patterns:
                if pattern.lower() not in stop_words and len(pattern) > 3:
                    logger.info(f"Found product pattern: {pattern}")
                    return pattern.lower()

        words = clean_query.lower().split()
        keywords_list = [w for w in words if w not in stop_words]
        keywords = ' '.join(keywords_list)

        keywords = ' '.join(keywords.split())
        return keywords if keywords and len(keywords) > 1 else ''

    def find_order_by_product_name(
        self, 
        product_name: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:

        sql = 

        params = [f"%{product_name.lower()}%"]

        if user_id:
            sql += " AND o.user_id = %s"
            params.append(user_id)

        sql += " ORDER BY o.order_date DESC LIMIT 1"

        results = self.execute_query(sql, tuple(params))
        return self.format_response(results)
