"""
Unit tests for specialized agents
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.agents.shopcore_agent import ShopCoreAgent
from backend.agents.shipstream_agent import ShipStreamAgent
from backend.agents.payguard_agent import PayGuardAgent
from backend.agents.caredesk_agent import CareDeskAgent

class TestShopCoreAgent:
    """Tests for ShopCore Agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ShopCoreAgent()
        assert agent.agent_name == "ShopCore"
        assert agent.db_name == "shopcore"
    
    def test_query_classification(self):
        """Test query classification"""
        agent = ShopCoreAgent()
        
        # Test order lookup classification
        query_type = agent._classify_query("Where is my order?")
        assert query_type == "ORDER_LOOKUP"
        
        # Test product search classification
        query_type = agent._classify_query("Find gaming monitor")
        assert query_type == "PRODUCT_SEARCH"
    
    def test_keyword_extraction(self):
        """Test product keyword extraction"""
        agent = ShopCoreAgent()
        
        keywords = agent._extract_product_keywords("Find the gaming monitor")
        assert "gaming" in keywords.lower()
        assert "monitor" in keywords.lower()

class TestShipStreamAgent:
    """Tests for ShipStream Agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = ShipStreamAgent()
        assert agent.agent_name == "ShipStream"
        assert agent.db_name == "shipstream"
    
    def test_tracking_number_extraction(self):
        """Test tracking number extraction"""
        agent = ShipStreamAgent()
        
        tracking = agent._extract_tracking_number("My tracking number is TRK12345")
        assert tracking == "TRK12345"
        
        tracking = agent._extract_tracking_number("No tracking here")
        assert tracking is None

class TestPayGuardAgent:
    """Tests for PayGuard Agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = PayGuardAgent()
        assert agent.agent_name == "PayGuard"
        assert agent.db_name == "payguard"

class TestCareDeskAgent:
    """Tests for CareDesk Agent"""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = CareDeskAgent()
        assert agent.agent_name == "CareDesk"
        assert agent.db_name == "caredesk"

# Integration test (requires database connection)
@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agents"""
    
    @pytest.mark.skip(reason="Requires database connection")
    def test_shopcore_query_execution(self):
        """Test ShopCore agent can execute queries"""
        agent = ShopCoreAgent()
        
        # This would require actual database connection
        # result = agent.process_query("Find Gaming Monitor", {"user_id": 1})
        # assert result["success"] == True
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
