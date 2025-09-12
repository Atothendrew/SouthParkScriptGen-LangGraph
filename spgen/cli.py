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
from typing import List, Optional

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a South Park episode.")
    parser.add_argument("prompt", nargs='?', help="High‑level episode idea (e.g., 'A school trip to the moon'). Optional when using --dynamic-prompt.")
    parser.add_argument("-n", "--num_parts", type=int, default=1, help="Number of parts to generate for the episode.")
    parser.add_argument("--include_personas", type=str, help="Comma-separated list of personas to include (e.g., 'Trey Parker,Matt Stone'). If provided, only these personas will be used.")
    parser.add_argument("--exclude_personas", type=str, help="Comma-separated list of personas to exclude (e.g., 'Chris Farley,Conan O'Brian'). These personas will be excluded.")
    parser.add_argument("--dynamic-prompt", action="store_true", help="Generate episode prompt from current trending news. When used, the prompt argument becomes optional.")
    args = parser.parse_args()

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
        from spgen.workflow.llm_client import set_tool_log_dir

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
