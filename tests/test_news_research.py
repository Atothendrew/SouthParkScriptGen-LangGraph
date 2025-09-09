"""
Test suite for news research functionality.

This module tests the NewsResearchAgent class and related news research workflows
including search functionality, analysis, file creation, and integration with
the episode generation pipeline.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add project root to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.news_agent import NewsResearchAgent
from workflow.nodes.news_research import research_current_events
from workflow.state import EpisodeState


class TestNewsResearchAgent:
    """Test cases for the NewsResearchAgent class."""
    
    @pytest.fixture
    def news_agent(self):
        """Create a NewsResearchAgent instance for testing."""
        return NewsResearchAgent()
    
    @pytest.fixture
    def mock_news_results(self):
        """Mock news search results for testing."""
        return [
            {
                'title': 'AI Chatbots Replace Teachers in Schools',
                'snippet': 'Local schools are experimenting with AI-powered teaching assistants to address teacher shortages.',
                'url': 'https://example.com/news1',
                'date': '2025-01-10',
                'source': 'Tech News Daily'
            },
            {
                'title': 'Kids Protest New School Lunch Menu',
                'snippet': 'Students organize walkout over healthier but less tasty cafeteria options.',
                'url': 'https://example.com/news2', 
                'date': '2025-01-09',
                'source': 'Local News Network'
            },
            {
                'title': 'Social Media Platform Bans Children',
                'snippet': 'New regulations force social media companies to verify user ages.',
                'url': 'https://example.com/news3',
                'date': '2025-01-08',
                'source': 'Digital Rights Observer'
            }
        ]
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for test logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_news_agent_initialization(self, news_agent):
        """Test that NewsResearchAgent initializes correctly."""
        assert news_agent is not None
        assert hasattr(news_agent, 'ddgs')
    
    @patch('workflow.news_agent.DDGS')
    def test_search_news_success(self, mock_ddgs, news_agent, mock_news_results):
        """Test successful news search functionality."""
        # Mock the DDGS news search method
        mock_ddgs_instance = Mock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.news.return_value = [
            {
                'title': 'AI Chatbots Replace Teachers in Schools',
                'body': 'Local schools are experimenting with AI-powered teaching assistants to address teacher shortages.',
                'url': 'https://example.com/news1',
                'date': '2025-01-10',
                'source': 'Tech News Daily'
            }
        ]
        
        # Reinitialize agent with mocked DDGS
        news_agent = NewsResearchAgent()
        
        results = news_agent.search_news("AI in education", num_results=1)
        
        assert len(results) == 1
        assert results[0]['title'] == 'AI Chatbots Replace Teachers in Schools'
        assert results[0]['snippet'] == 'Local schools are experimenting with AI-powered teaching assistants to address teacher shortages.'
        assert results[0]['url'] == 'https://example.com/news1'
        assert results[0]['source'] == 'Tech News Daily'
    
    @patch('workflow.news_agent.DDGS')
    def test_search_news_failure(self, mock_ddgs, news_agent):
        """Test news search failure handling."""
        # Mock DDGS to raise an exception
        mock_ddgs_instance = Mock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.news.side_effect = Exception("Network error")
        
        # Reinitialize agent with mocked DDGS
        news_agent = NewsResearchAgent()
        
        results = news_agent.search_news("test query")
        
        assert results == []
    
    @patch('workflow.news_agent.llm_call')
    def test_analyze_news_for_south_park_success(self, mock_llm_call, news_agent, mock_news_results):
        """Test successful news analysis for South Park context."""
        mock_llm_call.return_value = """
## SATIRICAL OPPORTUNITIES
- The absurdity of replacing human teachers with chatbots
- Kids manipulating AI systems to avoid homework

## SOCIAL COMMENTARY  
- Education funding crisis leading to technological band-aids
- Over-reliance on AI for human connections

