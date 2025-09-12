import sys
import os
import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from episodesummarycreator.agents import ResearcherAgent

@pytest.fixture
def researcher():
    return ResearcherAgent()

def test_research_episode(researcher):
    """
    Tests the research_episode method of the ResearcherAgent.
    This test makes a real web search and LLM call.
    """
    season = 1
    episode = 1
    title = "Cartman Gets an Anal Probe"
    
    research_material = researcher.research_episode(season, episode, title)
    
    assert research_material is not None
    assert isinstance(research_material, str)
    assert len(research_material) > 50  # Expect a reasonable amount of text
    assert "Cartman" in research_material
    assert "anal probe" in research_material.lower()
