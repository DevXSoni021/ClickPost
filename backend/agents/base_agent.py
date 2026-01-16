"""
Base Agent class for all specialized sub-agents
Handles text-to-SQL generation, query execution, and response formatting
"""

import os
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import google.generativeai as genai
from backend.database.connection import get_db_manager

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all specialized agents
    Provides common functionality for text-to-SQL and query execution
    """
    
    def __init__(self, agent_name: str, db_name: str, schema_description: str):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent (e.g., "ShopCore")
            db_name: Database name for connection (e.g., "shopcore")
            schema_description: Description of database schema for SQL generation
        """
        self.agent_name = agent_name
        self.db_name = db_name
        self.schema_description = schema_description
        self.db_manager = get_db_manager()
        
        # Initialize Gemini for text-to-SQL
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            logger.warning(f"{agent_name}: No GEMINI_API_KEY found, text-to-SQL will not work")
            self.model = None
    
    def _extract_order_id_from_text(self, query: str) -> Optional[int]:
        """Extract explicit order ID from text using pattern matching"""
        import re
        # matches patterns like: "order 1", "order id 5", "order #10", etc.
        match = re.search(r'order\s*(?:id|number|#)?\s*(\d+)', query.lower())
        if match:
            return int(match.group(1))
        return None
    
    def generate_sql(self, natural_language_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate SQL query from natural language using Gemini
        
        Args:
            natural_language_query: User's query in natural language
            context: Additional context (e.g., user_id, order_id from previous agents)
        
        Returns:
            SQL query string
        """
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        # Build prompt for SQL generation
        prompt = f"""You are a SQL expert. Generate a PostgreSQL query based on the following:

DATABASE SCHEMA:
{self.schema_description}

USER QUERY: {natural_language_query}

CONTEXT: {context if context else 'None'}

REQUIREMENTS:
1. Generate ONLY the SQL query, no explanations
2. Use single quotes for string literals derived from the user query (e.g. name LIKE '%Monitor%')
3. Use %s placeholders ONLY for structural IDs (user_id, order_id) that are likely provided in CONTEXT
4. Include appropriate JOINs if multiple tables are needed
5. Add ORDER BY and LIMIT clauses where appropriate
6. Return empty result if no data matches

EXAMPLE:
User Query: "Show me orders for Gaming Monitor"
Context: {{'user_id': 1}}
Correct SQL: SELECT * FROM orders o JOIN products p ON o.product_id = p.product_id WHERE o.user_id = %s AND p.name LIKE '%Gaming Monitor%'

SQL Query:"""
        
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up the SQL query
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # Escape % characters for psycopg2 execution (except %s placeholders)
            # This is critical because Gemini often generates LIKE '%...' which psycopg2 tries to interpolate
            sql_query = sql_query.replace('%', '%%').replace('%%s', '%s')
            
            logger.info(f"{self.agent_name} generated SQL: {sql_query}")
            return sql_query
        
        except Exception as e:
            logger.error(f"{self.agent_name} SQL generation error: {e}")
            raise
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query with parameters
        
        Args:
            query: SQL query with %s placeholders
            params: Query parameters
        
        Returns:
            List of dictionaries with query results
        """
        try:
            results = self.db_manager.execute_query(
                db_name=self.db_name,
                query=query,
                params=params,
                fetch=True
            )
            
            logger.info(f"{self.agent_name} query returned {len(results)} rows")
            return results
        
        except Exception as e:
            logger.error(f"{self.agent_name} query execution error: {e}")
            raise
    
    def format_response(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format query results into structured response
        
        Args:
            data: Raw query results
        
        Returns:
            Formatted response dictionary
        """
        return {
            "agent": self.agent_name,
            "database": self.db_name,
            "record_count": len(data),
            "data": data,
            "success": True
        }
    
    @abstractmethod
    def process_query(
        self, 
        natural_language_query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query (must be implemented by subclasses)
        
        Args:
            natural_language_query: User's query
            context: Additional context from other agents
        
        Returns:
            Formatted response with query results
        """
        pass
    
    def extract_parameters(self, query: str, context: Dict[str, Any]) -> tuple:
        """
        Extract parameters for parameterized query from context
        
        Args:
            query: SQL query with %s placeholders
            context: Context dictionary with values
        
        Returns:
            Tuple of parameter values
        """
        # Helper: Smart parameter extraction based on common patterns
        # If we have specific keys in context, prioritize them in a logical order
        # This is a heuristic since we don't strictly know the SQL structure here
        
        # Count number of %s in query
        param_count = query.count('%s')
        
        params = []
        
        # Priority keys often used in WHERE clauses
        priority_keys = ['order_id', 'user_id', 'product_id', 'shipment_id', 'wallet_id', 'ticket_id']
        
        # 1. Try to match params based on what's in context vs what might be needed
        # If we have exact keys in context, use them
        used_keys = set()
        
        # Heuristic: If prompt asked for user_id and order_id structural usage, they likely appear in that order 
        # or one of them appears.
        
        # Let's iterate priority keys and see if they are in context
        for key in priority_keys:
            if key in context and context[key] is not None:
                if len(params) < param_count:
                    params.append(context[key])
                    used_keys.add(key)
        
        # 2. If we still need params, fill with other available context values (like strings, product names)
        # filtered by what we haven't used
        if len(params) < param_count:
            for key, value in context.items():
                if key not in used_keys and value is not None:
                    params.append(value)
                    if len(params) >= param_count:
                        break
        
        # 3. Fallback: If we still don't have enough, Pad with None or empty string to match count
        # This prevents "tuple index out of range" or argument mismatch in psycopg2
        while len(params) < param_count:
             # Default fallback - often better to fail with "0 matches" than "IndexError"
             params.append(None)
             
        return tuple(params)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors and return formatted error response
        
        Args:
            error: Exception that occurred
        
        Returns:
            Error response dictionary
        """
        logger.error(f"{self.agent_name} error: {error}")
        
        return {
            "agent": self.agent_name,
            "database": self.db_name,
            "success": False,
            "error": str(error),
            "data": []
        }
    
    def validate_results(self, results: List[Dict[str, Any]]) -> bool:
        """
        Validate query results
        
        Args:
            results: Query results to validate
        
        Returns:
            True if results are valid
        """
        return isinstance(results, list)
