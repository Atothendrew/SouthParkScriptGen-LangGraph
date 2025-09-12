import sys
import os
from typing import Dict, List, Any
from pydantic import BaseModel
import json

# Add project root to Python path to allow importing from spgen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from spgen.workflow.llm_provider import llm_call
from spgen.tools.duckduckgo_search import search_web
from spgen.schemas.episode_summary import EpisodeSummary
from pydantic import BaseModel
from typing import List
import yaml

class ResearcherAgent:
    """
    Agent responsible for researching a South Park episode online.
    """
    def research_episode(self, season: int, episode: int, episode_title: str = "") -> str:
        """
        Uses LLM knowledge to generate detailed information about a specific South Park episode.

        Args:
            season: The season number of the episode.
            episode: The episode number within the season.
            episode_title: The title of the episode (optional).

        Returns:
            A string containing detailed episode information.
        """
        print(f"🧠 Generating episode information using LLM knowledge for S{season:02d}E{episode:02d}: \"{episode_title}\"")
        
        prompt = f"""
You are a South Park expert with comprehensive knowledge of all episodes.
Provide detailed information about South Park Season {season}, Episode {episode}{f' titled "{episode_title}"' if episode_title else ''}.

Include the following information:
- Episode title (if not provided)
- Air date
- Plot summary (detailed)
- Main characters involved
- Key themes and topics
- Cultural references or parodies
- Memorable quotes or scenes
- Any controversy or notable reception

Format the response as a comprehensive episode guide entry. Be accurate and detailed.
If this episode doesn't exist, clearly state that.
"""
        
        try:
            research_material, model_name = llm_call(
                prompt,
                temperature=0.2,  # Low temperature for factual accuracy
            )
            
            print(f"✅ Generated episode research (model: {model_name})")
            return research_material
            
        except Exception as e:
            print(f"❌ Error generating episode research: {e}")
            return f"Could not generate information for Season {season}, Episode {episode}."


class EpisodeSummaryAgent:
    """
    Agent responsible for generating comprehensive episode summaries using LLM knowledge.
    """
    def __init__(self):
        with open("docs/EPISODE_CREATION_GUIDELINES.md", "r", encoding="utf-8") as f:
            self.guidelines = f.read()

    def generate_episode_summary(self, season: int, episode: int, title: str) -> Dict:
        """
        Uses LLM knowledge to generate a comprehensive episode summary following the EpisodeSummary schema.

        Args:
            season: The season number.
            episode: The episode number.
            title: The episode title.

        Returns:
            A dictionary with the episode summary following the comprehensive schema.
        """
        # Define the comprehensive episode summary schema
        episode_summary_schema = {
            "type": "object",
            "properties": {
                "basic_info": {
                    "type": "object",
                    "properties": {
                        "season": {"type": "integer"},
                        "episode_number": {"type": "integer"},
                        "title": {"type": "string"},
                        "original_air_date": {"type": "string", "format": "date"},
                        "episode_type": {"type": "string", "enum": ["standalone", "multi_part", "special", "holiday"]}
                    },
                    "required": ["season", "episode_number", "title", "original_air_date", "episode_type"]
                },
            }
        }
        
        prompt = f"""
You are a South Park expert. Create a comprehensive episode summary for Season {season}, Episode {episode}: "{title}".

Use your knowledge of South Park to provide:
- Complete plot summary with all major story threads
- Character analysis and development
- Cultural references and parodies
- Themes and social commentary
- Production details (writers, directors, memorable quotes)
- Continuity connections to other episodes
- Historical context and reception

Guidelines:
{self.guidelines}

Be thorough and accurate. If you're unsure about specific details, use reasonable estimates rather than leaving fields empty.
"""
        
        print(f"🧠 Generating comprehensive episode summary for S{season:02d}E{episode:02d}...")
        
        try:
            episode_data, model_name = llm_call(
                prompt,
                temperature=0.2,  # Low temperature for factual accuracy
                response_format={"type": "json_object", "schema": episode_summary_schema}
            )
            
            print(f"✅ Generated comprehensive episode summary (model: {model_name})")
            
            # Parse and return the structured data
            return json.loads(episode_data)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Error generating episode summary: {e}")
            return {"error": "Failed to generate episode summary", "raw_error": str(e)}


