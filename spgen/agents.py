import os
import yaml
from typing import Dict

CONFIGS_DIR = "configs"

def is_script(prompt: str) -> bool:
    """Check if a prompt is a script."""
    return "\nEXT." in prompt or "\nINT." in prompt

def load_personas() -> Dict[str, Dict]:
    personas = {}
    for filename in os.listdir(CONFIGS_DIR):
        if filename.endswith(".yaml"):
            name = os.path.splitext(filename)[0]
            with open(os.path.join(CONFIGS_DIR, filename), 'r') as f:
                personas[name] = yaml.safe_load(f)
    return personas

PERSONAS = load_personas()

def get_persona(name: str) -> Dict:
    """Return persona dict for given name."""
    return PERSONAS.get(name, {})