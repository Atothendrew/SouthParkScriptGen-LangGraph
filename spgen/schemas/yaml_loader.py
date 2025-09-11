"""YAML loader utility for episode summaries."""

import yaml
from pathlib import Path
from datetime import date
from typing import Dict, Any, List, Optional

from .episode_summary import (
    EpisodeSummary,
    CharacterAppearance,
    PlotThread,
    CulturalReference,
    RunningGag,
    Location,
    ThematicElement,
    EpisodeType,
    CharacterRole
)


class EpisodeSummaryLoader:
    """Utility class for loading episode summaries from YAML files."""
    
    @staticmethod
    def load_from_yaml(file_path: str | Path) -> EpisodeSummary:
        """Load an episode summary from a YAML file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Episode summary file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return EpisodeSummaryLoader._dict_to_episode_summary(data)
    
    @staticmethod
    def load_from_yaml_string(yaml_content: str) -> EpisodeSummary:
        """Load an episode summary from a YAML string."""
        data = yaml.safe_load(yaml_content)
        return EpisodeSummaryLoader._dict_to_episode_summary(data)
    
    @staticmethod
    def save_to_yaml(episode_summary: EpisodeSummary, file_path: str | Path) -> None:
        """Save an episode summary to a YAML file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = EpisodeSummaryLoader._episode_summary_to_dict(episode_summary)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    @staticmethod
    def _dict_to_episode_summary(data: Dict[str, Any]) -> EpisodeSummary:
        """Convert a dictionary loaded from YAML to an EpisodeSummary object."""
        basic_info = data['basic_info']
        plot_data = data['plot']
        characters_data = data['characters']
        content_data = data['content_elements']
        continuity_data = data['continuity']
        production_data = data['production']
        context_data = data['context']
        themes_data = data['themes']
        
        return EpisodeSummary(
            # Basic Episode Information
            season=basic_info['season'],
            episode_number=basic_info['episode_number'],
            title=basic_info['title'],
            original_air_date=date.fromisoformat(basic_info['original_air_date']),
            episode_type=EpisodeType(basic_info['episode_type']),
            
            # Plot Summary
            logline=plot_data['logline'],
            plot_summary=plot_data['plot_summary'],
            plot_threads=[
                PlotThread(
                    title=thread['title'],
                    description=thread['description'],
                    characters_involved=thread['characters_involved'],
                    resolution_status=thread['resolution_status'],
                    connects_to_episodes=thread.get('connects_to_episodes', [])
                ) for thread in plot_data['plot_threads']
            ],
            
            # Characters
            main_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char.get('key_moments', []),
                    character_development=char.get('character_development'),
                    relationships_affected=char.get('relationships_affected', [])
                ) for char in characters_data.get('main', [])
            ],
            supporting_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char.get('key_moments', []),
                    character_development=char.get('character_development'),
                    relationships_affected=char.get('relationships_affected', [])
                ) for char in characters_data.get('supporting', [])
            ],
            new_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char.get('key_moments', []),
                    character_development=char.get('character_development'),
                    relationships_affected=char.get('relationships_affected', [])
                ) for char in characters_data.get('new', [])
            ],
            
            # Content Elements
            cultural_references=[
                CulturalReference(
                    reference_type=ref['type'],
                    target=ref['target'],
                    description=ref['description'],
                    context=ref['context']
                ) for ref in content_data.get('cultural_references', [])
            ],
            running_gags=[
                RunningGag(
                    gag_name=gag['name'],
                    description=gag['description'],
                    frequency_in_episode=gag['frequency'],
                    first_appearance_episode=gag.get('first_appearance'),
                    evolution_notes=gag.get('evolution_notes')
                ) for gag in content_data.get('running_gags', [])
            ],
            locations=[
                Location(
                    name=loc['name'],
                    description=loc['description'],
                    is_new_location=loc.get('is_new', False),
                    significance=loc.get('significance', '')
                ) for loc in content_data.get('locations', [])
            ],
            
            # Themes and Analysis
            themes=[
                ThematicElement(
                    theme=theme['theme'],
                    description=theme['description'],
                    how_explored=theme['how_explored'],
                    moral_lesson=theme.get('moral_lesson')
                ) for theme in themes_data
            ],
            social_commentary=context_data.get('social_commentary', []),
            
            # Continuity Information
            callbacks_to_previous_episodes=continuity_data.get('callbacks', []),
            setup_for_future_episodes=continuity_data.get('setup_for_future', []),
            character_developments=continuity_data.get('character_developments', []),
            world_building_elements=continuity_data.get('world_building', []),
            
            # Production Notes
            notable_quotes=production_data.get('notable_quotes', []),
            memorable_scenes=production_data.get('memorable_scenes', []),
            animation_notes=production_data.get('animation_notes', []),
            writer_credits=production_data.get('writers', []),
            director_credits=production_data.get('directors', []),
            guest_voices=production_data.get('guest_voices', []),
            
            # Additional Context
            historical_context=context_data.get('historical_context'),
            controversy_notes=context_data.get('controversy_notes'),
            reception_notes=context_data.get('reception_notes')
        )
    
    @staticmethod
    def _episode_summary_to_dict(episode_summary: EpisodeSummary) -> Dict[str, Any]:
        """Convert an EpisodeSummary object to a dictionary for YAML serialization."""
        return {
            'basic_info': {
                'season': episode_summary.season,
                'episode_number': episode_summary.episode_number,
                'title': episode_summary.title,
                'original_air_date': episode_summary.original_air_date.isoformat(),
                'episode_type': episode_summary.episode_type.value
            },
            'plot': {
                'logline': episode_summary.logline,
                'plot_summary': episode_summary.plot_summary,
                'plot_threads': [
                    {
                        'title': thread.title,
                        'description': thread.description,
                        'characters_involved': thread.characters_involved,
                        'resolution_status': thread.resolution_status,
                        'connects_to_episodes': thread.connects_to_episodes
                    } for thread in episode_summary.plot_threads
                ]
            },
            'characters': {
                'main': [
                    {
                        'name': char.name,
                        'role': char.role.value,
                        'key_moments': char.key_moments,
                        'character_development': char.character_development,
                        'relationships_affected': char.relationships_affected
                    } for char in episode_summary.main_characters
                ],
                'supporting': [
                    {
                        'name': char.name,
                        'role': char.role.value,
                        'key_moments': char.key_moments,
                        'character_development': char.character_development,
                        'relationships_affected': char.relationships_affected
                    } for char in episode_summary.supporting_characters
                ],
                'new': [
                    {
                        'name': char.name,
                        'role': char.role.value,
                        'key_moments': char.key_moments,
                        'character_development': char.character_development,
                        'relationships_affected': char.relationships_affected
                    } for char in episode_summary.new_characters
                ]
            },
            'content_elements': {
                'cultural_references': [
                    {
                        'type': ref.reference_type,
                        'target': ref.target,
                        'description': ref.description,
                        'context': ref.context
                    } for ref in episode_summary.cultural_references
                ],
                'running_gags': [
                    {
                        'name': gag.gag_name,
                        'description': gag.description,
                        'frequency': gag.frequency_in_episode,
                        'first_appearance': gag.first_appearance_episode,
                        'evolution_notes': gag.evolution_notes
                    } for gag in episode_summary.running_gags
                ],
                'locations': [
                    {
                        'name': loc.name,
                        'description': loc.description,
                        'is_new': loc.is_new_location,
                        'significance': loc.significance
                    } for loc in episode_summary.locations
                ]
            },
            'themes': [
                {
                    'theme': theme.theme,
                    'description': theme.description,
                    'how_explored': theme.how_explored,
                    'moral_lesson': theme.moral_lesson
                } for theme in episode_summary.themes
            ],
            'continuity': {
                'callbacks': episode_summary.callbacks_to_previous_episodes,
                'setup_for_future': episode_summary.setup_for_future_episodes,
                'character_developments': episode_summary.character_developments,
                'world_building': episode_summary.world_building_elements
            },
            'production': {
                'notable_quotes': episode_summary.notable_quotes,
                'memorable_scenes': episode_summary.memorable_scenes,
                'animation_notes': episode_summary.animation_notes,
                'writers': episode_summary.writer_credits,
                'directors': episode_summary.director_credits,
                'guest_voices': episode_summary.guest_voices
            },
            'context': {
                'historical_context': episode_summary.historical_context,
                'controversy_notes': episode_summary.controversy_notes,
                'reception_notes': episode_summary.reception_notes,
                'social_commentary': episode_summary.social_commentary
            }
        }


