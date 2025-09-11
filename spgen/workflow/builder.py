"""
LangGraph workflow builder for South Park episode generation.

This module constructs and configs the complete 12-step workflow for collaborative
episode creation. The workflow implements a sophisticated multi-agent system where
AI personas collaborate through structured brainstorming, discussion, and refinement
phases to generate complete South Park episode scripts.

Key Features:
- Type-safe workflow construction using enums
- Comprehensive progress tracking and logging
- Conditional entry points for different episode types
- Modular node architecture for easy extension

The workflow follows this progression:
Research → Brainstorm → Q&A → Feedback → Merge → Refine → 
Final Discussion → Act Writing (1-3) → Script Assembly → Summary

Architecture Pattern:
- Uses LangGraph's StateGraph for workflow orchestration
- Each node is wrapped with progress tracking
- State flows through all nodes maintaining context
- Supports both linear and conditional execution paths
"""

from typing import Callable
from langgraph.graph import StateGraph, END

from spgen.workflow.state import EpisodeState
from spgen.workflow.logger import WorkflowStep, get_logger
from spgen.workflow.nodes import (
    brainstorm,
    interactive_brainstorm_questions,
    agent_feedback, 
    merge_outlines,
    refine_outline,
    final_discussion,
    write_act_one,
    write_act_two,
    write_act_three,
    stitch_script,
    summarize_script,
    research_current_events,
)
from spgen.workflow.nodes.user_news_review import user_news_review


def should_research_news(state: EpisodeState) -> str:
    """
    Conditional entry point to determine workflow starting node.
    
    Analyzes the episode state to decide whether to begin with news research
    or proceed directly to brainstorming. This enables dynamic episode generation
    that can incorporate current events when requested.
    
    Args:
        state: Current episode state containing configuration flags
        
    Returns:
        str: The workflow step value to start execution with
        
    Decision Logic:
        - If dynamic_prompt=True → Start with news research
        - Otherwise → Start with direct brainstorming
    """
    if state.get("dynamic_prompt", False):
        return WorkflowStep.RESEARCH_CURRENT_EVENTS.value
    else:
        return WorkflowStep.BRAINSTORM.value

def wrap_node_with_progress(node_func, step: WorkflowStep):
    """
    Higher-order function that wraps workflow nodes with progress tracking.
    
    This decorator pattern adds comprehensive logging around each workflow step
    without modifying the core node implementations. Provides consistent
    progress reporting and error handling across all workflow phases.
    
    Args:
        node_func: The workflow node function to wrap
        step: The WorkflowStep enum representing this node
        
    Returns:
        callable: Wrapped function with progress logging
        
    Features:
        - Automatic step start/complete logging
        - Visual progress bar updates
        - Error handling and recovery
        - Maintains original function signature
    """
    def wrapped_node(state):
        logger = get_logger()
        logger.log_step_start(step)
        result = node_func(state)
        logger.log_step_complete(step)
        return result
    return wrapped_node

