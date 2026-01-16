"""
Super Agent - Orchestrates multiple specialized agents using LangGraph
Handles query analysis, dependency resolution, and response synthesis
"""

import os
import logging
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import google.generativeai as genai

# Import specialized agents
from backend.agents.shopcore_agent import ShopCoreAgent
from backend.agents.shipstream_agent import ShipStreamAgent
from backend.agents.payguard_agent import PayGuardAgent
from backend.agents.caredesk_agent import CareDeskAgent

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State schema for LangGraph workflow"""
    original_query: str
    user_id: Optional[int]
    agents_needed: Dict[str, bool]
    execution_order: List[str]
    context: Dict[str, Any]
    agent_results: Dict[str, Any]
    narrative_response: str
    timestamp: str

class OmniRetailSuperAgent:
    """
    Super Agent that orchestrates multiple specialized agents
    Uses LangGraph for state management and workflow coordination
    """
    
    def __init__(self):
        """Initialize super agent with all sub-agents"""
        self.shopcore_agent = ShopCoreAgent()
        self.shipstream_agent = ShipStreamAgent()
        self.payguard_agent = PayGuardAgent()
        self.caredesk_agent = CareDeskAgent()
        
        # Initialize Gemini for query analysis and synthesis
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            logger.warning("No GEMINI_API_KEY found")
            self.model = None
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        logger.info("✓ Super Agent initialized with 4 sub-agents")
    
    def analyze_query(self, query: str, user_id: Optional[int] = None) -> AgentState:
        """
        Analyze user query to determine which agents are needed
        
        Args:
            query: Natural language query from user
            user_id: Optional user ID for context
        
        Returns:
            Initial agent state with analysis
        """
        query_lower = query.lower()
        
        # Determine which agents are needed
        agents_needed = {
            'ShopCore': False,
            'ShipStream': False,
            'PayGuard': False,
            'CareDesk': False
        }
        
        # ShopCore: order, product, purchase queries
        if any(word in query_lower for word in ['order', 'ordered', 'product', 'purchase', 'bought', 'buy']):
            agents_needed['ShopCore'] = True
        
        # ShipStream: tracking, delivery, shipment queries
        if any(word in query_lower for word in ['track', 'delivery', 'shipment', 'where', 'location', 'arrive', 'delivered']):
            agents_needed['ShipStream'] = True
            agents_needed['ShopCore'] = True  # Need order_id from ShopCore
        
        # PayGuard: payment, refund, transaction queries
        if any(word in query_lower for word in ['refund', 'payment', 'transaction', 'paid', 'wallet', 'balance']):
            agents_needed['PayGuard'] = True
            if 'order' in query_lower or 'refund' in query_lower:
                agents_needed['ShopCore'] = True  # Need order_id
        
        # CareDesk: support, ticket, complaint queries
        if any(word in query_lower for word in ['ticket', 'support', 'complaint', 'issue', 'help', 'problem']):
            agents_needed['CareDesk'] = True
            if 'order' in query_lower:
                agents_needed['ShopCore'] = True  # Need order_id
        
        # Determine execution order based on dependencies
        execution_order = self._determine_execution_order(agents_needed)
        
        state: AgentState = {
            'original_query': query,
            'user_id': user_id,
            'agents_needed': agents_needed,
            'execution_order': execution_order,
            'context': {'user_id': user_id} if user_id else {},
            'agent_results': {},
            'narrative_response': '',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Query analysis: {sum(agents_needed.values())} agents needed - {execution_order}")
        return state
    
    def _determine_execution_order(self, agents_needed: Dict[str, bool]) -> List[str]:
        """
        Determine optimal execution order based on dependencies
        ShopCore must run first as it provides order_id for other agents
        """
        order = []
        
        # ShopCore always first if needed (provides order_id)
        if agents_needed['ShopCore']:
            order.append('ShopCore')
        
        # Other agents can run in parallel after ShopCore
        # But we'll execute sequentially for simplicity
        if agents_needed['ShipStream']:
            order.append('ShipStream')
        
        if agents_needed['PayGuard']:
            order.append('PayGuard')
        
        if agents_needed['CareDesk']:
            order.append('CareDesk')
        
        return order
    
    def execute_agents(self, state: AgentState) -> AgentState:
        """
        Execute agents in the determined order
        
        Args:
            state: Current agent state
        
        Returns:
            Updated state with agent results
        """
        for agent_name in state['execution_order']:
            try:
                logger.info(f"▶️  Executing {agent_name} Agent...")
                
                if agent_name == 'ShopCore':
                    result = self.shopcore_agent.process_query(
                        state['original_query'],
                        state['context']
                    )
                    # Update context with order_id if found
                    if result.get('success') and result.get('data'):
                        if 'context' in result:
                            state['context'].update(result['context'])
                        elif len(result['data']) > 0 and 'order_id' in result['data'][0]:
                            state['context']['order_id'] = result['data'][0]['order_id']
                
                elif agent_name == 'ShipStream':
                    result = self.shipstream_agent.process_query(
                        state['original_query'],
                        state['context']
                    )
                
                elif agent_name == 'PayGuard':
                    result = self.payguard_agent.process_query(
                        state['original_query'],
                        state['context']
                    )
                
                elif agent_name == 'CareDesk':
                    result = self.caredesk_agent.process_query(
                        state['original_query'],
                        state['context']
                    )
                
                else:
                    continue
                
                state['agent_results'][agent_name] = result
                logger.info(f"✓ {agent_name} completed: {result.get('record_count', 0)} records")
            
            except Exception as e:
                logger.error(f"✗ {agent_name} failed: {e}")
                state['agent_results'][agent_name] = {
                    'agent': agent_name,
                    'success': False,
                    'error': str(e),
                    'data': []
                }
        
        return state
    
    def synthesize_response(self, state: AgentState) -> AgentState:
        """
        Synthesize natural language response from agent results
        
        Args:
            state: State with agent results
        
        Returns:
            Updated state with narrative response
        """
        if not self.model:
            # Fallback: simple text synthesis
            state['narrative_response'] = self._simple_synthesis(state)
            return state
        
        # Build context for Gemini
        prompt = f"""You are a helpful customer support assistant. Synthesize a natural, conversational response based on the following:

