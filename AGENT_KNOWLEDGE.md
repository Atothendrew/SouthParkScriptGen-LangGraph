# Agent Knowledge Base - South Park Script Generator

## Project Overview
The South Park Script Generator is a sophisticated multi-agent AI system built with LangGraph that simulates a collaborative writers' room environment. The system generates complete South Park episode scripts through structured brainstorming, discussion, and refinement phases using multiple AI personas.

## Core Architecture

### LangGraph Workflow System
- **Framework**: LangGraph StateGraph for workflow orchestration
- **State Management**: TypedDict-based `EpisodeState` flows through all nodes
- **Progress Tracking**: Comprehensive logging with visual progress bars
- **Type Safety**: Full type hints and enum-based workflow steps

### Multi-Agent Collaboration
- **Personas**: Configurable AI agents (Trey Parker, Matt Stone, Bill Hader, etc.)
- **Specialized Prompts**: Each persona has unique templates for different workflow phases
- **Temperature Control**: Dynamic creativity levels based on workflow step
- **Collaborative Process**: Structured Q&A, feedback, and refinement loops

## Workflow Structure

### 13-Step Process
1. **Research Current Events** (conditional) - News gathering for topical episodes
2. **User News Review** - User selection of relevant news items
3. **Brainstorm** - Initial independent idea generation by each persona
4. **Interactive Brainstorm Questions** - Targeted Q&A between agents
5. **Agent Feedback** - Collaborative discussion and critique
6. **Merge Outlines** - Consolidation of ideas into unified outline
7. **Refine Outline** - Enhancement and polishing of merged concept
8. **Final Discussion** - Last collaborative feedback round
9. **Write Act One** - First act script generation
10. **Write Act Two** - Second act script generation
11. **Write Act Three** - Third act script generation
12. **Stitch Script** - Assembly of complete episode script
13. **Summarize Script** - Final episode summary generation

### Conditional Entry Points
- **Dynamic Prompt Mode**: Starts with news research for current events
- **Direct Mode**: Bypasses research, goes straight to brainstorming

## Key Files and Components

### Core Workflow Files
- `spgen/workflow/builder.py` - LangGraph workflow construction and orchestration
- `spgen/workflow/state.py` - Episode state definition and type structures
- `spgen/workflow/logger.py` - Comprehensive logging system with progress tracking
- `spgen/workflow/nodes/` - Individual workflow step implementations

### Configuration and Personas
- `configs/` - YAML configuration files for each AI persona
- `spgen/agents.py` - Persona management and prompt template system

### CLI and Interface
- `spgen/cli.py` - Command-line interface for episode generation
- Support for multi-part episodes, persona inclusion/exclusion, dynamic prompts

## State Management

### EpisodeState Structure
```python
class EpisodeState(TypedDict):
    prompt: str                           # User-provided episode idea
    agent_outputs: List[Dict]             # Persona brainstorming results
    discussion_history: List[str]         # Q&A and feedback logs
    merged_outline: str                   # Consolidated episode outline
    act_one_script: str                   # First act content
    act_two_script: str                   # Second act content
    act_three_script: str                 # Third act content
    script: str                           # Complete assembled script
    script_summary: str                   # Final episode summary
    continuity: Optional[EpisodeContinuity] # Multi-part episode context
    news_context_files: Optional[Dict]    # Current events context
    dynamic_prompt: bool                  # Research mode flag
```

### Progress Tracking
- Visual progress bars with █/░ characters
- Step-by-step completion logging
- Timestamped file logging to `process.txt`
- Console output with emojis and formatting

## LLM Integration

### LM Studio Configuration
- Local LLM inference via OpenAI-compatible API
- Configurable endpoint (default: http://10.0.0.87:1234/v1)
- Temperature control per workflow phase
- Model: llama3.1 (default)

### Prompt Engineering
- Persona-specific templates for each workflow step
- Context-aware prompt construction
- Dynamic prompt enhancement with current events
- Structured output formats for consistency

## Episode Generation Features

### Content Types
- Standard episodes from user prompts
- News-based topical episodes with current events research
- Multi-part episode series with continuity tracking
- Character development and running gag preservation

### Collaboration Simulation
- Realistic writers' room discussions
- Targeted questions between specific personas
- Iterative refinement through multiple feedback rounds
- Authentic South Park voice and tone

## Error Handling and Reliability

### Graceful Degradation
- Continues workflow even if individual nodes fail
- Comprehensive error logging for debugging
- State validation between workflow steps
- Automatic recovery mechanisms

### Testing Infrastructure
- Unit tests for core components
- Example prompts for validation
- Pytest configuration for test automation
- Coverage tracking for reliability

## Development Patterns

### Code Organization
- Modular node architecture for easy extension
- Separation of concerns between workflow, state, and personas
- Type-safe interfaces throughout
- Comprehensive documentation and examples

### Extension Points
- New persona addition via YAML configuration
- Custom workflow steps through node system
- Configurable LLM backends
- Plugin architecture for additional features

## Usage Examples

### Basic Episode Generation
```bash
spgen generate "Randy discovers a new conspiracy theory"
```

### News-Based Episodes
```bash
spgen generate --dynamic-prompt "Create episode about recent AI developments"
```

### Multi-Part Series
```bash
spgen generate --parts 3 "The boys start a streaming service"
```

### Persona Customization
```bash
spgen generate --include "Trey Parker,Matt Stone" --exclude "Bill Hader"
```

## Production Considerations

### Performance
- Optimized for local LLM inference
- Minimal external dependencies
- Efficient state management
- Progress tracking for long-running workflows

### Monitoring
- Comprehensive logging to files and console
- Visual progress indicators
- Error tracking and debugging support
- Workflow timing and performance metrics

## Episode Summary System

### YAML-Based Episode Database
- **Schema**: Comprehensive `EpisodeSummary` dataclass with structured episode information
- **Storage**: YAML files in `episode_summaries/` directory for human-readable episode data
- **Loader**: `EpisodeSummaryLoader` class for YAML serialization/deserialization
- **Database**: `EpisodeDatabase` class for querying and managing episode collections

### Episode Schema Structure
```python
@dataclass
class EpisodeSummary:
    # Basic episode information (season, episode, title, air date, type)
    # Plot details (logline, summary, plot threads)
    # Character information (main, supporting, new characters with roles)
    # Content elements (cultural references, running gags, locations)
    # Themes and analysis (thematic elements, social commentary)
    # Continuity tracking (callbacks, setup, character development)
    # Production notes (quotes, scenes, animation, credits)
    # Context (historical, controversy, reception notes)
```

### Continuity Integration
- **Character Consistency**: Track character development across episodes
- **Running Gags**: Monitor evolution of recurring jokes and elements
- **Plot Continuity**: Connect storylines and unresolved plot threads
- **World Building**: Maintain consistency of locations and established rules
- **Cultural References**: Catalog parodies and topical content for context

### Usage in Script Generation
- **Pre-Generation Context**: Load relevant episode summaries for continuity
- **Character Voice**: Reference established character patterns and development
- **Callback Opportunities**: Identify potential references to previous episodes
- **Consistency Checking**: Ensure new content aligns with established canon

This knowledge base provides the essential context for understanding the South Park Script Generator's architecture, workflow, and capabilities for effective AI collaboration in creative writing tasks.
