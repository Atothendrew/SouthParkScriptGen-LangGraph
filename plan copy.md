# Plan: South Park Episode Generator

This document outlines the plan for creating a langgraph example application that writes South Park episodes.

## 1. Core Concept

The application will use a multi-agent system to simulate a writer's room, where different comedic personas collaborate to create a South Park episode based on a user's prompt. The process will be transparent, with the agents' discussions and the script's evolution saved to markdown files.

## 2. Agents

We will create agents representing the following individuals:

*   **Trey Parker:** The showrunner, will have the final say on the script.
*   **Matt Stone:** Co-creator, will focus on the social commentary and satire.
*   **Bill Hader:** Master of voices and characters, will contribute to character development and dialogue.
*   **Andy Samberg:** Known for his digital shorts, will bring a modern and absurd sense of humor.
*   **Conan O'Brien:** A master of wit and absurdity, will contribute to the overall comedic tone.
*   **Chris Farley:** High-energy and physical comedian, will inspire over-the-top and chaotic scenes.

Each agent will be a langgraph-powered LLM with a specific persona and instructions.

## 3. The Graph (Workflow)

We will use a `StatefulGraph` to manage the workflow. The state will contain:

*   `topic`: The user's initial prompt.
*   `ideas`: A list of initial episode ideas from each agent.
*   `selected_idea`: The idea chosen for the episode.
*   `script`: The evolving script.
*   `discussion_history`: A log of the agents' conversation.

The graph will have the following nodes:

1.  **`initial_ideas`:** Each agent generates an initial idea based on the topic.
2.  **`discuss_ideas`:** The agents discuss and critique the generated ideas.
3.  **`select_idea`:** Trey Parker (the showrunner) selects the best idea.
4.  **`write_script`:** The agents collaborate on writing the script.
5.  **`refine_script`:** The agents review and refine the script.
6.  **`finalize_script`:** The final script is produced.

## 4. Output

At each stage of the process, the application will write the current state (ideas, discussion, script) to a markdown file. This will create a clear audit trail of the creative process. The final output will be a markdown file containing the complete episode script.

## 5. Project Structure

The project will be organized as follows:

*   `agents.py`: Defines the agents and their personas.
*   `graph.py`: Defines the langgraph graph and the workflow.
*   `cli.py`: Provides a command-line interface for running the application.
*   `logger.py`: Handles logging.
*   `plan.md`: This document.
*   `output/`: A directory where the markdown files will be saved.

## 6. Implementation Steps

1.  **Setup:** Initialize the project, install dependencies, and create the file structure.
2.  **Agents:** Implement the agents in `agents.py`.
3.  **Graph:** Build the graph in `graph.py`.
4.  **CLI:** Create the CLI in `cli.py`.
5.  **Testing:** Test the application with various prompts.