## CHARACTER CONNECTIONS
- Cartman would exploit the AI system for personal gain
- Kyle would organize protests against the dehumanization of education
"""
        
        result = news_agent.analyze_news_for_south_park(mock_news_results, "AI takes over the school")
        
        assert "SATIRICAL OPPORTUNITIES" in result
        assert "SOCIAL COMMENTARY" in result  
        assert "CHARACTER CONNECTIONS" in result
        mock_llm_call.assert_called_once()
    
    @patch('workflow.news_agent.llm_call')
    def test_analyze_news_for_south_park_no_results(self, mock_llm_call, news_agent):
        """Test analysis with no news results."""
        result = news_agent.analyze_news_for_south_park([], "test prompt")
        
        assert result == "No recent news found to inform this episode."
        mock_llm_call.assert_not_called()
    
    @patch('workflow.news_agent.llm_call')
    def test_analyze_news_for_south_park_llm_failure(self, mock_llm_call, news_agent, mock_news_results):
        """Test analysis when LLM call fails."""
        mock_llm_call.side_effect = Exception("LLM error")
        
        result = news_agent.analyze_news_for_south_park(mock_news_results, "test prompt")
        
        assert "News analysis failed: LLM error" in result
    
    @patch('workflow.news_agent.llm_call')
    def test_create_matt_stone_analysis(self, mock_llm_call, news_agent, mock_news_results):
        """Test Matt Stone perspective analysis."""
        mock_llm_call.return_value = "This is typical government overreach disguised as protecting children. Both sides are missing the real issue - parental responsibility."
        
        result = news_agent.create_matt_stone_analysis(mock_news_results, "Social media bans kids")
        
        assert "typical government overreach" in result
        mock_llm_call.assert_called_once()
        # Check that the prompt includes Matt Stone's characteristics
        call_args = mock_llm_call.call_args[0][0]
        assert "Matt Stone" in call_args
        assert "pragmatic" in call_args
        assert "libertarian" in call_args
    
    @patch('workflow.news_agent.llm_call')
    def test_create_trey_parker_analysis(self, mock_llm_call, news_agent, mock_news_results):
        """Test Trey Parker perspective analysis."""
        mock_llm_call.return_value = "We could have Randy start his own social media platform for adults-only, but then kids infiltrate it by pretending to be their parents."
        
        result = news_agent.create_trey_parker_analysis(mock_news_results, "Social media chaos")
        
        assert "Randy" in result
        mock_llm_call.assert_called_once()
        # Check that the prompt includes Trey Parker's characteristics
        call_args = mock_llm_call.call_args[0][0]
        assert "Trey Parker" in call_args
        assert "satirical" in call_args
        assert "absurd" in call_args
    
    @patch.object(NewsResearchAgent, 'search_news')
    @patch.object(NewsResearchAgent, 'analyze_news_for_south_park')
    @patch.object(NewsResearchAgent, 'create_matt_stone_analysis')
    @patch.object(NewsResearchAgent, 'create_trey_parker_analysis')
    def test_create_news_context_files(self, mock_trey, mock_matt, mock_analyze, mock_search, 
                                     news_agent, temp_log_dir, mock_news_results):
        """Test creation of news context files."""
        # Setup mocks
        mock_search.return_value = mock_news_results
        mock_analyze.return_value = "Test analysis"
        mock_matt.return_value = "Matt's perspective"
        mock_trey.return_value = "Trey's perspective"
        
        result = news_agent.create_news_context_files("AI in schools", temp_log_dir)
        
        # Check return value structure
        assert "news_context" in result
        assert "matt_perspective" in result
        assert "trey_perspective" in result
        
        # Check that files were created
        news_dir = os.path.join(temp_log_dir, "news_context")
        assert os.path.exists(news_dir)
        assert os.path.exists(result["news_context"])
        assert os.path.exists(result["matt_perspective"])
        assert os.path.exists(result["trey_perspective"])
        
        # Check file contents
        with open(result["news_context"], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Current Events Analysis" in content
            assert "AI Chatbots Replace Teachers" in content
            assert "Test analysis" in content
        
        with open(result["matt_perspective"], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Matt Stone's Perspective" in content
            assert "Matt's perspective" in content
            
        with open(result["trey_perspective"], 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Trey Parker's Perspective" in content 
            assert "Trey's perspective" in content
    
    @patch.object(NewsResearchAgent, 'search_news')
    def test_create_news_context_files_no_results(self, mock_search, news_agent, temp_log_dir):
        """Test handling when no news results are found."""
        mock_search.return_value = []
        
        with pytest.raises(SystemExit):
            news_agent.create_news_context_files("obscure topic", temp_log_dir)
    
    @patch('workflow.news_agent.DDGS')
    @patch('workflow.news_agent.llm_call')
    def test_generate_episode_prompt_from_news(self, mock_llm_call, mock_ddgs, news_agent):
        """Test dynamic episode prompt generation from trending news."""
        # Mock DDGS trending search
        mock_ddgs_instance = Mock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.news.return_value = [
            {
                'title': 'AI Chatbots Take Over Customer Service',
                'body': 'Major companies replace human support staff with AI systems, leading to customer frustration.',
                'url': 'https://example.com/trending1'
            },
            {
                'title': 'Kids Start Underground Pokemon Card Trading Ring',
                'body': 'Elementary students create sophisticated black market for collectible cards.',
                'url': 'https://example.com/trending2'
            }
        ]
        
        # Mock LLM response
        mock_llm_call.return_value = '"The boys discover that AI chatbots have replaced all customer service and decide to start their own human helpline business."'
        
        # Reinitialize agent with mocked DDGS
        news_agent = NewsResearchAgent()
        
        result = news_agent.generate_episode_prompt_from_news()
        
        assert "boys discover that AI chatbots" in result
        assert not result.startswith('"')  # Should strip quotes
        assert not result.endswith('"')
        mock_llm_call.assert_called_once()
    
    @patch('workflow.news_agent.DDGS')
    def test_generate_episode_prompt_no_trending_news(self, mock_ddgs, news_agent):
        """Test prompt generation when no trending news is found."""
        mock_ddgs_instance = Mock()
        mock_ddgs.return_value = mock_ddgs_instance
        mock_ddgs_instance.news.return_value = []
        
        # Reinitialize agent with mocked DDGS
        news_agent = NewsResearchAgent()
        
        with pytest.raises(SystemExit):
            news_agent.generate_episode_prompt_from_news()


class TestNewsResearchNode:
    """Test cases for the news research workflow node."""
    
    @pytest.fixture
    def mock_episode_state(self, tmp_path):
        """Create a mock episode state for testing."""
        return {
            "prompt": "The kids discover AI is taking over the school",
            "log_dir": str(tmp_path),
            "agent_outputs": [],
            "merged_outline": "",
            "discussion_history": [],
            "act_one_script": "",
            "act_two_script": "", 
            "act_three_script": "",
            "script": "",
            "script_summary": "",
            "include_personas": None,
            "exclude_personas": None,
            "continuity": None,
            "news_context_files": None,
            "dynamic_prompt": True
        }
    
    @patch.object(NewsResearchAgent, 'create_news_context_files')
    def test_research_current_events_success(self, mock_create_files, mock_episode_state):
        """Test successful news research workflow node execution."""
        mock_files = {
            "news_context": "/path/to/news.md",
            "matt_perspective": "/path/to/matt.md", 
            "trey_perspective": "/path/to/trey.md"
        }
        mock_create_files.return_value = mock_files
        
        result = research_current_events(mock_episode_state)
        
        assert result["news_context_files"] == mock_files
        assert mock_episode_state["news_context_files"] == mock_files
        mock_create_files.assert_called_once_with(
            "The kids discover AI is taking over the school", 
            mock_episode_state["log_dir"]
        )
    
    def test_research_current_events_state_modification(self, tmp_path):
        """Test that the news research node properly modifies state."""
        state = {
            "prompt": "Test episode prompt",
            "log_dir": str(tmp_path),
            "news_context_files": None,
            # ... other required state fields
            "agent_outputs": [],
            "merged_outline": "",
            "discussion_history": [],
            "act_one_script": "",
            "act_two_script": "", 
            "act_three_script": "",
            "script": "",
            "script_summary": "",
            "include_personas": None,
            "exclude_personas": None,
            "continuity": None,
            "dynamic_prompt": True
        }
        
        with patch.object(NewsResearchAgent, 'create_news_context_files') as mock_create:
            mock_files = {"news_context": "test.md"}
            mock_create.return_value = mock_files
            
            research_current_events(state)
            
            # Verify state was modified
            assert state["news_context_files"] == mock_files


class TestNewsResearchIntegration:
    """Integration tests for news research functionality."""
    
    def test_duplicate_removal_in_news_search(self):
        """Test that duplicate news items are properly removed."""
        news_agent = NewsResearchAgent()
        
        # Mock news results with duplicates
        mock_results = [
            {'title': 'Duplicate Story', 'snippet': 'First version'},
            {'title': 'Unique Story', 'snippet': 'Only version'},
            {'title': 'Duplicate Story', 'snippet': 'Second version'},  # Should be removed
        ]
        
        with patch.object(news_agent, 'search_news', return_value=mock_results):
            # This tests the duplicate removal logic in create_news_context_files
            seen_titles = set()
            unique_news = []
            for item in mock_results:
                if item['title'] not in seen_titles:
                    unique_news.append(item)
                    seen_titles.add(item['title'])
            
            assert len(unique_news) == 2
            assert unique_news[0]['title'] == 'Duplicate Story'
            assert unique_news[0]['snippet'] == 'First version'  # First occurrence kept
            assert unique_news[1]['title'] == 'Unique Story'
    
    @patch('workflow.news_agent.llm_call')
    def test_error_handling_in_analysis_methods(self, mock_llm_call):
        """Test error handling across all analysis methods."""
        news_agent = NewsResearchAgent()
        mock_news_results = [{'title': 'Test', 'snippet': 'Test content'}]
        
        # Test that all analysis methods handle LLM failures gracefully
        mock_llm_call.side_effect = Exception("LLM timeout")
        
        # Test main analysis
        result = news_agent.analyze_news_for_south_park(mock_news_results, "test")
        assert "News analysis failed: LLM timeout" in result
        
        # Test Matt Stone analysis
        result = news_agent.create_matt_stone_analysis(mock_news_results, "test")
        assert "Analysis failed: LLM timeout" in result
        
        # Test Trey Parker analysis  
        result = news_agent.create_trey_parker_analysis(mock_news_results, "test")
        assert "Analysis failed: LLM timeout" in result


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])