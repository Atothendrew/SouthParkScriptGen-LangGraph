# Episode Summaries

This directory contains comprehensive summaries of South Park episodes stored in YAML format. These summaries are designed to provide detailed continuity information for the South Park Script Generator.

## Schema Overview

Each episode summary follows a structured schema that captures:

### Basic Information
- Season and episode number
- Title and original air date
- Episode type (standalone, multi-part, special, holiday)

### Plot Details
- One-sentence logline
- Detailed plot summary
- Individual plot threads with resolution status
- Connections to other episodes

### Character Information
- Main, supporting, and new characters
- Character roles and key moments
- Character development notes
- Relationship impacts

### Content Elements
- Cultural references and parodies
- Running gags and their evolution
- Locations and their significance
- Themes and moral lessons

### Continuity Tracking
- Callbacks to previous episodes
- Setup for future episodes
- Character developments
- World-building elements

### Production Notes
- Notable quotes and memorable scenes
- Animation notes
- Writer and director credits
- Guest voice actors

### Context
- Historical context
- Controversy notes
- Reception information
- Social commentary

## Usage

### Loading Episode Summaries

```python
from spgen.schemas import EpisodeSummaryLoader, EpisodeDatabase

# Load a single episode
episode = EpisodeSummaryLoader.load_from_yaml("episode_summaries/s01e01_cartman_gets_an_anal_probe.yaml")

# Use the episode database for multiple episodes
db = EpisodeDatabase("episode_summaries")
episode = db.get_episode(1, 1)  # Season 1, Episode 1
```

### Searching Episodes

```python
# Search by content
alien_episodes = db.search_episodes("alien")

# Find character appearances
cartman_episodes = db.get_character_appearances("Cartman")

# Find running gag episodes
kenny_death_episodes = db.get_running_gag_episodes("Kenny Dies")
```

### Creating New Summaries

```python
from spgen.schemas import EpisodeSummary, EpisodeType
from datetime import date

# Create a new episode summary
episode = EpisodeSummary(
    season=1,
    episode_number=2,
    title="Weight Gain 4000",
    original_air_date=date(1997, 8, 20),
    episode_type=EpisodeType.STANDALONE,
    logline="Cartman becomes famous for an essay contest win.",
    plot_summary="...",
    # ... other fields
)

# Save to YAML
EpisodeSummaryLoader.save_to_yaml(episode, "episode_summaries/s01e02_weight_gain_4000.yaml")
```

## File Naming Convention

Episode YAML files follow this naming pattern:
```
s{season:02d}e{episode:02d}_{title_slug}.yaml
```

Examples:
- `s01e01_cartman_gets_an_anal_probe.yaml`
- `s01e02_weight_gain_4000.yaml`
- `s05e14_kenny_dies.yaml`

## Available Episodes

### Season 1
- **S01E01**: Cartman Gets an Anal Probe ✅

*More episodes to be added...*

## Integration with Script Generator

The episode summaries are designed to integrate with the South Park Script Generator workflow to provide:

1. **Continuity Context**: Understanding character relationships and ongoing storylines
2. **Character Consistency**: Maintaining character voice and development patterns
3. **Reference Material**: Cultural references and running gags to incorporate
4. **World Building**: Established locations and rules of the South Park universe

## Schema Validation

All episode summaries are validated against the `EpisodeSummary` dataclass schema to ensure consistency and completeness. The schema includes:

- Type hints for all fields
- Enums for standardized values (EpisodeType, CharacterRole)
- Optional fields for flexibility
- Serialization/deserialization methods

## Contributing

When adding new episode summaries:

1. Follow the established YAML structure
2. Use the provided schema classes
3. Include comprehensive character and plot information
4. Add cultural references and running gags
5. Note continuity elements and connections
6. Test loading with the provided utilities

## Dependencies

The episode summary system requires:
- `pyyaml` for YAML parsing
- `dataclasses` for schema definition
- `typing` for type hints
- `datetime` for date handling
- `pathlib` for file operations
