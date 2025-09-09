# GEMINI.md

## Project Overview

This project is a sophisticated AI-powered system that generates South Park episodes through collaborative multi-agent brainstorming. It leverages LangGraph workflows to simulate a writers' room environment where multiple AI personas, each with a unique voice and style, collaborate to create episode ideas, outlines, and scripts.

The project is built with Python and utilizes a number of libraries, including LangGraph for workflow orchestration and YAML for persona configuration. The system is designed to be highly modular and extensible, allowing for the easy addition of new personas or workflow steps.

### Key Technologies

*   **Python 3.8+**: The core programming language.
*   **LangGraph**: Used for orchestrating the multi-agent workflow.
*   **YAML**: For configuring the AI personas.
*   **LM Studio**: For local LLM inference.

### Architecture

The system follows a 12-step collaborative workflow:

1.  **Research Current Events** (optional)
2.  **Initial Brainstorming**
3.  **Interactive Q&A**
4.  **Agent Feedback**
5.  **Merge Outlines**
6.  **Refine Outline**
7.  **Final Discussion**
8.  **Write Act One**
9.  **Write Act Two**
10. **Write Act Three**
11. **Stitch Script**
12. **Summarize Script**

Each step in the workflow is a node in the LangGraph, and the state of the episode is passed from node to node.

## Building and Running

### Prerequisites

*   Python 3.8+
*   LM Studio (or another OpenAI-compatible API)

### Installation

1.  Clone the repository.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Set the `LMSTUDIO_ENDPOINT` environment variable to your LM Studio endpoint:

    ```bash
    export LMSTUDIO_ENDPOINT="http://localhost:1234/v1"
    ```

2.  (Optional) Customize the AI personas by editing the YAML files in the `configs` directory.

### Running the Generator

To generate a South Park episode, run the `cli.py` script with a prompt:

```bash
python spgen/cli.py "The kids build a startup that sells AI-generated South Park episodes"
```

You can also use the following options:

*   `-n, --num_parts`: Generate a multi-part episode.
*   `--include_personas`: Specify a comma-separated list of personas to include.
*   `--exclude_personas`: Specify a comma-separated list of personas to exclude.
*   `--dynamic-prompt`: Generate an episode prompt from current trending news.

## Development Conventions

### Code Style

The project follows the PEP 8 style guide for Python code. Type hints are used throughout the codebase.

### Testing

The project uses pytest for testing. To run the tests, install the test requirements and run pytest:

```bash
pip install -r requirements-test.txt
pytest
```

### Contribution Guidelines

*   When adding new personas, create a new YAML file in the `configs` directory.
*   When adding new workflow steps, create a new node in the `spgen/workflow/nodes` directory and add it to the graph in `spgen/workflow/builder.py`.
*   Ensure that all new code is well-documented and includes type hints.
*   Write tests for all new functionality.
