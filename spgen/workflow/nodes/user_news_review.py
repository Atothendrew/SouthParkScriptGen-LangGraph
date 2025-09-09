from typing import Dict
from spgen.workflow.state import EpisodeState
from spgen.workflow.logger import get_logger, WorkflowStep
import os

def user_news_review(state: EpisodeState) -> Dict:
    logger = get_logger()
    logger.info("📝 Reviewing news research and awaiting user feedback...")

    news_context_files = state.get("news_context_files", {})
    if not news_context_files:
        logger.error("No news context files found for review.")
        return {"next": WorkflowStep.BRAINSTORM.value}

    # Display news context to the user
    for key, file_path in news_context_files.items():
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            logger.info(f"--- {key.replace('_', ' ').title()} ---")
            logger.info(content)
            logger.info("-" * (len(key) + 10))
        else:
            logger.warning(f"Context file not found: {file_path}")

    # Prompt user for feedback
    user_feedback = input(
        "Please review the news research above. "
        "Enter any feedback or additional thoughts for the agents, or press Enter to continue: "
    )

    # Store user feedback in the state
    current_feedback = state.get("user_feedback", [])
    current_feedback.append({"step": WorkflowStep.USER_NEWS_REVIEW.value, "feedback": user_feedback})
    
    return {"user_feedback": current_feedback}
