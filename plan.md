# South Park Episode Generator Plan

## Overview
Create a LangGraph application that simulates a creative writing workshop with six “agents” representing Trey Parker, Matt Stone, Bill Hader, Andy Samburg, Conan O’Brian, and Chris Farley.  
The workflow:

1. **Prompt Intake** – User supplies a high‑level episode idea (e.g., “A school trip to the moon”).
2. **Initial Brainstorm** – Each agent independently generates a short outline or concept.
3. **Collaborative Discussion** – Agents compare, critique, and merge ideas to produce a single episode outline.
4. **Script Drafting** – The chosen outline is expanded into a full script.
5. **Markdown Logging** – Every step (agent thoughts, discussion notes, draft versions) is written to a Markdown file so the evolution of the episode can be tracked.

## Detailed Steps & Checklist
- [ ] **Project Setup**  
  - Create `southpark-langgraph/` directory.  
  - Initialize a Python virtual environment and install LangGraph, LLM provider SDK (e.g., OpenAI), and helper libraries.  
  - Add a `README.md` with project description.

- [ ] **Define Agent Personas**  
  - Create `agents.py` mapping each agent name to a brief bio / style description and prompt templates for brainstorming and discussion.

- [ ] **Build LangGraph Flow**  
  - `graph.py`:  
    - Node: *Prompt Intake* – receives user prompt.  
    - Nodes: *Brainstorming* (one per agent) – each calls LLM with its persona prompt.  
    - Node: *Discussion* – aggregates all brainstorm outputs, runs a second LLM pass to compare and merge.  
    - Node: *Script Draft* – expands merged outline into a full script.  
  - Use LangGraph’s `AgentNode` and `StatefulGraph`.

- [ ] **Logging Mechanism**  
  - Implement `logger.py` that writes:  
    - Agent brainstorm outputs.  
    - Discussion notes (selected best idea, reasons).  
    - Draft script versions with timestamps.  
  - Store logs in `logs/` directory, one Markdown file per episode.

- [ ] **User Interface**  
  - Simple CLI (`cli.py`) that:  
    - Prompts for episode idea.  
    - Runs the graph.  
    - Displays final script and path to log file.

- [ ] **Testing & Validation**  
  - Unit tests for each graph node.  
  - Integration test that runs a full episode generation and checks log file creation.

- [ ] **Documentation**  
  - Update `README.md` with usage instructions.  
  - Add a `CONTRIBUTING.md`.

- [ ] **Optional Enhancements**  
  - Web UI with FastAPI + React.  
  - Agent voting on best outline before drafting.

## Deliverables
| Item | Description |
|------|-------------|
| `southpark-langgraph/` | Project root |
| `agents.py` | Persona definitions |
| `graph.py` | LangGraph workflow |
| `logger.py` | Markdown logging |
| `cli.py` | Command‑line interface |
| `logs/episode-<id>.md` | Generated episode logs |
| `README.md`, `CONTRIBUTING.md` | Documentation |

## Next Steps
1. Create project skeleton (directories, virtualenv, dependencies).  
2. Implement persona module (`agents.py`).  
3. Build LangGraph nodes in `graph.py`.  
4. Add logging (`logger.py`).  
5. Write CLI to tie everything together.  
6. Run a test episode and verify Markdown log.
