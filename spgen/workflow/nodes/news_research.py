"""News research node for dynamic prompt enhancement."""

from typing import Dict

from spgen.workflow.state import EpisodeState
from spgen.workflow.news_agent import NewsResearchAgent
from spgen.workflow.logger import WorkflowStep


def research_current_events(state: EpisodeState) -> Dict:
    """Research current events related to the episode prompt."""
    prompt = state["prompt"]
    log_dir = state["log_dir"]
    
    # Initialize news research agent
    news_agent = NewsResearchAgent()
    
    # Create news context files
    context_files = news_agent.create_news_context_files(prompt, log_dir)
    
    # Add the context file paths to state for other nodes to reference
    state["news_context_files"] = context_files
    
    print(f"📰 News research complete. Context files created:")
    for file_type, file_path in context_files.items():
        print(f"   - {file_type}: {file_path}")
    
    if state.get("dynamic_prompt", False):
        return {"next": WorkflowStep.USER_NEWS_REVIEW.value}
    else:
        return {"next": WorkflowStep.BRAINSTORM.value}


