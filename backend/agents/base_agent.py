import os
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import google.generativeai as genai
from backend.database.connection import get_db_manager

logger = logging.getLogger(__name__)

class BaseAgent(ABC):

    def __init__(self, agent_name: str, db_name: str, schema_description: str):

        self.agent_name = agent_name
        self.db_name = db_name
        self.schema_description = schema_description
        self.db_manager = get_db_manager()

        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            logger.warning(f"{agent_name}: No GEMINI_API_KEY found, text-to-SQL will not work")
            self.model = None

    def _extract_order_id_from_text(self, query: str) -> Optional[int]:

        import re
        match = re.search(r'order\s*(?:id|number|#)?\s*(\d+)', query.lower())
        if match:
            return int(match.group(1))
        return None

    def generate_sql(self, natural_language_query: str, context: Optional[Dict[str, Any]] = None) -> str:

        if not self.model:
            raise ValueError("Gemini model not initialized")

        prompt = f

        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()

            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

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

        pass

    def extract_parameters(self, query: str, context: Dict[str, Any]) -> tuple:

        param_count = query.count('%s')

        params = []

        priority_keys = ['order_id', 'user_id', 'product_id', 'shipment_id', 'wallet_id', 'ticket_id']

        used_keys = set()

        for key in priority_keys:
            if key in context and context[key] is not None:
                if len(params) < param_count:
                    params.append(context[key])
                    used_keys.add(key)

        if len(params) < param_count:
            for key, value in context.items():
                if key not in used_keys and value is not None:
                    params.append(value)
                    if len(params) >= param_count:
                        break

        while len(params) < param_count:
             params.append(None)

        return tuple(params)

    def handle_error(self, error: Exception) -> Dict[str, Any]:

        logger.error(f"{self.agent_name} error: {error}")

        return {
            "agent": self.agent_name,
            "database": self.db_name,
            "success": False,
            "error": str(error),
            "data": []
        }

    def validate_results(self, results: List[Dict[str, Any]]) -> bool:

        return isinstance(results, list)
