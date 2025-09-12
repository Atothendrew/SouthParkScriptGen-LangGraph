# Episode Summary Creation Guidelines

This document provides detailed guidelines for LLMs creating new South Park episode summary files that conform to the `EpisodeSummary` schema.

## 📋 Overview

When creating new episode summary YAML files, follow these guidelines to ensure 100% schema compliance and maintain consistency across the episode database.

## 🏗️ File Structure Requirements

### File Naming Convention
```
s{season:02d}e{episode:02d}_{title_slug}.yaml
```
- Example: `s01e01_cartman_gets_an_anal_probe.yaml`
- Title slug: lowercase, underscores for spaces, remove special characters

### Required YAML Structure
Every episode file MUST contain these top-level sections:
```yaml
---
basic_info:
plot:
characters:
content_elements:
themes:
continuity:
production:
context:
```

## 📝 Section-by-Section Guidelines

### 1. basic_info
**Required fields (all mandatory):**
```yaml
basic_info:
  season: 1                           # Integer: season number
  episode_number: 1                   # Integer: episode number within season
  title: "Episode Title"              # String: official episode title
  original_air_date: "1997-08-13"     # String: ISO date format (YYYY-MM-DD)
  episode_type: "standalone"          # Enum: standalone|multi_part|special|holiday
```

**Episode type values:**
- `standalone` - Regular self-contained episode (most common)
- `multi_part` - Part of a multi-episode story arc
- `special` - Special episodes (longer format, special events)
- `holiday` - Holiday-themed episodes

### 2. plot
**Required fields:**
```yaml
plot:
  logline: "One-sentence episode summary"                    # String: 1 sentence max
  plot_summary: |                                           # String: 2-3 paragraphs
    Detailed episode summary explaining the main events...
  plot_threads:                                             # Array: List of plot threads
    - title: "Main Plot"                                    # String: thread name
      description: "Description of this plot thread"        # String: what happens
      characters_involved:                                  # Array: character names
        - "Stan Marsh"
        - "Kyle Broflovski"
      resolution_status: "resolved"                         # Enum: resolved|unresolved|partially_resolved
      connects_to_episodes: []                              # Array: episode IDs this connects to
```

**Plot thread guidelines:**
- Always include at least one plot thread
- Main characters: Stan Marsh, Kyle Broflovski, Eric Cartman, Kenny McCormick
- Resolution status: `resolved` (most episodes), `unresolved` (cliffhangers), `partially_resolved` (some loose ends)

### 3. characters
**Required structure:**
```yaml
characters:
  main: []                    # Array: main characters (usually the boys)
  supporting: []              # Array: important secondary characters
  new: []                     # Array: characters introduced in this episode
```

**Character object structure:**
```yaml
- name: "Character Name"                    # String: full character name
  role: "main"                             # Enum: main|supporting|minor|cameo
  key_moments: []                          # Array: important moments for this character
  character_development: ""                # String: how character grows/changes
  relationships_affected: []               # Array: other characters affected by this character
```

**Character role guidelines:**
- `main` - Stan, Kyle, Cartman, Kenny, or other central characters
- `supporting` - Important recurring characters (Chef, parents, etc.)
- `minor` - Characters with small but notable roles
- `cameo` - Brief appearances

### 4. content_elements
**Required structure:**
```yaml
content_elements:
  cultural_references: []     # Array: things being referenced/parodied
  running_gags: []           # Array: recurring jokes in South Park
  locations: []              # Array: important locations in episode
```

**Cultural reference object:**
```yaml
- type: "movie"                         # Enum: celebrity|movie|tv_show|current_event|historical|internet_meme
  target: "Movie/Show/Person Name"      # String: what's being referenced
  description: "How it's referenced"    # String: description of the reference
  context: "Why it's used"             # String: context within the episode
```

**Running gag object:**
```yaml
- name: "Kenny Dies"                    # String: name of the gag
  description: "Kenny gets killed"      # String: what happens
  frequency: 1                         # Integer: how many times in episode
  first_appearance: "S01E01"           # String: episode ID where gag started (optional)
  evolution_notes: null                # String: how gag evolved (optional)
```

**Location object:**
```yaml
- name: "South Park Elementary"         # String: location name
  description: "The boys' school"       # String: description
  is_new: false                        # Boolean: new location in South Park universe
  significance: "Main setting"         # String: why location matters
```

### 5. themes
**Required structure (array of theme objects):**
```yaml
themes:
  - theme: "Friendship and Loyalty"           # String: theme name
    description: "Description of theme"       # String: what the theme is about
    how_explored: "How episode explores it"   # String: methods used to explore theme
    moral_lesson: null                       # String: lesson learned (optional)
```

