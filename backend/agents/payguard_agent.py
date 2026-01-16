"""
PayGuard Agent - Handles payment, transactions, and refund queries
"""

from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

PAYGUARD_SCHEMA = """
Tables:
1. wallets (wallet_id, user_id, balance, currency, wallet_status, created_at, last_updated)
2. transactions (transaction_id, wallet_id, order_id, reference_id, amount, transaction_type, 
                 status, timestamp, description, metadata)
3. payment_methods (method_id, wallet_id, provider, provider_token, expiry_date, is_default, 
                     created_at, last_used)

Relationships:
- transactions.wallet_id -> wallets.wallet_id
- payment_methods.wallet_id -> wallets.wallet_id
- wallets.user_id links to users in ShopCore

Transaction Types: DEBIT, REFUND, CREDIT, REVERSAL
Transaction Status: PENDING, COMPLETED, FAILED, REVERSED
Payment Providers: CREDIT_CARD, DEBIT_CARD, PAYPAL, BANK_TRANSFER, UPI
"""

class PayGuardAgent(BaseAgent):
    """Agent for handling payment and transaction queries"""
    
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
        """
        Process payment and transaction queries
        
        Args:
            natural_language_query: User's query about payments/refunds
            context: Additional context (order_id, user_id, etc.)
        
        Returns:
            Formatted response with transaction data
        """
        try:
            query_lower = natural_language_query.lower()
            
            # Check for refund queries
            if 'refund' in query_lower:
                return self._handle_refund_query(context)
            
            # Check for wallet balance queries
            elif 'balance' in query_lower or 'wallet' in query_lower:
                return self._handle_wallet_query(context)
            
            # Check for transaction history
            elif 'transaction' in query_lower or 'payment' in query_lower:
                return self._handle_transaction_query(context)
            
            # Generic query
            else:
                return self._handle_generic_query(natural_language_query, context)
        
        except Exception as e:
            return self.handle_error(e)
    
    def _handle_refund_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle refund status queries"""
        
        order_id = context.get('order_id') if context else None
        user_id = context.get('user_id') if context else None
        
        if order_id:
            # Find refund for specific order
            sql = """
            SELECT t.transaction_id, t.order_id, t.amount, t.transaction_type, 
                   t.status, t.timestamp, t.description, w.user_id
            FROM transactions t
            JOIN wallets w ON t.wallet_id = w.wallet_id
            WHERE t.order_id = %s AND t.transaction_type = 'REFUND'
            ORDER BY t.timestamp DESC
            LIMIT 1
            """
            params = (order_id,)
        
        elif user_id:
            # Find all refunds for user
            sql = """
            SELECT t.transaction_id, t.order_id, t.amount, t.transaction_type, 
                   t.status, t.timestamp, t.description
            FROM transactions t
            JOIN wallets w ON t.wallet_id = w.wallet_id
            WHERE w.user_id = %s AND t.transaction_type = 'REFUND'
            ORDER BY t.timestamp DESC
            LIMIT 10
            """
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
        """Handle wallet balance queries"""
        
        user_id = context.get('user_id') if context else None
        
        if not user_id:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id required for wallet query",
                "data": []
            }
        
        sql = """
        SELECT wallet_id, user_id, balance, currency, wallet_status, 
               created_at, last_updated
        FROM wallets
        WHERE user_id = %s
        """
        
        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)
    
    def _handle_transaction_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle transaction history queries"""
        
        order_id = context.get('order_id') if context else None
        user_id = context.get('user_id') if context else None
        
        if order_id:
            # Get transactions for specific order
            sql = """
            SELECT t.transaction_id, t.order_id, t.amount, t.transaction_type, 
                   t.status, t.timestamp, t.description
            FROM transactions t
            WHERE t.order_id = %s
            ORDER BY t.timestamp DESC
            """
            params = (order_id,)
        
        elif user_id:
            # Get all transactions for user
            sql = """
            SELECT t.transaction_id, t.order_id, t.amount, t.transaction_type, 
                   t.status, t.timestamp, t.description
            FROM transactions t
            JOIN wallets w ON t.wallet_id = w.wallet_id
            WHERE w.user_id = %s
            ORDER BY t.timestamp DESC
            LIMIT 20
            """
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
        """Handle generic payment queries"""
        
        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})
        
        results = self.execute_query(sql, params)
        return self.format_response(results)
    
    def get_payment_methods(self, user_id: int) -> Dict[str, Any]:
        """Get payment methods for a user"""
        
        sql = """
        SELECT pm.method_id, pm.provider, pm.expiry_date, pm.is_default, 
               pm.created_at, pm.last_used
        FROM payment_methods pm
        JOIN wallets w ON pm.wallet_id = w.wallet_id
        WHERE w.user_id = %s
        ORDER BY pm.is_default DESC, pm.last_used DESC
        """
        
        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)
    
    def get_transaction_by_order(self, order_id: int) -> Dict[str, Any]:
        """
        Get all transactions for an order (used by orchestrator)
        
        Args:
            order_id: Order ID to look up
        
        Returns:
            Transaction information
        """
        sql = """
        SELECT t.transaction_id, t.order_id, t.amount, t.transaction_type, 
               t.status, t.timestamp, t.description, w.user_id
        FROM transactions t
        JOIN wallets w ON t.wallet_id = w.wallet_id
        WHERE t.order_id = %s
        ORDER BY t.timestamp DESC
        """
        
        results = self.execute_query(sql, (order_id,))
        return self.format_response(results)
