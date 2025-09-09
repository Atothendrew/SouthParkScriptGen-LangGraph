# Technical Architecture Documentation 🏗️

## System Overview

The South Park Episode Generator is a sophisticated multi-agent AI system built on modern Python workflows and LangGraph orchestration. It demonstrates advanced patterns in AI collaboration, state management, and production software engineering.

## Core Architecture Patterns

### 1. **Multi-Agent Orchestration Pattern**
```python
# Each persona is a specialized agent with unique capabilities
personas = {
    "Trey Parker": {
        "bio": "Co-creator, focuses on satirical storytelling",
        "temperature": {"brainstorm": 0.9, "discussion": 0.7, "refine": 0.5},
        "prompts": {...}  # Specialized prompt templates
    }
}

# Agents collaborate through structured workflows
workflow_steps = [
    brainstorm → interactive_q_and_a → agent_feedback → merge_outlines → 
    refine → final_discussion → script_generation → assembly
]
```

### 2. **State Management Pattern**
```python
@dataclass
class EpisodeState:
    """Immutable state object that flows through the entire workflow"""
    prompt: str
    agent_outputs: List[Dict]
    discussion_history: List[str]
    merged_outline: str
    # ... all workflow data preserved
```

### 3. **Workflow Orchestration with LangGraph**
```python
def build_graph() -> StateGraph:
    graph = StateGraph(EpisodeState)
    
    # Type-safe node definitions with progress tracking
    for step in WorkflowStep:
        graph.add_node(
            step.value, 
            wrap_node_with_progress(node_func, step)
        )
    
    # Linear flow with conditional entry points
    graph.add_edge(step1, step2)  # Explicit dependencies
    
    return graph
```

## Key Design Principles

### **Type Safety First**
- Full type hints throughout codebase
- Enum-based workflow steps prevent string errors
- Structured data classes for state management
- Runtime type validation where needed

### **Comprehensive Observability**
- Dual logging (console + file) with structured formats
- Visual progress indicators for user experience
- Complete audit trail of all AI interactions
- Debug logging for troubleshooting complex workflows

### **Modular Architecture**
- Clear separation of concerns across modules
- Pluggable persona system via YAML configurations
- Extensible workflow nodes for new creative processes
- Clean interfaces between components

### **Production Ready**
- Error handling and graceful degradation
- Resource management and cleanup
- Configuration management via environment variables
- Professional logging and monitoring capabilities

## Technical Components

### **1. Workflow Engine (`workflow/`)**

#### `builder.py` - LangGraph Orchestration
```python
def wrap_node_with_progress(node_func, step: WorkflowStep):
    """Higher-order function adds logging to all workflow nodes"""
    def wrapped_node(state):
        logger.log_step_start(step)
        result = node_func(state)  # Execute actual workflow logic
        logger.log_step_complete(step)
        return result
    return wrapped_node
```

#### `logger.py` - Production Logging System
```python
class WorkflowLogger:
    """Dual-output logger with progress tracking"""
    
    def __init__(self, log_dir: str):
        # Creates both file and console handlers
        # File: Timestamped structured logging
        # Console: User-friendly progress indicators
        
    def log_step_start(self, step: WorkflowStep):
        # Visual progress bar: [██░░░░] 2/12
        # Step identification with emojis for clarity
```

#### `state.py` - Workflow State Management
```python
class EpisodeState(TypedDict):
    """Type-safe state container"""
    prompt: str
    agent_outputs: List[Dict]
    discussion_history: List[str]
    # ... maintains context across all 12 workflow steps
```

### **2. Multi-Agent System (`workflow/nodes/`)**

#### `brainstorm.py` - Creative Collaboration Engine
```python
def interactive_brainstorm_questions(state: EpisodeState) -> Dict:
    """Implements sophisticated agent-to-agent communication"""
    
    # 1. Targeted Q&A: Agent A asks specific Agent B
    for asker in personas:
        target = random.choice(other_agents)  # Realistic pairing
        question = generate_targeted_question(asker, target)
    
    # 2. Response Generation with Follow-up Support
    for responder in personas:
        response = generate_response(directed_questions)
        if contains_follow_up(response):
            schedule_follow_up_round()
    
    # 3. Multi-Round Conversation Support
    for round in range(max_rounds):
        process_follow_up_questions()
```

**Follow-up Question Pattern:**
```python
# Agents can trigger additional conversation rounds
response = """
Great idea! That could work really well.

FOLLOW-UP QUESTION FOR TREY: What if we combine that with the subplot about Randy's latest obsession?
"""

# System automatically parses and routes follow-up questions
```

#### `discussion.py` - Feedback Aggregation
```python
def merge_outlines(state: EpisodeState) -> Dict:
    """Trey Parker persona consolidates all collaborative feedback"""
    
    all_discussions = "\n\n".join(state["discussion_history"])
    # Includes: initial Q&A + responses + follow-ups + agent feedback
    
    merged_outline = llm_call(
        PERSONAS["Trey Parker"]["discussion_prompt"],
        outlines=all_individual_ideas,
        discussion=all_discussions  # Full context preservation
    )
```

