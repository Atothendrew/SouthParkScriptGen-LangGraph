#!/usr/bin/env python3
"""
South Park Episode Generator - Command Line Interface

A professional CLI for generating South Park episodes through multi-agent AI collaboration.
This system orchestrates multiple AI personas (Trey Parker, Matt Stone, Bill Hader, etc.)
through structured brainstorming, discussion, and script generation workflows.

Features:
- Single or multi-part episode generation
- Persona inclusion/exclusion controls  
- Current events integration
- Comprehensive logging and progress tracking
- Complete creative process documentation

Usage Examples:
    python cli.py "The kids discover time travel"
    python cli.py "Randy becomes mayor" -n 3
    python cli.py "Social media drama" --include_personas "Trey Parker,Matt Stone"
    python cli.py "Current events satire" --dynamic_prompt

Author: AI Collaboration System
Version: 2.0.0
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
from pathlib import Path
import os
import re
import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from spgen.workflow import build_graph, EpisodeState, EpisodeContinuity
from spgen.workflow.state import ExtractedContinuityElements
from spgen.workflow.logger import WorkflowLogger, set_logger, WorkflowStep

LOG_DIR = "logs"

def extract_continuity_elements(final_state: EpisodeState) -> ExtractedContinuityElements:
    """Extract continuity elements from a completed episode part."""
    script = final_state["script"]
    merged_outline = final_state["merged_outline"]
    
    # Extract character developments (look for character growth moments)
    character_developments = []
    if "learns" in script.lower() or "realizes" in script.lower() or "discovers" in script.lower():
        # Simple extraction - in real implementation, could use LLM to extract these
        character_developments.append("Character development occurred in this part")
    
    # Extract running gags (look for repeated elements)
    running_gags = []
    if "running gag" in script.lower() or "callback" in script.lower():
        running_gags.append("Running gag established")
    
    # Extract unresolved plotlines (look for cliffhangers or open threads)
    unresolved_plotlines = []
    if "to be continued" in script.lower() or "meanwhile" in script.lower() or "but" in script[-200:].lower():
        unresolved_plotlines.append("Unresolved plotline detected")
    
    # Extract established locations (look for location names)
    established_locations = []
    common_locations = ["school", "home", "park", "store", "restaurant", "city hall"]
    for location in common_locations:
        if location in script.lower():
            established_locations.append(location.title())
    
    return ExtractedContinuityElements(
        character_developments=character_developments,
        running_gags=running_gags,
        unresolved_plotlines=unresolved_plotlines,
        established_locations=list(set(established_locations))
    )

def save_continuity_data(continuity_data: dict, prompt_dir: str):
    """Save continuity data to a JSON file for the next part to use."""
    continuity_file = os.path.join(prompt_dir, "episode_continuity.json")
    with open(continuity_file, "w", encoding="utf-8") as f:
        json.dump(continuity_data, f, indent=2, ensure_ascii=False)

def load_continuity_data(prompt_dir: str) -> dict:
    """Load continuity data from previous parts."""
    continuity_file = os.path.join(prompt_dir, "episode_continuity.json")
    if os.path.exists(continuity_file):
        with open(continuity_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "previous_summaries": [],
        "previous_outlines": [],
        "character_developments": [],
        "running_gags": [],
        "unresolved_plotlines": [],
        "established_locations": [],
        "previous_log_dirs": []
    }

def generate_combined_script(timestamp_dir: str, num_parts: int, original_prompt: str):
    """Generate a combined all_parts.md file from multipart episode scripts."""
    all_parts_file = os.path.join(timestamp_dir, "all_parts.md")
    
    with open(all_parts_file, "w", encoding="utf-8") as f:
        # Write header
        f.write(f"# Complete Episode: {original_prompt}\\n\\n")
        f.write(f"**Total Parts:** {num_parts}\\n")
        f.write(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\\n\\n")
        f.write("---\\n\\n")
        
        # Combine all parts
        for i in range(1, num_parts + 1):
            part_dir = os.path.join(timestamp_dir, f"part_{i:02d}")
            script_file = os.path.join(part_dir, "script.md")
            
            if os.path.exists(script_file):
                f.write(f"## Part {i}\\n\\n")
                
                # Read and include the script content
                with open(script_file, "r", encoding="utf-8") as script_f:
                    script_content = script_f.read()
                    # Remove the "# Episode Script" header from individual parts
                    if script_content.startswith("# Episode Script"):
                        script_content = script_content.split('\\n', 1)[1] if '\\n' in script_content else ""
                    
                    f.write(script_content.strip())
                    f.write("\\n\\n")
                
                # Add separator between parts (except for the last part)
                if i < num_parts:
                    f.write("---\\n\\n")
            else:
                f.write(f"## Part {i}\\n\\n")
                f.write("*Script not found*\\n\\n")
                if i < num_parts:
                    f.write("---\\n\\n")
        
        # Add episode summary section
        f.write("## Episode Summary\\n\\n")
        f.write("*This multipart episode follows the adventures as described above, ")
        f.write("with character development and plot progression across all parts.*\\n\\n")
        
        # Add continuity notes
        continuity_file = os.path.join(os.path.dirname(timestamp_dir), "episode_continuity.json")
        if os.path.exists(continuity_file):
            try:
                with open(continuity_file, "r", encoding="utf-8") as cont_f:
                    continuity_data = json.load(cont_f)
                
                f.write("## Continuity Elements\\n\\n")
                
                if continuity_data.get("character_developments"):
                    f.write("**Character Developments:**\\n")
                    for dev in continuity_data["character_developments"]:
                        f.write(f"- {dev}\\n")
                    f.write("\\n")
                
                if continuity_data.get("running_gags"):
                    f.write("**Running Gags:**\\n")
                    for gag in continuity_data["running_gags"]:
                        f.write(f"- {gag}\\n")
                    f.write("\\n")
                
                if continuity_data.get("established_locations"):
                    f.write("**Established Locations:**\\n")
                    f.write(f"{', '.join(continuity_data['established_locations'])}\\n\\n")
                
                if continuity_data.get("unresolved_plotlines"):
                    f.write("**Unresolved Plotlines:**\\n")
                    for plot in continuity_data["unresolved_plotlines"]:
                        f.write(f"- {plot}\\n")
                    f.write("\\n")
            
            except Exception as e:
                f.write(f"*Could not load continuity data: {e}*\\n\\n")


def _find_parent_dir_matching(start: str, predicate) -> Optional[str]:
    """Walk up from start until predicate(dir) is True or root is reached."""
    current = os.path.abspath(start)
    if os.path.isfile(current):
        current = os.path.dirname(current)
    while True:
        if predicate(current):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def _is_part_dir(path: str) -> bool:
    base = os.path.basename(path)
    return bool(re.match(r"^part_\d{2}$", base)) and os.path.exists(os.path.join(path, "process.txt"))


def _is_timestamp_dir(path: str) -> bool:
    base = os.path.basename(path)
    return bool(re.match(r"^\d{8}_\d{6}$", base))


def _parse_total_parts_from_process(process_file: str) -> Optional[int]:
    try:
        with open(process_file, "r", encoding="utf-8") as f:
            for line in f:
                if "Starting episode generation for part" in line and "of" in line:
                    # e.g. "Starting episode generation for part 1 of 3..."
                    m = re.search(r"part\s+(\d+)\s+of\s+(\d+)", line)
                    if m:
                        return int(m.group(2))
    except Exception:
        pass
    return None


def _is_part_complete(process_file: str) -> bool:
    try:
        with open(process_file, "r", encoding="utf-8") as f:
            content = f.read()
            return "generation complete!" in content
    except Exception:
        return False


def _extract_prompt_from_part(part_dir: str) -> Optional[str]:
    prompt_path = os.path.join(part_dir, "prompt.md")
    if not os.path.exists(prompt_path):
        return None
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            text = f.read()
        # The first line is a header like "# Part X Prompt"; prompt follows
        lines = text.splitlines()
        # Find first non-header line
        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                continue
            # Collect until Continuity Context section if present
            body = "\n".join(lines[i:])
            if "## Continuity Context" in body:
                body = body.split("## Continuity Context", 1)[0].strip()
            return body.strip()
    except Exception:
        return None


def _resolve_resume_context(path: str) -> Tuple[str, str, str]:
    """
    Given a path to any file/dir under a run, return (prompt_dir, timestamp_dir, part_dir).
    Raises ValueError if it cannot resolve.
    """
    abs_path = os.path.abspath(path)
    part_dir = _find_parent_dir_matching(abs_path, _is_part_dir)
    if not part_dir:
        # Fallback: look for a directory named part_XX even without process.txt
        part_dir = _find_parent_dir_matching(abs_path, lambda p: re.match(r"^part_\d{2}$", os.path.basename(p)) is not None)
        if not part_dir:
            raise ValueError("Could not locate part directory from the provided path")
    timestamp_dir = _find_parent_dir_matching(part_dir, _is_timestamp_dir)
    if not timestamp_dir:
        raise ValueError("Could not locate timestamp directory for the run")
    prompt_dir = os.path.dirname(timestamp_dir)
    return prompt_dir, timestamp_dir, part_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a South Park episode.")
    parser.add_argument("prompt", nargs='?', help="High‑level episode idea (e.g., 'A school trip to the moon'). Optional when using --dynamic-prompt.")
    parser.add_argument("-n", "--num_parts", type=int, default=1, help="Number of parts to generate for the episode.")
    parser.add_argument("--include_personas", type=str, help="Comma-separated list of personas to include (e.g., 'Trey Parker,Matt Stone'). If provided, only these personas will be used.")
    parser.add_argument("--exclude_personas", type=str, help="Comma-separated list of personas to exclude (e.g., 'Chris Farley,Conan O'Brian'). These personas will be excluded.")
    parser.add_argument("--dynamic-prompt", action="store_true", help="Generate episode prompt from current trending news. When used, the prompt argument becomes optional.")
    parser.add_argument("--next-from", dest="next_from", type=str, default=None, help="Path to any file or directory under a previous run's logs to generate the next part.")
    parser.add_argument("--resume-from", dest="resume_from", type=str, default=None, help="Path to any file or directory under a previous run's logs to resume from.")
    args = parser.parse_args()

    # Handle generate-next flow
    if args.next_from:
        prompt_dir, timestamp_dir, current_part_dir = _resolve_resume_context(args.next_from)
        print(f"➕ Generating next part for run at: {timestamp_dir}")

        # Determine next part number by scanning existing part_XX dirs
        part_dirs = sorted([d for d in os.listdir(timestamp_dir) if re.match(r"^part_\d{2}$", d)])
        if not part_dirs:
            raise SystemExit("No existing parts found under the given run. Cannot determine next part number.")
        last_num = max(int(d.split("_")[1]) for d in part_dirs)
        next_num = last_num + 1

        # Load continuity data
        continuity_data = load_continuity_data(prompt_dir)

        # Determine original prompt from first part if available
        first_part = os.path.join(timestamp_dir, "part_01")
        original_prompt = _extract_prompt_from_part(first_part) or ""

        # Build continuation prompt based on last summary and unresolved plotlines
        if continuity_data["previous_summaries"]:
            last_summary = continuity_data["previous_summaries"][-1]
            prompt = f"Continuing from the previous part: {last_summary}"
        else:
            prompt = original_prompt or "Continue the episode."
        if continuity_data["unresolved_plotlines"]:
            prompt += f"\n\nUnresolved plotlines to address: {', '.join(continuity_data['unresolved_plotlines'][-3:])}"

        # Prepare dirs
        part_dir = os.path.join(timestamp_dir, f"part_{next_num:02d}")
        os.makedirs(part_dir, exist_ok=True)
        log_dir = part_dir

        # Create continuity object for this next part
        continuity = EpisodeContinuity(
            part_number=next_num,
            total_parts=next_num,  # best-effort; unknown total, use current count
            original_prompt=original_prompt,
            previous_summaries=continuity_data["previous_summaries"],
            previous_outlines=continuity_data["previous_outlines"],
            character_developments=continuity_data["character_developments"],
            running_gags=continuity_data["running_gags"],
            unresolved_plotlines=continuity_data["unresolved_plotlines"],
            established_locations=continuity_data["established_locations"],
            previous_log_dirs=continuity_data["previous_log_dirs"],
        )

        # Write prompt file
        with open(os.path.join(log_dir, "prompt.md"), "w", encoding="utf-8") as f:
            f.write(f"# Part {next_num} Prompt\n\n{prompt}")

        # Build and run graph
        graph = build_graph()
        app = graph.compile()

        state: EpisodeState = {
            "prompt": prompt,
            "agent_outputs": [],
            "merged_outline": "",
            "discussion_history": [],
            "act_one_script": "",
            "act_two_script": "",
            "act_three_script": "",
            "script": "",
            "script_summary": "",
            "log_dir": log_dir,
            "include_personas": [p.strip() for p in args.include_personas.split(',')] if args.include_personas else None,
            "exclude_personas": [p.strip() for p in args.exclude_personas.split(',')] if args.exclude_personas else None,
            "continuity": continuity,
            "news_context_files": None,
            "dynamic_prompt": False,
        }

        logger = WorkflowLogger(log_dir)
        set_logger(logger)

        from spgen.workflow.llm_provider import set_tool_log_dir
        set_tool_log_dir(log_dir)

        logger.info("➕ Generating next part from existing run")
        logger.log_workflow_start(next_num, next_num)
        final_state = app.invoke(state)
        logger.log_workflow_complete(next_num)

        # Update continuity and save
        new_continuity_elements = extract_continuity_elements(final_state)
        continuity_data["previous_summaries"].append(final_state["script_summary"])
        continuity_data["previous_outlines"].append(final_state["merged_outline"])
        continuity_data["character_developments"].extend(new_continuity_elements.character_developments)
        continuity_data["running_gags"].extend(new_continuity_elements.running_gags)
        continuity_data["unresolved_plotlines"].extend(new_continuity_elements.unresolved_plotlines)
        continuity_data["established_locations"].extend(new_continuity_elements.established_locations)
        continuity_data["previous_log_dirs"].append(log_dir)
        continuity_data["established_locations"] = list(set(continuity_data["established_locations"]))
        save_continuity_data(continuity_data, prompt_dir)

        # Regenerate combined script to include the new part
        try:
            generate_combined_script(timestamp_dir, next_num, original_prompt or "Episode")
        except Exception as e:
            print(f"⚠️ Could not generate combined script: {e}")

        print(f"\n🎬 Next part generated: {part_dir}")
        print(f"📁 Episode root: {prompt_dir}")
        print(f"📖 Combined script: {os.path.join(timestamp_dir, 'all_parts.md')}")
        return

    # Handle resume flow
    if args.resume_from:
        prompt_dir, timestamp_dir, target_part_dir = _resolve_resume_context(args.resume_from)
        print(f"🔁 Resuming run at: {target_part_dir}")
        # Load continuity data for this prompt
        continuity_data = load_continuity_data(prompt_dir)
        # Determine original prompt from any part's prompt.md (prefer first part)
        first_part = os.path.join(timestamp_dir, "part_01")
        original_prompt = _extract_prompt_from_part(first_part) or _extract_prompt_from_part(target_part_dir) or ""
        prompt = original_prompt

        # Determine total planned parts from process.txt if possible
        process_file = os.path.join(target_part_dir, "process.txt")
        total_planned = _parse_total_parts_from_process(process_file)

        # List existing parts under the timestamp dir
        part_dirs = sorted([d for d in os.listdir(timestamp_dir) if re.match(r"^part_\d{2}$", d)])
        completed_parts = []
        for d in part_dirs:
            pf = os.path.join(timestamp_dir, d, "process.txt")
            if os.path.exists(pf) and _is_part_complete(pf):
                completed_parts.append(d)

        # Choose how many parts to run now
        num_parts_to_run = total_planned or args.num_parts or len(part_dirs)

        # Starting index: if target part is incomplete, start there, else start at next part
        target_idx = int(os.path.basename(target_part_dir).split("_")[1])
        target_complete = os.path.exists(process_file) and _is_part_complete(process_file)
        start_part_num = target_idx if not target_complete else max(target_idx + 1, len(completed_parts) + 1)

        # Ensure directories exist up to planned parts
        for i in range(1, num_parts_to_run + 1):
            d = os.path.join(timestamp_dir, f"part_{i:02d}")
            os.makedirs(d, exist_ok=True)

        # Iterate remaining parts starting from start_part_num
        for i in range(start_part_num, num_parts_to_run + 1):
            print(f"--- Resuming Part {i}/{num_parts_to_run} ---")
            part_dir = os.path.join(timestamp_dir, f"part_{i:02d}")
            os.makedirs(part_dir, exist_ok=True)

            log_dir = part_dir

            # Create continuity object for this part if not first
            continuity = None
            if i > 1:
                continuity = EpisodeContinuity(
                    part_number=i,
                    total_parts=num_parts_to_run,
                    original_prompt=original_prompt,
                    previous_summaries=continuity_data["previous_summaries"],
                    previous_outlines=continuity_data["previous_outlines"],
                    character_developments=continuity_data["character_developments"],
                    running_gags=continuity_data["running_gags"],
                    unresolved_plotlines=continuity_data["unresolved_plotlines"],
                    established_locations=continuity_data["established_locations"],
                    previous_log_dirs=continuity_data["previous_log_dirs"],
                )

            # If prompt.md missing, write it; otherwise keep existing
            prompt_md_path = os.path.join(log_dir, "prompt.md")
            if not os.path.exists(prompt_md_path):
                with open(prompt_md_path, "w", encoding="utf-8") as f:
                    f.write(f"# Part {i} Prompt\n\n{prompt}")

            # Build and run graph
            graph = build_graph()
            app = graph.compile()

            state: EpisodeState = {
                "prompt": prompt,
                "agent_outputs": [],
                "merged_outline": "",
                "discussion_history": [],
                "act_one_script": "",
                "act_two_script": "",
                "act_three_script": "",
                "script": "",
                "script_summary": "",
                "log_dir": log_dir,
                "include_personas": [p.strip() for p in args.include_personas.split(',')] if args.include_personas else None,
                "exclude_personas": [p.strip() for p in args.exclude_personas.split(',')] if args.exclude_personas else None,
                "continuity": continuity,
                "news_context_files": None,
                "dynamic_prompt": False,
            }

            logger = WorkflowLogger(log_dir)
            set_logger(logger)

            from spgen.workflow.llm_provider import set_tool_log_dir
            set_tool_log_dir(log_dir)

            logger.info("🔁 Resuming episode generation workflow")
            logger.log_workflow_start(i, num_parts_to_run)
            final_state = app.invoke(state)
            logger.log_workflow_complete(i)

            # Update continuity for next part
            new_continuity_elements = extract_continuity_elements(final_state)
            continuity_data["previous_summaries"].append(final_state["script_summary"])
            continuity_data["previous_outlines"].append(final_state["merged_outline"])
            continuity_data["character_developments"].extend(new_continuity_elements.character_developments)
            continuity_data["running_gags"].extend(new_continuity_elements.running_gags)
            continuity_data["unresolved_plotlines"].extend(new_continuity_elements.unresolved_plotlines)
            continuity_data["established_locations"].extend(new_continuity_elements.established_locations)
            continuity_data["previous_log_dirs"].append(log_dir)
            continuity_data["established_locations"] = list(set(continuity_data["established_locations"]))
            save_continuity_data(continuity_data, prompt_dir)

            # Prepare prompt for next part if needed
            if i < num_parts_to_run:
                continuation_prompt = f"Continuing from the previous part: {final_state['script_summary']}"
                if continuity_data["unresolved_plotlines"]:
                    continuation_prompt += f"\n\nUnresolved plotlines to address: {', '.join(continuity_data['unresolved_plotlines'][-3:])}"
                prompt = continuation_prompt

        # If multipart, generate combined script
        if num_parts_to_run > 1:
            print(f"\n📝 Generating combined script for {num_parts_to_run}-part episode...")
            generate_combined_script(timestamp_dir, num_parts_to_run, original_prompt)

        print(f"\n🎬 Resume complete. Episode updated in: {prompt_dir}")
        if num_parts_to_run > 1:
            print(f"📖 Combined script: {os.path.join(timestamp_dir, 'all_parts.md')}")
        return

    # Handle dynamic prompt generation
    if args.dynamic_prompt:
        if args.prompt:
            print("⚠️  When using --dynamic-prompt, the episode idea will be generated from current events.")
            print("   Your provided prompt will be ignored in favor of trending news analysis.")

        print("🔍 Generating episode concept from trending news...")
        from spgen.workflow.news_agent import NewsResearchAgent
        news_agent = NewsResearchAgent()
        generated_prompt = news_agent.generate_episode_prompt_from_news()
        print(f"📰 Generated concept: {generated_prompt}")

        original_prompt = generated_prompt
        prompt = generated_prompt
    else:
        if not args.prompt:
            parser.error("Episode prompt is required unless using --dynamic-prompt")
        original_prompt = args.prompt
        prompt = args.prompt

    # Parse include/exclude lists
    include_personas = [p.strip() for p in args.include_personas.split(',')] if args.include_personas else None
    exclude_personas = [p.strip() for p in args.exclude_personas.split(',')] if args.exclude_personas else None

    # Create main episode directory
    sanitized_prompt = re.sub(r'[^\w\s-]', '', original_prompt).strip().replace(' ', '_')[:100]
    prompt_dir = os.path.join(LOG_DIR, sanitized_prompt)
    os.makedirs(prompt_dir, exist_ok=True)

    # Load existing continuity data
    continuity_data = load_continuity_data(prompt_dir)

    # Create timestamped directory for this episode session
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    timestamp_dir = os.path.join(prompt_dir, timestamp)
    os.makedirs(timestamp_dir, exist_ok=True)

    for i in range(args.num_parts):
        print(f"--- Generating Part {i+1}/{args.num_parts} ---")

        # Create part directory under the timestamped folder
        part_dir = os.path.join(timestamp_dir, f"part_{i+1:02d}")
        os.makedirs(part_dir, exist_ok=True)

        log_dir = part_dir

        # Create continuity object for this part
        continuity = None
        if i > 0:  # Not the first part
            continuity = EpisodeContinuity(
                part_number=i + 1,
                total_parts=args.num_parts,
                original_prompt=original_prompt,
                previous_summaries=continuity_data["previous_summaries"],
                previous_outlines=continuity_data["previous_outlines"],
                character_developments=continuity_data["character_developments"],
                running_gags=continuity_data["running_gags"],
                unresolved_plotlines=continuity_data["unresolved_plotlines"],
                established_locations=continuity_data["established_locations"],
                previous_log_dirs=continuity_data["previous_log_dirs"]
            )

        # Write prompt and continuity context
        with open(os.path.join(log_dir, "prompt.md"), "w", encoding="utf-8") as f:
            f.write(f"# Part {i+1} Prompt\\n\\n{prompt}")

            if continuity:
                f.write(f"\\n\\n## Continuity Context\\n\\n")
                f.write(f"**Part {i+1} of {args.num_parts}**\\n\\n")
                f.write(f"**Original Prompt:** {original_prompt}\\n\\n")

                if continuity["previous_summaries"]:
                    f.write("**Previous Parts:**\\n")
                    for idx, summary in enumerate(continuity["previous_summaries"]):
                        f.write(f"- Part {idx+1}: {summary}\\n")
                    f.write("\\n")

                if continuity["character_developments"]:
                    f.write("**Character Developments:**\\n")
                    for dev in continuity["character_developments"]:
                        f.write(f"- {dev}\\n")
                    f.write("\\n")

                if continuity["running_gags"]:
                    f.write("**Running Gags:**\\n")
                    for gag in continuity["running_gags"]:
                        f.write(f"- {gag}\\n")
                    f.write("\\n")

                if continuity["unresolved_plotlines"]:
                    f.write("**Unresolved Plotlines:**\\n")
                    for plot in continuity["unresolved_plotlines"]:
                        f.write(f"- {plot}\\n")
                    f.write("\\n")

        # Build and compile graph
        graph = build_graph()
        app = graph.compile()

        print(f"🔧 Built episode generation workflow with {len(WorkflowStep)} steps")

        # Run the graph
        state: EpisodeState = {
            "prompt": prompt, 
            "agent_outputs": [], 
            "merged_outline": "", 
            "discussion_history": [], 
            "act_one_script": "", 
            "act_two_script": "", 
            "act_three_script": "", 
            "script": "", 
            "script_summary": "",
            "log_dir": log_dir,
            "include_personas": include_personas,
            "exclude_personas": exclude_personas,
            "continuity": continuity,
            "news_context_files": None,
            "dynamic_prompt": args.dynamic_prompt,
        }

        # Set up logger for this part
        logger = WorkflowLogger(log_dir)
        set_logger(logger)

        # Set up tool logging directory
        from spgen.workflow.llm_provider import set_tool_log_dir

        set_tool_log_dir(log_dir)

        # Log workflow initiarlization and start
        logger.info("🔧 Episode generation workflow initialized")
        logger.log_workflow_start(i+1, args.num_parts)

        final_state = app.invoke(state)

        # Log workflow completion
        logger.log_workflow_complete(i+1)

        # Extract continuity elements from this part
        new_continuity_elements = extract_continuity_elements(final_state)

        # Update continuity data for next part
        continuity_data["previous_summaries"].append(final_state["script_summary"])
        continuity_data["previous_outlines"].append(final_state["merged_outline"])
        continuity_data["character_developments"].extend(new_continuity_elements.character_developments)
        continuity_data["running_gags"].extend(new_continuity_elements.running_gags)
        continuity_data["unresolved_plotlines"].extend(new_continuity_elements.unresolved_plotlines)
        continuity_data["established_locations"].extend(new_continuity_elements.established_locations)
        continuity_data["previous_log_dirs"].append(log_dir)

        # Remove duplicates
        continuity_data["established_locations"] = list(set(continuity_data["established_locations"]))

        # Save updated continuity data
        save_continuity_data(continuity_data, prompt_dir)

        # Use the generated script summary as the prompt for the next part, but enhance it
        if i < args.num_parts - 1:  # Not the last part
            continuation_prompt = f"Continuing from the previous part: {final_state['script_summary']}"

            # Add context about unresolved elements
            if continuity_data["unresolved_plotlines"]:
                continuation_prompt += f"\\n\\nUnresolved plotlines to address: {', '.join(continuity_data['unresolved_plotlines'][-3:])}"

            prompt = continuation_prompt

        print(f"Part {i+1} complete. ")
        if i < args.num_parts - 1:
            print(f"Next part will continue with: {prompt[:100]}...")

    # Generate final combined script for multipart episodes
    if args.num_parts > 1:
        print(f"\\n📝 Generating combined script for {args.num_parts}-part episode...")
        generate_combined_script(timestamp_dir, args.num_parts, original_prompt)

    print(f"\\n🎬 Complete {args.num_parts}-part episode generated!")
    print(f"📁 All parts saved in: {prompt_dir}")
    if args.num_parts > 1:
        print(f"📖 Combined script: {os.path.join(timestamp_dir, 'all_parts.md')}")


if __name__ == "__main__":
    main()