USER QUERY: {state['original_query']}

AGENT RESULTS:
"""
        
        for agent_name, result in state['agent_results'].items():
            prompt += f"\n{agent_name} Agent:\n"
            if result.get('success'):
                prompt += f"  Found {result.get('record_count', 0)} records\n"
                if result.get('data'):
                    prompt += f"  Data: {result['data']}\n"
            else:
                prompt += f"  Error: {result.get('error', 'Unknown error')}\n"
        
        prompt += """
REQUIREMENTS:
1. Provide a natural, conversational response
2. Include all relevant information from the agents
3. Be specific with dates, amounts, tracking numbers, etc.
4. If information is missing, acknowledge it politely
5. Keep the tone friendly and helpful
6. Format the response in a clear, readable way

Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            state['narrative_response'] = response.text.strip()
        except Exception as e:
            logger.error(f"Response synthesis error: {e}")
            state['narrative_response'] = self._simple_synthesis(state)
        
        return state
    
    def _simple_synthesis(self, state: AgentState) -> str:
        """Simple fallback synthesis without LLM"""
        parts = [f"Query: {state['original_query']}\n"]
        
        for agent_name, result in state['agent_results'].items():
            parts.append(f"\n{agent_name}:")
            if result.get('success') and result.get('data'):
                parts.append(f"  Found {len(result['data'])} record(s)")
                for item in result['data'][:2]:  # Show first 2 items
                    parts.append(f"  - {item}")
            else:
                parts.append(f"  No data found")
        
        return '\n'.join(parts)
    
    def process_complex_query(
        self, 
        query: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process a complex multi-agent query
        
        Args:
            query: Natural language query
            user_id: Optional user ID
        
        Returns:
            Complete response with narrative and data sources
        """
        logger.info(f"📝 Processing query: {query}")
        
        # Step 1: Analyze query
        state = self.analyze_query(query, user_id)
        
        # Step 2: Execute agents
        state = self.execute_agents(state)
        
        # Step 3: Synthesize response
        state = self.synthesize_response(state)
        
        # Build final response
        response = {
            'timestamp': state['timestamp'],
            'original_query': state['original_query'],
            'agents_invoked': [agent for agent, needed in state['agents_needed'].items() if needed],
            'narrative_response': state['narrative_response'],
            'data_sources': state['agent_results']
        }
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': state['timestamp'],
            'query': query,
            'response': state['narrative_response'],
            'agents_used': response['agents_invoked']
        })
        
        logger.info(f"✅ Query processed successfully")
        return response
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Super Agent resources")
        # Database connections are managed by db_manager
