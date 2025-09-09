"""Utility functions for the South Park episode generation workflow."""

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