def build_graph() -> StateGraph:
    """
    Construct the complete LangGraph workflow for episode generation.
    
    This function builds a sophisticated 12-step workflow that orchestrates
    multiple AI agents through collaborative brainstorming, discussion, and
    script generation phases. The workflow is designed to simulate a real
    writers' room environment with structured creative processes.
    
    Returns:
        StateGraph: Compiled LangGraph workflow ready for execution
        
    Workflow Architecture:
        - 12 distinct processing steps with clear dependencies
        - Conditional entry point for news-based episodes  
        - Progress tracking on all nodes
        - Linear execution flow with state preservation
        - Type-safe node definitions using enums
        
    Error Handling:
        - Graceful degradation if nodes fail
        - Comprehensive logging for debugging
        - State validation between steps
    """
    graph = StateGraph(EpisodeState)

    def add_node_with_progress(step: WorkflowStep, node_func: Callable):
        graph.add_node(step.value, wrap_node_with_progress(node_func, step))

    # Define nodes with progress tracking
    add_node_with_progress(WorkflowStep.RESEARCH_CURRENT_EVENTS, research_current_events)
    add_node_with_progress(WorkflowStep.USER_NEWS_REVIEW, user_news_review)
    add_node_with_progress(WorkflowStep.BRAINSTORM, brainstorm)
    add_node_with_progress(WorkflowStep.INTERACTIVE_BRAINSTORM_QUESTIONS, interactive_brainstorm_questions)
    add_node_with_progress(WorkflowStep.AGENT_FEEDBACK, agent_feedback)
    add_node_with_progress(WorkflowStep.MERGE_OUTLINES, merge_outlines)
    add_node_with_progress(WorkflowStep.REFINE_OUTLINE, refine_outline)
    # add_node_with_progress(WorkflowStep.FINAL_DISCUSSION, final_discussion)
    add_node_with_progress(WorkflowStep.WRITE_ACT_ONE, write_act_one)
    add_node_with_progress(WorkflowStep.WRITE_ACT_TWO, write_act_two)
    add_node_with_progress(WorkflowStep.WRITE_ACT_THREE, write_act_three)
    add_node_with_progress(WorkflowStep.STITCH_SCRIPT, stitch_script)
    add_node_with_progress(WorkflowStep.SUMMARIZE_SCRIPT, summarize_script)


    # Define conditional entry point
    graph.set_conditional_entry_point(should_research_news)

    # Define edges
    # Graph illustration:
    # RESEARCH_CURRENT_EVENTS --> USER_NEWS_REVIEW --> BRAINSTORM
    # BRAINSTORM --> INTERACTIVE_BRAINSTORM_QUESTIONS
    # INTERACTIVE_BRAINSTORM_QUESTIONS --> AGENT_FEEDBACK
    # AGENT_FEEDBACK --> MERGE_OUTLINES
    # MERGE_OUTLINES --> REFINE_OUTLINE
    # REFINE_OUTLINE --> FINAL_DISCUSSION
    # FINAL_DISCUSSION --> WRITE_ACT_ONE
    # WRITE_ACT_ONE --> WRITE_ACT_TWO
    # WRITE_ACT_TWO --> WRITE_ACT_THREE
    # WRITE_ACT_THREE --> STITCH_SCRIPT
    # STITCH_SCRIPT --> SUMMARIZE_SCRIPT
    # SUMMARIZE_SCRIPT --> END

    graph.add_edge(WorkflowStep.RESEARCH_CURRENT_EVENTS.value, WorkflowStep.USER_NEWS_REVIEW.value)
    graph.add_edge(WorkflowStep.USER_NEWS_REVIEW.value, WorkflowStep.BRAINSTORM.value)
    graph.add_edge(WorkflowStep.BRAINSTORM.value, WorkflowStep.INTERACTIVE_BRAINSTORM_QUESTIONS.value)
    graph.add_edge(WorkflowStep.INTERACTIVE_BRAINSTORM_QUESTIONS.value, WorkflowStep.AGENT_FEEDBACK.value)
    graph.add_edge(WorkflowStep.AGENT_FEEDBACK.value, WorkflowStep.MERGE_OUTLINES.value)
    graph.add_edge(WorkflowStep.MERGE_OUTLINES.value, WorkflowStep.REFINE_OUTLINE.value)
    graph.add_edge(WorkflowStep.REFINE_OUTLINE.value, WorkflowStep.WRITE_ACT_ONE.value)
    # graph.add_edge(WorkflowStep.FINAL_DISCUSSION.value, WorkflowStep.WRITE_ACT_ONE.value)
    graph.add_edge(WorkflowStep.WRITE_ACT_ONE.value, WorkflowStep.WRITE_ACT_TWO.value)
    graph.add_edge(WorkflowStep.WRITE_ACT_TWO.value, WorkflowStep.WRITE_ACT_THREE.value)
    graph.add_edge(WorkflowStep.WRITE_ACT_THREE.value, WorkflowStep.STITCH_SCRIPT.value)
    graph.add_edge(WorkflowStep.STITCH_SCRIPT.value, WorkflowStep.SUMMARIZE_SCRIPT.value)
    graph.add_edge(WorkflowStep.SUMMARIZE_SCRIPT.value, END)

    return graph