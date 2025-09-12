"""Script generation nodes for episode creation."""

import os
from typing import Dict

from spgen.workflow.state import EpisodeState
from spgen.workflow.llm_provider import llm_call, get_available_tools
from spgen.workflow.logger import get_logger
from spgen.agents import PERSONAS


def write_act_one(state: EpisodeState) -> Dict:
    """Writes the script for Act One."""
    logger = get_logger()
    logger.info("📝 Writing Act One script...")
    discussion_context = "\n\n".join(state.get("discussion_history", []))
    logger.info(f"📋 Using {len(state.get('discussion_history', []))} discussion items for context")
    act_one_prompt = (
        "You are a scriptwriter for South Park. Write Act One of a full episode script based on the following outline. "
        "Act One should introduce the characters and the main conflict. "
        "The script should be in the standard script format, with scene headings, character names, and dialogue. "
        "Make sure to include plenty of jokes and satire, in the style of South Park.\n\n"
        "Use the collaborative discussion and feedback below to inform your writing and incorporate the best ideas:\n\n"
        "COLLABORATIVE FEEDBACK:\n{discussion_context}\n\n---\n\n"
        "OUTLINE:\n{outline}"
    )
    script, model_name = llm_call(
        act_one_prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["brainstorm"],
        tools=get_available_tools(),
        outline=state["merged_outline"],
        discussion_context=discussion_context,
    )
    state["act_one_script"] = script
    logger.info("✅ Act One script completed!")
    return {"act_one_script": script}


def write_act_two(state: EpisodeState) -> Dict:
    """Writes the script for Act Two."""
    logger = get_logger()
    logger.info("📝 Writing Act Two script...")
    discussion_context = "\n\n".join(state.get("discussion_history", []))
    logger.info(f"📋 Using {len(state.get('discussion_history', []))} discussion items for context")
    act_two_prompt = (
        "You are a scriptwriter for South Park. Write Act Two of a full episode script based on the following outline. "
        "Act Two should develop the conflict and raise the stakes. "
        "The script should be in the standard script format, with scene headings, character names, and dialogue. "
        "Make sure to include plenty of jokes and satire, in the style of South Park.\n\n"
        "Use the collaborative discussion and feedback below to inform your writing and incorporate the best ideas:\n\n"
        "COLLABORATIVE FEEDBACK:\n{discussion_context}\n\n---\n\n"
        "OUTLINE:\n{outline}"
    )
    script, model_name = llm_call(
        act_two_prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["brainstorm"],
        tools=get_available_tools(),
        outline=state["merged_outline"],
        discussion_context=discussion_context,
    )
    state["act_two_script"] = script
    logger.info("✅ Act Two script completed!")
    return {"act_two_script": script}


def write_act_three(state: EpisodeState) -> Dict:
    """Writes the script for Act Three."""
    logger = get_logger()
    logger.info("📝 Writing Act Three script...")
    discussion_context = "\n\n".join(state.get("discussion_history", []))
    logger.info(f"📋 Using {len(state.get('discussion_history', []))} discussion items for context")
    act_three_prompt = (
        "You are a scriptwriter for South Park. Write Act Three of a full episode script based on the following outline. "
        "Act Three should resolve the conflict and provide a satisfying conclusion. "
        "The script should be in the standard script format, with scene headings, character names, and dialogue. "
        "Make sure to include plenty of jokes and satire, in the style of South Park.\n\n"
        "Use the collaborative discussion and feedback below to inform your writing and incorporate the best ideas:\n\n"
        "COLLABORATIVE FEEDBACK:\n{discussion_context}\n\n---\n\n"
        "OUTLINE:\n{outline}"
    )
    script, model_name = llm_call(
        act_three_prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["brainstorm"],
        tools=get_available_tools(),
        outline=state["merged_outline"],
        discussion_context=discussion_context,
    )
    state["act_three_script"] = script
    logger.info("✅ Act Three script completed!")
    return {"act_three_script": script}


def stitch_script(state: EpisodeState) -> Dict:
    """Stitches the three acts together into a single script."""
    logger = get_logger()
    logger.info("🎬 Stitching all acts together...")
    script = f"{state['act_one_script']}\n\n{state['act_two_script']}\n\n{state['act_three_script']}"
    state["script"] = script

    with open(os.path.join(state["log_dir"], "script.md"), "w", encoding="utf-8") as f:
        f.write(f"# Episode Script\n\n{script}")

    logger.info(
        f"✅ Complete script saved to {os.path.abspath(os.path.join(state['log_dir'], 'script.md'))}"
    )
    return {"script": script}


def summarize_script(state: EpisodeState) -> Dict:
    """Summarizes the final script."""
    logger = get_logger()
    logger.info("📄 Creating script summary...")
    summary_prompt = (
        "You are a scriptwriter for South Park. Summarize the following script in a few sentences. "
        "The summary should capture the main plot points and the overall tone of the episode.\n\n---\n\n{script}"
    )
    summary, model_name = llm_call(
        summary_prompt,
        temperature=PERSONAS["Trey Parker"]["temperature"]["discussion"],
        tools=get_available_tools(),
        script=state["script"],
    )
    state["script_summary"] = summary
    logger.info("✅ Script summary completed!")
    return {"script_summary": summary}
