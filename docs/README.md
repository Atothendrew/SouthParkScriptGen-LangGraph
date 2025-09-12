# South Park Episode Generator - Documentation

This directory contains comprehensive documentation for the South Park Episode Generator system.

## 📋 Documentation Index

### Core Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns
- **[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)** - Visual workflow diagrams and process flows
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive usage instructions

### Episode Management
- **[EPISODE_RAG_GUIDE.md](EPISODE_RAG_GUIDE.md)** - Episode RAG system documentation
- **[EPISODE_CREATION_GUIDELINES.md](EPISODE_CREATION_GUIDELINES.md)** - Guidelines for creating new episode summaries

### LLM Integration
- **[CLAUDE.md](CLAUDE.md)** - Claude-specific integration notes
- **[GEMINI.md](GEMINI.md)** - Gemini-specific integration notes
- **[LLM_TOOLS_PROPOSAL.md](LLM_TOOLS_PROPOSAL.md)** - LLM tools architecture proposal

## 🎯 Quick Reference

### For Users
1. Start with [USAGE_GUIDE.md](USAGE_GUIDE.md) for basic usage
2. Refer to [EPISODE_RAG_GUIDE.md](EPISODE_RAG_GUIDE.md) for episode search capabilities

### For Developers
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Check [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) for process flows
3. See [LLM_TOOLS_PROPOSAL.md](LLM_TOOLS_PROPOSAL.md) for tools architecture

### For Content Creators
1. Follow [EPISODE_CREATION_GUIDELINES.md](EPISODE_CREATION_GUIDELINES.md) for creating new episodes
2. Use the validation tools in `../tools/` to ensure quality

## 🛠️ Related Tools

The main tools for working with the system are located in `../tools/`:
- `validate_episode.py` - Validate episode YAML files
- `test_episode_yaml.py` - Test episode database loading

---

For the main project overview, see the [main README](../README.md).
