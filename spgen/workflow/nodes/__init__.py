"""Graph nodes for South Park episode generation workflow."""

from spgen.workflow.nodes.brainstorm import brainstorm, interactive_brainstorm_questions, refine_outline
from spgen.workflow.nodes.discussion import agent_feedback, merge_outlines, final_discussion
from spgen.workflow.nodes.script import write_act_one, write_act_two, write_act_three, stitch_script, summarize_script
from spgen.workflow.nodes.news_research import research_current_events

__all__ = [
    "brainstorm",
    "interactive_brainstorm_questions",
    "refine_outline", 
    "agent_feedback",
    "merge_outlines",
    "final_discussion",
    "write_act_one",
    "write_act_two", 
    "write_act_three",
    "stitch_script",
    "summarize_script",
    "research_current_events"
]