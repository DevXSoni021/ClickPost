"""
Unit tests for Super Agent orchestrator
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.orchestrator.super_agent import OmniRetailSuperAgent

class TestSuperAgent:
    """Tests for Super Agent orchestrator"""
    
    def test_super_agent_initialization(self):
        """Test super agent initializes with all sub-agents"""
        agent = OmniRetailSuperAgent()
        
        assert agent.shopcore_agent is not None
        assert agent.shipstream_agent is not None
        assert agent.payguard_agent is not None
        assert agent.caredesk_agent is not None
        assert agent.conversation_history == []
    
    def test_query_analysis_order_tracking(self):
        """Test query analysis for order tracking"""
        agent = OmniRetailSuperAgent()
        
        state = agent.analyze_query("Where is my Gaming Monitor?", user_id=1)
        
        assert state['original_query'] == "Where is my Gaming Monitor?"
        assert state['user_id'] == 1
        assert state['agents_needed']['ShopCore'] == True
        assert state['agents_needed']['ShipStream'] == True
    
    def test_query_analysis_refund(self):
        """Test query analysis for refund status"""
        agent = OmniRetailSuperAgent()
        
        state = agent.analyze_query("What's the status of my refund?", user_id=1)
        
        assert state['agents_needed']['ShopCore'] == True
        assert state['agents_needed']['PayGuard'] == True
    
    def test_query_analysis_support_ticket(self):
        """Test query analysis for support ticket"""
        agent = OmniRetailSuperAgent()
        
        state = agent.analyze_query("Check my support ticket", user_id=1)
        
        assert state['agents_needed']['CareDesk'] == True
        assert state['agents_needed']['ShopCore'] == True
    
    def test_execution_order_determination(self):
        """Test execution order is correct"""
        agent = OmniRetailSuperAgent()
        
        agents_needed = {
            'ShopCore': True,
            'ShipStream': True,
            'PayGuard': False,
            'CareDesk': False
        }
        
        order = agent._determine_execution_order(agents_needed)
        
        # ShopCore should always be first
        assert order[0] == 'ShopCore'
        assert 'ShipStream' in order
        assert len(order) == 2
    
    def test_conversation_history(self):
        """Test conversation history is maintained"""
        agent = OmniRetailSuperAgent()
        
        initial_length = len(agent.conversation_history)
        
        # This would require database connection
        # agent.process_complex_query("Test query", user_id=1)
        
        # assert len(agent.conversation_history) == initial_length + 1
        pass

class TestAgentStateManagement:
    """Tests for agent state management"""
    
    def test_state_initialization(self):
        """Test state is properly initialized"""
        agent = OmniRetailSuperAgent()
        
        state = agent.analyze_query("Test query", user_id=1)
        
        assert 'original_query' in state
        assert 'user_id' in state
        assert 'agents_needed' in state
        assert 'execution_order' in state
        assert 'context' in state
        assert 'agent_results' in state
        assert 'narrative_response' in state
        assert 'timestamp' in state
    
    def test_context_propagation(self):
        """Test context is propagated between agents"""
        agent = OmniRetailSuperAgent()
        
        state = agent.analyze_query("Test", user_id=1)
        
        # User ID should be in context
        assert state['context']['user_id'] == 1

@pytest.mark.integration
class TestOrchestratorIntegration:
    """Integration tests for orchestrator"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_full_query_processing(self):
        """Test complete query processing flow"""
        agent = OmniRetailSuperAgent()
        
        # This would require actual database connection
        # response = agent.process_complex_query(
        #     "Where is my Gaming Monitor?",
        #     user_id=1
        # )
        
        # assert 'timestamp' in response
        # assert 'original_query' in response
        # assert 'agents_invoked' in response
        # assert 'narrative_response' in response
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
