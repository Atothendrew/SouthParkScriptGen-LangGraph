# South Park Episode Generator 🎬

A sophisticated AI-powered system that generates South Park episodes through collaborative multi-agent brainstorming, leveraging LangGraph workflows to simulate a writers' room environment.

## 🏗️ Architecture Overview

### Core Philosophy
This system simulates the collaborative creative process of a real writers' room, where multiple personas (Trey Parker, Matt Stone, Bill Hader, Andy Samberg, etc.) work together to brainstorm, refine, and develop episode ideas through structured discussion and feedback loops.

### Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                    South Park Episode Generator              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐     │
│  │   Personas  │    │   Workflow   │    │   Logging   │     │
│  │   System    │    │    Engine    │    │   System    │     │
│  └─────────────┘    └──────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         │            ┌──────────────┐            │          │
│         └────────────│  LangGraph   │────────────┘          │
│                      │  Orchestrator│                       │
│                      └──────────────┘                       │
│                             │                               │
│                      ┌──────────────┐                       │
│                      │   LLM API    │                       │
│                      │ (LM Studio)  │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Workflow Architecture

The episode generation follows a **13-step collaborative workflow**:

> 📋 **Visual Workflow Diagram**: See [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) for a complete visual representation of the LangGraph flow.

### Phase 1: Initial Creation
1. **Research Current Events** (optional) - Gather news context for topical episodes
2. **Initial Brainstorming** - Each persona generates independent episode ideas
3. **Interactive Q&A** - Agents ask targeted questions to specific other agents
4. **Agent Feedback** - Collaborative discussion and critique

### Phase 2: Refinement
5. **Merge Outlines** - Trey Parker consolidates ideas using all feedback
6. **Refine Outline** - Each persona refines the merged concept
7. **Final Discussion** - Last round of collaborative feedback

### Phase 3: Script Generation
8. **Write Act One** - Generate opening act with full context
9. **Write Act Two** - Develop conflict and raise stakes  
10. **Write Act Three** - Resolution and conclusion
11. **Stitch Script** - Combine acts into complete episode
12. **Summarize Script** - Generate episode summary

## 🤖 Multi-Agent System

### Persona Management
Each writer persona is defined with:
- **Unique voice and comedy style**
- **Character background and perspective**
- **Temperature settings** for different creative phases
- **Specialized prompts** for brainstorming, discussion, and refinement

### Intelligent Interactions
- **Targeted Q&A**: Agents ask specific other agents focused questions
- **Follow-up Conversations**: Support for multi-round back-and-forth discussions
- **Collaborative Refinement**: Ideas evolve through genuine peer feedback
- **Context Preservation**: All discussions inform final script generation

## 🔧 Technical Implementation

### Technology Stack
- **Python 3.8+** with type hints throughout
- **LangGraph** for workflow orchestration
- **LM Studio** for local LLM inference
- **YAML** configuration for persona management
- **Structured logging** with file and console output

### Key Design Patterns

#### 1. **Enum-Based Workflow Steps**
```python
class WorkflowStep(Enum):
    BRAINSTORM = "brainstorm"
    INTERACTIVE_BRAINSTORM_QUESTIONS = "interactive_brainstorm_questions"
    # ... etc
```
Ensures type safety and consistent step tracking.

#### 2. **Comprehensive Logging**
```python
class WorkflowLogger:
    def log_step_start(self, step: WorkflowStep):
        # Progress tracking with visual indicators
        progress = "█" * step_num + "░" * remaining
        self.logger.info(f"📊 Progress: [{progress}] {step_num}/{total}")
```

#### 3. **Stateful Workflow Management**
```python
@dataclass 
class EpisodeState:
    prompt: str
    agent_outputs: List[Dict]
    discussion_history: List[str]
    merged_outline: str
    # ... maintains context across all steps
```

## 📁 Project Structure

```
southpark-langgraph/
├── README.md                    # This file
├── cli.py                      # Command-line interface
├── agents.py                   # Persona management system
├── configs/                    # Individual persona configurations
│   ├── Trey Parker.yaml
│   ├── Matt Stone.yaml
│   └── ...
├── workflow/                   # Core workflow engine
│   ├── __init__.py
│   ├── builder.py             # LangGraph workflow definition
│   ├── logger.py              # Logging system with enum steps
│   ├── llm_client.py         # LLM API integration
│   ├── state.py              # Workflow state management
│   └── nodes/                # Individual workflow nodes
│       ├── brainstorm.py     # Initial creation & Q&A
│       ├── discussion.py     # Feedback & outline merging  
│       └── script.py         # Script generation
└── logs/                     # Generated episode outputs
    └── {episode_title}_{timestamp}/
        ├── process.txt       # Complete workflow log
        ├── ideas/           # Initial brainstorming
        ├── brainstorm_questions/ # Agent questions
        ├── brainstorm_responses/ # Agent responses
        ├── final_merged_outline.md
        └── script.md        # Final episode script
```