class EpisodeDatabase:
    """Database-like interface for managing episode summaries."""
    
    def __init__(self, summaries_directory: str | Path = "episode_summaries"):
        """Initialize the episode database with a directory containing YAML files."""
        self.summaries_directory = Path(summaries_directory)
        self._episodes: Dict[str, EpisodeSummary] = {}
        self._load_all_episodes()
    
    def _load_all_episodes(self) -> None:
        """Load all episode summaries from YAML files in the directory."""
        if not self.summaries_directory.exists():
            return
        
        for yaml_file in self.summaries_directory.glob("*.yaml"):
            try:
                episode = EpisodeSummaryLoader.load_from_yaml(yaml_file)
                episode_id = f"S{episode.season:02d}E{episode.episode_number:02d}"
                self._episodes[episode_id] = episode
            except Exception as e:
                print(f"Warning: Failed to load episode from {yaml_file}: {e}")
    
    def get_episode(self, season: int, episode_number: int) -> Optional[EpisodeSummary]:
        """Get an episode summary by season and episode number."""
        episode_id = f"S{season:02d}E{episode_number:02d}"
        return self._episodes.get(episode_id)
    
    def get_episode_by_id(self, episode_id: str) -> Optional[EpisodeSummary]:
        """Get an episode summary by episode ID (e.g., 'S01E01')."""
        return self._episodes.get(episode_id)
    
    def get_all_episodes(self) -> List[EpisodeSummary]:
        """Get all loaded episode summaries."""
        return list(self._episodes.values())
    
    def get_episodes_by_season(self, season: int) -> List[EpisodeSummary]:
        """Get all episodes from a specific season."""
        return [ep for ep in self._episodes.values() if ep.season == season]
    
    def search_episodes(self, query: str) -> List[EpisodeSummary]:
        """Search episodes by title, plot summary, or character names."""
        query_lower = query.lower()
        results = []
        
        for episode in self._episodes.values():
            # Search in title
            if query_lower in episode.title.lower():
                results.append(episode)
                continue
            
            # Search in plot summary
            if query_lower in episode.plot_summary.lower():
                results.append(episode)
                continue
            
            # Search in character names
            all_characters = (episode.main_characters + 
                            episode.supporting_characters + 
                            episode.new_characters)
            if any(query_lower in char.name.lower() for char in all_characters):
                results.append(episode)
                continue
        
        return results
    
    def get_character_appearances(self, character_name: str) -> List[EpisodeSummary]:
        """Get all episodes where a specific character appears."""
        character_lower = character_name.lower()
        results = []
        
        for episode in self._episodes.values():
            all_characters = (episode.main_characters + 
                            episode.supporting_characters + 
                            episode.new_characters)
            if any(character_lower in char.name.lower() for char in all_characters):
                results.append(episode)
        
        return results
    
    def get_running_gag_episodes(self, gag_name: str) -> List[EpisodeSummary]:
        """Get all episodes that feature a specific running gag."""
        gag_lower = gag_name.lower()
        results = []
        
        for episode in self._episodes.values():
            if any(gag_lower in gag.gag_name.lower() for gag in episode.running_gags):
                results.append(episode)
        
        return results
    
    def add_episode(self, episode: EpisodeSummary, save_to_file: bool = True) -> None:
        """Add a new episode to the database."""
        episode_id = f"S{episode.season:02d}E{episode.episode_number:02d}"
        self._episodes[episode_id] = episode
        
        if save_to_file:
            filename = f"s{episode.season:02d}e{episode.episode_number:02d}_{episode.title.lower().replace(' ', '_').replace(':', '').replace('?', '').replace('!', '')}.yaml"
            file_path = self.summaries_directory / filename
            EpisodeSummaryLoader.save_to_yaml(episode, file_path)
    
    def reload(self) -> None:
        """Reload all episodes from the directory."""
        self._episodes.clear()
        self._load_all_episodes()
    
    def __len__(self) -> int:
        """Return the number of loaded episodes."""
        return len(self._episodes)
    
    def __iter__(self):
        """Iterate over all episodes."""
        return iter(self._episodes.values())
