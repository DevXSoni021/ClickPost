"""
ShopCore Agent - Handles e-commerce orders, products, and user queries
"""

from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

SHOPCORE_SCHEMA = """
Tables:
1. users (user_id, email, name, phone, premium_status, account_created_at, last_login, profile_data)
2. products (product_id, name, category, description, price, stock_quantity, sku, created_at)
3. orders (order_id, user_id, product_id, order_date, status, quantity, total_amount, special_notes)

Relationships:
- orders.user_id -> users.user_id
- orders.product_id -> products.product_id

Order Status Values: PLACED, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
"""

class ShopCoreAgent(BaseAgent):
    """Agent for handling e-commerce queries"""
    
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
        """
        Process e-commerce related queries
        
        Args:
            natural_language_query: User's query about orders/products
            context: Additional context (user_id, etc.)
        
        Returns:
            Formatted response with order/product data
        """
        try:
            # Determine query type
            query_type = self._classify_query(natural_language_query)
            
            if query_type == "ORDER_LOOKUP":
                return self._handle_order_lookup(natural_language_query, context)
            elif query_type == "PRODUCT_SEARCH":
                return self._handle_product_search(natural_language_query, context)
            elif query_type == "USER_ORDERS":
                return self._handle_user_orders(context)
            else:
                # Generic query - use text-to-SQL
                return self._handle_generic_query(natural_language_query, context)
        
        except Exception as e:
            return self.handle_error(e)
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['order', 'ordered', 'purchase', 'bought']):
            return "ORDER_LOOKUP"
        elif any(word in query_lower for word in ['product', 'item', 'find', 'search']):
            return "PRODUCT_SEARCH"
        elif 'my orders' in query_lower or 'order history' in query_lower:
            return "USER_ORDERS"
        else:
            return "GENERIC"
    
    def _handle_order_lookup(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle order lookup queries"""
        
        # Extract product name or order details from query
        user_id = context.get('user_id') if context else None
        
        # Extract product keywords from query
        product_keywords = self._extract_product_keywords(query)
        
        # Build SQL to find orders - filter by product name if mentioned
        if user_id:
            if product_keywords and len(product_keywords) > 2:  # Only filter if we have meaningful keywords
                # Try multiple variations of the product name search
                sql = """
                SELECT o.order_id, p.name as product_name, o.order_date, 
                       o.status, o.quantity, o.total_amount, o.special_notes
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.user_id = %s AND (
                    LOWER(p.name) LIKE %s OR 
                    LOWER(p.name) LIKE %s OR
                    LOWER(p.name) LIKE %s
                )
                ORDER BY o.order_date DESC
                LIMIT 10
                """
                # Try with hyphen, without hyphen, and with spaces
                keywords_lower = product_keywords.lower()
                params = (
                    user_id, 
                    f"%{keywords_lower}%",
                    f"%{keywords_lower.replace('-', '')}%",
                    f"%{keywords_lower.replace('-', ' ')}%"
                )
            else:
                sql = """
                SELECT o.order_id, p.name as product_name, o.order_date, 
                       o.status, o.quantity, o.total_amount, o.special_notes
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.user_id = %s
                ORDER BY o.order_date DESC
                LIMIT 10
                """
                params = (user_id,)
        else:
            # Try to extract product name from query
            if product_keywords and len(product_keywords) > 2:
                sql = """
                SELECT o.order_id, p.name as product_name, o.order_date, 
                       o.status, o.quantity, o.total_amount, u.name as user_name
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN users u ON o.user_id = u.user_id
                WHERE LOWER(p.name) LIKE %s
                ORDER BY o.order_date DESC
                LIMIT 10
                """
                params = (f"%{product_keywords}%",)
            else:
                sql = """
                SELECT o.order_id, p.name as product_name, o.order_date, 
                       o.status, o.quantity, o.total_amount, u.name as user_name
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN users u ON o.user_id = u.user_id
                ORDER BY o.order_date DESC
                LIMIT 10
                """
                params = ()
        
        results = self.execute_query(sql, params)
        
        # Add order_id to context for downstream agents
        if results and len(results) > 0:
            context = context or {}
            # Get the most recent matching order
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
        """Handle product search queries"""
        
        # Extract product keywords
        keywords = self._extract_product_keywords(query)
        
        sql = """
        SELECT product_id, name, category, description, price, stock_quantity, sku
        FROM products
        WHERE LOWER(name) LIKE %s OR LOWER(description) LIKE %s
        ORDER BY created_at DESC
        LIMIT 10
        """
        
        search_term = f"%{keywords}%"
        params = (search_term, search_term)
        
        results = self.execute_query(sql, params)
        return self.format_response(results)
    
    def _handle_user_orders(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get all orders for a user"""
        
        user_id = context.get('user_id') if context else None
        
        if not user_id:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id required for order history",
                "data": []
            }
        
        sql = """
        SELECT o.order_id, p.name as product_name, o.order_date, 
               o.status, o.quantity, o.total_amount
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
        """
        
        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)
    
    def _handle_generic_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle generic queries using text-to-SQL"""
        
        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})
        
        results = self.execute_query(sql, params)
        return self.format_response(results)
    
    def _extract_product_keywords(self, query: str) -> str:
        """Extract product keywords from query"""
        # Simple keyword extraction - remove common words but keep product names
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'my', 'i', 'where', 'what', 'find', 'search', 'ordered', 'order', 'purchase', 'bought', 'when', 'will', 'it', 'arrive', 'status', 'payment', 'days', 'ago'}
        
        # First, try to find product names (words with hyphens or capital letters)
        import re
        # Look for product-like patterns: USB-C Hub, Gaming Monitor, etc.
        product_patterns = re.findall(r'\b[A-Z][A-Za-z0-9-]+\s+[A-Z][A-Za-z]+|\b[A-Z][A-Za-z0-9-]+', query)
        if product_patterns:
            # Return the first product-like pattern found
            return ' '.join(product_patterns[0].split()).lower()
        
        # Fallback: remove stop words
        words = query.lower().split()
        keywords = ' '.join([w for w in words if w not in stop_words])
        # Clean up the keywords - remove extra spaces
        keywords = ' '.join(keywords.split())
        return keywords if keywords and len(keywords) > 1 else ''
    
    def find_order_by_product_name(
        self, 
        product_name: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Find orders by product name (used by orchestrator)
        
        Args:
            product_name: Name of the product
            user_id: Optional user ID to filter
        
        Returns:
            Order information
        """
        sql = """
        SELECT o.order_id, p.name as product_name, o.order_date, 
               o.status, o.quantity, o.total_amount, o.user_id
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        WHERE LOWER(p.name) LIKE %s
        """
        
        params = [f"%{product_name.lower()}%"]
        
        if user_id:
            sql += " AND o.user_id = %s"
            params.append(user_id)
        
        sql += " ORDER BY o.order_date DESC LIMIT 1"
        
        results = self.execute_query(sql, tuple(params))
        return self.format_response(results)
