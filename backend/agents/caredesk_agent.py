"""
CareDesk Agent - Handles customer support tickets and queries
"""

from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

CAREDESK_SCHEMA = """
Tables:
1. tickets (ticket_id, user_id, order_id, reference_id, reference_type, issue_type, title, description, 
            priority, status, assigned_agent_id, created_at, resolved_at, resolution_notes)
2. ticket_messages (message_id, ticket_id, sender_type, sender_id, content, attachments, 
                     created_at, is_public)
3. satisfaction_surveys (survey_id, ticket_id, rating, comments, response_date, sentiment_analysis)

Relationships:
- ticket_messages.ticket_id -> tickets.ticket_id
- satisfaction_surveys.ticket_id -> tickets.ticket_id
- tickets.order_id -> orders.order_id (Hard Link)

Reference Types: ORDER, TRANSACTION, GENERAL
Issue Types: DELIVERY_ISSUE, PAYMENT_ISSUE, PRODUCT_QUALITY, REFUND_REQUEST, COMPLAINT
Priority: LOW, MEDIUM, HIGH, URGENT
Status: OPEN, IN_PROGRESS, ON_HOLD, RESOLVED, CLOSED
Sender Types: USER, AGENT, SYSTEM
"""

class CareDeskAgent(BaseAgent):
    """Agent for handling customer support queries"""
    
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
        """
        Process customer support queries
        
        Args:
            natural_language_query: User's query about support tickets
            context: Additional context (user_id, order_id, etc.)
        
        Returns:
            Formatted response with ticket data
        """
        try:
            query_lower = natural_language_query.lower()
            
            # 1. Try to extract order_id from text (Explicit Override Logic)
            text_id = self._extract_order_id_from_text(natural_language_query)
            if text_id and context:
                logger.info(f"Extracted Order {text_id} from text for CareDesk (Overriding context)")
                context['order_id'] = text_id

            # Check for ticket status queries
            if 'ticket' in query_lower or 'support' in query_lower:
                return self._handle_ticket_query(context)
            
            # Check for complaint queries
            elif 'complaint' in query_lower or 'issue' in query_lower:
                return self._handle_issue_query(context)
            
            # Generic query
            else:
                return self._handle_generic_query(natural_language_query, context)
        
        except Exception as e:
            return self.handle_error(e)
    
    def _handle_ticket_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle ticket status queries"""
        
        user_id = context.get('user_id') if context else None
        order_id = context.get('order_id') if context else None
        
        if order_id:
            # Efficiency Fix: Prioritize Hard Link (order_id column) over Reference logic
            logger.info(f"Looking up tickets via explicit Order ID: {order_id}")
            sql = """
            SELECT t.ticket_id, t.order_id, t.issue_type, t.title, t.description, 
                   t.priority, t.status, t.assigned_agent_id, t.created_at, t.resolved_at
            FROM tickets t
            WHERE t.order_id = %s
            ORDER BY t.created_at DESC
            """
            params = (order_id,)
        
        elif user_id:
            # Find all tickets for user
            sql = """
            SELECT t.ticket_id, t.order_id, t.issue_type, t.title, t.description, 
                   t.priority, t.status, t.assigned_agent_id, t.created_at, t.resolved_at
            FROM tickets t
            WHERE t.user_id = %s
            ORDER BY t.created_at DESC
            LIMIT 10
            """
            params = (user_id,)
        
        else:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id or order_id required for ticket query",
                "data": []
            }
        
        results = self.execute_query(sql, params)
        
        # If tickets found, get messages for the most recent one
        if results:
            ticket_id = results[0]['ticket_id']
            messages = self._get_ticket_messages(ticket_id)
            results[0]['messages'] = messages
        
        return self.format_response(results)
    
    def _handle_issue_query(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle issue/complaint queries"""
        
        user_id = context.get('user_id') if context else None
        
        if not user_id:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": "user_id required for issue query",
                "data": []
            }
        
        sql = """
        SELECT ticket_id, issue_type, title, description, priority, status, created_at
        FROM tickets
        WHERE user_id = %s AND status IN ('OPEN', 'IN_PROGRESS')
        ORDER BY priority DESC, created_at DESC
        LIMIT 5
        """
        
        results = self.execute_query(sql, (user_id,))
        return self.format_response(results)
    
    def _get_ticket_messages(self, ticket_id: int) -> List[Dict[str, Any]]:
        """Get messages for a specific ticket"""
        
        sql = """
        SELECT message_id, sender_type, sender_id, content, created_at, is_public
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at ASC
        LIMIT 20
        """
        
        return self.execute_query(sql, (ticket_id,))
    
    def _handle_generic_query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle generic support queries"""
        
        sql = self.generate_sql(query, context)
        params = self.extract_parameters(sql, context or {})
        
        results = self.execute_query(sql, params)
        return self.format_response(results)
    
    def get_ticket_by_id(self, ticket_id: int) -> Dict[str, Any]:
        """Get ticket details by ID"""
        
        sql = """
        SELECT t.ticket_id, t.user_id, t.order_id, t.issue_type, t.title, 
               t.description, t.priority, t.status, t.assigned_agent_id, 
               t.created_at, t.resolved_at, t.resolution_notes
        FROM tickets t
        WHERE t.ticket_id = %s
        """
        
        results = self.execute_query(sql, (ticket_id,))
        
        if results:
            # Get messages
            messages = self._get_ticket_messages(ticket_id)
            results[0]['messages'] = messages
        
        return self.format_response(results)
    
    def get_tickets_by_order(self, order_id: int) -> Dict[str, Any]:
        """
        Get tickets related to an order (used by orchestrator)
        
        Args:
            order_id: Order ID to look up
        
        Returns:
            Ticket information
        """
        sql = """
        SELECT ticket_id, user_id, issue_type, title, description, 
               priority, status, assigned_agent_id, created_at, resolved_at
        FROM tickets
        WHERE order_id = %s
        ORDER BY created_at DESC
        """
        
        results = self.execute_query(sql, (order_id,))
        return self.format_response(results)
    
    def get_satisfaction_rating(self, ticket_id: int) -> Dict[str, Any]:
        """Get satisfaction survey for a ticket"""
        
        sql = """
        SELECT survey_id, ticket_id, rating, comments, response_date
        FROM satisfaction_surveys
        WHERE ticket_id = %s
        """
        
        results = self.execute_query(sql, (ticket_id,))
        return self.format_response(results)
