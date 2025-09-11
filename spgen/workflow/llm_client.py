"""LLM client and tools for South Park episode generation."""

import os
from typing import List, Optional

from openai import OpenAI
from langchain_core.tools import tool

# Load LMStudio endpoint from environment variable or default
LMSTUDIO_ENDPOINT = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")


# class LLMClient:
#     """
#     LLM client for generating responses using OpenAI-compatible APIs.

#     Supports both OpenAI API and local LMStudio endpoints.
#     """

#     def __init__(
#         self,
#         base_url: Optional[str] = None,
#         api_key: Optional[str] = None,
#         model: Optional[str] = None,
#     ):
#         """
#         Initialize the LLM client.

#         Args:
#             base_url: API base URL (defaults to environment or LMStudio)
#             api_key: API key (defaults to environment or "not-needed" for LMStudio)
#             model: Model name (defaults to environment or "gpt-oss-20b")
#         """
#         # Determine base URL
#         if base_url:
#             self.base_url = base_url
#         elif os.getenv("OPENAI_BASE_URL"):
#             self.base_url = os.getenv("OPENAI_BASE_URL")
#         else:
#             self.base_url = LMSTUDIO_ENDPOINT

#         # Determine API key
#         if api_key:
#             self.api_key = api_key
#         elif os.getenv("OPENAI_API_KEY"):
#             self.api_key = os.getenv("OPENAI_API_KEY")
#         else:
#             self.api_key = "not-needed"

#         # Determine model
#         if model:
#             self.model = model
#         else:
#             self.model = os.environ.get("OPENAI_MODEL", "gpt-oss-20b")

#         # Initialize OpenAI client
#         self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

#     def generate_response(
#         self,
#         prompt: str,
#         temperature: float = 0.7,
#         max_tokens: Optional[int] = None,
#         tools: Optional[List] = None,
#     ) -> str:
#         """
#         Generate a response using the LLM.

#         Args:
#             prompt: The input prompt
#             temperature: Sampling temperature (0.0 to 1.0)
#             max_tokens: Maximum tokens to generate
#             tools: List of tools (currently ignored for LMStudio compatibility)

#         Returns:
#             Generated response text
#         """
#         try:
#             messages = [{"role": "user", "content": prompt}]

#             # Prepare completion parameters
#             completion_params = {
#                 "model": self.model,
#                 "messages": messages,
#                 "temperature": temperature,
#             }

#             # Add max_tokens if specified
#             if max_tokens is not None:
#                 completion_params["max_tokens"] = max_tokens

#             # Note: LMStudio typically doesn't support function calling, so we ignore tools
#             # In a production system, you would handle tool calling separately
#             response = self.client.chat.completions.create(**completion_params)

#             # Print usage information if available
#             if hasattr(response, "usage") and response.usage:
#                 print(f"{response.usage=}")

#             # Handle cases where content might be None
#             content = response.choices[0].message.content
#             if content is None:
#                 return ""

#             return content.strip()

#         except Exception as e:
#             print(f"❌ Error generating LLM response: {e}")
#             return f"Error: Failed to generate response - {str(e)}"

#     def generate(self, prompt: str, temperature: float = 0.7, **kwargs) -> str:
#         """
#         Alias for generate_response for backward compatibility.

#         Args:
#             prompt: The input prompt
#             temperature: Sampling temperature
#             **kwargs: Additional parameters

#         Returns:
#             Generated response text
#         """
#         return self.generate_response(prompt, temperature, **kwargs)


@tool
def search_tool(query: str) -> str:
    """Searches the web for the given query."""
    # In a real application, you would integrate a web search API here.
    # For this example, we'll return a dummy response.
    return f"Search results for '{query}': South Park is an American animated sitcom created by Trey Parker and Matt Stone."


def llm_call(template: str, temperature: float = 0.7, tools: List = None, **kwargs) -> str:
    """Call LMStudio chat completion with the given template and kwargs."""
    prompt = template.format(**kwargs)

    if (i := os.getenv("OPENAI_BASE_URL")) and (k := os.getenv("OPENAI_API_KEY")):
        client = OpenAI(base_url=i, api_key=k)
    else:
        client = OpenAI(base_url=LMSTUDIO_ENDPOINT, api_key="not-needed")

    messages = [{"role": "user", "content": prompt}]

    # Note: LMStudio typically doesn't support function calling, so we ignore tools
    # In a production system, you would handle tool calling separately
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-oss-20b"),
        messages=messages,
        temperature=temperature,
    )

    print(f"{response.usage=}")

    # Handle cases where content might be None
    content = response.choices[0].message.content
    if content is None:
        return ""
    return content.strip()


def llm_call_with_model(
    template: str, temperature: float = 0.7, tools: List = None, **kwargs
) -> tuple[str, str]:
    """Call LMStudio chat completion and return both content and model name."""
    prompt = template.format(**kwargs)

    if (i := os.getenv("OPENAI_BASE_URL")) and (k := os.getenv("OPENAI_API_KEY")):
        client = OpenAI(base_url=i, api_key=k)
    else:
        client = OpenAI(base_url=LMSTUDIO_ENDPOINT, api_key="not-needed")

    messages = [{"role": "user", "content": prompt}]

    # Note: LMStudio typically doesn't support function calling, so we ignore tools
    # In a production system, you would handle tool calling separately
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-oss-20b"),
        messages=messages,
        temperature=temperature,
    )

    print(f"{response.usage=}")

    # Handle cases where content might be None
    content = response.choices[0].message.content
    if content is None:
        content = ""

    # Get the model name from the response
    model_name = (
        response.model
        if hasattr(response, "model")
        else os.environ.get("OPENAI_MODEL", "gpt-oss-20b")
    )

    return content.strip(), model_name
