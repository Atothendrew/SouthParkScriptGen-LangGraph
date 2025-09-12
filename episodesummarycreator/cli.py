import sys
import os
import argparse

# Add project root to Python path to allow importing from spgen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from episodesummarycreator.workflow import build_summary_creator_graph, EpisodeSummaryState

def main():
    parser = argparse.ArgumentParser(description="Create missing South Park episode summaries.")
    # No arguments needed for now, as the workflow finds missing episodes automatically.
    args = parser.parse_args()

    app = build_summary_creator_graph()

    initial_state = {
        "all_episodes": [],
        "existing_episodes": set(),
    }

    print("🚀 Starting episode summary creation for all missing episodes...")
    app.invoke(initial_state)
    print("\n✅ Workflow complete!")

if __name__ == "__main__":
    main()

