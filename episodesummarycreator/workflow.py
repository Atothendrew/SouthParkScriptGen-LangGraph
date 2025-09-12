import sys
import os
import re
from typing import TypedDict, List, Dict, Any, Set, Tuple

# Add project root to Python path to allow importing from spgen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langgraph.graph import StateGraph, END
from episodesummarycreator.agents import EpisodeListAgent, EpisodeSummaryAgent

# Define the state for the graph
class EpisodeSummaryState(TypedDict):
    all_episodes: List[Dict[str, Any]]
    existing_episodes: Set[Tuple[int, int]]

# Create instances of the agents
episode_lister = EpisodeListAgent()
episode_summarizer = EpisodeSummaryAgent()

def get_existing_episodes() -> Set[Tuple[int, int]]:
    """
    Scans the episode_summaries directory and returns a set of existing (season, episode) tuples.
    """
    existing = set()
    summaries_dir = "episode_summaries"
    if not os.path.isdir(summaries_dir):
        os.makedirs(summaries_dir)
        return existing

    # Check both old format and new season folder format
    for item in os.listdir(summaries_dir):
        item_path = os.path.join(summaries_dir, item)
        
        if os.path.isfile(item_path):
            # Old format: s01e01_title.yaml
            match = re.match(r"s(\d{2})e(\d{2})_.*\.yaml", item)
            if match:
                season, episode = int(match.group(1)), int(match.group(2))
                existing.add((season, episode))
        
        elif os.path.isdir(item_path) and item.isdigit():
            # New format: season folders (1, 2, 3, etc.)
            season = int(item)
            for filename in os.listdir(item_path):
                match = re.match(r"e(\d{2})_.*\.yaml", filename)
                if match:
                    episode = int(match.group(1))
                    existing.add((season, episode))
    
    return existing

# Define the nodes for the graph
def get_episode_lists_node(state: EpisodeSummaryState):
    print("--- Step: Get Episode Lists ---")
    all_episodes = episode_lister.get_all_episodes()
    existing_episodes = get_existing_episodes()
    return {"all_episodes": all_episodes, "existing_episodes": existing_episodes}

def process_missing_episodes_node(state: EpisodeSummaryState):
    print("--- Step: Process Missing Episodes ---")
    all_episodes = state['all_episodes']
    existing_episodes = state['existing_episodes']
    
    missing_episodes = [
        e for e in all_episodes 
        if (e['season'], e['episode']) not in existing_episodes
    ]

    if not missing_episodes:
        print("✅ No missing episodes found. All summaries are up to date.")
        return {}

    print(f"Found {len(missing_episodes)} missing episode summaries. Starting creation process...")

    # Group episodes by season for organized processing
    episodes_by_season = {}
    for episode_info in missing_episodes:
        season = episode_info['season']
        if season not in episodes_by_season:
            episodes_by_season[season] = []
        episodes_by_season[season].append(episode_info)

    # Process each season
    for season in sorted(episodes_by_season.keys()):
        season_episodes = episodes_by_season[season]
        print(f"\n📺 Processing Season {season} ({len(season_episodes)} missing episodes)")
        
        # Create season directory
        season_dir = os.path.join("episode_summaries", str(season))
        os.makedirs(season_dir, exist_ok=True)
        
        # Process each episode in the season
        for episode_info in season_episodes:
            episode = episode_info['episode']
            title = episode_info['title']
            
            print(f"\n🚀 Generating summary for S{season:02d}E{episode:02d}: \"{title}\"")
            
            # Generate comprehensive episode summary directly from LLM
            episode_summary = episode_summarizer.generate_episode_summary(season, episode, title)
            
            if "error" in episode_summary:
                print(f"❌ Error generating summary for S{season:02d}E{episode:02d}: {episode_summary.get('error')}")
                continue

            # Save to season folder
            import yaml
            try:
                final_yaml = yaml.dump(episode_summary, sort_keys=False, allow_unicode=True, default_flow_style=False)
                
                title_slug = title.lower().replace(' ', '_')
                title_slug = "".join(c for c in title_slug if c.isalnum() or c == '_')
                filename = f"e{episode:02d}_{title_slug}.yaml"
                
                output_path = os.path.join(season_dir, filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write("---\n")  # YAML document separator
                    f.write(final_yaml)
                
                print(f"✅ Saved comprehensive summary to {output_path}")
            except Exception as e:
                print(f"❌ Error saving YAML for S{season:02d}E{episode:02d}: {e}")

    return {}


# Define the graph
def build_summary_creator_graph():
    workflow = StateGraph(EpisodeSummaryState)

    workflow.add_node("get_lists", get_episode_lists_node)
    workflow.add_node("process_missing", process_missing_episodes_node)

    workflow.set_entry_point("get_lists")
    workflow.add_edge("get_lists", "process_missing")
    workflow.add_edge("process_missing", END)

    return workflow.compile()