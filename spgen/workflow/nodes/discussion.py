"""Discussion and feedback nodes for episode generation."""

import os
from typing import Dict

from spgen.workflow.state import EpisodeState
from spgen.workflow.llm_client import llm_call, llm_call_with_model, search_tool
from spgen.workflow.logger import get_logger
from spgen.workflow.utils import should_include_persona, sanitize_filename
from spgen.agents import PERSONAS


def agent_feedback(state: EpisodeState) -> Dict:
    """Each agent provides feedback on the other agents' ideas in a brainstorm session."""
    logger = get_logger()
    logger.info("💭 Starting agent feedback phase...")

    # Log context size and content for debugging
    outlines_text = "\n\n".join(
        f"**{item['name']}**:\n{item['outline']}" for item in state["agent_outputs"]
    )
    logger.info(f"📊 Outlines context size: {len(outlines_text)} characters")
    logger.info(f"📝 Processing {len(state['agent_outputs'])} agent outlines")

    # Log existing discussion history for context analysis
    existing_history = state.get("discussion_history", [])
    logger.info(f"📚 Existing discussion history: {len(existing_history)} items")
    if existing_history:
        total_history_chars = sum(len(item) for item in existing_history)
        logger.info(f"📊 Discussion history size: {total_history_chars} characters")

    feedback = []
    brainstorm_session_dir = os.path.join(state["log_dir"], "brainstorm_session")
    os.makedirs(brainstorm_session_dir, exist_ok=True)

    for name, persona in PERSONAS.items():
        if not should_include_persona(name, state):
            continue

        logger.info(f"💭 {name} is providing feedback...")
        feedback_prompt = persona["discussion_prompt"]
        response, model_name = llm_call_with_model(
            feedback_prompt,
            temperature=persona["temperature"]["discussion"],
            tools=[search_tool],
            outlines=outlines_text,
        )
        feedback.append(f"**{name}'s Brainstorm Ideas:**\n{response}")
        filename = f"{sanitize_filename(name)}.md"
        filepath = os.path.join(brainstorm_session_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {name} Brainstorm Session\n\n{response}")
        logger.info(f"✅ {name}'s feedback saved to {os.path.abspath(filepath)}")
        logger.info(
            f"📊 {name}'s feedback size: {len(response)} characters ({model_name})"
        )

    # Append to existing discussion history instead of overwriting
    new_discussion_history = existing_history + feedback
    total_new_size = sum(len(item) for item in new_discussion_history)
    logger.info(f"📊 Updated discussion history: {len(new_discussion_history)} total items, {total_new_size} characters")
    state["discussion_history"] = new_discussion_history

    with open(os.path.join(state["log_dir"], "brainstorm_session.md"), "w", encoding="utf-8") as f:
        f.write("# Brainstorm Session\n\n")
        for item in feedback:
            f.write(f"{item}\n\n")

    logger.info(f"💭 Agent feedback phase complete! {len(feedback)} feedback items collected.")
    logger.info(f"📊 Total context being passed forward: {total_new_size} characters")
    return {"discussion_history": new_discussion_history}


def merge_outlines(state: EpisodeState) -> Dict:
    """A neutral persona (Trey) merges outlines based on feedback."""
    logger = get_logger()
    logger.info("🔀 Merging outlines with Trey Parker...")
    outlines_text = "\n\n".join(
        f"**{item['name']}**:\n{item['outline']}" for item in state["agent_outputs"]
    )
    discussion_history = "\n\n".join(state["discussion_history"])

    # Enhanced logging for debugging large context issues
    logger.info(f"📋 Using {len(state['agent_outputs'])} outlines and {len(state['discussion_history'])} discussion items")
    logger.info(f"📊 Outlines text size: {len(outlines_text)} characters")
    logger.info(f"📊 Discussion history size: {len(discussion_history)} characters")
    logger.info(f"📊 Total context size for merge: {len(outlines_text) + len(discussion_history)} characters")

    # Log what context is actually being used
    logger.info(f"🔍 Context being passed to Trey Parker for merging:")
    logger.info(f"  - Outlines: {len(outlines_text)} chars from {len(state['agent_outputs'])} agents")
    logger.info(f"  - Discussion: {len(discussion_history)} chars from {len(state['discussion_history'])} entries")

    # Use a neutral persona (Trey) to merge
    merge_prompt = PERSONAS["Trey Parker"]["discussion_prompt"]
    prompt = f"{merge_prompt}\n\nHere is the discussion history:\n{discussion_history}"
    merged_outline, model_name = llm_call_with_model(
        prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["discussion"],
        tools=[search_tool],
        outlines=outlines_text,
    )

    logger.info(
        f"📊 Merged outline output size: {len(merged_outline)} characters ({model_name})"
    )
    state["merged_outline"] = merged_outline

    with open(os.path.join(state["log_dir"], "final_merged_outline.md"), "w", encoding="utf-8") as f:
        f.write(f"# Final Merged Outline\n\n{merged_outline}")

    logger.info(
        f"✅ Outline merging complete! Saved to {os.path.abspath(os.path.join(state['log_dir'], 'final_merged_outline.md'))}"
    )
    return {"merged_outline": merged_outline}


def final_discussion(state: EpisodeState) -> Dict:
    """Agents have a final discussion and merge refined outlines."""
    logger = get_logger()
    logger.info("🎯 Starting final discussion phase...")

    # Log context analysis for final discussion
    outlines_text = "\n\n".join(
        f"**{item['name']}**:\n{item['outline']}" for item in state["agent_outputs"]
    )
    existing_history = state.get("discussion_history", [])
    logger.info(f"📊 Final discussion context sizes:")
    logger.info(f"  - Outlines: {len(outlines_text)} characters from {len(state['agent_outputs'])} agents")
    logger.info(f"  - Existing discussion: {len(existing_history)} items, {sum(len(item) for item in existing_history)} characters")

    feedback = []
    final_discussion_feedback_dir = os.path.join(state["log_dir"], "final_discussion_feedback")
    os.makedirs(final_discussion_feedback_dir, exist_ok=True)

    for name, persona in PERSONAS.items():
        if not should_include_persona(name, state):
            continue

        logger.info(f"🎯 {name} is providing final feedback...")
        feedback_prompt = persona["discussion_prompt"]
        response, model_name = llm_call_with_model(
            feedback_prompt,
            temperature=persona["temperature"]["discussion"],
            tools=[search_tool],
            outlines=outlines_text,
        )
        feedback.append(f"**{name}'s Final Feedback:**\n{response}")
        filename = f"{sanitize_filename(name)}.md"
        filepath = os.path.join(final_discussion_feedback_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {name} Final Feedback\n\n{response}")
        logger.info(f"✅ {name}'s final feedback saved to {os.path.abspath(filepath)}")
        logger.info(
            f"📊 {name}'s final feedback size: {len(response)} characters ({model_name})"
        )

    # Append to existing discussion history instead of overwriting
    new_final_history = existing_history + feedback
    total_final_size = sum(len(item) for item in new_final_history)
    logger.info(f"📊 Final discussion history: {len(new_final_history)} total items, {total_final_size} characters")
    state["discussion_history"] = new_final_history

    with open(os.path.join(state["log_dir"], "final_discussion_feedback.md"), "w", encoding="utf-8") as f:
        f.write("# Final Discussion Feedback\n\n")
        for item in feedback:
            f.write(f"{item}\n\n")

    logger.info("🔀 Trey Parker is creating final merged outline from discussion...")
    # Use Trey Parker to merge the final outlines based on the final discussion
    merge_prompt = PERSONAS["Trey Parker"]["discussion_prompt"]
    final_discussion_text = "\n\n".join(feedback)
    logger.info(f"🔍 Final merge context:")
    logger.info(f"  - Outlines: {len(outlines_text)} characters")
    logger.info(f"  - Final discussion: {len(final_discussion_text)} characters")
    logger.info(f"  - Total merge context: {len(outlines_text) + len(final_discussion_text)} characters")

    final_merged_outline, model_name = llm_call_with_model(
        merge_prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["discussion"],
        tools=[search_tool],
        outlines=outlines_text,
        discussion=final_discussion_text,
    )

    logger.info(
        f"📊 Final merged outline size: {len(final_merged_outline)} characters ({model_name})"
    )
    state["merged_outline"] = final_merged_outline

    with open(os.path.join(state["log_dir"], "final_merged_outline.md"), "w", encoding="utf-8") as f:
        f.write(f"# Final Merged Outline\n\n{final_merged_outline}")

    logger.info(f"🎯 Final discussion complete! {len(feedback)} final feedback items processed.")
    logger.info(f"📊 Total accumulated context: {total_final_size} characters")
    return {"merged_outline": final_merged_outline}
