"""LLM client and tools for South Park episode generation."""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from langchain_core.tools import tool, BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load LMStudio endpoint from environment variable or default
LMSTUDIO_ENDPOINT = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")


def log_tool_call(
    tool_name: str, tool_args: Dict[str, Any], tool_result: str, log_dir: str = None
) -> None:
    """
    Log tool calls and responses to tool_calls.txt file.

    Args:
        tool_name: Name of the tool that was called
        tool_args: Arguments passed to the tool
        tool_result: Result returned by the tool
        log_dir: Directory to write the log file (uses current working directory if None)
    """
    if log_dir is None:
        # Try to get log_dir from environment or current directory
        log_dir = os.getcwd()

    tool_log_file = os.path.join(log_dir, "tool_calls.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare log entry
    log_entry = f"""
===============================================
TOOL CALL: {timestamp}
===============================================
Tool: {tool_name}
Args: {json.dumps(tool_args, indent=2, ensure_ascii=False)}
Result Length: {len(str(tool_result))} characters
Result Preview: {str(tool_result)[:200]}{"..." if len(str(tool_result)) > 200 else ""}

Full Result:
{tool_result}

"""

    # Append to tool calls log file
    try:
        with open(tool_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Could not write to tool log file {tool_log_file}: {e}")


# Global variable to store current log directory
_current_log_dir = None


def set_tool_log_dir(log_dir: str) -> None:
    """Set the global log directory for tool call logging."""
    global _current_log_dir
    _current_log_dir = log_dir


def get_tool_log_dir() -> str:
    """Get the current log directory for tool call logging."""
    global _current_log_dir
    return _current_log_dir or os.getcwd()


# Import Episode RAG tool
try:
    from spgen.tools.episode_rag import search_south_park_episodes

    episode_rag_available = True
except ImportError:
    episode_rag_available = False
    print("⚠️  Episode RAG system not available - continuing with basic tools")

# Import DuckDuckGo search tools
try:
    from spgen.tools.duckduckgo_search import (
        search_web,
        search_news,
        search_trending_topics,
    )

    ddg_tools_available = True
except ImportError:
    ddg_tools_available = False
    print("⚠️  DuckDuckGo search tools not available - continuing without web search")


# Export tool logging functions for use by other modules
__all__ = [
    "llm_call",
    "llm_call_with_model",
    "get_available_tools",
    "log_tool_call",
    "set_tool_log_dir",
    "get_tool_log_dir",
]


def get_available_tools():
    """Get list of available tools for LLM calls."""
    tools = []  # Always include the basic search tool

    if episode_rag_available:
        tools.append(search_south_park_episodes)

    if ddg_tools_available:
        tools.extend([search_web, search_news, search_trending_topics])

    return tools


def llm_call(
    template: str, temperature: float = 0.7, tools: List = None, **kwargs
) -> tuple[str, str]:
    """
    Call LLM chat completion and return both content and model name.

    Args:
        template: Prompt template string
        temperature: Sampling temperature (0.0 to 1.0)
        tools: List of LangChain tools
        **kwargs: Template formatting parameters

    Returns:
        tuple[str, str]: (content, model_name)
    """
    prompt = template.format(**kwargs)
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # Determine API settings
    if os.getenv("OPENAI_BASE_URL") and os.getenv("OPENAI_API_KEY"):
        # Use provided API endpoint
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    else:
        # Use LMStudio endpoint
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=LMSTUDIO_ENDPOINT,
            api_key="not-needed",
        )

    # Check if we should use tools (only for non-LMStudio endpoints)
    use_tools = (
        tools
        and os.getenv("OPENAI_API_KEY")
        and os.getenv("OPENAI_BASE_URL")
        and os.getenv("OPENAI_BASE_URL") != LMSTUDIO_ENDPOINT
    )

    if use_tools:
        # Bind tools to the model for tool-enabled calls
        llm_with_tools = llm.bind_tools(tools)

        # Create message and invoke
        message = HumanMessage(content=prompt)
        response = llm_with_tools.invoke([message])

        # Handle tool calls if present
        content = response.content
        if response.tool_calls:
            print(f"🔧 Model made {len(response.tool_calls)} tool calls")

            # Execute tool calls and add results to conversation
            tool_messages = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the tool
                tool_result = None
                for tool in tools:
                    if tool.name == tool_name:
                        try:
                            tool_result = tool.invoke(tool_args)
                            print(
                                f"🔧 Executed {tool_name}: {str(tool_result)[:100]}..."
                            )

                            # Log the tool call and result
                            log_dir = get_tool_log_dir()
                            log_tool_call(
                                tool_name, tool_args, str(tool_result), log_dir
                            )

                            # Log the absolute path to the tool calls file
                            tool_log_file = os.path.join(log_dir, "tool_calls.txt")
                            print(
                                f"📝 Tool call logged to: {os.path.abspath(tool_log_file)}"
                            )

                            break
                        except Exception as e:
                            print(f"❌ Error executing {tool_name}: {e}")
                            tool_result = f"Error: {e}"

                            # Log the failed tool call
                            log_dir = get_tool_log_dir()
                            log_tool_call(tool_name, tool_args, tool_result, log_dir)

                            # Log the absolute path to the tool calls file
                            tool_log_file = os.path.join(log_dir, "tool_calls.txt")
                            print(
                                f"📝 Failed tool call logged to: {os.path.abspath(tool_log_file)}"
                            )

                if tool_result is not None:
                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": str(tool_result),
                        }
                    )

            # If we have tool results, get a final response
            if tool_messages:
                # Convert to LangChain format and get final response
                from langchain_core.messages import ToolMessage

                conversation = [message, response]
                for tm in tool_messages:
                    conversation.append(
                        ToolMessage(
                            content=tm["content"], tool_call_id=tm["tool_call_id"]
                        )
                    )

                final_response = llm.invoke(conversation)
                content = final_response.content

        # Get usage information if available
        usage_info = ""
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            usage_info = f", Usage: input={usage.get('input_tokens', 0)}, output={usage.get('output_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        elif (
            hasattr(response, "response_metadata")
            and "token_usage" in response.response_metadata
        ):
            usage = response.response_metadata["token_usage"]
            usage_info = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        else:
            # Debug: check what metadata is available
            if hasattr(response, "response_metadata"):
                # Check for usage in a different format
                metadata = response.response_metadata
                if "usage" in metadata:
                    usage = metadata["usage"]
                    usage_info = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"

        print(
            f"📊 Model: {model_name}, Tool calls: {len(response.tool_calls) if response.tool_calls else 0}{usage_info}"
        )

        return content.strip() if content else "", model_name

    else:
        # Use ChatOpenAI without tools
        message = HumanMessage(content=prompt)
        response = llm.invoke([message])

        content = response.content if response.content else ""

        # Get usage information if available
        usage_info = ""
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = response.usage_metadata
            usage_info = f", Usage: input={usage.get('input_tokens', 0)}, output={usage.get('output_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        elif (
            hasattr(response, "response_metadata")
            and "token_usage" in response.response_metadata
        ):
            usage = response.response_metadata["token_usage"]
            usage_info = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"
        else:
            # Check for usage in a different format
            if hasattr(response, "response_metadata"):
                metadata = response.response_metadata
                if "usage" in metadata:
                    usage = metadata["usage"]
                    usage_info = f", Usage: input={usage.get('prompt_tokens', 0)}, output={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}"

        print(
            f"📊 Model: {model_name}, Tool calls: {len(response.tool_calls) if response.tool_calls else 0}{usage_info}"
        )

        return content.strip(), model_name


# Backward compatibility alias (deprecated - use llm_call directly)
def llm_call_with_model(
    template: str, temperature: float = 0.7, tools: List = None, **kwargs
) -> tuple[str, str]:
    """
    Deprecated: Use llm_call() directly instead.

    This function is kept for backward compatibility but will be removed in future versions.
    """
    return llm_call(template, temperature, tools, **kwargs)