class EpisodeListAgent:
    """
    Agent responsible for getting the list of all South Park episodes.
    """
    def get_all_episodes(self) -> List[Dict[str, Any]]:
        """
        Uses LLM's built-in knowledge to generate a comprehensive list of South Park episodes one at a time.

        Returns:
            A list of dictionaries, where each dictionary represents an episode
            with 'season', 'episode', and 'title'.
        """
        all_episodes = []
        
        # South Park has 24+ seasons, generate episodes one at a time to avoid context overflow
        total_seasons = 24
        print(f"🧠 Generating episode list using LLM knowledge for {total_seasons} seasons (one episode at a time)...")
        
        for season in range(1, total_seasons + 1):
            print(f"🧠 Processing Season {season}...")
            
            # First, get the episode count for this season
            episode_count = self._get_season_episode_count(season)
            if episode_count == 0:
                print(f"  ⚠️ Season {season} has no episodes or doesn't exist")
                continue
            
            print(f"  📊 Season {season} has {episode_count} episodes")
            
            # Generate each episode individually
            season_episodes = []
            for ep_num in range(1, episode_count + 1):
                episode_info = self._generate_single_episode(season, ep_num)
                if episode_info:
                    season_episodes.append(episode_info)
                    print(f"    ✅ S{season:02d}E{ep_num:02d}: \"{episode_info['title']}\"")
                else:
                    print(f"    ❌ Failed to generate S{season:02d}E{ep_num:02d}")
            
            all_episodes.extend(season_episodes)
            print(f"  ✅ Season {season}: {len(season_episodes)}/{episode_count} episodes generated")
        
        print(f"🎯 Total episodes generated across all seasons: {len(all_episodes)}")
        return all_episodes
    
    def _get_season_episode_count(self, season: int) -> int:
        """
        Get the number of episodes in a specific season.
        """
        class SeasonInfo(BaseModel):
            season: int
            episode_count: int
            exists: bool
        
        prompt = f"""
You are a South Park expert. How many episodes are in Season {season} of South Park?

If Season {season} doesn't exist, set exists to false and episode_count to 0.
If it exists, provide the exact number of episodes in that season.
"""
        
        try:
            import lmstudio as lms
            
            models = lms.list_loaded_models()
            if not models:
                return 0
            
            model = lms.llm(models[0].identifier)
            result = model.respond(prompt, response_format=SeasonInfo)
            
            data = result.parsed
            if isinstance(data, dict):
                return data.get('episode_count', 0) if data.get('exists', False) else 0
            else:
                return data.episode_count if data.exists else 0
                
        except Exception as e:
            print(f"    ❌ Error getting episode count for Season {season}: {e}")
            return 0
    
    def _generate_single_episode(self, season: int, episode: int) -> Dict[str, Any]:
        """
        Generate information for a single episode.
        """
        class Episode(BaseModel):
            season: int
            episode: int
            title: str
        
        prompt = f"""
You are a South Park expert. Provide information about Season {season}, Episode {episode} of South Park.

Give the exact episode title for this specific episode. Be accurate.
"""
        
        try:
            import lmstudio as lms
            
            models = lms.list_loaded_models()
            if not models:
                return None
            
            model = lms.llm(models[0].identifier)
            result = model.respond(prompt, response_format=Episode)
            
            data = result.parsed
            if isinstance(data, dict):
                ep_dict = data
            else:
                ep_dict = {"season": data.season, "episode": data.episode, "title": data.title}
            
            # Validate the episode
            if (isinstance(ep_dict.get('season'), int) and 
                isinstance(ep_dict.get('episode'), int) and 
                ep_dict['season'] == season and
                ep_dict['episode'] == episode and
                ep_dict.get('title')):
                return ep_dict
            else:
                return None
                
        except Exception as e:
            print(f"    ❌ Error generating S{season:02d}E{episode:02d}: {e}")
            return None

    