#### `script.py` - Context-Aware Generation
```python
def write_act_one(state: EpisodeState) -> Dict:
    """Script generation uses full collaborative context"""
    
    discussion_context = "\n\n".join(state.get("discussion_history", []))
    # ALL previous conversations inform script writing
    
    script_prompt = f"""
    Write Act One using this outline: {merged_outline}
    
    Incorporate ideas from collaborative discussions:
    {discussion_context}
    """
```

### **3. Persona Management System**

#### YAML-Based Configuration
```yaml
# configs/Trey Parker.yaml
bio: "Co-creator of South Park, satirical storytelling focus"
brainstorm_prompt: |
  You are Trey Parker brainstorming a South Park episode.
  Focus on satirical social commentary with absurd escalation.
  Episode idea: {prompt}
  
discussion_prompt: |
  You are Trey Parker providing feedback in a writers' room.
  Build on others' ideas while maintaining satirical edge.
  
temperature:
  brainstorm: 0.9    # High creativity for initial ideas
  discussion: 0.7    # Balanced for collaboration
  refine: 0.5        # Focused for polish
```

#### Dynamic Persona Loading
```python
def load_personas() -> Dict[str, PersonaConfig]:
    """Dynamically loads all YAML persona configurations"""
    personas = {}
    for config_file in glob("configs/*.yaml"):
        with open(config_file) as f:
            persona_data = yaml.safe_load(f)
            personas[extract_name(config_file)] = persona_data
    return personas
```

## Advanced Technical Features

### **1. Intelligent Conversation Routing**
```python
def parse_follow_up_questions(response_text: str) -> List[FollowUpQuestion]:
    """Robust parsing of follow-up conversation triggers"""
    
    # Pattern: "FOLLOW-UP QUESTION FOR [NAME]: [question]"
    pattern = r"FOLLOW-UP QUESTION FOR\s+([^:]+):\s*(.+)"
    
    for match in re.finditer(pattern, response_text):
        target_name = match.group(1).strip()
        question = match.group(2).strip()
        
        # Route to appropriate persona for response
        yield FollowUpQuestion(
            asker=extract_asker_from_response(response_text),
            target=target_name,
            question=question
        )
```

### **2. Context Preservation Architecture**
```python
# Information flows through all workflow phases:
initial_ideas → targeted_questions → responses → follow_ups → 
agent_feedback → merged_outline → refined_outline → 
final_discussion → script_generation

# Each phase preserves and builds upon previous context
def preserve_context(current_phase_output: Dict, accumulated_context: List[str]):
    return accumulated_context + [format_for_context(current_phase_output)]
```

### **3. Multi-Part Episode Continuity**
```python
@dataclass
class EpisodeContinuity:
    """Maintains story continuity across episode parts"""
    part_number: int
    total_parts: int
    previous_summaries: List[str]
    character_developments: List[str]
    running_gags: List[str]
    established_locations: List[str]
    
def extract_continuity_elements(completed_episode: EpisodeState) -> EpisodeContinuity:
    """AI-powered extraction of continuity elements"""
    # Analyzes completed script for:
    # - Character growth moments
    # - Running gag establishment
    # - Unresolved plot threads
    # - New location introductions
```

## Performance Characteristics

### **Computational Requirements**
- **Memory**: ~500MB peak (excluding LLM inference)
- **CPU**: Moderate during workflow orchestration
- **GPU**: Depends on LLM backend (LM Studio handles inference)
- **Storage**: ~5-10MB per generated episode with full logs

### **Scalability Considerations**
- **Concurrent Episodes**: Limited by LLM backend capacity
- **Persona Scaling**: Linear scaling with number of active personas
- **Multi-Part Episodes**: State preservation across parts adds minimal overhead
- **File I/O**: Efficient batched writes with UTF-8 encoding

### **Error Handling Strategy**
```python
def robust_llm_call(prompt: str, **kwargs) -> str:
    """Production-grade LLM interaction with fallbacks"""
    try:
        return llm_api_call(prompt, **kwargs)
    except ConnectionError:
        logger.warning("LLM connection failed, using fallback response")
        return generate_fallback_response(prompt)
    except ValidationError:
        logger.error("Invalid LLM response format")
        return retry_with_cleaner_prompt(prompt)
```

## Extension Points

### **Adding New Workflow Steps**
1. Define new enum value in `WorkflowStep`
2. Implement node function in appropriate module
3. Add to workflow graph in `builder.py`
4. Update progress tracking and logging

### **Custom Persona Creation**
1. Create YAML config in `configs/` directory
2. Define unique prompts and temperature settings
3. Restart system to load new persona
4. Use `--include_personas` to test

### **New Output Formats**
1. Extend `EpisodeState` with new fields
2. Add generation logic in appropriate node
3. Update file output in workflow completion
4. Enhance logging for new outputs

---

*This architecture demonstrates production-ready AI system design with emphasis on maintainability, observability, and extensibility.*