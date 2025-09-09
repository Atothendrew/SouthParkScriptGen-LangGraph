"""Episode state definition for the South Park episode generator."""

from typing import Dict, List, TypedDict, Optional
from dataclasses import dataclass


@dataclass
class ExtractedContinuityElements:
    """
    Continuity elements extracted from a completed episode part.
    """
    character_developments: List[str]
    running_gags: List[str]
    unresolved_plotlines: List[str]
    established_locations: List[str]


class EpisodeContinuity(TypedDict):
    """
    Continuity data from previous episode parts.
    """
    part_number: int
    total_parts: int
    original_prompt: str
    previous_summaries: List[str]
    previous_outlines: List[str] 
    character_developments: List[str]
    running_gags: List[str]
    unresolved_plotlines: List[str]
    established_locations: List[str]
    previous_log_dirs: List[str]


class EpisodeState(TypedDict):
    """
    State dictionary for the episode generation graph.
    Keys:
        prompt (str): The user-provided episode idea.
        agent_outputs (List[Dict]): List of dicts with keys 'name' and 'outline'.
        merged_outline (str): The combined outline after discussion.
        discussion_history (List[str]): A log of the conversation between the agents.
        act_one_script (str): The script for Act One.
        act_two_script (str): The script for Act Two.
        act_three_script (str): The script for Act Three.
        script (str): The final episode script.
        script_summary (str): A summary of the final episode script.
        log_dir (str): The directory to save the logs to.
        include_personas (List[str] | None): List of personas to include.
        exclude_personas (List[str] | None): List of personas to exclude.
        continuity (Optional[EpisodeContinuity]): Context from previous episode parts.
        news_context_files (Optional[Dict[str, str]]): Paths to news context markdown files.
        dynamic_prompt (bool): Whether to use dynamic prompt with current events research.
    """
    prompt: str
    agent_outputs: List[Dict]
    merged_outline: str
    discussion_history: List[str]
    act_one_script: str
    act_two_script: str
    act_three_script: str
    script: str
    script_summary: str
    log_dir: str
    include_personas: List[str] | None
    exclude_personas: List[str] | None
    continuity: Optional[EpisodeContinuity]
    news_context_files: Optional[Dict[str, str]]
    dynamic_prompt: bool