**Common South Park themes:**
- Friendship and Loyalty
- Social Commentary
- Coming of Age
- Authority vs. Youth
- Media Satire
- Religious Commentary
- Political Satire

### 6. continuity
**Required structure:**
```yaml
continuity:
  callbacks: []                    # Array: references to previous episodes
  setup_for_future: []            # Array: things that set up future episodes
  character_developments: []       # Array: character growth/changes
  world_building: []              # Array: additions to South Park universe
```

### 7. production
**Required structure:**
```yaml
production:
  notable_quotes: []              # Array: memorable quotes from episode
  memorable_scenes: []            # Array: iconic scenes
  animation_notes: []             # Array: special animation techniques
  writers: []                     # Array: episode writers
  directors: []                   # Array: episode directors
  guest_voices: []               # Array: guest voice actors
```

**Default values:**
- Writers: Usually `["Trey Parker", "Matt Stone"]`
- Directors: Usually `["Trey Parker"]`

### 8. context
**Required structure:**
```yaml
context:
  historical_context: "When episode aired and cultural context"     # String
  controversy_notes: "Any controversies or issues"                  # String
  reception_notes: "How episode was received"                       # String
  social_commentary: []                                             # Array: social issues addressed
```

## ✅ Validation Checklist

Before finalizing an episode summary, verify:

### Basic Requirements
- [ ] File follows naming convention
- [ ] All 8 top-level sections present
- [ ] All required fields in each section present
- [ ] YAML starts with `---` document marker

### Data Types
- [ ] season/episode_number are integers
- [ ] dates in YYYY-MM-DD format
- [ ] episode_type is valid enum value
- [ ] character roles are valid enum values
- [ ] all arrays are properly formatted

### Content Quality
- [ ] logline is one sentence
- [ ] plot_summary is 2-3 paragraphs
- [ ] at least one plot thread present
- [ ] main characters (Stan, Kyle, Cartman, Kenny) included when relevant
- [ ] cultural references properly categorized
- [ ] themes are meaningful and relevant

### South Park Specific
- [ ] Character names match established spellings
- [ ] Locations match South Park universe
- [ ] Running gags align with series continuity
- [ ] Social commentary reflects episode's message

## 🎯 Best Practices

### Writing Style
- Use present tense for plot descriptions
- Be concise but descriptive
- Focus on key events and character moments
- Include both humor and serious elements when present

### Character Handling
- Always include the four main boys when they appear
- Use full character names (e.g., "Eric Cartman" not "Cartman")
- Capture character growth and relationships
- Note new character introductions

### Cultural Context
- Research references for accuracy
- Explain parodies clearly
- Note historical/cultural significance
- Link references to episode themes

### Continuity Awareness
- Reference previous episodes when relevant
- Note character/relationship developments
- Track running gags and their evolution
- Identify world-building elements

## 🔧 Common Mistakes to Avoid

1. **Schema Violations:**
   - Missing required fields
   - Wrong data types
   - Invalid enum values
   - Incorrect YAML formatting

2. **Content Issues:**
   - Overly long loglines
   - Missing main characters
   - Incorrect character spellings
   - Missing cultural references

3. **Structure Problems:**
   - Empty required arrays without default content
   - Missing plot threads
   - Inconsistent character role assignments
   - Wrong episode type classification

## 📚 Reference Examples

For examples of properly formatted episodes, refer to:
- `s01e01_cartman_gets_an_anal_probe.yaml` - Perfect schema compliance
- `s01e02_weight_gain_4000.yaml` - Good cultural references
- `s01e03_volcano.yaml` - Multiple plot threads example

## 🧪 Testing Your Episode

After creating an episode summary:

1. Run the validation test:
```bash
python test_episode_yaml.py
```

2. Check for your episode in the database:
```bash
python -c "
from spgen.schemas.yaml_loader import EpisodeDatabase
db = EpisodeDatabase()
print(f'Loaded {len(db)} episodes')
episode = db.get_episode(SEASON, EPISODE_NUMBER)
print(f'Your episode: {episode.title if episode else \"Not found\"}')
"
```

## 📖 Schema Reference

For the complete technical schema definition, see:
- `spgen/schemas/episode_summary.py` - EpisodeSummary dataclass
- `spgen/schemas/yaml_loader.py` - YAML loading implementation

---

Following these guidelines ensures your episode summaries integrate seamlessly with the South Park episode database and maintain the high quality standards established in the existing collection.