## 🚀 Usage

### Basic Episode Generation
```bash
uv run python spgen/cli.py "Episode idea here"
```

### Multi-Part Episodes
```bash
uv run python spgen/cli.py "Epic storyline" -n 3  # Generate 3-part episode
```

### Persona Selection
```bash
# Include specific writers only
uv run python spgen/cli.py "Episode idea" --include_personas "Trey Parker,Matt Stone,Bill Hader"

# Exclude certain writers
uv run python spgen/cli.py "Episode idea" --exclude_personas "Chris Farley,Conan O'Brian"
```

### Dynamic News Integration
```bash
uv run python spgen/cli.py "Episode idea" --dynamic_prompt  # Include current events
```

## 📊 Output Examples

### Process Logging (`process.txt`)
```
2025-01-10 15:30:45 - 🚀 Starting episode generation for part 1 of 1...
2025-01-10 15:30:45 - 📁 Working directory: logs/episode_20250110_153045/part_01
2025-01-10 15:30:45 - ⏳ Step 1/12: Brainstorm
2025-01-10 15:30:45 - 📊 Progress: [█░░░░░░░░░░░] 1/12
2025-01-10 15:30:45 - 🧠 Starting initial brainstorming phase...
2025-01-10 15:30:45 - 📝 4 personas will brainstorm ideas: Trey Parker, Matt Stone, Bill Hader, Andy Samberg
2025-01-10 15:30:46 - 💡 Trey Parker is generating an initial idea...
2025-01-10 15:30:52 - ✅ Trey Parker completed their idea (saved to ideas/Trey Parker.md)
```

### Collaborative Q&A Structure
```markdown
# Interactive Brainstorm Q&A Session

**Trey Parker asks Bill Hader:**
Hey Bill, I love the anxiety spiral concept with Kyle. What if we made his "cat-speech" 
accidentally trigger the portal opening? Like his nervous tics literally break reality?

**Bill Hader responds:**
That's brilliant, Trey! And what if every time Kyle tries to explain what happened, 
his explanation gets more absurd and actually makes the situation worse?

FOLLOW-UP QUESTION FOR TREY: Should Kyle's anxiety be the key to closing the portal too?
```

## 🎯 Key Features for Management

### Business Value
- **Automated Content Generation**: Reduces initial drafting time for creative teams
- **Consistent Quality**: Maintains South Park's signature style through persona modeling
- **Scalable Process**: Can generate multiple episodes or multi-part storylines
- **Iterative Refinement**: Built-in collaborative feedback loops improve output quality

### Technical Excellence
- **Type-Safe Codebase**: Full Python type hints prevent runtime errors
- **Comprehensive Logging**: Complete audit trail of creative process
- **Modular Architecture**: Easy to extend with new personas or workflow steps
- **Error Handling**: Graceful degradation with fallback responses

### Monitoring & Observability
- **Real-time Progress Tracking**: Visual progress bars and step completion
- **Detailed Process Logs**: Every decision and interaction logged with timestamps
- **File-based Outputs**: All intermediate and final results saved for review
- **Performance Metrics**: Track generation time and LLM usage

## 🔧 Configuration

### LLM Setup
Set your LM Studio endpoint:
```bash
export LMSTUDIO_ENDPOINT="http://localhost:1234/v1"
```

### Persona Customization
Each persona is fully configurable via YAML:
```yaml
# configs/Custom Writer.yaml
bio: "Description of writer's style and background"
brainstorm_prompt: "Template for initial idea generation"
discussion_prompt: "Template for collaborative feedback"
refine_prompt: "Template for outline refinement"
temperature:
  brainstorm: 0.9    # High creativity for initial ideas
  discussion: 0.7    # Balanced for collaboration  
  refine: 0.5        # Focused for polishing
```

## 📈 Performance Characteristics

- **Episode Generation Time**: ~10-15 minutes for full episode (model dependent)
- **Memory Usage**: ~500MB peak (excludes LLM inference)
- **Disk Usage**: ~5-10MB per generated episode with full logs
- **Extensibility**: Adding new workflow steps requires minimal code changes

---

*This system demonstrates advanced AI orchestration, multi-agent collaboration, and production-ready software engineering practices in the creative content domain.*