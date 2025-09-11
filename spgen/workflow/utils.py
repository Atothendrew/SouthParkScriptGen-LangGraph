"""Utility functions for the South Park episode generation workflow."""

import os
import re
from typing import List, Optional
from spgen.workflow.state import EpisodeState


def should_include_persona(name: str, state: EpisodeState) -> bool:
    """
    Check if a persona should be included based on include/exclude filters.
    
    Args:
        name: The persona name to check
        state: Current episode state containing filter settings
        
    Returns:
        bool: True if the persona should be included, False otherwise
        
    Logic:
        - If include_personas is set and name is not in it, exclude
        - If exclude_personas is set and name is in it, exclude  
        - Otherwise, include
    """
    # Check include filter
    if state["include_personas"] and name not in state["include_personas"]:
        return False

    # Check exclude filter
    if state["exclude_personas"] and name in state["exclude_personas"]:
        return False

    return True


def sanitize_filename(name: str) -> str:
    """
    Sanitize a name for use in filenames by replacing spaces and special characters.

    Args:
        name: The name to sanitize (e.g., "Tina Fey", "Andy Samburg")

    Returns:
        str: Sanitized filename-safe version (e.g., "Tina_Fey", "Andy_Samburg")
    """
    # Replace spaces with underscores
    sanitized = name.replace(" ", "_")

    # Remove or replace other problematic characters
    sanitized = re.sub(r"[^\w\-_.]", "", sanitized)

    return sanitized


def write_file_with_logging(
    filepath: str,
    content: str,
    logger,
    action_description: str,
    persona_name: str = None,
) -> str:
    """
    Write content to a file and log the action with absolute path.

    Args:
        filepath: Path where to write the file
        content: Content to write to the file
        logger: Logger instance to use for logging
        action_description: Description of what was saved (e.g., "idea", "feedback", "script")
        persona_name: Optional persona name for personalized logging

    Returns:
        str: Absolute path of the written file
    """
    abs_filepath = os.path.abspath(filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    if persona_name:
        logger.info(f"✅ {persona_name}'s {action_description} saved to {abs_filepath}")
    else:
        logger.info(f"✅ {action_description.capitalize()} saved to {abs_filepath}")

    return abs_filepath


def append_file_with_logging(
    filepath: str,
    content: str,
    logger,
    action_description: str,
    persona_name: str = None,
) -> str:
    """
    Append content to a file and log the action with absolute path.

    Args:
        filepath: Path where to append the file
        content: Content to append to the file
        logger: Logger instance to use for logging
        action_description: Description of what was added (e.g., "follow-up", "response")
        persona_name: Optional persona name for personalized logging

    Returns:
        str: Absolute path of the file
    """
    abs_filepath = os.path.abspath(filepath)

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

    if persona_name:
        logger.info(f"✅ {persona_name}'s {action_description} added to {abs_filepath}")
    else:
        logger.info(f"✅ {action_description.capitalize()} added to {abs_filepath}")

    return abs_filepath


def log_response_size(
    logger,
    persona_name: str,
    response: str,
    model_name: str,
    action_type: str = "response",
):
    """
    Log the size of a response with model information.

    Args:
        logger: Logger instance to use
        persona_name: Name of the persona who generated the response
        response: The response content
        model_name: Name of the model that generated the response
        action_type: Type of action (e.g., "response", "questions", "follow-up")
    """
    logger.info(
        f"📊 {persona_name}'s {action_type} size: {len(response)} characters ({model_name})"
    )


def create_persona_filename(
    persona_name: str, suffix: str = "", extension: str = "md"
) -> str:
    """
    Create a sanitized filename for a persona.

    Args:
        persona_name: Name of the persona
        suffix: Optional suffix to add (e.g., "_all_responses")
        extension: File extension (default: "md")

    Returns:
        str: Sanitized filename
    """
    sanitized_name = sanitize_filename(persona_name)
    if suffix:
        return f"{sanitized_name}{suffix}.{extension}"
    return f"{sanitized_name}.{extension}"


def create_conversation_filename(asker_name: str, responder_name: str) -> str:
    """
    Create a sanitized filename for a conversation between two personas.

    Args:
        asker_name: Name of the persona asking questions
        responder_name: Name of the persona responding

    Returns:
        str: Sanitized conversation filename
    """
    sanitized_asker = sanitize_filename(asker_name)
    sanitized_responder = sanitize_filename(responder_name)
    return f"{sanitized_asker}_asks_{sanitized_responder}.md"


def create_review_filename(idea_creator: str, reviewer: str) -> str:
    """
    Create a sanitized filename for a Q&A review session.

    This makes it clear that one person created an idea and another is reviewing it,
    rather than the confusing "X asks Y" format.

    Args:
        idea_creator: Name of the persona who created the original idea
        reviewer: Name of the persona reviewing/auditing the idea

    Returns:
        str: Sanitized review filename like "Andy_Samburg_idea_reviewed_by_Bill_Hader.md"
    """
    sanitized_creator = sanitize_filename(idea_creator)
    sanitized_reviewer = sanitize_filename(reviewer)
    return f"{sanitized_creator}_idea_reviewed_by_{sanitized_reviewer}.md"
