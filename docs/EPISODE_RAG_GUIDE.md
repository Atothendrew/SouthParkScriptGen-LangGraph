# South Park Episode RAG System

## Overview

The South Park Episode RAG (Retrieval-Augmented Generation) system provides semantic search capabilities over historical South Park episodes to help AI personas reference existing content when brainstorming new episodes. This system is based on the [LangGraph Agentic RAG tutorial](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/#1-preprocess-documents) and implements intelligent document grading and query rewriting.

## Features

✅ **Semantic Search** - Find episodes by themes, characters, cultural references, or plot elements  
✅ **Intelligent Grading** - Automatically assess relevance of retrieved episodes  
✅ **Query Rewriting** - Improve search results with automatic query enhancement  
✅ **LangGraph Integration** - Available as a tool in the brainstorming workflow  
✅ **Comprehensive Coverage** - Searches across plot, characters, themes, and production notes

## Architecture

```
Episode YAML Files → Document Processing → Vector Embeddings → Semantic Search
                                                              ↓
Query Input → Initial Search → Relevance Grading → Results (or Query Rewrite)
```

### Components

1. **Document Preprocessing** (`EpisodeRAG.preprocess_episodes()`)
   - Loads YAML episode summaries from `episode_summaries/` directory
   - Converts structured data to searchable text
   - Splits into chunks for optimal retrieval

2. **Vector Storage** (`EpisodeRAG.create_vectorstore()`)
   - Uses OpenAI embeddings for semantic understanding
   - In-memory vector store for fast retrieval
   - Configurable retrieval parameters

3. **Document Grading** (`EpisodeRAG.grade_episode_relevance()`)
   - LLM-powered relevance assessment
   - Considers themes, characters, cultural references, and plot elements
   - Binary scoring with reasoning

4. **Query Enhancement** (`EpisodeRAG.rewrite_query()`)
   - Automatic query improvement when no relevant results found
   - Focuses on South Park-specific concepts and running gags

## Usage

### Basic Search

```python
from spgen.tools.episode_rag import search_south_park_episodes

# Search for episodes about specific themes
result = search_south_park_episodes.invoke({
    "query": "episodes about Kenny dying"
})
print(result)
```

### Advanced Usage

```python
from spgen.tools.episode_rag import EpisodeRAG, EpisodeRAGConfig

# Custom configuration
config = EpisodeRAGConfig(
    chunk_size=500,
    chunk_overlap=100,
    retrieval_k=5
)

# Initialize RAG system
rag = EpisodeRAG(config)
rag.initialize()

# Search with detailed results
results = rag.search_episodes("Cartman schemes and manipulation", max_results=3)
for result in results:
    print(f"Episode: {result['metadata']['title']}")
    print(f"Relevance: {result['relevance']}")
    print(f"Content: {result['content'][:200]}...")
```

### Integration with Workflow

The Episode RAG tool is automatically available to all AI personas during brainstorming:

```python
from spgen.workflow.llm_provider import get_available_tools

tools = get_available_tools()
# ['search_tool', 'search_south_park_episodes']
```

## Configuration

### EpisodeRAGConfig Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `episode_summaries_dir` | `"episode_summaries"` | Directory containing episode YAML files |
| `chunk_size` | `500` | Size of text chunks for embedding |
| `chunk_overlap` | `100` | Overlap between chunks |
| `embedding_model` | `"text-embedding-3-small"` | OpenAI embedding model |
| `retrieval_k` | `5` | Number of documents to retrieve |
| `temperature` | `0.0` | Temperature for grading model |

### Environment Setup

The system requires OpenAI API access for embeddings and grading:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Example Queries and Results

### Successful Searches

1. **"episodes about Kenny dying"** → Found 3 relevant episodes
   - S1E3: Volcano
   - S1E1: Cartman Gets an Anal Probe  
   - S1E9: Mr. Hankey, the Christmas Poo

2. **"Cartman schemes and manipulation"** → Found 3 relevant episodes
   - S1E2: Weight Gain 4000
   - S1E1: Cartman Gets an Anal Probe
   - S1E2: Weight Gain 4000

3. **"episodes with aliens or supernatural elements"** → Found 3 relevant episodes
   - S1E1: Cartman Gets an Anal Probe
   - S1E3: Volcano (hunting/supernatural themes)
   - S1E10: Damien (supernatural character)

4. **"Christmas or holiday episodes"** → Found 1 relevant episode
   - S1E9: Mr. Hankey, the Christmas Poo

### Query Rewriting Examples

When no relevant results are found, the system automatically improves queries:

- `"test query"` → `"South Park episodes featuring key themes of social commentary, character dynamics between Stan, Kyle, Cartman, and Kenny, cultural parodies of current events..."`

## Available Episodes

Currently loaded episodes from Season 1:
- S01E01: Cartman Gets an Anal Probe
- S01E02: Weight Gain 4000  
- S01E03: Volcano
- S01E04: Big Gay Al's Big Gay Boat Ride
- S01E05: An Elephant Makes Love to a Pig
- S01E06: Death
- S01E07: Pinkeye
- S01E08: Starvin' Marvin
- S01E09: Mr. Hankey, the Christmas Poo
- S01E10: Damien
- S01E11: Tom's Rhinoplasty
- S01E12: Mecha-Streisand
- S01E13: Cartman's Mom is a Dirty Slut

## Performance

- **Preprocessing**: 13 episodes → 48-80 text chunks
- **Search Speed**: ~1-2 seconds per query with grading
- **Accuracy**: Intelligent relevance filtering reduces false positives
- **Memory Usage**: In-memory vector store for fast retrieval

## How Personas Can Use This

During brainstorming sessions, AI personas can now:

1. **Reference Similar Themes**: "Find episodes about political satire to inspire our new episode about social media"

2. **Check Character Consistency**: "How has Cartman's manipulation been portrayed in past episodes?"

3. **Avoid Repetition**: "What alien-related episodes have we already done?"

4. **Find Running Gags**: "Which episodes feature the 'Oh my God, they killed Kenny!' running gag?"

5. **Cultural Reference Inspiration**: "Find episodes that parodied celebrities for ideas on our new episode"

## Troubleshooting

### Common Issues

1. **"No module named 'langchain_community'"**
   ```bash
   pip install langchain-community langchain-openai langchain-text-splitters
   ```

2. **"Episode RAG system not available"**
   - Ensure OpenAI API key is set
   - Check that episode_summaries directory exists
   - Verify YAML files are properly formatted

3. **Poor search results**
   - Use more specific queries
   - Include character names and themes
   - The system works better with South Park-specific concepts

### Debug Mode

```python
from spgen.tools.episode_rag import get_episode_rag

rag = get_episode_rag()
documents = rag.preprocess_episodes()
print(f"Loaded {len(documents)} documents")
```

## Future Enhancements

- **Multi-season Support**: Expand beyond Season 1
- **Character-specific Search**: Find episodes by character focus
- **Theme Clustering**: Group episodes by similar themes
- **Production Notes Search**: Search by writers, directors, or production details
- **Cross-episode References**: Find connected storylines across episodes

## API Reference

### Core Classes

- `EpisodeRAG`: Main RAG system class
- `EpisodeRAGConfig`: Configuration object
- `EpisodeGrade`: Relevance grading schema

### Key Functions

- `search_south_park_episodes(query: str)`: Tool function for LangGraph integration
- `get_episode_rag()`: Get global RAG instance
- `initialize_episode_rag(config)`: Initialize with custom config

### Workflow Integration

- `get_available_tools()`: Returns list including episode search tool
- Tools automatically available in brainstorm.py, discussion.py, and script.py nodes

---

**Built with ❤️ for South Park script generation using LangGraph and LangChain**
