"""Episode summary schema for South Park episode continuity tracking."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum


class EpisodeType(Enum):
    """Types of South Park episodes."""
    STANDALONE = "standalone"
    MULTI_PART = "multi_part"
    SPECIAL = "special"
    HOLIDAY = "holiday"


class CharacterRole(Enum):
    """Character roles in episodes."""
    MAIN = "main"
    SUPPORTING = "supporting"
    MINOR = "minor"
    CAMEO = "cameo"


@dataclass
class CharacterAppearance:
    """Character appearance in an episode."""
    name: str
    role: CharacterRole
    key_moments: List[str] = field(default_factory=list)
    character_development: Optional[str] = None
    relationships_affected: List[str] = field(default_factory=list)


@dataclass
class PlotThread:
    """A plot thread within an episode."""
    title: str
    description: str
    characters_involved: List[str]
    resolution_status: str  # "resolved", "unresolved", "partially_resolved"
    connects_to_episodes: List[str] = field(default_factory=list)  # Episode IDs this connects to


@dataclass
class CulturalReference:
    """Cultural references and parodies in the episode."""
    reference_type: str  # "celebrity", "movie", "tv_show", "current_event", "historical", "internet_meme"
    target: str  # What is being referenced/parodied
    description: str
    context: str  # How it's used in the episode


@dataclass
class RunningGag:
    """Running gags that appear in the episode."""
    gag_name: str
    description: str
    frequency_in_episode: int
    first_appearance_episode: Optional[str] = None
    evolution_notes: Optional[str] = None


@dataclass
class Location:
    """Locations featured in the episode."""
    name: str
    description: str
    is_new_location: bool = False
    significance: str = ""  # Why this location matters to the plot


@dataclass
class ThematicElement:
    """Themes and messages in the episode."""
    theme: str
    description: str
    how_explored: str
    moral_lesson: Optional[str] = None


@dataclass
class EpisodeSummary:
    """Comprehensive summary schema for South Park episodes."""
    
    # Basic Episode Information
    season: int
    episode_number: int
    title: str
    original_air_date: date
    episode_type: EpisodeType
    
    # Plot Summary
    logline: str  # One-sentence summary
    plot_summary: str  # 2-3 paragraph detailed summary
    plot_threads: List[PlotThread]
    
    # Characters
    main_characters: List[CharacterAppearance]
    supporting_characters: List[CharacterAppearance]
    new_characters: List[CharacterAppearance] = field(default_factory=list)
    
    # Content Elements
    cultural_references: List[CulturalReference] = field(default_factory=list)
    running_gags: List[RunningGag] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    
    # Themes and Analysis
    themes: List[ThematicElement] = field(default_factory=list)
    social_commentary: List[str] = field(default_factory=list)
    
    # Continuity Information
    callbacks_to_previous_episodes: List[str] = field(default_factory=list)
    setup_for_future_episodes: List[str] = field(default_factory=list)
    character_developments: List[str] = field(default_factory=list)
    world_building_elements: List[str] = field(default_factory=list)
    
    # Production Notes
    notable_quotes: List[str] = field(default_factory=list)
    memorable_scenes: List[str] = field(default_factory=list)
    animation_notes: List[str] = field(default_factory=list)
    
    # Metadata
    writer_credits: List[str] = field(default_factory=list)
    director_credits: List[str] = field(default_factory=list)
    guest_voices: List[str] = field(default_factory=list)
    
    # Additional Context
    historical_context: Optional[str] = None
    controversy_notes: Optional[str] = None
    reception_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the episode summary to a dictionary."""
        return {
            'basic_info': {
                'season': self.season,
                'episode_number': self.episode_number,
                'title': self.title,
                'original_air_date': self.original_air_date.isoformat(),
                'episode_type': self.episode_type.value
            },
            'plot': {
                'logline': self.logline,
                'plot_summary': self.plot_summary,
                'plot_threads': [
                    {
                        'title': thread.title,
                        'description': thread.description,
                        'characters_involved': thread.characters_involved,
                        'resolution_status': thread.resolution_status,
                        'connects_to_episodes': thread.connects_to_episodes
                    } for thread in self.plot_threads
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
                    } for char in self.main_characters
                ],
                'supporting': [
                    {
                        'name': char.name,
                        'role': char.role.value,
                        'key_moments': char.key_moments,
                        'character_development': char.character_development,
                        'relationships_affected': char.relationships_affected
                    } for char in self.supporting_characters
                ],
                'new': [
                    {
                        'name': char.name,
                        'role': char.role.value,
                        'key_moments': char.key_moments,
                        'character_development': char.character_development,
                        'relationships_affected': char.relationships_affected
                    } for char in self.new_characters
                ]
            },
            'content_elements': {
                'cultural_references': [
                    {
                        'type': ref.reference_type,
                        'target': ref.target,
                        'description': ref.description,
                        'context': ref.context
                    } for ref in self.cultural_references
                ],
                'running_gags': [
                    {
                        'name': gag.gag_name,
                        'description': gag.description,
                        'frequency': gag.frequency_in_episode,
                        'first_appearance': gag.first_appearance_episode,
                        'evolution_notes': gag.evolution_notes
                    } for gag in self.running_gags
                ],
                'locations': [
                    {
                        'name': loc.name,
                        'description': loc.description,
                        'is_new': loc.is_new_location,
                        'significance': loc.significance
                    } for loc in self.locations
                ]
            },
            'themes': [
                {
                    'theme': theme.theme,
                    'description': theme.description,
                    'how_explored': theme.how_explored,
                    'moral_lesson': theme.moral_lesson
                } for theme in self.themes
            ],
            'continuity': {
                'callbacks': self.callbacks_to_previous_episodes,
                'setup_for_future': self.setup_for_future_episodes,
                'character_developments': self.character_developments,
                'world_building': self.world_building_elements
            },
            'production': {
                'notable_quotes': self.notable_quotes,
                'memorable_scenes': self.memorable_scenes,
                'animation_notes': self.animation_notes,
                'writers': self.writer_credits,
                'directors': self.director_credits,
                'guest_voices': self.guest_voices
            },
            'context': {
                'historical_context': self.historical_context,
                'controversy_notes': self.controversy_notes,
                'reception_notes': self.reception_notes,
                'social_commentary': self.social_commentary
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpisodeSummary':
        """Create an EpisodeSummary from a dictionary."""
        basic_info = data['basic_info']
        plot_data = data['plot']
        characters_data = data['characters']
        content_data = data['content_elements']
        continuity_data = data['continuity']
        production_data = data['production']
        context_data = data['context']
        
        return cls(
            season=basic_info['season'],
            episode_number=basic_info['episode_number'],
            title=basic_info['title'],
            original_air_date=date.fromisoformat(basic_info['original_air_date']),
            episode_type=EpisodeType(basic_info['episode_type']),
            logline=plot_data['logline'],
            plot_summary=plot_data['plot_summary'],
            plot_threads=[
                PlotThread(
                    title=thread['title'],
                    description=thread['description'],
                    characters_involved=thread['characters_involved'],
                    resolution_status=thread['resolution_status'],
                    connects_to_episodes=thread['connects_to_episodes']
                ) for thread in plot_data['plot_threads']
            ],
            main_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char['key_moments'],
                    character_development=char['character_development'],
                    relationships_affected=char['relationships_affected']
                ) for char in characters_data['main']
            ],
            supporting_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char['key_moments'],
                    character_development=char['character_development'],
                    relationships_affected=char['relationships_affected']
                ) for char in characters_data['supporting']
            ],
            new_characters=[
                CharacterAppearance(
                    name=char['name'],
                    role=CharacterRole(char['role']),
                    key_moments=char['key_moments'],
                    character_development=char['character_development'],
                    relationships_affected=char['relationships_affected']
                ) for char in characters_data['new']
            ],
            cultural_references=[
                CulturalReference(
                    reference_type=ref['type'],
                    target=ref['target'],
                    description=ref['description'],
                    context=ref['context']
                ) for ref in content_data['cultural_references']
            ],
            running_gags=[
                RunningGag(
                    gag_name=gag['name'],
                    description=gag['description'],
                    frequency_in_episode=gag['frequency'],
                    first_appearance_episode=gag['first_appearance'],
                    evolution_notes=gag['evolution_notes']
                ) for gag in content_data['running_gags']
            ],
            locations=[
                Location(
                    name=loc['name'],
                    description=loc['description'],
                    is_new_location=loc['is_new'],
                    significance=loc['significance']
                ) for loc in content_data['locations']
            ],
            themes=[
                ThematicElement(
                    theme=theme['theme'],
                    description=theme['description'],
                    how_explored=theme['how_explored'],
                    moral_lesson=theme['moral_lesson']
                ) for theme in data['themes']
            ],
            social_commentary=context_data['social_commentary'],
            callbacks_to_previous_episodes=continuity_data['callbacks'],
            setup_for_future_episodes=continuity_data['setup_for_future'],
            character_developments=continuity_data['character_developments'],
            world_building_elements=continuity_data['world_building'],
            notable_quotes=production_data['notable_quotes'],
            memorable_scenes=production_data['memorable_scenes'],
            animation_notes=production_data['animation_notes'],
            writer_credits=production_data['writers'],
            director_credits=production_data['directors'],
            guest_voices=production_data['guest_voices'],
            historical_context=context_data['historical_context'],
            controversy_notes=context_data['controversy_notes'],
            reception_notes=context_data['reception_notes']
        )
