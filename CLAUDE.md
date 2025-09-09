# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangGraph-based South Park episode generator that simulates a creative writing workshop using multiple AI personas (Trey Parker, Matt Stone, Bill Hader, Andy Samberg, Conan O'Brian, Chris Farley, etc.). The system creates episodes through collaborative brainstorming, discussion, and iterative refinement.

## Architecture

### Core Components

- **`southpark-langgraph/graph.py`**: Main LangGraph workflow definition with nodes for brainstorming, agent feedback, outline merging, refinement, and script generation
- **`southpark-langgraph/agents.py`**: Persona management system that loads YAML configurations from `configs/` directory
- **`southpark-langgraph/cli.py`**: Command-line interface for episode generation
- **`southpark-langgraph/configs/*.yaml`**: Individual persona configurations containing bio, style, prompts, and temperature settings

### Workflow Structure

The episode generation follows this multi-stage process:
1. **Brainstorm**: Each persona generates initial outlines
2. **Agent Feedback**: Personas critique and discuss each other's ideas  
3. **Merge Outlines**: Trey Parker persona consolidates feedback into single outline
4. **Refine Outline**: Each persona refines the merged outline
5. **Final Discussion**: Second round of feedback on refined outlines
6. **Script Generation**: Three-act script writing (Act One → Act Two → Act Three)
7. **Script Assembly**: Stitching acts together and generating summary

## Development Commands

### Running the Application
```bash
cd southpark-langgraph
python cli.py "Your episode idea here"
```

### Multi-part Episodes
```bash
python cli.py "Episode idea" -n 3  # Generate 3-part episode
```

### Persona Selection
```bash
# Include specific personas only
python cli.py "Episode idea" --include_personas "Trey Parker,Matt Stone,Bill Hader"

# Exclude specific personas
python cli.py "Episode idea" --exclude_personas "Chris Farley,Conan O'Brian"
```

## LLM Configuration

The system uses LMStudio as the default LLM provider:
- **Endpoint**: Configurable via `LMSTUDIO_ENDPOINT` environment variable (default: `http://localhost:1234/v1`)
- **Model**: Uses `llama3.1` model by default
- **Integration**: Uses OpenAI-compatible API through the `openai` Python package

### Setting Up LMStudio
```bash
export LMSTUDIO_ENDPOINT="http://localhost:1234/v1"
```

## Persona System

Each persona is defined in `configs/{Name}.yaml` with:
- **bio**: Character background and style description
- **brainstorm_prompt**: Template for initial outline generation
- **discussion_prompt**: Template for collaborative feedback
- **refine_prompt**: Template for outline refinement
- **temperature**: Dict with different temperature values for brainstorm/discussion/refine phases

## Output Structure

Generated episodes are saved in `logs/` with this structure:
```
logs/{sanitized_episode_title}_{timestamp}/
├── prompt.md                    # Original user prompt
├── agent_outlines.md           # Initial brainstorm outputs
├── discussion_feedback.md      # Agent feedback and discussion
├── final_merged_outline.md     # Consolidated outline
├── script.md                   # Final three-act script
└── brainstorm/                 # Individual agent brainstorm files
    ├── Trey Parker.md
    ├── Matt Stone.md
    └── ...
```

## Key Technical Details

- **State Management**: Uses `EpisodeState` TypedDict for managing workflow state across nodes
- **File Handling**: All outputs are written to markdown files with UTF-8 encoding
- **Error Handling**: Basic error handling in LLM calls, uses dummy responses for unavailable tools
- **Concurrency**: Sequential node execution (no parallel processing of agents)

## Code Conventions

- Uses type hints throughout (`typing.Dict`, `typing.List`, etc.)
- Follows Python naming conventions (snake_case for functions/variables)
- Extensive use of f-strings for string formatting
- Each graph node returns a dict with updated state fields
- YAML configuration files use consistent structure across all personas