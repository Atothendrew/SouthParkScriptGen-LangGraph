"""LLM client and tools for South Park episode generation."""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

# Load LMStudio endpoint from environment variable or default
LMSTUDIO_ENDPOINT = os.getenv("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1")

# Import LM Studio client
try:
    from .lm_studio_client import (
        llm_call_with_lmstudio,
        check_lmstudio_availability,
        get_available_models
    )
    LMSTUDIO_SDK_AVAILABLE = True
except ImportError:
    LMSTUDIO_SDK_AVAILABLE = False
    print("⚠️  LM Studio SDK client not available")

# ---------- Tool-call logging utilities ----------
# Import shared logging utilities from LM Studio client
try:
    from .lm_studio_client import log_tool_call, set_tool_log_dir, get_tool_log_dir
except ImportError:
    # Fallback logging utilities if LM Studio client not available
    def log_tool_call(
        tool_name: str, tool_args: Dict[str, Any], tool_result: str, log_dir: Optional[str] = None
    ) -> None:
        """Log tool calls and responses to tool_calls.txt file."""
        if log_dir is None:
            log_dir = os.getcwd()

        tool_log_file = os.path.join(log_dir, "tool_calls.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        try:
            with open(tool_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ Could not write to tool log file {tool_log_file}: {e}")

    _current_log_dir: Optional[str] = None

    def set_tool_log_dir(log_dir: str) -> None:
        """Set the global log directory for tool call logging."""
        global _current_log_dir
        _current_log_dir = log_dir

    def get_tool_log_dir() -> str:
        """Get the current log directory for tool call logging."""
        return _current_log_dir or os.getcwd()

# ---------- Optional tools (RAG + DDG) ----------

try:
    from spgen.tools.episode_rag import search_south_park_episodes
    episode_rag_available = True
except ImportError:
    episode_rag_available = False
    print("⚠️  Episode RAG system not available - continuing with basic tools")

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
    tools = []
    if episode_rag_available:
        tools.append(search_south_park_episodes)
    if ddg_tools_available:
        tools.extend([search_web, search_news, search_trending_topics])
    return tools

# ---------- LLM invocation ----------

def _build_llm(temperature: float) -> ChatOpenAI:
    """
    Build a ChatOpenAI client from env:
      - If OPENAI_API_KEY is set (with or without OPENAI_BASE_URL) -> use OpenAI (or custom-compatible) endpoint.
      - Else -> use LM Studio at LMSTUDIO_ENDPOINT with a dummy key.
    """
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if api_key:
        # Use OpenAI (or compatible) with provided API key; pass base_url only if provided
        kwargs: Dict[str, Any] = dict(model=model_name, temperature=temperature, api_key=api_key)
        if base_url:
            kwargs["base_url"] = base_url
        return ChatOpenAI(**kwargs)
    else:
        # Fall back to LM Studio
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            base_url=LMSTUDIO_ENDPOINT,
            api_key="not-needed",
        )

def _safe_tool_calls_len(msg: Any) -> int:
    tc = getattr(msg, "tool_calls", None)
    return len(tc) if isinstance(tc, list) else 0

def _extract_usage_strings(msg: Any) -> str:
    usage_info = ""
    try:
        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
            u = msg.usage_metadata
            usage_info = f", Usage: input={u.get('input_tokens', 0)}, output={u.get('output_tokens', 0)}, total={u.get('total_tokens', 0)}"
        elif hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
            rm = msg.response_metadata
            if "token_usage" in rm and isinstance(rm["token_usage"], dict):
                tu = rm["token_usage"]
                usage_info = f", Usage: input={tu.get('prompt_tokens', 0)}, output={tu.get('completion_tokens', 0)}, total={tu.get('total_tokens', 0)}"
            elif "usage" in rm and isinstance(rm["usage"], dict):
                tu = rm["usage"]
                usage_info = f", Usage: input={tu.get('prompt_tokens', 0)}, output={tu.get('completion_tokens', 0)}, total={tu.get('total_tokens', 0)}"
    except Exception:
        pass
    # Try to add reasoning tokens if available
    try:
        thinking_tokens = 0
        # usage_metadata
        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
            u = msg.usage_metadata
            thinking_tokens = max(thinking_tokens, int(u.get("reasoning_tokens", 0) or u.get("thinking_tokens", 0) or u.get("total_reasoning_tokens", 0) or 0))
            thinking_tokens = max(thinking_tokens, int(u.get("reasoning_input_tokens", 0) or 0) + int(u.get("reasoning_output_tokens", 0) or 0))
        # response_metadata
        if hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
            rm = msg.response_metadata
            for container_key in ("token_usage", "usage"):
                if container_key in rm and isinstance(rm[container_key], dict):
                    tu = rm[container_key]
                    thinking_tokens = max(thinking_tokens, int(tu.get("reasoning_tokens", 0) or tu.get("thinking_tokens", 0) or tu.get("total_reasoning_tokens", 0) or 0))
                    thinking_tokens = max(thinking_tokens, int(tu.get("reasoning_input_tokens", 0) or 0) + int(tu.get("reasoning_output_tokens", 0) or 0))
        if thinking_tokens > 0:
            usage_info += f", thinking={thinking_tokens}"
    except Exception:
        pass
    return usage_info

def _extract_model_name(msg: Any, default_model: str) -> str:
    try:
        if hasattr(msg, "response_metadata") and isinstance(msg.response_metadata, dict):
            meta = msg.response_metadata
            return meta.get("model_name") or meta.get("model") or default_model
    except Exception:
        pass
    return default_model

def llm_call(
    template: str,
    temperature: float = 0.7,
    tools: Optional[List[Any]] = None,
    override_use_lmstudio_sdk: Optional[bool] = False,
    **kwargs
) -> tuple[str, str]:
    """
    Call LLM chat completion and return both content and model name.

    Returns:
        tuple[str, str]: (content, model_name)
    """
    prompt = template.format(**kwargs)
    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    # Determine which client to use:
    # 1. OpenAI if API key is available
    # 2. LM Studio SDK if available and has models loaded
    # 3. OpenAI-compatible API endpoint as fallback
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    use_openai = bool(api_key)
    use_lmstudio_sdk = (
        override_use_lmstudio_sdk is not False and (
            override_use_lmstudio_sdk is True or (
                override_use_lmstudio_sdk is None and
                LMSTUDIO_SDK_AVAILABLE and
                check_lmstudio_availability() and
                not use_openai
            )
        )
    )
    use_openai_compatible = not use_openai and not use_lmstudio_sdk

    # Use LM Studio SDK if available and no OpenAI key
    if use_lmstudio_sdk:
        print("🤖 Using LM Studio SDK with tool calling support")
        try:
            lmstudio_model = os.getenv("LMSTUDIO_MODEL", "default")
            return llm_call_with_lmstudio(
                template=prompt,
                temperature=temperature,
                tools=tools,
                model_name=lmstudio_model,
                **kwargs
            )
        except Exception as e:
            print(f"❌ LM Studio SDK failed: {e}, falling back to OpenAI-compatible mode")
            use_openai_compatible = True

    llm = _build_llm(temperature=temperature)

    # Determine if we should enable tool calling:
    # - OpenAI supports tools natively
    # - LM Studio SDK supports tools (handled above)
    # - OpenAI-compatible servers may not support tools fully
    use_tools = (tools is not None) and (use_openai or use_lmstudio_sdk)

    message = HumanMessage(content=prompt)

    if use_tools:
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke([message])
        content = response.content or ""

        # Execute tool calls if present
        tool_calls = getattr(response, "tool_calls", None) or []
        if tool_calls:
            print(f"🔧 Model made {len(tool_calls)} tool call(s)")
            tool_messages: List[ToolMessage] = []

            for tc in tool_calls:
                tool_name = tc.get("name")
                tool_args = tc.get("args", {})
                tool_result = None

                # Find the tool by name
                for t in tools:
                    if getattr(t, "name", None) == tool_name:
                        try:
                            tool_result = t.invoke(tool_args)
                            preview = str(tool_result)
                            print(f"🔧 Executed {tool_name}: {preview[:100]}{'...' if len(preview) > 100 else ''}")

                            log_tool_call(tool_name, tool_args, preview, get_tool_log_dir())
                            print(f"📝 Tool call logged to: {os.path.abspath(os.path.join(get_tool_log_dir(), 'tool_calls.txt'))}")
                        except Exception as e:
                            err = f"Error: {e}"
                            print(f"❌ Error executing {tool_name}: {e}")
                            log_tool_call(tool_name, tool_args, err, get_tool_log_dir())
                            print(f"📝 Failed tool call logged to: {os.path.abspath(os.path.join(get_tool_log_dir(), 'tool_calls.txt'))}")
                            tool_result = err
                        break  # stop after the first matching tool

                if tool_result is not None:
                    tool_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tc.get("id")))

            # Follow-up model call with tool results
            if tool_messages:
                conversation = [message, response, *tool_messages]
                final_response = llm.invoke(conversation)
                content = (final_response.content or "").strip()
        else:
            final_response = None

        # Metrics / model name
        usage_info = _extract_usage_strings(final_response or response)
        actual_model_name = _extract_model_name(final_response or response, model_name)
        print(f"📊 Model: {actual_model_name}, Tool calls: {_safe_tool_calls_len(response)}{usage_info}")

        return content.strip(), actual_model_name

    # --- No tools path ---
    response = llm.invoke([message])
    content = (response.content or "").strip()

    usage_info = _extract_usage_strings(response)
    actual_model_name = _extract_model_name(response, model_name)
    print(f"📊 Model: {actual_model_name}, Tool calls: {_safe_tool_calls_len(response)}{usage_info}")

    return content, actual_model_name

# Backward compatibility alias (deprecated - use llm_call directly)
def llm_call_with_model(
    template: str, temperature: float = 0.7, tools: Optional[List[Any]] = None, **kwargs
) -> tuple[str, str]:
    """Deprecated: Use llm_call() directly instead."""
    return llm_call(template, temperature, tools, **kwargs)