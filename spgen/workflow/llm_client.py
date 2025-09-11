"""LLM client and tools for South Park episode generation."""

import os
from typing import List

from openai import OpenAI
from langchain_core.tools import tool

# Load LMStudio endpoint from environment variable or default
LMSTUDIO_ENDPOINT = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")


@tool
def search_tool(query: str) -> str:
    """Searches the web for the given query."""
    # In a real application, you would integrate a web search API here.
    # For this example, we'll return a dummy response.
    return f"Search results for '{query}': South Park is an American animated sitcom created by Trey Parker and Matt Stone."


def llm_call(template: str, temperature: float = 0.7, tools: List = None, **kwargs) -> str:
    """Call LMStudio chat completion with the given template and kwargs."""
    prompt = template.format(**kwargs)
    client = OpenAI(base_url=LMSTUDIO_ENDPOINT, api_key="not-needed")
    
    messages = [{"role": "user", "content": prompt}]

    # Note: LMStudio typically doesn't support function calling, so we ignore tools
    # In a production system, you would handle tool calling separately
    response = client.chat.completions.create(
        model="llama3.1",
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
