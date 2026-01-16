"""
Super Agent - Orchestrates multiple specialized agents using LangGraph
Handles query analysis, dependency resolution, and response synthesis
"""

import os
import logging
import asyncio
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
    """State schema for workflow"""
    original_query: str
    user_id: Optional[int]
    agents_needed: Dict[str, bool]
    execution_order: List[List[str]] # List of lists for stages (e.g., [['ShopCore'], ['ShipStream', 'CareDesk']])
    context: Dict[str, Any]
    agent_results: Dict[str, Any]
    narrative_response: str
    timestamp: str

class OmniRetailSuperAgent:
    """
    Super Agent that orchestrates multiple specialized agents
    Architecture: Planner -> Parallel Execution -> Result Merger
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
        
        # Conversation history & Session State
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_sessions: Dict[int, Dict[str, Any]] = {} # In-memory session store {user_id: context}
        
        logger.info("✓ Super Agent initialized with 4 sub-agents")
    
    def analyze_query(self, query: str, user_id: Optional[int] = None, session_context: Optional[Dict[str, Any]] = None) -> AgentState:
        """
        Planner: Analyzes query to determine required agents and dependencies
        """
        query_lower = query.lower()
        
        # 1. Determine which agents are needed
        agents_needed = {
            'ShopCore': False,
            'ShipStream': False,
            'PayGuard': False,
            'CareDesk': False
        }
        
        # 0. NEW: Detect Session Reset Request (Clear context when new chat starts)
        reset_triggers = ['new chat', 'reset session', 'clear memory', 'start over', 'clear context', 'reset']
        if any(trigger in query_lower for trigger in reset_triggers):
            logger.info("Session reset requested. Wiping session context.")
            if user_id and user_id in self.user_sessions:
                self.user_sessions[user_id] = {}
                
            return {
                'original_query': query,
                'user_id': user_id,
                'agents_needed': agents_needed,
                'execution_order': [],
                'context': {},
                'agent_results': {},
                'narrative_response': 'I have cleared our conversation context. How can I help you today?',
                'timestamp': datetime.now().isoformat()
            }
            
        # Pre-check: Do we have an active order context?
        has_active_order = session_context and 'order_id' in session_context
        
        # 1.5 NEW: Detect explicit Order ID in text (Uniform Architecture Orchestration)
        import re
        extracted_order_id = None
        match = re.search(r'order\s*(?:id|number|#)?\s*(\d+)', query_lower)
        if match:
            extracted_order_id = int(match.group(1))
            has_active_order = True # Treat as follow-up capable
            
        is_follow_up = False
        
        # Detect follow-up intent (e.g. "give complete info", "tell me more", "status")
        follow_up_triggers = ['complete', 'all info', 'details', 'everything', 'tracking', 'status', 'ticket', 'support']
        if has_active_order and any(trigger in query_lower for trigger in follow_up_triggers):
            is_follow_up = True
            
        # ShopCore: order, product, purchase queries
        if any(word in query_lower for word in ['order', 'ordered', 'product', 'purchase', 'bought', 'buy', 'price', 'cost']) or is_follow_up:
            agents_needed['ShopCore'] = True
        
        # ShipStream: tracking, delivery, shipment queries
        if any(word in query_lower for word in ['track', 'delivery', 'shipment', 'where', 'location', 'arrive', 'delivered']) or (is_follow_up and 'order' not in query_lower): 
            # If asking for "complete info", we usually want tracking
            agents_needed['ShipStream'] = True
            agents_needed['ShopCore'] = True  # Dependency
        
        # PayGuard: payment, refund, transaction queries
        if any(word in query_lower for word in ['refund', 'payment', 'transaction', 'paid', 'wallet', 'balance', 'credit', 'debit']) or (is_follow_up and 'all' in query_lower):
            agents_needed['PayGuard'] = True
        
        # CareDesk: support, ticket, complaint queries
        if any(word in query_lower for word in ['ticket', 'support', 'complaint', 'issue', 'help', 'problem', 'contact']) or (is_follow_up and 'all' in query_lower):
            agents_needed['CareDesk'] = True
            
        # Special Case: "Give complete info" -> Enable ALL agents if we have an order
        if is_follow_up and any(w in query_lower for w in ['complete', 'all', 'everything']):
            agents_needed['ShopCore'] = True
            agents_needed['ShipStream'] = True
            agents_needed['PayGuard'] = True
            agents_needed['CareDesk'] = True
        
        # 2. Determine Execution Stages (Planner Logic)
        stage_1 = []
        # If we ALREADY have order_id, we can potentially run everyone in parallel (Stage 1)
        # But to be safe and get fresh status, we might keep ShopCore first or parallel.
        # Strict rule: ShopCore resolves OrderID. 
        # If OrderID is in context, technically everyone can run in parallel.
        
        execution_order = []
        
        if has_active_order and is_follow_up:
            # We have the ID, so we can run everything in parallel!
            parallel_stage = []
            if agents_needed['ShopCore']: parallel_stage.append('ShopCore')
            if agents_needed['ShipStream']: parallel_stage.append('ShipStream')
            if agents_needed['PayGuard']: parallel_stage.append('PayGuard')
            if agents_needed['CareDesk']: parallel_stage.append('CareDesk')
            if parallel_stage:
                execution_order.append(parallel_stage)
        else:
            # Standard Dependency Flow
            if agents_needed['ShopCore']:
                stage_1.append('ShopCore')
                
            stage_2 = []
            if agents_needed['ShipStream']: stage_2.append('ShipStream')
            if agents_needed['PayGuard']: stage_2.append('PayGuard')
            if agents_needed['CareDesk']: stage_2.append('CareDesk')
            
            if stage_1: execution_order.append(stage_1)
            if stage_2: execution_order.append(stage_2)

        # Initial context merging
        current_context = {'user_id': user_id} if user_id else {}
        if session_context:
            current_context.update(session_context)
            
        # Priority: If we extracted a NEW order ID from the query text, it MUST override session context
        if extracted_order_id:
            current_context['order_id'] = extracted_order_id

        state: AgentState = {
            'original_query': query,
            'user_id': user_id,
            'agents_needed': agents_needed,
            'execution_order': execution_order,
            'context': current_context,
            'agent_results': {},
            'narrative_response': '',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Query analysis: {sum(agents_needed.values())} agents needed - Stages: {execution_order}")
        return state

    # ... (skipping _run_agent_sync and execute_agents as they remain mostly same, unless we need to update signature) ...
    # Wait, need to check where analyze_query is called.

    async def _run_agent_sync(self, agent_name: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper to run synchronous agents in a thread"""
        try:
            logger.info(f"▶️  Starting {agent_name} Agent...")
            if agent_name == 'ShopCore':
                return await asyncio.to_thread(self.shopcore_agent.process_query, query, context)
            elif agent_name == 'ShipStream':
                return await asyncio.to_thread(self.shipstream_agent.process_query, query, context)
            elif agent_name == 'PayGuard':
                return await asyncio.to_thread(self.payguard_agent.process_query, query, context)
            elif agent_name == 'CareDesk':
                return await asyncio.to_thread(self.caredesk_agent.process_query, query, context)
            else:
                return {'success': False, 'error': f'Unknown agent {agent_name}'}
        except Exception as e:
            logger.error(f"✗ {agent_name} execution failed: {e}")
            return {'success': False, 'error': str(e), 'data': []}

    async def execute_agents(self, state: AgentState) -> AgentState:
        """
        Execution Layer: Executes agents in concurrent stages
        """
        # Iterate through stages (sequential stages, parallel within stage)
        for stage in state['execution_order']:
            tasks = []
            
            # Prepare tasks for this stage
            for agent_name in stage:
                tasks.append(self._run_agent_sync(agent_name, state['original_query'], state['context']))
            
            if not tasks:
                continue
                
            # Execute stage concurrently
            results = await asyncio.gather(*tasks)
            
            # Process results and update context for next stage
            for agent_name, result in zip(stage, results):
                state['agent_results'][agent_name] = result
                
                # Context Propagation (Result Merging Logic)
                if result.get('success') and result.get('data'):
                    # ShopCore typically provides context for others
                    if agent_name == 'ShopCore':
                        if 'context' in result:
                            state['context'].update(result['context'])
                        elif len(result['data']) > 0 and 'order_id' in result['data'][0]:
                            state['context']['order_id'] = result['data'][0]['order_id']
                            if 'product_name' in result.get('data', [{}])[0]:
                                state['context']['product_name'] = result['data'][0]['product_name']
                                
                logger.info(f"✓ {agent_name} finished. Records: {result.get('record_count', 0)}")
        
        return state
    
    async def synthesize_response(self, state: AgentState) -> AgentState:
        """
        Synthesize natural language response from agent results
        """
        if state.get('narrative_response'):
            return state
            
        if not self.model:
            state['narrative_response'] = self._simple_synthesis(state)
            return state
        
        # Build context for Gemini
        prompt = f"""You are the Omni-Retail Super Agent. Synthesize a helpful response based strictly on the provided agent results.

USER QUERY: {state['original_query']}

AGENT RESULTS (Structured Data):
"""
        
        has_data = False
        for agent_name, result in state['agent_results'].items():
            prompt += f"\n--- {agent_name} Agent ---\n"
            if result.get('success'):
                count = result.get('record_count', 0)
                prompt += f"Status: Success (Found {count} records)\n"
                if result.get('data'):
                    prompt += f"Data: {result['data']}\n"
                    has_data = True
                else:
                    prompt += "Data: [] (No records found)\n"
            else:
                prompt += f"Status: Failed\nError: {result.get('error', 'Unknown')}\n"
        
        prompt += """
GUIDELINES:
1. Answer the user's question directly using the data provided.
2. If multiple agents returned data (e.g., Order details + Tracking), combine them into a coherent narrative.
3. If an agent returned no data (e.g., "Data: []"), clearly state that no information was found for that aspect.
4. Do NOT hallucinate. If data is missing/error, admit it.
5. Do NOT mention internal SQL tables, IDs, or schema details unless necessary for clarity (like Order ID).
6. Be concise and professional.
7. If data comes from context (previous turns), acknowledge that you are referring to the previously discussed item.

Final Answer:"""
        
        try:
            # Run LLM generation in thread to avoid blocking
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            state['narrative_response'] = response.text.strip()
        except Exception as e:
            logger.error(f"Response synthesis error: {e}")
            state['narrative_response'] = self._simple_synthesis(state)
        
        return state
    
    def _simple_synthesis(self, state: AgentState) -> str:
        """Simple fallback synthesis without LLM"""
        parts = []
        for agent_name, result in state['agent_results'].items():
            if result.get('success') and result.get('data'):
                parts.append(f"{agent_name}: Found {len(result['data'])} records.")
            elif result.get('success'):
                parts.append(f"{agent_name}: No data found.")
            else:
                parts.append(f"{agent_name}: Error occurred.")
        return " | ".join(parts) if parts else "No information available."
    
    async def process_complex_query(
        self, 
        query: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process a complex multi-agent query (Async)
        """
        logger.info(f"📝 Processing query: {query}")
        
        # Step 0: Load Session Context
        session_context = {}
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {}
            session_context = self.user_sessions[user_id]
            logger.info(f"Loaded session context for User {user_id}: {session_context}")
        
        # Step 1: Analyze query (Planner) - Pass session context
        state = self.analyze_query(query, user_id, session_context)
        
        # Step 2: Execute agents (Parallel Execution)
        state = await self.execute_agents(state)
        
        # Step 2.5: Update Session Context with new findings
        if user_id and 'context' in state:
            # Only update if we found something useful (like order_id)
            if 'order_id' in state['context']:
                self.user_sessions[user_id]['order_id'] = state['context']['order_id']
            if 'product_name' in state['context']:
                self.user_sessions[user_id]['product_name'] = state['context']['product_name']
            logger.info(f"Updated session context for User {user_id}: {self.user_sessions[user_id]}")
        
        # Step 3: Synthesize response
        state = await self.synthesize_response(state)
        
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
